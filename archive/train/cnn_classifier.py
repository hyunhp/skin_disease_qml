# -*- coding: utf-8 -*-
"""
CNN 분류기 — HAM10000 QGAN 논문 Table 1/2 스펙 그대로 재현.
동아대 대학원 QML 강의 3일차 — "증강 전 vs 증강 후" 비교 실습에 사용.
"""
import torch
import torch.nn as nn
from sklearn.metrics import roc_auc_score, accuracy_score


class PaperCNNClassifier(nn.Module):
    """논문 Table 2: conv 4층(kernel 3, stride 1) + BatchNorm + maxpool 2x2,
    Table 1: 완전연결 + dropout 2개 + sigmoid 출력, 460k 파라미터대."""

    def __init__(self, in_channels=1, img_size=64):
        super().__init__()
        # 논문(Table 2)은 conv 4층을 쓰지만, 이 강의는 큐빗 제약상 8x8·16x16처럼 아주 작은 인코딩
        # 해상도도 다뤄야 한다 — 4번 풀링(÷16)하면 8x8 이하 입력은 0 이하로 줄어들어 죽는다.
        # 그래서 "입력 크기가 허용하는 만큼만" conv+maxpool 레이어를 쌓도록 적응형으로 만든다
        # (img_size>=64면 원 논문과 동일하게 4층 그대로 나온다).
        chs_full = [in_channels, 16, 32, 64, 128]
        n_layers = 0
        size = img_size
        while size >= 2 and n_layers < 4:
            size //= 2
            n_layers += 1
        if n_layers == 0:
            n_layers = 1  # 최소 1층은 보장(2x2 이하 입력이면 풀링 없이 conv만)
        chs = chs_full[: n_layers + 1]

        layers = []
        size = img_size
        for i in range(n_layers):
            do_pool = size >= 2
            layers += [
                nn.Conv2d(chs[i], chs[i + 1], kernel_size=3, stride=1, padding=1),
                nn.BatchNorm2d(chs[i + 1]),
                nn.ReLU(),
            ]
            if do_pool:
                layers.append(nn.MaxPool2d(2, 2))
                size //= 2
        self.conv = nn.Sequential(*layers)
        flat_dim = chs[-1] * size * size
        self.fc = nn.Sequential(
            nn.Linear(flat_dim, 128), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(128, 32), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(32, 1), nn.Sigmoid(),
        )

    def forward(self, x):
        x = self.conv(x)
        x = x.flatten(1)
        return self.fc(x)


def train_classifier(model, train_loader, val_loader, epochs=20, lr=1.5e-3, device="cpu"):
    """논문 Table 1: ADAM, lr=1.5e-3, BCE loss."""
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    bce = nn.BCELoss()
    history = {"train_loss": [], "val_loss": [], "val_auc": []}
    model.to(device)
    for epoch in range(epochs):
        model.train()
        train_losses = []
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            pred = model(xb)
            loss = bce(pred, yb)
            loss.backward()
            opt.step()
            train_losses.append(loss.item())

        model.eval()
        val_losses, all_pred, all_true = [], [], []
        with torch.no_grad():
            for xb, yb in val_loader:
                xb, yb = xb.to(device), yb.to(device)
                pred = model(xb)
                val_losses.append(bce(pred, yb).item())
                all_pred.extend(pred.cpu().numpy().flatten().tolist())
                all_true.extend(yb.cpu().numpy().flatten().tolist())

        val_auc = roc_auc_score(all_true, all_pred) if len(set(all_true)) > 1 else float("nan")
        history["train_loss"].append(sum(train_losses) / len(train_losses))
        history["val_loss"].append(sum(val_losses) / len(val_losses))
        history["val_auc"].append(val_auc)
    return history


def evaluate(model, loader, device="cpu"):
    model.eval()
    all_pred, all_true = [], []
    with torch.no_grad():
        for xb, yb in loader:
            xb = xb.to(device)
            pred = model(xb).cpu().numpy().flatten()
            all_pred.extend(pred.tolist())
            all_true.extend(yb.numpy().flatten().tolist())
    binary_pred = [1 if p > 0.5 else 0 for p in all_pred]
    return {
        "accuracy": accuracy_score(all_true, binary_pred),
        "auc_roc": roc_auc_score(all_true, all_pred) if len(set(all_true)) > 1 else float("nan"),
    }


if __name__ == "__main__":
    print("[검증] CNN 분류기 forward+1epoch 학습 동작 확인 — 랜덤 텐서 사용")
    torch.manual_seed(0)
    img_size = 16  # 테스트는 작은 사이즈로 빠르게

    model = PaperCNNClassifier(in_channels=1, img_size=img_size)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"파라미터 수: {n_params:,} (논문은 460k대, 이건 테스트용 {img_size}x{img_size} 축소판이라 다름)")

    x = torch.rand(4, 1, img_size, img_size)
    out = model(x)
    assert out.shape == (4, 1), f"출력 shape 이상: {out.shape}"
    assert (out >= 0).all() and (out <= 1).all(), "sigmoid 출력 범위 이상"
    print("OK — forward pass shape/range 정상:", tuple(out.shape))

    # 더미 데이터셋으로 1 epoch 학습 되는지 확인
    from torch.utils.data import TensorDataset, DataLoader
    xs = torch.rand(16, 1, img_size, img_size)
    ys = torch.randint(0, 2, (16, 1)).float()
    loader = DataLoader(TensorDataset(xs, ys), batch_size=4)

    hist = train_classifier(model, loader, loader, epochs=1)
    print("1epoch 학습 결과:", {k: round(v[-1], 4) for k, v in hist.items()})
    print("OK — 학습 루프(train/val/AUC) 정상 동작 확인")
