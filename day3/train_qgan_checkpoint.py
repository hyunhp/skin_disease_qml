# -*- coding: utf-8 -*-
"""
[준비 스크립트 ②] QGAN 체크포인트 학습 — HAM10000 DF(소수클래스) 세그멘테이션 이미지.

2026-10-01 커리큘럼 재설계 반영 — 확정 스펙이 기본값이다:
  **16x16 · 서브제너레이터 2개 · depth 10 (데이터 7 + 보조 1 = 8큐빗, patch 128)**
  → 큐빗 수·patch 크기가 논문 스펙과 정확히 일치하고, 실측 1.45s/step으로 가장 빠르다.
     (서브제너레이터가 적을수록 빠른 이유: 회로 호출 횟수가 상태벡터 크기보다 지배적. 근거는 README 실측표)
재설계 후 2일차(11/20)는 학생이 이 학습을 **라이브로** 돌린다(600스텝 약 20분). 이 스크립트는
3일차 비교 기준본이 될 강사 체크포인트를 미리 만들어두는 용도다.

입력은 두 가지 중 하나:
  (A) --npy  전처리 완료 npy(0~1) — **Kaggle 불필요, 로컬에서 바로 실행 가능(권장)**
  (B) --metadata + --img_dir  HAM10000 원본에서 세그멘테이션까지 직접 수행(Kaggle 필요)

실행 예:
    # (A) 권장 — 저장소의 16x16 전처리 npy로 로컬 학습
    C:/qmlvenv/Scripts/python.exe -X utf8 train_qgan_checkpoint.py \
        --npy assets/df_preprocessed.npy --out_dir ./checkpoints --epochs 600

    # (B) 원본에서 전처리까지
    C:/qmlvenv/Scripts/python.exe -X utf8 train_qgan_checkpoint.py \
        --metadata HAM10000_metadata.csv --img_dir ./ham10000 --out_dir ./checkpoints

⚠ 원 논문은 2000 epoch으로 1~1.5시간이 걸렸다(Table 10). 여기서 1 epoch은 데이터 1회 순회가 아니라
  **랜덤 배치 1스텝**이다 — 즉 --epochs 600 = 600스텝(실측 약 20분).
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data_pipeline import load_metadata, load_image, segment_fcm_kmeans, resize_for_encoding, TARGET_CLASSES
from qgan_model import PatchQuantumGenerator, ClassicalDiscriminator, train_step


def build_dataset(metadata_csv, img_dir, target_class, img_size, max_n=None):
    df = load_metadata(metadata_csv)
    df = df[df["dx"] == target_class]
    if max_n:
        df = df.head(max_n)
    imgs = []
    for _, row in df.iterrows():
        try:
            bgr = load_image(img_dir, row["image_id"])
            seg = segment_fcm_kmeans(bgr, n_clusters=4, resize_to=(64, 64))
            small = resize_for_encoding(seg, (img_size, img_size))
            imgs.append(small.astype(np.float32) / 255.0)
        except FileNotFoundError:
            continue
    return np.stack(imgs) if imgs else np.zeros((0, img_size, img_size), dtype=np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--npy", help="전처리 완료 npy(0~1) 경로. 지정하면 Kaggle·원본 이미지가 필요 없음(권장)")
    ap.add_argument("--metadata", help="--npy를 쓰지 않을 때만 필요(HAM10000_metadata.csv)")
    ap.add_argument("--img_dir", help="--npy를 쓰지 않을 때만 필요(HAM10000 이미지 폴더)")
    ap.add_argument("--out_dir", default="./checkpoints")
    ap.add_argument("--target_class", default="df", choices=["akiec", "bcc", "bkl", "df", "mel", "vasc"],
                     help="증강할 소수클래스 (논문 기본값: df)")
    ap.add_argument("--img_size", type=int, default=16, help="한 변 픽셀수 — 2026-10-01 확정 스펙은 16. "
                     "전체 픽셀수(img_size^2)가 n_generators로 나누어떨어지고 그 몫이 2의 거듭제곱이어야 함")
    ap.add_argument("--n_generators", type=int, default=2, help="서브제너레이터 개수 — 확정 스펙은 2 "
                     "(데이터 7 + 보조 1 = 8큐빗, patch 128 = 논문 스펙과 정확히 일치). "
                     "각 서브제너레이터가 이미지의 1/n_generators만큼의 patch를 담당(이어붙여 전체 이미지 생성)")
    ap.add_argument("--q_depth", type=int, default=10, help="PQC depth — 확정 스펙은 논문과 같은 10")
    ap.add_argument("--epochs", type=int, default=600, help="= 랜덤 배치 스텝 수(데이터 순회가 아님). 실측 600스텝 약 20분")
    ap.add_argument("--batch_size", type=int, default=8)
    ap.add_argument("--lr_g", type=float, default=0.05)
    ap.add_argument("--lr_d", type=float, default=0.001)
    args = ap.parse_args()

    # 서브제너레이터 n_generators개가 patch를 이어붙여 전체 이미지(img_size^2 픽셀)를 만드는 구조이므로,
    # 생성자 총 출력차원(n_generators * 2^n_data_qubits)이 실제 이미지 픽셀수와 같아야 한다.
    # (이 조건이 깨지면 판별자에 넣는 real 이미지와 fake 이미지의 차원이 달라져 학습 시 즉시 shape 에러가 남 —
    #  실제로 예전 버전은 n_generators를 고려하지 않고 n_data_qubits=log2(img_size^2)로만 계산해 이 버그가 있었음.)
    total_pixels = args.img_size ** 2
    assert total_pixels % args.n_generators == 0, (
        f"img_size^2({total_pixels})가 n_generators({args.n_generators})로 나누어떨어져야 함")
    patch_pixels = total_pixels // args.n_generators
    n_data_qubits = int(np.log2(patch_pixels))
    assert 2 ** n_data_qubits == patch_pixels, (
        f"patch당 픽셀수({patch_pixels})가 2의 거듭제곱이어야 함 — img_size/n_generators 조합을 조정할 것")

    print(f"[설정] target_class={args.target_class}, img_size={args.img_size}x{args.img_size}"
          f"({total_pixels}px), n_generators={args.n_generators}, patch당 {patch_pixels}px "
          f"→ n_data_qubits={n_data_qubits}, q_depth={args.q_depth}")

    if args.npy:
        print(f"[1/3] 전처리 npy 로드: {args.npy}")
        imgs = np.load(args.npy)
        if imgs.ndim == 2:  # (N, img_size^2)로 저장된 경우도 허용
            side = int(np.sqrt(imgs.shape[1]))
            imgs = imgs.reshape(len(imgs), side, side)
        if imgs.shape[1] != args.img_size:
            raise SystemExit(f"npy 해상도 {imgs.shape[1]}x{imgs.shape[2]}가 --img_size {args.img_size}와 다름 "
                             f"— 16x16 재생성이 안 된 파일일 수 있음(재생산 체인 ① 참고)")
        if imgs.min() < -0.01 or imgs.max() > 1.01:
            raise SystemExit(f"npy 값 범위가 0~1이 아님(min {imgs.min():.3f}, max {imgs.max():.3f}) — 척도 규약 위반")
        print(f"  로드된 이미지: {len(imgs)}장 ({imgs.shape[1]}x{imgs.shape[2]}, 0~1)")
    else:
        if not (args.metadata and args.img_dir):
            raise SystemExit("--npy 또는 (--metadata + --img_dir) 중 하나는 반드시 필요함")
        print("[1/3] 원본 로드 + 세그멘테이션 전처리...")
        imgs = build_dataset(args.metadata, args.img_dir, args.target_class, args.img_size)
        print(f"  로드된 {args.target_class} 클래스 이미지: {len(imgs)}장")
    if len(imgs) == 0:
        print("데이터가 없습니다 — 입력 경로를 확인하세요. 종료합니다.")
        return

    real_flat = torch.tensor(imgs.reshape(len(imgs), -1))
    # real을 확률 척도(픽셀 합=1)로 맞춤. 생성자는 patch별 '보조큐빗=0' 확률이라 총합·patch별 분포를 함께 학습함.
    real_flat = real_flat / real_flat.sum(dim=1, keepdim=True).clamp(min=1e-6)

    print("[2/3] QGAN 학습...")
    gen = PatchQuantumGenerator(n_generators=args.n_generators, n_data_qubits=n_data_qubits,
                                 n_ancillas=1, q_depth=args.q_depth)
    disc = ClassicalDiscriminator(input_dim=gen.output_dim)
    opt_g = torch.optim.Adam(gen.parameters(), lr=args.lr_g)
    opt_d = torch.optim.Adam(disc.parameters(), lr=args.lr_d)

    history = {"loss_g": [], "loss_d": []}
    t0 = time.time()
    for epoch in range(args.epochs):
        idx = torch.randint(0, len(real_flat), (min(args.batch_size, len(real_flat)),))
        batch = real_flat[idx]
        lg, ld = train_step(gen, disc, batch, opt_g, opt_d)
        history["loss_g"].append(lg); history["loss_d"].append(ld)
        if (epoch + 1) % max(1, args.epochs // 20) == 0:
            elapsed = time.time() - t0
            print(f"  epoch {epoch+1}/{args.epochs}  loss_g={lg:.4f}  loss_d={ld:.4f}  경과={elapsed/60:.1f}분")

    total_min = (time.time() - t0) / 60
    print(f"학습 완료 — 총 소요시간 {total_min:.1f}분")

    print("[3/3] 체크포인트 저장...")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ckpt_path = out_dir / f"qgan_{args.target_class}_{args.img_size}px.pt"
    torch.save({
        "generator_state_dict": gen.state_dict(),
        "discriminator_state_dict": disc.state_dict(),
        "config": {
            "n_generators": args.n_generators, "n_data_qubits": n_data_qubits,
            "n_ancillas": 1, "q_depth": args.q_depth, "img_size": args.img_size,
            "target_class": args.target_class, "scale": "prob", "epochs": args.epochs,
        },
        "history": history,  # 지표 ④ 손실곡선용
    }, ckpt_path)
    print(f"저장됨: {ckpt_path}")
    print("이 파일을 day3/assets/에 넣고 커밋·푸시하면 2·3일차 노트북이 git clone으로 바로 불러 씀.")
    print("평가·시각화 시에는 gen_metrics.to_unit_scale(x, \"prob\")로 0~1로 되돌려 MediQ-GAN과 비교할 것.")


if __name__ == "__main__":
    main()
