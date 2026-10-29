# -*- coding: utf-8 -*-
"""
[준비 스크립트 ②] QGAN checkpoint 학습 (HAM10000 DF segmentation 이미지).

- 기본값 = 실습 스펙: 16x16, sub-generator 4개, depth 10 (데이터 6 + ancilla 1 = 7큐빗).
  2·4·8·16개를 600 step으로 비교해 4개가 가장 좋았음(README sub-generator 실험)
- 3일차 비교 기준인 강사 checkpoint를 만듦. 2일차 학생은 같은 학습을 Colab에서 400 step 돌림
- --epochs는 랜덤 batch step 수임(데이터 순회 아님). 600 step 로컬 CPU 약 22분
- 입력: (A) --npy 전처리 npy(0~1, Kaggle 불필요, 권장) 또는 (B) --metadata + --img_dir 원본(Kaggle 필요)

실행 예:
    C:/qmlvenv/Scripts/python.exe -X utf8 train_qgan_checkpoint.py \
        --npy ../../practice/assets/df_preprocessed.npy --out_dir ./checkpoints --n_generators 4 --epochs 600
    C:/qmlvenv/Scripts/python.exe -X utf8 train_qgan_checkpoint.py \
        --metadata HAM10000_metadata.csv --img_dir ./ham10000 --out_dir ./checkpoints
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
    ap.add_argument("--npy", help="전처리 npy(0~1) 경로 (권장, Kaggle 불필요)")
    ap.add_argument("--metadata", help="--npy 대신 원본을 쓸 때 (HAM10000_metadata.csv)")
    ap.add_argument("--img_dir", help="--npy 대신 원본을 쓸 때 (이미지 폴더)")
    ap.add_argument("--out_dir", default="./checkpoints")
    ap.add_argument("--target_class", default="df", choices=["akiec", "bcc", "bkl", "df", "mel", "vasc"],
                     help="증강할 소수클래스 (논문 기본값: df)")
    ap.add_argument("--img_size", type=int, default=16, help="한 변 픽셀 수. img_size^2 / n_generators가 2의 거듭제곱이어야 함")
    ap.add_argument("--n_generators", type=int, default=4, help="sub-generator 개수 (4 = 7큐빗, patch 64)")
    ap.add_argument("--q_depth", type=int, default=10, help="PQC depth (논문과 같은 10)")
    ap.add_argument("--epochs", type=int, default=600, help="랜덤 batch step 수 (600 step 로컬 CPU 약 22분)")
    ap.add_argument("--batch_size", type=int, default=8)
    ap.add_argument("--lr_g", type=float, default=0.05)
    ap.add_argument("--lr_d", type=float, default=0.001)
    args = ap.parse_args()

    # 생성자 출력(n_generators × 2^n_data_qubits)이 이미지 픽셀 수와 같아야 함
    total_pixels = args.img_size ** 2
    assert total_pixels % args.n_generators == 0, (
        f"img_size^2({total_pixels})가 n_generators({args.n_generators})로 나누어떨어져야 함")
    patch_pixels = total_pixels // args.n_generators
    n_data_qubits = int(np.log2(patch_pixels))
    assert 2 ** n_data_qubits == patch_pixels, (
        f"patch당 픽셀수({patch_pixels})가 2의 거듭제곱이어야 함 - img_size/n_generators 조합을 조정할 것")

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
                             f"- 16x16 재생성이 안 된 파일일 수 있음(재생산 체인 ① 참고)")
        if imgs.min() < -0.01 or imgs.max() > 1.01:
            raise SystemExit(f"npy 값 범위가 0~1이 아님(min {imgs.min():.3f}, max {imgs.max():.3f}) - 척도 규약 위반")
        print(f"  로드된 이미지: {len(imgs)}장 ({imgs.shape[1]}x{imgs.shape[2]}, 0~1)")
    else:
        if not (args.metadata and args.img_dir):
            raise SystemExit("--npy 또는 (--metadata + --img_dir) 중 하나는 반드시 필요함")
        print("[1/3] 원본 로드 + segmentation 전처리...")
        imgs = build_dataset(args.metadata, args.img_dir, args.target_class, args.img_size)
        print(f"  로드된 {args.target_class} 클래스 이미지: {len(imgs)}장")
    if len(imgs) == 0:
        print("데이터 없음 - 입력 경로를 확인할 것. 종료함.")
        return

    real_flat = torch.tensor(imgs.reshape(len(imgs), -1))
    # real을 확률 척도(장당 합 1)로 맞춤
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
    print(f"학습 완료 - 총 소요시간 {total_min:.1f}분")

    print("[3/3] checkpoint 저장...")
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
    print("이 파일을 practice/assets/에 넣고 커밋·푸시하면 2·3일차 노트북이 git clone으로 바로 불러 씀.")
    print("평가·시각화 시에는 gen_metrics.to_unit_scale(x, \"prob\")로 0~1로 되돌려 MediQ-GAN과 비교할 것.")


if __name__ == "__main__":
    main()
