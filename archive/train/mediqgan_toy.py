# -*- coding: utf-8 -*-
"""
MediQ-GAN(arXiv:2506.21015) dual-stream 생성자 - 3일차 실습용 축소판.

- 양자 stream은 원 논문 스펙 그대로: sub-generator 5개 × 16큐빗, depth 8, lightning.qubit + adjoint.
  회로는 공식 레포(mediq-gan.py의 quantum_circuit)와 같음: RY→RX encoding, [RY + 인접 CZ], PauliX 측정
- 단순화: 고전 encoder/decoder가 conv 대신 MLP, 입력이 64×64 RGB 대신 16×16 그레이스케일
"""
import math
import torch
import torch.nn as nn
import pennylane as qml


class ToyDualStreamGenerator(nn.Module):
    """잠재벡터를 절반씩 고전/양자 stream으로 처리한 뒤 concat으로 융합 (논문 Fig.1 "Feature Split").

    양자 stream: 16 site 중 [0,4,8,11,15]만 회로 5개가 처리 → 큐빗 평균 스칼라를 4×4 맵에 배치 → 1×1 conv.
    q_depth는 논문 그림 기준 8 (레포 CLI 기본값 6).
    """

    def __init__(self, in_dim=64, n_qubits=16, q_depth=8, n_generators=5, out_dim=64,
                 q_ch=16, dev_name="lightning.qubit"):
        super().__init__()
        assert in_dim % 2 == 0, "고전/양자 stream으로 절반씩 나누려면 in_dim이 짝수여야 함"
        self.half = in_dim // 2
        assert self.half % 16 == 0, "양자 쪽 절반을 4×4=16 site로 나누려면 in_dim/2가 16의 배수여야 함"
        self.site_dim = self.half // 16
        self.n_qubits = n_qubits
        self.q_depth = q_depth
        self.n_generators = n_generators
        self.site_idx = torch.linspace(0, 15, steps=n_generators).round().long().tolist()

        # 고전 stream (원 논문 conv encoder를 MLP로 단순화)
        self.classical_stream = nn.Sequential(
            nn.Linear(self.half, 32), nn.ReLU(),
            nn.Linear(32, self.half),
        )

        # site 벡터를 큐빗 수(16)에 맞춤 (레포의 q_align)
        self.q_align = nn.Linear(self.site_dim, n_qubits)

        dev = qml.device(dev_name, wires=n_qubits)

        @qml.qnode(dev, interface="torch", diff_method="adjoint")
        def q_circuit(x, weights):
            # 공식 레포와 같은 회로
            for i in range(n_qubits):
                qml.RY(x[i], wires=i)
                qml.RX(x[i], wires=i)
            for layer in range(q_depth):
                for i in range(n_qubits):
                    qml.RY(weights[layer, i], wires=i)
                for i in range(n_qubits - 1):
                    qml.CZ(wires=[i, i + 1])
            return [qml.expval(qml.PauliX(i)) for i in range(n_qubits)]

        self.q_circuit = q_circuit
        self.q_weights = nn.ParameterList([
            nn.Parameter(torch.rand(q_depth, n_qubits) * math.pi) for _ in range(n_generators)
        ])
        # 5채널 4×4 맵 → q_ch채널 (1×1 conv, 레포의 proj_qexp)
        self.proj_qexp = nn.Conv2d(n_generators, q_ch, 1)

        # 융합 특징 → 최종 이미지 (원 논문 conv decoder를 MLP로 단순화)
        fused_dim = self.half + q_ch * 16
        self.decoder = nn.Sequential(
            nn.Linear(fused_dim, 32), nn.ReLU(),
            nn.Linear(32, out_dim), nn.Tanh(),
        )

    def quantum_stream(self, z_quantum):
        B = z_quantum.shape[0]
        sites = z_quantum.view(B, 16, self.site_dim)       # 4×4 = 16 site
        tokens = self.q_align(sites)                        # (B, 16, n_qubits)
        q_maps = torch.zeros(B, self.n_generators, 4, 4, dtype=z_quantum.dtype)
        for g, si in enumerate(self.site_idx):              # sub-generator g ↔ site si
            outs = torch.stack([torch.stack(self.q_circuit(tokens[b, si], self.q_weights[g]))
                                for b in range(B)])         # (B, n_qubits)
            y, x = divmod(si, 4)
            q_maps[:, g, y, x] = outs.mean(dim=1).to(z_quantum.dtype)  # 큐빗 평균 → 스칼라
        return self.proj_qexp(q_maps).flatten(1)            # (B, q_ch*16)

    def forward(self, z):
        # 잠재벡터를 절반씩 두 stream에 분배
        z_classical, z_quantum = z[:, :self.half], z[:, self.half:]
        classical_feat = self.classical_stream(z_classical)  # (batch, half)
        quantum_feat = self.quantum_stream(z_quantum)        # (batch, q_ch*16)
        fused = torch.cat([classical_feat, quantum_feat], dim=1)  # skip-connection 융합
        return self.decoder(fused)


if __name__ == "__main__":
    import time

    print("[검증] MediQ-GAN dual-stream 생성자 forward+backward 확인 (원 논문 스펙: 16큐빗×5 sub-generator)")
    torch.manual_seed(0)

    # 구조 검증용으로 작은 8x8(64픽셀) 입력을 씀 - 실습 스펙은 16x16(256). batch 1
    IMG_SIZE = 8
    gen = ToyDualStreamGenerator(in_dim=IMG_SIZE * IMG_SIZE, n_qubits=16, q_depth=8,
                                  n_generators=5, out_dim=IMG_SIZE * IMG_SIZE)
    z = torch.rand(1, IMG_SIZE * IMG_SIZE)

    t0 = time.perf_counter()
    out = gen(z)
    t1 = time.perf_counter()
    print(f"출력 shape: {tuple(out.shape)} (forward 소요: {(t1 - t0) * 1000:.0f}ms)")
    assert out.shape == (1, IMG_SIZE * IMG_SIZE)

    t2 = time.perf_counter()
    loss = out.pow(2).mean()
    loss.backward()
    t3 = time.perf_counter()
    has_grad_classical = gen.classical_stream[0].weight.grad is not None
    has_grad_quantum = all(w.grad is not None for w in gen.q_weights)
    print(f"backward 소요: {(t3 - t2) * 1000:.0f}ms")
    print("고전 stream gradient 존재:", has_grad_classical)
    print("양자 stream gradient 존재(sub-generator 5개 전부):", has_grad_quantum)
    assert has_grad_classical and has_grad_quantum, "두 stream 중 하나는 학습이 안 됨 - 버그"
    print("OK - 고전+양자 stream(5개 sub-generator 전부) 역전파(gradient) 정상 흐름 확인")
    print("→ 위 forward+backward 소요시간이 Colab 라이브 시연(1회 forward, 학습 없음) 기준 수용 가능한지 확인할 것")
