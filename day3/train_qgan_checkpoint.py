# -*- coding: utf-8 -*-
"""
[10월 준비 스크립트] QGAN 증강 모델 실제 학습 — HAM10000 DF(소수) vs NV(다수) 세그멘테이션 이미지.
컨설팅-목표.xlsx 10월4주차 계획: "QGAN 증강 모델 체크포인트 ... 사전 학습 완료" 항목에 대응.

실행 전 준비물:
1. HAM10000_metadata.csv + 이미지 폴더(HAM10000_images_part_1/2) — Kaggle에서 다운로드
   !kaggle datasets download -d kmader/skin-cancer-mnist-ham10000
2. 이 스크립트와 같은 폴더에 data_pipeline.py, qgan_model.py가 있어야 함(2일차 노트북과 공유하는 모듈)

실행:
    python train_qgan_checkpoint.py --metadata HAM10000_metadata.csv --img_dir ./ham10000 \
        --out_dir ./checkpoints --epochs 300 --img_size 8

⚠ 참고: 원 논문은 2000 epoch으로 1~1.5시간이 걸렸다(Table 10). 이 스크립트는 --epochs로 조절 가능하게
해뒀으니, 실제 시간을 보면서 강의에 쓸 수준(품질 vs 소요시간)으로 타협해서 돌릴 것 — 강의 3일차
실습에서는 "학습"이 아니라 "이 체크포인트를 불러와서 생성"만 하므로, 여기서 한 번 잘 돌려두면 된다.
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
    ap.add_argument("--metadata", required=True)
    ap.add_argument("--img_dir", required=True)
    ap.add_argument("--out_dir", default="./checkpoints")
    ap.add_argument("--target_class", default="df", choices=["akiec", "bcc", "bkl", "df", "mel", "vasc"],
                     help="증강할 소수클래스 (논문 기본값: df)")
    ap.add_argument("--img_size", type=int, default=8, help="한 변 픽셀수(8,16,32...) — 전체 픽셀수(img_size^2)가 "
                     "n_generators로 나누어떨어지고 그 몫이 2의 거듭제곱이어야 함")
    ap.add_argument("--n_generators", type=int, default=4, help="서브제너레이터 개수(원논문 16 → 강의용 축소). "
                     "각 서브제너레이터가 이미지의 1/n_generators만큼의 patch를 담당(patch들을 이어붙여 전체 이미지 생성)")
    ap.add_argument("--q_depth", type=int, default=4, help="PQC depth(원논문 10 → 강의용 축소)")
    ap.add_argument("--epochs", type=int, default=300)
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

    print("[1/3] 데이터 로드 + 세그멘테이션 전처리...")
    imgs = build_dataset(args.metadata, args.img_dir, args.target_class, args.img_size)
    print(f"  로드된 {args.target_class} 클래스 이미지: {len(imgs)}장")
    if len(imgs) == 0:
        print("데이터가 없습니다 — metadata/img_dir 경로를 확인하세요. 종료합니다.")
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

    t0 = time.time()
    for epoch in range(args.epochs):
        idx = torch.randint(0, len(real_flat), (min(args.batch_size, len(real_flat)),))
        batch = real_flat[idx]
        lg, ld = train_step(gen, disc, batch, opt_g, opt_d)
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
        "config": {
            "n_generators": args.n_generators, "n_data_qubits": n_data_qubits,
            "n_ancillas": 1, "q_depth": args.q_depth, "img_size": args.img_size,
            "target_class": args.target_class,
        },
    }, ckpt_path)
    print(f"저장됨: {ckpt_path}")
    print("이 파일을 3일차 노트북의 checkpoints/ 폴더에 넣고 Colab에 업로드(또는 Drive 공유)할 것.")


if __name__ == "__main__":
    main()
