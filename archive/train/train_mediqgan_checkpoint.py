# -*- coding: utf-8 -*-
"""
[준비 스크립트 ③] MediQ-GAN 사전학습 - 3일차 미세조정용 checkpoint 생성.

- 16큐빗 시뮬레이션이 비싸(샘플당 약 3초) 수업에서는 이 checkpoint에서 출발해 미세조정만 함
- 입력은 전처리 npy(0~1)뿐이라 Kaggle 불필요. 로컬 CPU epoch당 약 7.8분(25 epoch 196분)
- 중간 checkpoint(--save_every)를 남김. 수렴한 모델로는 미세조정 손실이 거의 움직이지 않아 덜 학습된 본을 수업용으로 씀
- 마지막 epoch이 최선은 아님(uniform z 실측: 40 epoch이 20 epoch보다 나빴음). 출력되는 [품질] 수치로 고를 것
- 학습률: lr_g 0.02로는 3 epoch 만에 loss_d 0.0027로 붕괴함. DCGAN 관례(lr 2e-4, betas (0.5, 0.999))가 기본값
- 척도: real을 2x-1로 맞춰 Tanh 출력과 학습함. 평가 때는 gen_metrics.to_unit_scale(x, "tanh")

실행 예:
    C:/qmlvenv/Scripts/python.exe -X utf8 train_mediqgan_checkpoint.py \
        --npy ../../practice/assets/df_preprocessed.npy --out_dir ./checkpoints --epochs 30 --save_every 5
    ... --resume ./checkpoints/mediqgan_last.pt          # 이어하기
    C:/qmlvenv/Scripts/python.exe -X utf8 train_mediqgan_checkpoint.py --smoke   # 합성 데이터로 코드 점검(1분 이내)
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

# 품질 모니터링용 gen_metrics는 practice/에 있음
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "practice"))

from mediqgan_toy import ToyDualStreamGenerator
from qgan_model import ClassicalDiscriminator


def load_real(npy_path, img_size, max_n=None):
    """전처리 npy(0~1) → Tanh 척도(-1~1) 평탄화 텐서."""
    arr = np.load(npy_path)
    if arr.ndim == 3:
        if arr.shape[1] != img_size:
            raise ValueError(f"npy 해상도 {arr.shape[1]}x{arr.shape[2]}가 --img_size {img_size}와 다름 "
                             f"- 16x16 재생성이 안 된 파일일 수 있음")
        arr = arr.reshape(len(arr), -1)
    if arr.shape[1] != img_size * img_size:
        raise ValueError(f"npy 차원 {arr.shape[1]} != img_size^2 {img_size * img_size}")
    if max_n:
        arr = arr[:max_n]
    if arr.min() < -0.01 or arr.max() > 1.01:
        raise ValueError(f"npy 값 범위가 0~1이 아님(min {arr.min():.3f}, max {arr.max():.3f}) - 척도 규약 위반")
    return torch.tensor(arr * 2.0 - 1.0, dtype=torch.float32)


def sample_z(n, in_dim, dist="uniform", device="cpu"):
    return torch.rand(n, in_dim, device=device) if dist == "uniform" else torch.randn(n, in_dim, device=device)


def train_step(generator, discriminator, real_batch, opt_g, opt_d, in_dim, device="cpu", z_dist="uniform"):
    """MediQ-GAN 한 step (표준 BCE GAN, 판별자는 논문 Table 4)."""
    bce = nn.BCELoss()
    bsz = real_batch.shape[0]
    real_labels = torch.ones(bsz, 1, device=device)
    fake_labels = torch.zeros(bsz, 1, device=device)

    # --- 판별자 ---
    opt_d.zero_grad()
    loss_d_real = bce(discriminator(real_batch), real_labels)
    z = sample_z(bsz, in_dim, z_dist, device)
    fake = generator(z).detach()
    loss_d_fake = bce(discriminator(fake), fake_labels)
    loss_d = loss_d_real + loss_d_fake
    loss_d.backward()
    opt_d.step()

    # --- 생성자 (양자 stream까지 역전파) ---
    opt_g.zero_grad()
    z = sample_z(bsz, in_dim, z_dist, device)
    loss_g = bce(discriminator(generator(z)), real_labels)
    loss_g.backward()
    opt_g.step()

    return loss_g.item(), loss_d.item()


def save_checkpoint(path, generator, discriminator, cfg, history, epoch, opt_g=None, opt_d=None):
    """옵티마이저 상태까지 저장 (없으면 --resume 직후 학습이 흔들림)."""
    payload = {
        "generator_state_dict": generator.state_dict(),
        "discriminator_state_dict": discriminator.state_dict(),
        "config": cfg,
        "history": history,
        "epoch": epoch,
    }
    if opt_g is not None:
        payload["opt_g_state_dict"] = opt_g.state_dict()
        payload["opt_d_state_dict"] = opt_d.state_dict()
    torch.save(payload, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--npy", help="전처리 완료 npy 경로(0~1). --smoke일 때는 불필요")
    ap.add_argument("--out_dir", default="./checkpoints")
    ap.add_argument("--img_size", type=int, default=16, help="2일차 자산과 같아야 함")
    ap.add_argument("--n_qubits", type=int, default=16, help="원 논문 스펙 16 (내리지 말 것)")
    ap.add_argument("--q_depth", type=int, default=8, help="원 논문 그림 기준 8(레포 CLI 기본값은 6)")
    ap.add_argument("--n_generators", type=int, default=5, help="원 논문 스펙 5")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch_size", type=int, default=4,
                    help="키워도 빨라지지 않음 (샘플마다 회로를 따로 실행)")
    ap.add_argument("--lr_g", type=float, default=2e-4,
                    help="DCGAN 관례. QGAN처럼 크게 두면 mode collapse")
    ap.add_argument("--lr_d", type=float, default=2e-4)
    ap.add_argument("--beta1", type=float, default=0.5, help="GAN 관례 0.5 (0.9는 불안정)")
    ap.add_argument("--z_dist", default="normal", choices=["uniform", "normal"],
                    help="잠재벡터 분포 (normal이 uniform보다 다양성·상관 모두 좋았음)")
    ap.add_argument("--save_every", type=int, default=5, help="중간 checkpoint 저장 간격(epoch)")
    ap.add_argument("--max_n", type=int, default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--resume", default=None, help="이어할 checkpoint 경로")
    ap.add_argument("--smoke", action="store_true",
                    help="합성 데이터·축소 스펙으로 코드만 점검")
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.smoke:
        args.n_qubits, args.q_depth, args.n_generators = 6, 2, 2
        args.epochs, args.img_size = 3, 16
        rng = np.random.default_rng(0)
        yy, xx = np.mgrid[0:args.img_size, 0:args.img_size]
        blob = np.exp(-((yy - args.img_size / 2) ** 2 + (xx - args.img_size / 2) ** 2) / 8.0)
        synth = np.clip(blob[None] + rng.normal(0, 0.1, (12, args.img_size, args.img_size)), 0, 1)
        real = torch.tensor(synth.reshape(12, -1) * 2 - 1, dtype=torch.float32)
        print("[smoke] 합성 데이터 12장 · 축소 스펙으로 코드 점검만 수행")
    else:
        if not args.npy:
            ap.error("--npy가 필요함(또는 --smoke로 코드만 점검)")
        real = load_real(args.npy, args.img_size, args.max_n)
        print(f"학습 데이터: {len(real)}장 ({args.img_size}x{args.img_size}, Tanh 척도로 변환됨)")

    in_dim = args.img_size * args.img_size
    gen = ToyDualStreamGenerator(in_dim=in_dim, n_qubits=args.n_qubits, q_depth=args.q_depth,
                                 n_generators=args.n_generators, out_dim=in_dim)
    disc = ClassicalDiscriminator(input_dim=in_dim)
    cfg = {"img_size": args.img_size, "in_dim": in_dim, "n_qubits": args.n_qubits,
           "q_depth": args.q_depth, "n_generators": args.n_generators,
           "scale": "tanh", "lr_g": args.lr_g, "lr_d": args.lr_d, "beta1": args.beta1,
           "z_dist": args.z_dist, "batch_size": args.batch_size}
    print(f"생성자 스펙: {args.n_generators}개 sub-generator × {args.n_qubits}큐빗, depth {args.q_depth} "
          f"| site_dim={gen.site_dim}, 사용 site={gen.site_idx}")

    betas = (args.beta1, 0.999)
    opt_g = torch.optim.Adam(gen.parameters(), lr=args.lr_g, betas=betas)
    opt_d = torch.optim.Adam(disc.parameters(), lr=args.lr_d, betas=betas)

    history = {"loss_g": [], "loss_d": [], "epoch_sec": []}
    start_epoch = 0
    if args.resume:
        ck = torch.load(args.resume, map_location="cpu")
        gen.load_state_dict(ck["generator_state_dict"])
        disc.load_state_dict(ck["discriminator_state_dict"])
        history = ck.get("history", history)
        start_epoch = ck.get("epoch", 0)
        if "opt_g_state_dict" in ck:
            opt_g.load_state_dict(ck["opt_g_state_dict"])
            opt_d.load_state_dict(ck["opt_d_state_dict"])
            print("옵티마이저 상태(Adam 모멘텀)도 복원함")
        else:
            print("주의: 이 checkpoint에는 옵티마이저 상태가 없음(구버전) - 이어하는 몇 epoch은 학습이 흔들릴 수 있음")
        print(f"이어하기: {args.resume} (epoch {start_epoch}부터)")

    steps_per_epoch = max(1, len(real) // args.batch_size)
    print(f"epoch당 {steps_per_epoch}step · 총 {args.epochs - start_epoch}epoch 예정")

    t_start = time.time()
    for epoch in range(start_epoch, args.epochs):
        t_ep = time.time()
        perm = torch.randperm(len(real))
        ep_g, ep_d = [], []
        for s in range(steps_per_epoch):
            idx = perm[s * args.batch_size:(s + 1) * args.batch_size]
            if len(idx) == 0:
                continue
            lg, ld = train_step(gen, disc, real[idx], opt_g, opt_d, in_dim, z_dist=args.z_dist)
            ep_g.append(lg); ep_d.append(ld)
            history["loss_g"].append(lg); history["loss_d"].append(ld)
        dt = time.time() - t_ep
        history["epoch_sec"].append(dt)
        ep_d_mean = float(np.mean(ep_d))
        if ep_d_mean < 0.01:
            print("  주의: 판별자 완승(loss_d < 0.01) - 생성자가 학습 신호를 잃는 상태임. "
                  "lr_g를 더 낮추거나 라벨 스무딩을 쓸 것. 이대로 계속 돌려도 쓸 수 있는 checkpoint가 안 나옴",
                  flush=True)
        done = epoch + 1 - start_epoch
        eta = (args.epochs - epoch - 1) * (time.time() - t_start) / max(1, done)
        print(f"[epoch {epoch + 1}/{args.epochs}] loss_g {np.mean(ep_g):.4f} | loss_d {np.mean(ep_d):.4f} "
              f"| {dt / 60:.1f}분 | 남은 예상 {eta / 60:.0f}분", flush=True)

        # 품질 모니터링 - 저장 시점마다 상관계수·다양성을 찍어 조용히 망가지는 것을 막음
        if args.save_every and (epoch + 1) % args.save_every == 0:
            try:
                import gen_metrics as _gm
                with torch.no_grad():
                    probe = gen(sample_z(8, in_dim, args.z_dist)).numpy().reshape(8, args.img_size, args.img_size)
                pu = _gm.to_unit_scale(probe, "tanh")
                ru = _gm.to_unit_scale(real.numpy().reshape(len(real), -1) / 2 + 0.5, "unit")
                ru = ru.reshape(len(real), args.img_size, args.img_size)
                corr = _gm.mean_image_correlation(pu, _gm.class_mean_image(ru)).mean()
                div = _gm.sample_diversity(pu)["pairwise_mean"]
                print(f"  [품질] 클래스평균 상관 {corr:.3f} / 샘플간 다양성 {div:.3f} "
                      f"(실제 데이터 다양성 {_gm.sample_diversity(ru)['pairwise_mean']:.3f})", flush=True)
            except Exception as e:
                print(f"  [품질] 측정 실패(학습엔 영향 없음): {e}", flush=True)

        # 중단 대비 최신본 + 수업용 중간본
        save_checkpoint(out_dir / "mediqgan_last.pt", gen, disc, cfg, history, epoch + 1, opt_g, opt_d)
        if args.save_every and (epoch + 1) % args.save_every == 0 and (epoch + 1) < args.epochs:
            mid = out_dir / f"mediqgan_e{epoch + 1:03d}.pt"
            save_checkpoint(mid, gen, disc, cfg, history, epoch + 1, opt_g, opt_d)
            print(f"  → 중간 checkpoint 저장: {mid.name} (3일차 미세조정 출발점 후보)")

    final = out_dir / "mediqgan_final.pt"
    save_checkpoint(final, gen, disc, cfg, history, args.epochs, opt_g, opt_d)
    with open(out_dir / "mediqgan_history.json", "w", encoding="utf-8") as f:
        json.dump({"config": cfg, **history}, f, ensure_ascii=False, indent=2)

    with torch.no_grad():
        sample = gen(sample_z(4, in_dim, args.z_dist)).numpy()
    print(f"\n완료 - 총 {(time.time() - t_start) / 60:.1f}분")
    print(f"최종 checkpoint: {final}")
    print(f"생성 샘플 값 범위: {sample.min():.3f} ~ {sample.max():.3f} (Tanh이므로 -1~1이 정상)")
    print("3일차에서는 gen_metrics.to_unit_scale(x, \"tanh\")로 0~1로 되돌려 QGAN과 비교할 것")


if __name__ == "__main__":
    main()
