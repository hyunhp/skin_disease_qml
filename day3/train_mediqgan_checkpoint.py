# -*- coding: utf-8 -*-
"""
[준비 스크립트 ③] MediQ-GAN(ToyDualStreamGenerator) 사전학습 — 3일차 라이브 미세조정용 체크포인트 생성.

2026-10-01 커리큘럼 재설계: 3일차는 "원 논문 스펙(16큐빗×5·depth 8)을 유지한 채 사전학습
체크포인트를 불러와 수업 중 10~60스텝만 미세조정"하는 방식이다. 16큐빗은 상태벡터
시뮬레이션 자체가 비용(실측 샘플당 2.99s)이라 전체 학습을 라이브로 돌릴 수 없기 때문.
→ 이 스크립트가 그 사전학습을 담당한다.

⚠ Kaggle이 필요 없다. 입력은 전처리 완료된 npy(0~1, (N, img_size, img_size))뿐이므로
   로컬에서 밤새 돌리면 된다. 실측 기준 DF 115장 × 30에폭 ≈ 2.9시간.

⚠ 체크포인트를 2개 이상 남긴다 — 최종본과 **덜 학습된 중간본**. 이미 수렴한 모델에서
   10~25스텝 미세조정하면 손실이 거의 움직이지 않아 3일차 "학습 체험"이 심심해지므로,
   중간본(--save_every로 저장됨)을 수업용 출발점으로 쓴다.

⚠ 에폭을 늘리면 좋아지는 게 아니다(2026-10-01 실측): uniform z 기준 40에폭이 20에폭보다 나빴다
   (상관 0.207 -> 0.114, Tanh 포화 88%% -> 97%%). 생성자가 포화 쪽으로 드리프트하므로, --save_every로
   중간 체크포인트를 남기고 **출력되는 [품질] 수치로 최적 에폭을 골라 쓸 것**(마지막 체크포인트가 최선이 아님).

⚠ 학습률 주의(2026-10-01 사고): 처음엔 QGAN과 같은 lr_g=0.02를 썼는데 3에폭 만에 loss_d가 0.0027로
   붕괴하고 다양성 0.000(모드붕괴)까지 겹쳤다. MediQ-GAN은 고전 MLP 디코더가 출력을 만들어 Tanh가
   포화되면 z와 무관한 상수 이미지가 나온다. DCGAN 관례(lr 2e-4, betas (0.5,0.999))가 기본값이며,
   8큐빗 축소판 실측으로 loss_d 1.387(이론 균형 ln4=1.386)·상관 0.207을 확인했다. 기본값을 올리지 말 것.

척도: 입력 npy는 0~1인데 생성자 출력이 Tanh(-1~1)이므로 real을 2x-1로 매핑해 학습한다
      (공식 레포·DCGAN 관례). 평가·시각화 때 0~1로 되돌리는 것은 gen_metrics.to_unit_scale(x, "tanh").

실행 예:
    # 본 학습(로컬 밤샘) — 중간 체크포인트는 5에폭마다
    C:/qmlvenv/Scripts/python.exe -X utf8 train_mediqgan_checkpoint.py \
        --npy assets/df_preprocessed.npy --out_dir ./checkpoints --epochs 30 --save_every 5

    # 중단된 학습 이어하기
    ... --resume ./checkpoints/mediqgan_last.pt

    # 코드만 빠르게 점검(합성 데이터·축소 스펙, 1분 이내)
    C:/qmlvenv/Scripts/python.exe -X utf8 train_mediqgan_checkpoint.py --smoke
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

from mediqgan_toy import ToyDualStreamGenerator
from qgan_model import ClassicalDiscriminator


def load_real(npy_path, img_size, max_n=None):
    """전처리 npy(0~1) → Tanh 척도(-1~1) 평탄화 텐서."""
    arr = np.load(npy_path)
    if arr.ndim == 3:
        if arr.shape[1] != img_size:
            raise ValueError(f"npy 해상도 {arr.shape[1]}x{arr.shape[2]}가 --img_size {img_size}와 다름 "
                             f"— 16x16 재생성이 안 된 파일일 수 있음")
        arr = arr.reshape(len(arr), -1)
    if arr.shape[1] != img_size * img_size:
        raise ValueError(f"npy 차원 {arr.shape[1]} != img_size^2 {img_size * img_size}")
    if max_n:
        arr = arr[:max_n]
    if arr.min() < -0.01 or arr.max() > 1.01:
        raise ValueError(f"npy 값 범위가 0~1이 아님(min {arr.min():.3f}, max {arr.max():.3f}) — 척도 규약 위반")
    return torch.tensor(arr * 2.0 - 1.0, dtype=torch.float32)


def sample_z(n, in_dim, dist="uniform", device="cpu"):
    return torch.rand(n, in_dim, device=device) if dist == "uniform" else torch.randn(n, in_dim, device=device)


def train_step(generator, discriminator, real_batch, opt_g, opt_d, in_dim, device="cpu", z_dist="uniform"):
    """MediQ-GAN 한 스텝 — 표준 BCE GAN(판별자는 논문 Table 4 계열 5층 FC 재사용)."""
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

    # --- 생성자 (양자 스트림까지 역전파) ---
    opt_g.zero_grad()
    z = sample_z(bsz, in_dim, z_dist, device)
    loss_g = bce(discriminator(generator(z)), real_labels)
    loss_g.backward()
    opt_g.step()

    return loss_g.item(), loss_d.item()


def save_checkpoint(path, generator, discriminator, cfg, history, epoch, opt_g=None, opt_d=None):
    """옵티마이저 상태까지 저장한다 - Adam 모멘텀을 복원하지 않고 --resume하면
    이어하는 몇 에폭 동안 학습이 흔들려 품질이 일시적으로 꺾인다."""
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
    ap.add_argument("--img_size", type=int, default=16, help="2일차 산출물과 반드시 동일(재설계 후 16)")
    ap.add_argument("--n_qubits", type=int, default=16, help="원 논문 스펙 16 — 내리지 말 것(README 참고)")
    ap.add_argument("--q_depth", type=int, default=8, help="원 논문 그림 기준 8(레포 CLI 기본값은 6)")
    ap.add_argument("--n_generators", type=int, default=5, help="원 논문 스펙 5")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch_size", type=int, default=4,
                    help="⚠ 배치를 키워도 속도는 안 빨라짐 — quantum_stream이 샘플을 파이썬 for로 돌아 "
                         "에폭 비용이 샘플 수에 비례함")
    ap.add_argument("--lr_g", type=float, default=2e-4,
                    help="DCGAN 관례. ⚠ QGAN의 0.05/0.02를 그대로 쓰면 Tanh가 포화돼 모드붕괴함(2026-10-01 실측)")
    ap.add_argument("--lr_d", type=float, default=2e-4)
    ap.add_argument("--beta1", type=float, default=0.5, help="Adam beta1 - GAN 관례는 0.5(기본 0.9는 불안정)")
    ap.add_argument("--z_dist", default="normal", choices=["uniform", "normal"],
                    help="잠재벡터 분포. normal이 기본 - 8큐빗 선별에서 uniform 대비 다양성 0.028->0.170, "
                         "상관 0.207->0.245, Tanh 포화 88%%->58%%로 모두 좋았음(2026-10-01 실측)")
    ap.add_argument("--save_every", type=int, default=5, help="중간 체크포인트 저장 간격(에폭)")
    ap.add_argument("--max_n", type=int, default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--resume", default=None, help="이어하기 — 저장된 체크포인트 경로")
    ap.add_argument("--smoke", action="store_true",
                    help="합성 데이터 + 축소 스펙으로 코드만 점검(6큐빗·2서브제너레이터·3에폭)")
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
    print(f"생성자 스펙: {args.n_generators}개 서브제너레이터 × {args.n_qubits}큐빗, depth {args.q_depth} "
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
            print("⚠ 이 체크포인트에는 옵티마이저 상태가 없음(구버전) - 이어하는 몇 에폭은 학습이 흔들릴 수 있음")
        print(f"이어하기: {args.resume} (에폭 {start_epoch}부터)")

    steps_per_epoch = max(1, len(real) // args.batch_size)
    print(f"에폭당 {steps_per_epoch}스텝 · 총 {args.epochs - start_epoch}에폭 예정")

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
            print("  ⚠ 판별자 완승(loss_d < 0.01) - 생성자가 학습 신호를 잃는 상태임. "
                  "lr_g를 더 낮추거나 라벨 스무딩을 쓸 것. 이대로 계속 돌려도 쓸 수 있는 체크포인트가 안 나옴",
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
            print(f"  → 중간 체크포인트 저장: {mid.name} (3일차 미세조정 출발점 후보)")

    final = out_dir / "mediqgan_final.pt"
    save_checkpoint(final, gen, disc, cfg, history, args.epochs, opt_g, opt_d)
    with open(out_dir / "mediqgan_history.json", "w", encoding="utf-8") as f:
        json.dump({"config": cfg, **history}, f, ensure_ascii=False, indent=2)

    with torch.no_grad():
        sample = gen(sample_z(4, in_dim, args.z_dist)).numpy()
    print(f"\n완료 — 총 {(time.time() - t_start) / 60:.1f}분")
    print(f"최종 체크포인트: {final}")
    print(f"생성 샘플 값 범위: {sample.min():.3f} ~ {sample.max():.3f} (Tanh이므로 -1~1이 정상)")
    print("3일차에서는 gen_metrics.to_unit_scale(x, \"tanh\")로 0~1로 되돌려 QGAN과 비교할 것")


if __name__ == "__main__":
    main()
