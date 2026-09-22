# -*- coding: utf-8 -*-
"""
Patch Quantum GAN — HAM10000 QGAN 논문(Andra et al.) Section 3.2 / Table 3,4 재현
동아대 대학원 QML 강의 2~3일차용. 원 논문 스펙(7+1큐빗, 서브제너레이터 16개, PQC depth 10, 2000 epoch)은
Colab 무료 시뮬레이터로 라이브 실습하기엔 크므로, 강의용으로 축소한 스펙을 기본값으로 둔다.
아키텍처 자체(서브제너레이터 앙상블 + patch 방식 + 고전 판별자)는 논문과 동일하게 유지.

측정 방식: 원 논문/Huang et al.(2020)의 patch method처럼 보조큐빗(ancilla)이 |0>인 경우만 채택한다
(사후선택, post-selection). shot 단위 사후선택 대신 exact 시뮬레이터의 qml.probs()로 전체 큐빗 확률을 구한 뒤
'보조큐빗=0' 항목만 patch로 쓰는 방식이며, PennyLane 공식 QGAN 튜토리얼과 같은 방향이다(튜토리얼과 달리
patch별 재정규화는 하지 않아 patch 밝기 총합 0~1도 학습 대상이 됨).
2026-09-22 변경: 이전에는 데이터 큐빗만 측정(보조큐빗 partial trace)해 patch 합이 항상 1로 고정됐는데,
세그멘테이션 이미지는 배경 patch 합이 0에 가까워 판별자가 이 차이만으로 항상 이겨 생성 품질이 무너졌다.
"""
import math
import torch
import torch.nn as nn
import pennylane as qml


class PatchQuantumGenerator(nn.Module):
    """서브제너레이터 앙상블 기반 양자 생성자.

    원 논문 스펙(기본값 인자로 그대로 재현 가능): n_generators=16, n_data_qubits=7, n_ancillas=1, q_depth=10
    강의 실습 기본값(빠른 반복을 위해 축소): n_generators=4, n_data_qubits=4, n_ancillas=1, q_depth=3
    """

    def __init__(self, n_generators=4, n_data_qubits=4, n_ancillas=1, q_depth=3, dev_name="default.qubit"):
        super().__init__()
        self.n_generators = n_generators
        self.n_data_qubits = n_data_qubits
        self.n_ancillas = n_ancillas
        self.n_qubits = n_data_qubits + n_ancillas
        self.q_depth = q_depth
        self.patch_dim = 2 ** n_data_qubits  # 서브제너레이터 1개가 만드는 patch 길이
        self.anc_stride = 2 ** n_ancillas  # 보조큐빗이 마지막 wire → '보조큐빗=0' 항목은 이 간격마다 위치함

        dev = qml.device(dev_name, wires=self.n_qubits)
        n_qubits = self.n_qubits

        @qml.qnode(dev, interface="torch", diff_method="backprop")
        def circuit(noise, weights):
            # 1) 노이즈를 angle encoding으로 초기 회전각에 인코딩 (HAM10000/MosaiQ 논문과 동일한 Rx/Ry 방식)
            for i in range(n_qubits):
                qml.RY(noise[i], wires=i)
            # 2) 학습 가능한 변분 레이어 — 단일큐빗 회전 + 인접큐빗 CZ 얽힘 반복 (논문 Fig.10 방식)
            for layer in range(q_depth):
                for i in range(n_qubits):
                    qml.RY(weights[layer, i], wires=i)
                for i in range(n_qubits - 1):
                    qml.CZ(wires=[i, i + 1])
            # 보조큐빗까지 전체 측정 → forward에서 '보조큐빗=0' 항목만 patch로 사용 (논문의 사후선택에 해당)
            return qml.probs(wires=range(n_qubits))

        self.circuit = circuit
        self.q_params = nn.ParameterList([
            nn.Parameter(torch.rand(q_depth, self.n_qubits) * math.pi) for _ in range(n_generators)
        ])

    def forward(self, batch_size, device="cpu"):
        all_patches = []
        for gen_idx in range(self.n_generators):
            weights = self.q_params[gen_idx]
            batch_patches = []
            for _ in range(batch_size):
                noise = torch.rand(self.n_qubits, device=device) * math.pi
                probs = self.circuit(noise, weights)[::self.anc_stride]  # 보조큐빗=0 항목만 → (2**n_data_qubits,)
                batch_patches.append(probs)
            all_patches.append(torch.stack(batch_patches))  # (batch, patch_dim)
        # 서브제너레이터 출력을 이어붙여 최종 이미지 벡터 생성 (논문: "sub-patches combined into one image")
        images = torch.cat(all_patches, dim=1)  # (batch, n_generators * patch_dim)
        # PennyLane qml.probs()는 float64를 반환하는데 판별자(PyTorch 기본 float32)와 dtype이 안 맞으므로 캐스팅
        return images.float()

    @property
    def output_dim(self):
        return self.n_generators * self.patch_dim


