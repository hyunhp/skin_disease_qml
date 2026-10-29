# -*- coding: utf-8 -*-
"""
Patch Quantum GAN (Andra et al. Section 3.2, Table 3·4).

sub-generator 여러 개가 patch를 만들어 이어붙이고, 판별자는 고전 5층 FC.
측정: 전체 큐빗 확률 중 ancilla qubit=0 항목만 patch로 씀(post-selection). patch별 재정규화는 하지 않아
patch 밝기 총합(0~1)도 학습됨. 데이터 큐빗만 측정하면 patch 합이 1로 고정돼 배경 patch를 표현하지 못함.
"""
import math
import torch
import torch.nn as nn
import pennylane as qml


class PatchQuantumGenerator(nn.Module):
    """sub-generator ensemble 양자 생성자.

    논문 스펙: n_generators=16, n_data_qubits=7, n_ancillas=1, q_depth=10
    실습 스펙: n_generators=4, n_data_qubits=6, n_ancillas=1, q_depth=10 (train_qgan_checkpoint.py가 지정)
    """

    def __init__(self, n_generators=4, n_data_qubits=4, n_ancillas=1, q_depth=3, dev_name="default.qubit"):
        super().__init__()
        self.n_generators = n_generators
        self.n_data_qubits = n_data_qubits
        self.n_ancillas = n_ancillas
        self.n_qubits = n_data_qubits + n_ancillas
        self.q_depth = q_depth
        self.patch_dim = 2 ** n_data_qubits  # sub-generator 1개가 만드는 patch 길이
        self.anc_stride = 2 ** n_ancillas  # ancilla qubit=0 항목의 간격 ([::2])

        dev = qml.device(dev_name, wires=self.n_qubits)
        n_qubits = self.n_qubits

        @qml.qnode(dev, interface="torch", diff_method="backprop")
        def circuit(noise, weights):
            # 1) 노이즈 angle encoding
            for i in range(n_qubits):
                qml.RY(noise[i], wires=i)
            # 2) 변분 layer: 회전 + 인접 CZ (논문 Fig.10)
            for layer in range(q_depth):
                for i in range(n_qubits):
                    qml.RY(weights[layer, i], wires=i)
                for i in range(n_qubits - 1):
                    qml.CZ(wires=[i, i + 1])
            # 전체 측정 → forward에서 ancilla qubit=0 항목만 사용 (post-selection)
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
                probs = self.circuit(noise, weights)[::self.anc_stride]  # ancilla qubit=0 항목만 → (2**n_data_qubits,)
                batch_patches.append(probs)
            all_patches.append(torch.stack(batch_patches))  # (batch, patch_dim)
        # patch를 이어붙여 이미지 벡터로
        images = torch.cat(all_patches, dim=1)  # (batch, n_generators * patch_dim)
        # qml.probs는 float64 → 판별자(float32)에 맞춰 캐스팅
        return images.float()

    @property
    def output_dim(self):
        return self.n_generators * self.patch_dim


class ClassicalDiscriminator(nn.Module):
    """논문 Table 4 판별자: 5층 FC, ReLU, sigmoid."""

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
    """QGAN 한 step (논문 Eq.(5)를 표준 BCE GAN으로 구현)."""
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
    print("[검증] QGAN 생성자/판별자 forward+backward(gradient) 동작 확인 - 실제 데이터 없이 랜덤값 사용")
    torch.manual_seed(0)

    gen = PatchQuantumGenerator(n_generators=2, n_data_qubits=3, n_ancillas=1, q_depth=2)
    disc = ClassicalDiscriminator(input_dim=gen.output_dim)
    print(f"생성자 출력 차원: {gen.output_dim} (sub-generator {gen.n_generators} x patch {gen.patch_dim})")
    print(f"생성자 전체 큐빗: {gen.n_qubits} (데이터 {gen.n_data_qubits} + ancilla {gen.n_ancillas})")

    fake_batch = gen(batch_size=4)
    print("생성 이미지 batch shape:", tuple(fake_batch.shape))
    assert fake_batch.shape == (4, gen.output_dim)
    # patch는 ancilla qubit=0 확률이라 0 이상, 합 1 이하여야 함
    for i in range(gen.n_generators):
        patch = fake_batch[0, i * gen.patch_dim:(i + 1) * gen.patch_dim]
        assert patch.min().item() >= 0 and patch.sum().item() <= 1.0 + 1e-4, f"sub-generator {i} 출력 이상: {patch.sum().item()}"
    print("OK - 각 sub-generator 출력이 유효한 부분 확률(0 이상, 합 1 이하) 확인")

    real_batch = torch.rand(4, gen.output_dim)
    real_batch = real_batch / real_batch.sum(dim=1, keepdim=True)  # 확률분포처럼 정규화(테스트용)

    opt_g = torch.optim.Adam(gen.parameters(), lr=0.1)
    opt_d = torch.optim.Adam(disc.parameters(), lr=0.01)

    losses_before = train_step(gen, disc, real_batch, opt_g, opt_d)
    print(f"1 step 학습 후 loss_g={losses_before[0]:.4f}, loss_d={losses_before[1]:.4f}")

    # 파라미터가 실제로 갱신됐는지(gradient가 제대로 흘렀는지) 확인
    param_before = gen.q_params[0].clone()
    train_step(gen, disc, real_batch, opt_g, opt_d)
    param_after = gen.q_params[0]
    changed = not torch.allclose(param_before, param_after)
    print("양자 회로 파라미터가 학습으로 실제 갱신됨:", changed)
    assert changed, "gradient가 양자 회로까지 전파되지 않음 - 버그"
    print("OK - 양자 생성자까지 역전파(gradient) 정상 흐름 확인")
