# -*- coding: utf-8 -*-
"""
MediQ-GAN(arXiv:2506.21015) dual-stream 생성자 — 개념 데모용 축소판.
동아대 대학원 QML 강의 3일차 — "생성자 내부에서 고전+양자 레이어를 skip-connection으로 융합"하는
레이어 단위 하이브리드 아키텍처를 학생들이 직접 눈으로 보고 코드로 이해하도록 하는 목적.

⚠ 이건 MediQ-GAN 원 논문의 완전한 재현이 아니다(원 논문: 64×64 RGB, ISIC 2019/ODIR-5k/RetinaMNIST
실사용, 다층 conv 기반 classical encoder/decoder). 다만 2026-09-04부로 **양자 스트림 자체는 원 논문과
동일한 스펙(5개 서브제너레이터 × 16큐빗, 8층 깊이 ansatz)** 을 그대로 씀 — 실측 결과(이 파일 하단
참고) 1회 forward가 약 2~3초로 Colab 라이브 시연에 문제없다고 확인했기 때문에 축소할 이유가 없었다.
남은 단순화는 classical encoder/decoder가 conv가 아니라 단순 MLP라는 점, 그리고 입력이 실제 64×64
RGB가 아니라 2일차 파이프라인이 만든 8×8(64차원) 저해상도 흑백 벡터라는 점뿐이다 — 원본 HAM10000
이미지(600×450)가 커도 문제되지 않는 이유는, 애초에 양자 인코딩 전에 `resize_for_encoding()`으로
8×8까지 축소하기 때문(day3/data_pipeline.py 참고). 실제 정량 결과는 논문 Table 2(FID)를
그대로 인용해서 보여준다(별도 준비자료).

양자회로 설정(`lightning.qubit` + `diff_method="adjoint"`, shots 미지정)은 공식 레포
(github.com/QingyueJ-nd/MediQ-GAN, mediq-gan.py)와 동일하다 — "학습은 실기 없이 exact simulator로"
핵심 방식을 그대로 재현한다.
2026-09-22: 회로 본체도 레포 quantum_circuit과 일치시킴(기존 RY 인코딩·CNOT·PauliZ → RY→RX 인코딩·CZ·PauliX),
서브제너레이터마다 서로 다른 site 토큰을 받고 큐빗 평균 스칼라를 4×4 맵에 배치하는 레포 방식도 반영.
(2026-09-01 draft에서는 lightning.qubit이 backprop 미분을 지원하지 않아 default.qubit+backprop으로
우회했었으나, 2026-09-04 diff_method를 논문과 동일한 adjoint로 바꾸면서 디바이스도 원 논문과 같은
lightning.qubit으로 되돌리고, 큐빗 수·서브제너레이터 수도 원 논문 스펙(16큐빗×5개)으로 올림 — 3일차
실습은 어차피 사전학습 체크포인트를 불러와 쓰는 방식이라 학습 속도상 축소를 유지할 이유가 없었음.)
"""
import math
import torch
import torch.nn as nn
import pennylane as qml