class ClassicalDiscriminator(nn.Module):
    """HAM10000 QGAN 논문 Table 4 그대로 — 5층 완전연결, ReLU, sigmoid 출력, BCE loss."""

    def __init__(self, input_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64), nn.ReLU(),
            nn.Linear(64, 32), nn.ReLU(),
            nn.Linear(32, 16), nn.ReLU(),
            nn.Linear(16, 8), nn.ReLU(),
            nn.Linear(8, 1), nn.Sigmoid(),
        )

    def forward(self, x):
        return self.net(x)


def train_step(generator, discriminator, real_batch, opt_g, opt_d, device="cpu"):
    """QGAN 한 스텝 학습 — 논문 Eq.(5)의 min-max 목적함수를 표준 BCE GAN 학습으로 구현."""
    bce = nn.BCELoss()
    batch_size = real_batch.shape[0]
    real_labels = torch.ones(batch_size, 1, device=device)
    fake_labels = torch.zeros(batch_size, 1, device=device)

    # --- 판별자 학습 ---
    opt_d.zero_grad()
    real_pred = discriminator(real_batch)
    loss_d_real = bce(real_pred, real_labels)

    fake_batch = generator(batch_size, device=device).detach()
    fake_pred = discriminator(fake_batch)
    loss_d_fake = bce(fake_pred, fake_labels)

    loss_d = loss_d_real + loss_d_fake
    loss_d.backward()
    opt_d.step()

    # --- 생성자 학습 ---
    opt_g.zero_grad()
    fake_batch = generator(batch_size, device=device)
    fake_pred = discriminator(fake_batch)
    loss_g = bce(fake_pred, real_labels)  # 판별자를 속이도록 학습
    loss_g.backward()
    opt_g.step()

    return loss_g.item(), loss_d.item()


if __name__ == "__main__":
    print("[검증] QGAN 생성자/판별자 forward+backward(그래디언트) 동작 확인 — 실제 데이터 없이 랜덤값 사용")
    torch.manual_seed(0)

    gen = PatchQuantumGenerator(n_generators=2, n_data_qubits=3, n_ancillas=1, q_depth=2)
    disc = ClassicalDiscriminator(input_dim=gen.output_dim)
    print(f"생성자 출력 차원: {gen.output_dim} (서브제너레이터 {gen.n_generators} x patch {gen.patch_dim})")
    print(f"생성자 전체 큐빗: {gen.n_qubits} (데이터 {gen.n_data_qubits} + 보조 {gen.n_ancillas})")

    fake_batch = gen(batch_size=4)
    print("생성 이미지 배치 shape:", tuple(fake_batch.shape))
    assert fake_batch.shape == (4, gen.output_dim)
    # 각 서브제너레이터의 patch는 '보조큐빗=0' 확률이므로 값이 0 이상이고 합이 1 이하여야 함(검증)
    for i in range(gen.n_generators):
        patch = fake_batch[0, i * gen.patch_dim:(i + 1) * gen.patch_dim]
        assert patch.min().item() >= 0 and patch.sum().item() <= 1.0 + 1e-4, f"서브제너레이터 {i} 출력 이상: {patch.sum().item()}"
    print("OK — 각 서브제너레이터 출력이 유효한 부분 확률(0 이상, 합 1 이하) 확인")

    real_batch = torch.rand(4, gen.output_dim)
    real_batch = real_batch / real_batch.sum(dim=1, keepdim=True)  # 확률분포처럼 정규화(테스트용)

    opt_g = torch.optim.Adam(gen.parameters(), lr=0.1)
    opt_d = torch.optim.Adam(disc.parameters(), lr=0.01)

    losses_before = train_step(gen, disc, real_batch, opt_g, opt_d)
    print(f"1스텝 학습 후 loss_g={losses_before[0]:.4f}, loss_d={losses_before[1]:.4f}")

    # 파라미터가 실제로 갱신됐는지(그래디언트가 제대로 흘렀는지) 확인
    param_before = gen.q_params[0].clone()
    train_step(gen, disc, real_batch, opt_g, opt_d)
    param_after = gen.q_params[0]
    changed = not torch.allclose(param_before, param_after)
    print("양자 회로 파라미터가 학습으로 실제 갱신됨:", changed)
    assert changed, "그래디언트가 양자 회로까지 전파되지 않음 — 버그"
    print("OK — 양자 생성자까지 역전파(그래디언트) 정상 흐름 확인")
