# -*- coding: utf-8 -*-
"""
[10월 준비 스크립트] CNN 분류기 2종(증강 전/후) 학습 — train_qgan_checkpoint.py 다음에 실행.
컨설팅-목표.xlsx 10월4주차 계획: "증강 전/후 CNN 분류기 2종 사전 학습 완료" 항목에 대응.

실행:
    python train_cnn_comparison.py --metadata HAM10000_metadata.csv --img_dir ./ham10000 \
        --qgan_ckpt ./checkpoints/qgan_df_8px.pt --out_dir ./checkpoints --epochs 20

출력: cnn_before.pt, cnn_after.pt, comparison_result.json (3일차 노트북에서 그대로 로드해서 비교 실습에 사용)
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data_pipeline import load_metadata, load_image, segment_fcm_kmeans, resize_for_encoding
from qgan_model import PatchQuantumGenerator
from cnn_classifier import PaperCNNClassifier, train_classifier, evaluate
from train_qgan_checkpoint import build_dataset


def make_loader(pos_imgs, neg_imgs, batch_size=8):
    x = np.concatenate([pos_imgs, neg_imgs], axis=0)[:, None, :, :]
    y = np.concatenate([np.ones(len(pos_imgs)), np.zeros(len(neg_imgs))])
    ds = TensorDataset(torch.tensor(x, dtype=torch.float32), torch.tensor(y, dtype=torch.float32).unsqueeze(1))
    return DataLoader(ds, batch_size=batch_size, shuffle=True)


def split_train_val(imgs, val_frac=0.2, seed=0):
    """held-out validation 분할 — index를 섞어서 val_frac만큼 검증용으로 뗀다."""
    n = len(imgs)
    rng = np.random.RandomState(seed)
    idx = rng.permutation(n)
    n_val = max(1, int(round(n * val_frac)))
    val_idx, train_idx = idx[:n_val], idx[n_val:]
    return imgs[train_idx], imgs[val_idx]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metadata", required=True)
    ap.add_argument("--img_dir", required=True)
    ap.add_argument("--qgan_ckpt", required=True)
    ap.add_argument("--majority_class", default="nv")
    ap.add_argument("--out_dir", default="./checkpoints")
    ap.add_argument("--epochs", type=int, default=20)
    args = ap.parse_args()

    print("[1/4] QGAN 체크포인트 로드...")
    ckpt = torch.load(args.qgan_ckpt, map_location="cpu")
    cfg = ckpt["config"]
    gen = PatchQuantumGenerator(n_generators=cfg["n_generators"], n_data_qubits=cfg["n_data_qubits"],
                                 n_ancillas=cfg["n_ancillas"], q_depth=cfg["q_depth"])
    gen.load_state_dict(ckpt["generator_state_dict"])
    gen.eval()
    img_size = cfg["img_size"]
    minority_class = cfg["target_class"]
    print(f"  설정: {minority_class} 증강용, img_size={img_size}, n_generators={cfg['n_generators']}")

    print("[2/4] 원본 데이터 로드(소수/다수 클래스)...")
    minority_imgs = build_dataset(args.metadata, args.img_dir, minority_class, img_size)
    majority_imgs = build_dataset(args.metadata, args.img_dir, args.majority_class, img_size,
                                   max_n=len(minority_imgs) * 3)  # 논문처럼 극단적 불균형까진 안 가고 적당히 제한
    print(f"  소수({minority_class}): {len(minority_imgs)}장, 다수({args.majority_class}): {len(majority_imgs)}장")

    # held-out 검증셋 분할 — 증강 전/후 두 모델이 "같은" 검증셋으로 평가되어야 공정한 비교가 됨.
    # 검증셋에는 합성 이미지를 절대 섞지 않는다(학습 데이터에만 증강 적용).
    minority_train, minority_val = split_train_val(minority_imgs)
    majority_train, majority_val = split_train_val(majority_imgs)
    print(f"  train/val 분할: 소수 train={len(minority_train)}/val={len(minority_val)}, "
          f"다수 train={len(majority_train)}/val={len(majority_val)}")

    print("[3/4] QGAN으로 오버샘플링 생성 (train셋에만 적용)...")
    n_synth = max(0, len(majority_train) - len(minority_train))
    # 생성자 출력(확률 척도)을 실제 전처리 이미지의 픽셀 척도(0~1 밝기)로 환산
    with torch.no_grad():
        synth = gen(n_synth).numpy() if n_synth > 0 else np.zeros((0, img_size * img_size))
    pixel_scale = minority_train.reshape(len(minority_train), -1).sum(axis=1).mean() / max(synth.sum(axis=1).mean(), 1e-9) if n_synth > 0 else 1.0
    synth = (synth * pixel_scale).reshape(-1, img_size, img_size)
    synth = synth.astype(np.float32)
    minority_train_augmented = np.concatenate([minority_train, synth], axis=0)
    print(f"  생성된 합성 이미지: {n_synth}장 → 증강 후 소수클래스 train 총 {len(minority_train_augmented)}장")

    print("[4/4] CNN 학습 — 증강 전 / 증강 후 각각 (같은 held-out 검증셋으로 평가)...")
    loader_before_train = make_loader(minority_train, majority_train)
    loader_after_train = make_loader(minority_train_augmented, majority_train)
    loader_val = make_loader(minority_val, majority_val)

    model_before = PaperCNNClassifier(in_channels=1, img_size=img_size)
    hist_before = train_classifier(model_before, loader_before_train, loader_val, epochs=args.epochs)
    metrics_before = evaluate(model_before, loader_val)
    print(f"  [증강 전] val accuracy={metrics_before['accuracy']:.3f}  val AUC-ROC={metrics_before['auc_roc']:.3f}")

    model_after = PaperCNNClassifier(in_channels=1, img_size=img_size)
    hist_after = train_classifier(model_after, loader_after_train, loader_val, epochs=args.epochs)
    metrics_after = evaluate(model_after, loader_val)
    print(f"  [증강 후] val accuracy={metrics_after['accuracy']:.3f}  val AUC-ROC={metrics_after['auc_roc']:.3f}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save({"model_state_dict": model_before.state_dict(), "img_size": img_size},
               out_dir / "cnn_before.pt")
    torch.save({"model_state_dict": model_after.state_dict(), "img_size": img_size},
               out_dir / "cnn_after.pt")
    with open(out_dir / "comparison_result.json", "w", encoding="utf-8") as f:
        json.dump({
            "minority_class": minority_class, "majority_class": args.majority_class,
            "n_minority_real": len(minority_imgs), "n_synthetic": n_synth,
            "n_minority_train": len(minority_train), "n_minority_val": len(minority_val),
            "n_majority_train": len(majority_train), "n_majority_val": len(majority_val),
            "eval_set": "held_out_validation",
            "before": metrics_before, "after": metrics_after,
            "history_before": hist_before, "history_after": hist_after,
        }, f, ensure_ascii=False, indent=2)
    print(f"저장됨: {out_dir}/cnn_before.pt, cnn_after.pt, comparison_result.json")
    print("이 3개 파일을 3일차 노트북의 checkpoints/ 폴더에 넣고 Colab에 업로드(또는 Drive 공유)할 것.")


if __name__ == "__main__":
    main()