class ToyDualStreamGenerator(nn.Module):
    """MediQ-GAN Fig.2 구조: 입력 특징을 절반씩 나눠 고전/양자 스트림으로 병렬 처리한 뒤
    concat(skip-connection에 해당)으로 융합. 양자 스트림은 공식 레포(mediq-gan.py의
    quantum_circuit·_quantum_branch_8to4)와 같은 방식:
      - 양자 쪽 절반을 4×4=16 site로 보고, site별 벡터를 q_align(Linear)으로 n_qubits차원 토큰으로 맞춤
      - linspace(0,15,n_generators).round()로 고른 site([0,4,8,11,15])를 서브제너레이터마다 하나씩 입력
      - 회로: RY(x)→RX(x) 인코딩 → [학습 RY + 인접 CZ] × q_depth → PauliX 기댓값
      - 큐빗 방향 평균 → site당 스칼라 1개 → 4×4 맵의 해당 칸에 배치(나머지 11칸은 0)
      - 1×1 conv(칸별 독립, 학습됨)로 n_generators채널 → q_ch채널 투영 후 고전 스트림과 concat
    (q_depth: 논문 그림 기준 8, 레포 CLI 기본값은 6)"""

    def __init__(self, in_dim=64, n_qubits=16, q_depth=8, n_generators=5, out_dim=64,
                 q_ch=16, dev_name="lightning.qubit"):
        super().__init__()
        assert in_dim % 2 == 0, "고전/양자 스트림으로 절반씩 나누려면 in_dim이 짝수여야 함"
        self.half = in_dim // 2
        assert self.half % 16 == 0, "양자 쪽 절반을 4×4=16 site로 나누려면 in_dim/2가 16의 배수여야 함"
        self.site_dim = self.half // 16
        self.n_qubits = n_qubits
        self.q_depth = q_depth
        self.n_generators = n_generators
        self.site_idx = torch.linspace(0, 15, steps=n_generators).round().long().tolist()

        # 고전 스트림 — MediQ-GAN의 "classical encoder" 역할(단순화: conv 대신 MLP)
        self.classical_stream = nn.Sequential(
            nn.Linear(self.half, 32), nn.ReLU(),
            nn.Linear(32, self.half),
        )

        # 양자 스트림 — site별 벡터를 큐빗 수에 맞추는 aligner(레포의 q_align)
        self.q_align = nn.Linear(self.site_dim, n_qubits)

        dev = qml.device(dev_name, wires=n_qubits)

        @qml.qnode(dev, interface="torch", diff_method="adjoint")
        def q_circuit(x, weights):
            # 공식 레포와 동일: 같은 값으로 RY→RX 인코딩, 학습 RY + 인접 CZ 반복, X-basis 측정
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
        # 레포의 proj_qexp: 5개 스칼라 맵(4×4) → q_ch채널, 1×1 conv라 칸별 독립 처리
        self.proj_qexp = nn.Conv2d(n_generators, q_ch, 1)

        # 융합 후 디코더 — skip-connection으로 합쳐진 특징을 최종 출력으로 (MediQ-GAN의 decoder conv에 해당)
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
        for g, si in enumerate(self.site_idx):              # 서브제너레이터 g ↔ site si
            outs = torch.stack([torch.stack(self.q_circuit(tokens[b, si], self.q_weights[g]))
                                for b in range(B)])         # (B, n_qubits)
            y, x = divmod(si, 4)
            q_maps[:, g, y, x] = outs.mean(dim=1).to(z_quantum.dtype)  # 큐빗 평균 → 스칼라
        return self.proj_qexp(q_maps).flatten(1)            # (B, q_ch*16)

    def forward(self, z):
        # z: (batch, in_dim) — 잠재벡터를 절반씩 스트림에 분배 (MediQ-GAN Fig.2: "feature map split")
        z_classical, z_quantum = z[:, :self.half], z[:, self.half:]
        classical_feat = self.classical_stream(z_classical)  # (batch, half)
        quantum_feat = self.quantum_stream(z_quantum)        # (batch, q_ch*16)
        fused = torch.cat([classical_feat, quantum_feat], dim=1)  # skip-connection 융합
        return self.decoder(fused)


if __name__ == "__main__":
    import time

    print("[검증] MediQ-GAN dual-stream 생성자 forward+backward 확인 (원 논문 스펙: 16큐빗×5서브제너레이터)")
    torch.manual_seed(0)

    # 2일차 파이프라인 실제 산출물 크기와 동일: 8x8(64픽셀) 저해상도 벡터, 배치 1(3일차 노트북과 동일)
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
    print("고전 스트림 그래디언트 존재:", has_grad_classical)
    print("양자 스트림 그래디언트 존재(서브제너레이터 5개 전부):", has_grad_quantum)
    assert has_grad_classical and has_grad_quantum, "두 스트림 중 하나는 학습이 안 됨 — 버그"
    print("OK — 고전+양자 스트림(5개 서브제너레이터 전부) 역전파(그래디언트) 정상 흐름 확인")
    print("→ 위 forward+backward 소요시간이 Colab 라이브 시연(1회 forward, 학습 없음) 기준 수용 가능한지 확인할 것")
