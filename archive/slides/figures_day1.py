"""1일차 슬라이드용 설명 그림 생성. 출력: fig_day1/*.png (dpi 200).

수치 출처: MediQ-GAN (arXiv:2506.21015v2) Table 1, Extended Data Table 2·3·4.
사용법: python3 figures_day1.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

for f in ("/root/.fonts/NotoSansKR-Regular.ttf", "/root/.fonts/NotoSansKR-Bold.ttf"):
    if os.path.exists(f):
        fm.fontManager.addfont(f)
plt.rcParams.update({
    "font.family": ["Noto Sans KR", "DejaVu Sans"], "axes.unicode_minus": False,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#9A9A9A", "axes.labelcolor": "#424242", "xtick.color": "#6B6B6B", "ytick.color": "#6B6B6B",
    "font.size": 11, "savefig.dpi": 200, "savefig.bbox": "tight", "savefig.facecolor": "white",
})
# 덱 팔레트
DARK, GREEN, SAND, GRAY, LGRAY, PURPLE, ORANGE = "#1E3932", "#00754A", "#DFC49D", "#6B6B6B", "#C9C6BE", "#5B3F8C", "#B45F06"
INK = "#212121"
PURPLE_BG = "#ECE6F5"
GREEN2 = "#006241"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig_day1")
os.makedirs(OUT, exist_ok=True)


def save(fig, name):
    fig.savefig(os.path.join(OUT, name))
    plt.close(fig)


def box(ax, x, y, w, h, text, fc="#F2F0EB", ec=GRAY, tc=INK, fs=11, bold=False, lw=1.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=tc, fontsize=fs,
            fontweight="bold" if bold else "normal", linespacing=1.4)


def arrow(ax, x1, y1, x2, y2, color=GRAY, lw=1.6, style="-|>", rad=0.0, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=14, color=color, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}", linestyle=ls))


# 1. GAN 구조 -------------------------------------------------------------
def fig_gan():
    fig, ax = plt.subplots(figsize=(9.6, 3.9))
    ax.set_xlim(0, 12); ax.set_ylim(0, 5); ax.axis("off")
    box(ax, 0.1, 2.0, 1.5, 1.0, "잠재 노이즈\nz ~ p(z)", fs=10.5)
    box(ax, 2.6, 1.8, 2.2, 1.4, "Generator\nG(z; θ_G)", fc="#E4F0EA", ec=GREEN, tc=GREEN, bold=True)
    box(ax, 5.6, 2.0, 1.6, 1.0, "생성 샘플\nx̃ = G(z)", fs=10.5)
    box(ax, 5.6, 0.1, 1.6, 1.0, "실제 샘플\nx ~ p_data", fs=10.5)
    box(ax, 8.2, 1.8, 2.0, 1.4, "Discriminator\nD(x; θ_D)", fc="#ECE6F5", ec=PURPLE, tc=PURPLE, bold=True)
    box(ax, 10.9, 2.0, 1.0, 1.0, "진짜/가짜\n점수", fs=10, ec=DARK)
    arrow(ax, 1.65, 2.5, 2.55, 2.5); arrow(ax, 4.85, 2.5, 5.55, 2.5); arrow(ax, 7.25, 2.5, 8.15, 2.5)
    arrow(ax, 7.25, 0.65, 9.2, 1.75); arrow(ax, 10.25, 2.5, 10.85, 2.5)
    arrow(ax, 11.4, 3.1, 3.7, 3.3, color=GREEN, rad=0.35, ls="--")
    ax.text(7.6, 4.75, "G 갱신: D를 속이는 방향", color=GREEN, fontsize=10.5, ha="center")
    arrow(ax, 11.4, 1.9, 9.2, 1.75, color=PURPLE, rad=-0.35, ls="--")
    ax.text(10.7, 0.75, "D 갱신: 실제와\n생성을 구분하는 방향", color=PURPLE, fontsize=10.5, ha="center")
    save(fig, "gan_game.png")


# 2. RY 회전과 측정 확률 -----------------------------------------------------
def fig_ry():
    th = np.linspace(0, 2 * np.pi, 400)
    fig, ax = plt.subplots(figsize=(5.6, 3.5))
    ax.plot(th, np.sin(th / 2) ** 2, color=GREEN, lw=2.2, label="P(1) = sin²(θ/2)")
    ax.plot(th, np.cos(th / 2) ** 2, color=GRAY, lw=2.2, label="P(0) = cos²(θ/2)")
    for t, lab in ((0, "θ=0"), (np.pi / 2, "θ=π/2"), (np.pi, "θ=π")):
        ax.plot([t], [np.sin(t / 2) ** 2], "o", color=GREEN, ms=8, mec="white", mew=1.5)
    ax.set_xticks([0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi])
    ax.set_xticklabels(["0", "π/2", "π", "3π/2", "2π"])
    ax.set_xlabel("회전각 θ (RY 게이트)"); ax.set_ylabel("측정 확률")
    ax.set_ylim(-0.02, 1.05)
    ax.text(0.15, 0.08, "|0⟩", color=GRAY, fontsize=10); ax.text(np.pi - 0.2, 0.93, "|1⟩", color=GREEN, fontsize=10)
    ax.text(np.pi / 2 + 0.05, 0.56, "50 : 50", color=INK, fontsize=10)
    ax.legend(frameon=False, loc="center right", fontsize=10)
    ax.grid(axis="y", color="#E6E3DC", lw=0.8)
    save(fig, "qubit_ry_curve.png")


# 3. 얽힘: 독립 상태 vs Bell 상태 ---------------------------------------------
def fig_bell():
    labels = ["00", "01", "10", "11"]
    prod = [0.25] * 4
    bell = [0.5, 0, 0, 0.5]
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.2), sharey=True)
    for ax, vals, title, col in ((axes[0], prod, "얽힘 없음\nRY(π/2) ⊗ RY(π/2)", GRAY),
                                 (axes[1], bell, "얽힘\nRY(π/2) 후 CNOT", GREEN)):
        ax.bar(range(4), vals, width=0.5, color=col)
        ax.set_xticks(range(4)); ax.set_xticklabels([f"|{l}⟩" for l in labels])
        ax.set_title(title, fontsize=10.5, color=INK, pad=8)
        for i, v in enumerate(vals):
            ax.text(i, v + 0.015, f"{v:.2f}", ha="center", fontsize=10, color=INK)
        ax.set_ylim(0, 0.62); ax.grid(axis="y", color="#E6E3DC", lw=0.8); ax.set_axisbelow(True)
    axes[0].set_ylabel("측정 확률")
    fig.tight_layout(w_pad=2)
    save(fig, "bell_bars.png")


# 4. shot 수와 기댓값 추정 오차 ------------------------------------------------
def fig_shots():
    rng = np.random.default_rng(0)
    theta = np.pi / 3
    p1 = np.sin(theta / 2) ** 2
    true = 1 - 2 * p1  # <Z> = cos(theta) = 0.5
    ns = np.unique(np.round(np.logspace(1, 5, 40)).astype(int))
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    for _ in range(12):
        est = [1 - 2 * rng.binomial(n, p1) / n for n in ns]
        ax.plot(ns, est, color=LGRAY, lw=1.0)
    ax.axhline(true, color=GREEN, lw=2.2, label="exact ⟨Z⟩ = 0.5")
    sd = np.sqrt((1 - true ** 2) / ns)
    ax.fill_between(ns, true - sd, true + sd, color=GREEN, alpha=0.14, label="±1σ = √((1-⟨Z⟩²)/N)")
    ax.set_xscale("log"); ax.set_xlabel("shot 수 N"); ax.set_ylabel("⟨Z⟩ 추정값")
    ax.set_ylim(-0.2, 1.2)
    ax.legend(frameon=False, fontsize=10, loc="lower right")
    ax.grid(axis="y", color="#E6E3DC", lw=0.8)
    ax.text(12, 1.08, "회색: 독립 실험 12회 (θ = π/3)", fontsize=9.5, color=GRAY)
    save(fig, "shots_convergence.png")


# 5. hybrid 학습 루프 ---------------------------------------------------------
def fig_loop():
    fig, ax = plt.subplots(figsize=(10.4, 3.5))
    ax.set_xlim(0, 13); ax.set_ylim(-0.6, 4.4); ax.axis("off")
    box(ax, 0.1, 1.5, 1.9, 1.3, "입력 z\n(노이즈)", fs=10.5)
    box(ax, 2.6, 1.3, 3.0, 1.7, "양자회로 U(z, θ)\nencoding + ansatz", fc="#ECE6F5", ec=PURPLE, tc=PURPLE, bold=True, fs=10.5)
    box(ax, 6.2, 1.5, 2.0, 1.3, "측정\n⟨X_i⟩ 또는 확률", fc="#ECE6F5", ec=PURPLE, tc=PURPLE, fs=10.5)
    box(ax, 8.8, 1.5, 1.8, 1.3, "고전 모델\n+ 손실 L", fc="#E4F0EA", ec=GREEN, tc=GREEN, fs=10.5, bold=True)
    box(ax, 11.0, 1.5, 1.9, 1.3, "optimizer\n(Adam 등)", fc="#E4F0EA", ec=GREEN, tc=GREEN, fs=10.5)
    arrow(ax, 2.05, 2.15, 2.55, 2.15); arrow(ax, 5.65, 2.15, 6.15, 2.15)
    arrow(ax, 8.25, 2.15, 8.75, 2.15); arrow(ax, 10.65, 2.15, 10.95, 2.15)
    arrow(ax, 11.95, 1.45, 4.1, 1.25, color=ORANGE, rad=-0.18, ls="--", lw=1.8)
    ax.text(7.2, -0.35, "θ 갱신: ∂L/∂θ (adjoint 또는 parameter-shift)", color=ORANGE, fontsize=10.5, ha="center")
    ax.text(3.6, 3.55, "양자 영역", color=PURPLE, fontsize=10.5, fontweight="bold", ha="center")
    ax.text(10.5, 3.55, "고전 영역", color=GREEN, fontsize=10.5, fontweight="bold", ha="center")
    ax.plot([2.6, 8.2], [3.35, 3.35], color=PURPLE, lw=1.4); ax.plot([8.8, 12.9], [3.35, 3.35], color=GREEN, lw=1.4)
    save(fig, "pqc_hybrid_loop.png")


# 6. state vector 메모리 -------------------------------------------------------
def fig_memory():
    n = np.arange(1, 51)
    mem = (2.0 ** n) * 16  # complex128 = 16 byte
    fig, ax = plt.subplots(figsize=(6.4, 3.7))
    ax.plot(n, mem, color=GREEN, lw=2.2)
    pts = [(8, "8큐빗 (QGAN)\n4 KiB"), (16, "16큐빗 (MediQ-GAN)\n1 MiB"), (30, "30큐빗\n16 GiB"), (50, "50큐빗\n16 PiB")]
    for q, lab in pts:
        m = 2.0 ** q * 16
        ax.plot([q], [m], "o", color=ORANGE, ms=8, mec="white", mew=1.5)
        if q <= 16:
            ax.annotate(lab, (q, m), xytext=(14, -14), textcoords="offset points", fontsize=9.5, color=INK,
                        ha="left", va="top", linespacing=1.3)
        else:
            ax.annotate(lab, (q, m), xytext=(-14, 16), textcoords="offset points", fontsize=9.5, color=INK,
                        ha="right", va="bottom", linespacing=1.3)
    ax.set_yscale("log"); ax.set_xlabel("큐빗 수 n"); ax.set_ylabel("state vector 메모리 (byte)")
    ax.set_ylim(10, 1e18); ax.set_xlim(0, 52)
    ax.set_yticks([1e3, 1e6, 1e9, 1e12, 1e15, 1e18]); ax.set_yticklabels(["1 KB", "1 MB", "1 GB", "1 TB", "1 PB", "1 EB"])
    ax.grid(axis="y", color="#E6E3DC", lw=0.8)
    ax.text(1, 3e16, "2ⁿ 복소 진폭 × 16 byte (complex128)", fontsize=9.5, color=GRAY)
    save(fig, "statevector_memory.png")


# 6b. 3큐빗 상태벡터 -> 측정 확률 -------------------------------------------------
def fig_state3():
    c = np.array([0.45, 0.30, 0.10, 0.55, 0.25, 0.35, 0.40, 0.30])
    c = c / np.linalg.norm(c)
    labs = [format(i, "03b") for i in range(8)]
    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    ax.bar(range(8), c ** 2, width=0.55, color=GREEN)
    for i, v in enumerate(c ** 2):
        ax.text(i, v + 0.008, f"{v:.2f}", ha="center", fontsize=9.5, color=INK)
    ax.set_xticks(range(8)); ax.set_xticklabels([f"|{l}⟩" for l in labs], fontsize=9.5)
    ax.set_ylabel("측정 확률 P(x) = |c_x|²"); ax.set_ylim(0, 0.3)
    ax.grid(axis="y", color="#E6E3DC", lw=0.8); ax.set_axisbelow(True)
    ax.text(7.4, 0.275, "8개 확률의 합 = 1", ha="right", fontsize=10, color=GRAY)
    save(fig, "state3_probs.png")


# 7. FID 개념도 -----------------------------------------------------------------
def fig_fid():
    rng = np.random.default_rng(3)
    real = rng.multivariate_normal([0, 0], [[1.0, 0.5], [0.5, 0.8]], 220)
    good = rng.multivariate_normal([0.35, 0.2], [[0.9, 0.4], [0.4, 0.8]], 220)
    bad = rng.multivariate_normal([2.4, 1.6], [[0.25, 0.0], [0.0, 0.25]], 220)
    fig, axes = plt.subplots(1, 2, figsize=(7.8, 3.5), sharex=True, sharey=True)
    for ax, gen, title, col in ((axes[0], good, "FID 낮음: 분포가 겹침", GREEN), (axes[1], bad, "FID 높음: 분포가 어긋남 (mode 부족)", ORANGE)):
        ax.scatter(real[:, 0], real[:, 1], s=9, color=GRAY, alpha=0.55, label="실제")
        ax.scatter(gen[:, 0], gen[:, 1], s=9, color=col, alpha=0.7, label="생성")
        ax.set_title(title, fontsize=10.5, color=INK, pad=6)
        ax.set_xticks([]); ax.set_yticks([]); ax.legend(frameon=False, fontsize=9, loc="lower right")
    axes[0].set_ylabel("Inception 특징 공간 (2차원 투영)", fontsize=9.5)
    fig.tight_layout(w_pad=1.5)
    save(fig, "fid_concept.png")


# 8. MediQ-GAN 소수 클래스 FID (Extended Data Table 2) --------------------------
def fig_fid_minority():
    ds = ["ISIC 2019", "ODIR-5k", "RetinaMNIST"]
    data = {
        "DCGAN": [259.9, 217.9, 197.5],
        "FastGAN": [230.8, 217.5, 186.9],
        "DiT": [179.6, 181.0, 130.8],
        "MediQ-GAN": [174.5, 158.9, 141.4],
    }
    cols = {"DCGAN": LGRAY, "FastGAN": "#9A9A9A", "DiT": SAND, "MediQ-GAN": GREEN}
    fig, ax = plt.subplots(figsize=(8.2, 3.7))
    w = 0.19
    x = np.arange(3)
    for k, (name, vals) in enumerate(data.items()):
        xs = x + (k - 1.5) * (w + 0.02)
        ax.bar(xs, vals, width=w, color=cols[name], label=name)
        for xx, v in zip(xs, vals):
            ax.text(xx, v + 4, f"{v:.0f}", ha="center", fontsize=9.5, color=INK, fontweight="bold" if name == "MediQ-GAN" else "normal")
    ax.set_xticks(x); ax.set_xticklabels(ds, fontsize=11)
    ax.set_ylabel("소수 클래스 평균 FID (낮을수록 좋음)"); ax.set_ylim(0, 300)
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.12), fontsize=10)
    ax.grid(axis="y", color="#E6E3DC", lw=0.8); ax.set_axisbelow(True)
    save(fig, "mediq_fid_minority.png")


# 9. IBM 실기 vs 시뮬레이션 FID (Extended Data Table 4) ---------------------------
def fig_ibm():
    cls = ["ISIC\nmel", "ISIC\ndf", "ISIC\nvasc", "ODIR\nN", "ODIR\nH", "ODIR\nM", "Retina\nGR0", "Retina\nGR3", "Retina\nGR4"]
    sim = [187.3, 182.2, 171.4, 162.8, 167.4, 144.3, 127.3, 159.7, 116.9]
    ibm = [256.3, 261.5, 214.3, 200.9, 197.5, 168.2, 146.3, 197.6, 177.7]
    fig, ax = plt.subplots(figsize=(8.4, 3.7))
    x = np.arange(len(cls))
    for i in x:
        ax.plot([i, i], [sim[i], ibm[i]], color=LGRAY, lw=2.0, zorder=1)
    ax.scatter(x, sim, s=70, color=GREEN, zorder=3, label="noiseless 시뮬레이션", edgecolor="white", linewidth=1.5)
    ax.scatter(x, ibm, s=70, color=ORANGE, zorder=3, label="IBM Marrakesh 실기", edgecolor="white", linewidth=1.5)
    for i in x:
        ax.text(i + 0.12, ibm[i], f"+{ibm[i] - sim[i]:.0f}", fontsize=9, color=INK, va="center")
    ax.set_xticks(x); ax.set_xticklabels(cls, fontsize=9.5)
    ax.set_ylabel("클래스별 FID (낮을수록 좋음)"); ax.set_ylim(90, 290)
    ax.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.13), fontsize=10)
    ax.grid(axis="y", color="#E6E3DC", lw=0.8); ax.set_axisbelow(True)
    save(fig, "mediq_ibm_fid.png")


# 10. 분류 정확도 dot plot (Table 1, EfficientNet-B0 / ViT-small) -------------------
def fig_acc():
    rows = [  # (label, baseline, fastgan, dit, mediq)
        ("ISIC 2019 · EffNet-B0", 72.24, 75.97, 73.82, 75.99),
        ("ISIC 2019 · ViT-small", 72.49, 80.22, 79.28, 82.60),
        ("ODIR-5k · EffNet-B0", 52.69, 56.52, 58.40, 59.52),
        ("ODIR-5k · ViT-small", 55.62, 58.63, 55.66, 59.06),
        ("RetinaMNIST · EffNet-B0", 47.50, 53.75, 55.62, 56.75),
        ("RetinaMNIST · ViT-small", 50.93, 64.37, 53.12, 63.75),
    ]
    fig, ax = plt.subplots(figsize=(8.4, 3.9))
    ys = np.arange(len(rows))[::-1]
    for y, (lab, b, f, d, m) in zip(ys, rows):
        ax.plot([min(b, f, d, m), max(b, f, d, m)], [y, y], color="#E6E3DC", lw=2.2, zorder=1)
        ax.scatter([b], [y], s=62, color=GRAY, zorder=3, edgecolor="white", linewidth=1.3, label="baseline (증강 없음)" if y == ys[0] else None)
        ax.scatter([f], [y], s=62, color="#B8B3A6", marker="s", zorder=3, edgecolor="white", linewidth=1.3, label="FastGAN" if y == ys[0] else None)
        ax.scatter([d], [y], s=62, color=SAND, marker="D", zorder=3, edgecolor="#B89B6B", linewidth=0.8, label="DiT" if y == ys[0] else None)
        ax.scatter([m], [y], s=92, color=GREEN, zorder=4, edgecolor="white", linewidth=1.5, label="MediQ-GAN" if y == ys[0] else None)
    ax.set_yticks(ys); ax.set_yticklabels([r[0] for r in rows], fontsize=10)
    ax.set_xlabel("분류 정확도 (%)")
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.45, 1.13), fontsize=9.5)
    ax.grid(axis="x", color="#E6E3DC", lw=0.8); ax.set_axisbelow(True)
    save(fig, "mediq_acc_dots.png")


# 11. MediQ-GAN 텐서 shape 흐름 ----------------------------------------------------
def fig_shapes():
    fig, ax = plt.subplots(figsize=(11.2, 3.6))
    ax.set_xlim(0, 15); ax.set_ylim(0, 4.6); ax.axis("off")
    box(ax, 0.05, 1.7, 1.9, 1.3, "z (128차원)\n노이즈\n+ class prototype", fs=9.5)
    box(ax, 2.55, 1.7, 2.1, 1.3, "encoder\n(1×1, 3×3 conv)\nF: 32×4×4", fs=9.5)
    box(ax, 5.35, 2.85, 2.2, 1.1, "고전 stream\nF_cls: 16×4×4", fs=9.5)
    box(ax, 5.35, 0.7, 2.2, 1.5, "양자 stream\n16큐빗 VQC × 5\nF_q: 16×4×4", fc="#ECE6F5", ec=PURPLE, tc=PURPLE, fs=9.5)
    box(ax, 8.3, 1.7, 1.9, 1.3, "concat\nF_fuse: 32×4×4", fc="#E4F0EA", ec=GREEN, tc=GREEN, fs=9.5, bold=True)
    box(ax, 10.9, 1.7, 2.2, 1.3, "decoder\nupsample-blur-conv\n× 3 단계", fs=9.5)
    box(ax, 13.6, 1.7, 1.3, 1.3, "RGB\n3×64×64", fs=9.5, ec=DARK)
    arrow(ax, 1.98, 2.35, 2.5, 2.35); arrow(ax, 4.7, 2.5, 5.3, 3.4); arrow(ax, 4.7, 2.2, 5.3, 1.5)
    arrow(ax, 7.6, 3.4, 8.25, 2.7); arrow(ax, 7.6, 1.5, 8.25, 2.0); arrow(ax, 10.25, 2.35, 10.85, 2.35); arrow(ax, 13.15, 2.35, 13.55, 2.35)
    ax.text(6.45, 0.25, "encoder 출력 32채널 중 16채널을 양자 stream에 투입", fontsize=9.5, color=GRAY, ha="center")
    save(fig, "mediq_shape_flow.png")


# 12. QML 분류: 데이터 종류 x 알고리즘 종류 ----------------------------------------
def fig_taxonomy():
    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.4); ax.axis("off")
    ax.text(5.9, 5.15, "알고리즘", ha="center", fontsize=11, color=GRAY, fontweight="bold")
    ax.text(3.9, 4.65, "고전", ha="center", fontsize=11, color=INK)
    ax.text(7.9, 4.65, "양자", ha="center", fontsize=11, color=INK)
    ax.text(0.25, 2.3, "데이터", ha="center", va="center", fontsize=11, color=GRAY, fontweight="bold", rotation=90)
    ax.text(1.0, 3.35, "고전", ha="center", va="center", fontsize=11, color=INK)
    ax.text(1.0, 1.2, "양자", ha="center", va="center", fontsize=11, color=INK)
    cells = [
        (1.7, 2.45, 4.4, 1.8, "일반 머신러닝\n(CC)", "#F2F0EB", GRAY, INK, False),
        (6.2, 2.45, 3.4, 1.8, "양자 머신러닝\n(CQ)\n이 강의: QGAN, MediQ-GAN", "#E4F0EA", GREEN, GREEN, True),
        (1.7, 0.2, 4.4, 1.8, "양자 시스템에\n고전 기법 적용 (QC)", "#F2F0EB", GRAY, INK, False),
        (6.2, 0.2, 3.4, 1.8, "양자 데이터를\n양자 알고리즘으로 (QQ)", "#F2F0EB", GRAY, INK, False),
    ]
    for x, y, w, h, t, fc, ec, tc, bold in cells:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.1", fc=fc, ec=ec, lw=2.0 if bold else 1.2))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=10.5, color=tc, fontweight="bold" if bold else "normal", linespacing=1.5)
    save(fig, "qml_taxonomy.png")


# 13. 간섭: 같은 회전을 두 번 적용하면 진폭이 상쇄 -------------------------------------
def fig_interference():
    r = 1 / np.sqrt(2)
    stages = [("시작\n|0⟩", [1, 0]), ("RY(π/2) 1회\n(중첩)", [r, r]), ("RY(−π/2) 추가\n(간섭: |1⟩ 상쇄)", [1, 0])]
    fig, axes = plt.subplots(1, 3, figsize=(8.4, 2.9), sharey=True)
    for ax, (title, amp) in zip(axes, stages):
        ax.bar([0, 1], amp, width=0.5, color=[GRAY, GREEN])
        for i, v in enumerate(amp):
            ax.text(i, v + 0.04, f"{v:.2f}", ha="center", fontsize=10, color=INK)
        ax.set_xticks([0, 1]); ax.set_xticklabels(["|0⟩", "|1⟩"])
        ax.set_title(title, fontsize=10, color=INK, pad=8, linespacing=1.4)
        ax.set_ylim(0, 1.25); ax.grid(axis="y", color="#E6E3DC", lw=0.8); ax.set_axisbelow(True)
    axes[0].set_ylabel("진폭")
    fig.tight_layout(w_pad=1.5)
    save(fig, "interference_amp.png")


# 14. 고전 layer와 변분 양자회로 layer 비교 ----------------------------------------------
def fig_layer_compare():
    fig, ax = plt.subplots(figsize=(10.0, 3.3))
    ax.set_xlim(0, 15); ax.set_ylim(0, 5); ax.axis("off")
    ax.text(0.1, 4.55, "고전 신경망 layer", fontsize=11.5, fontweight="bold", color=GRAY)
    ax.text(0.1, 2.2, "VQC (variational quantum circuit) layer", fontsize=11.5, fontweight="bold", color=PURPLE)
    row1 = [("입력 x", "#F2F0EB", GRAY, GRAY), ("W x + b\n(가중치 행렬)", "#F2F0EB", GRAY, GRAY), ("활성화 σ(·)", "#F2F0EB", GRAY, GRAY), ("출력 y", "#F2F0EB", GRAY, GRAY)]
    row2 = [("입력 x", "#F2F0EB", GRAY, GRAY), ("encoding\nRY(x)", PURPLE_BG, PURPLE, PURPLE), ("학습 회전 θ\n+ 얽힘 게이트", PURPLE_BG, PURPLE, PURPLE), ("측정\n⟨Z⟩ 또는 P(x)", PURPLE_BG, PURPLE, PURPLE), ("출력 y", "#F2F0EB", GRAY, GRAY)]
    for row, y in ((row1, 3.0), (row2, 0.55)):
        n = len(row); w = 2.4; gap = (14.8 - n * w) / (n - 1)
        for i, (t, fc, ec, tc) in enumerate(row):
            x = 0.1 + i * (w + gap)
            ax.add_patch(FancyBboxPatch((x, y), w, 1.2, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1.3))
            ax.text(x + w / 2, y + 0.6, t, ha="center", va="center", fontsize=10, color=INK if ec == GRAY else tc, linespacing=1.4)
            if i < n - 1:
                arrow(ax, x + w + 0.03, y + 0.6, x + w + gap - 0.03, y + 0.6)
    save(fig, "layer_compare.png")


# 15. ROC 곡선 예시 (개념도) ---------------------------------------------------------------
def fig_roc():
    rng = np.random.default_rng(7)
    neg = rng.normal(0.0, 1.0, 4000)
    pos_good = rng.normal(1.8, 1.0, 4000)
    pos_weak = rng.normal(0.5, 1.0, 4000)

    def roc(pos):
        th = np.linspace(-6, 8, 400)
        tpr = np.array([(pos > t).mean() for t in th])
        fpr = np.array([(neg > t).mean() for t in th])
        auc = -np.trapezoid(tpr, fpr)
        return fpr, tpr, auc

    fig, ax = plt.subplots(figsize=(4.6, 4.0))
    for pos, col, lab in ((pos_good, GREEN, "분리가 잘 되는 분류기"), (pos_weak, ORANGE, "분리가 약한 분류기")):
        f, t, a = roc(pos)
        ax.plot(f, t, color=col, lw=2.2, label=f"{lab} (AUC {a:.2f})")
    ax.plot([0, 1], [0, 1], color=LGRAY, lw=1.6, ls="--", label="무작위 (AUC 0.50)")
    ax.set_xlabel("FPR: 음성을 양성으로 잘못 판정한 비율"); ax.set_ylabel("TPR: 양성을 양성으로 맞힌 비율")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02)
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    ax.grid(color="#E6E3DC", lw=0.8); ax.set_axisbelow(True)
    ax.text(0.03, 0.93, "예시(개념도)", fontsize=9, color=GRAY)
    save(fig, "roc_example.png")


# 16. LPIPS 계산 흐름 ------------------------------------------------------------------------
def fig_lpips():
    fig, ax = plt.subplots(figsize=(10.4, 3.1))
    ax.set_xlim(0, 15.5); ax.set_ylim(0, 4.4); ax.axis("off")
    box(ax, 0.05, 2.75, 1.8, 1.0, "생성 이미지 A", fs=10)
    box(ax, 0.05, 0.65, 1.8, 1.0, "생성 이미지 B\n(같은 클래스)", fs=10)
    box(ax, 2.7, 1.7, 3.0, 1.1, "사전학습 CNN\n(AlexNet, VGG 등, 고정)", fc="#E4F0EA", ec=GREEN, tc=GREEN, fs=10, bold=True)
    box(ax, 6.6, 1.7, 3.0, 1.1, "layer별 특징 차이\n(채널 정규화 후 제곱 차)", fs=10)
    box(ax, 10.5, 1.7, 2.4, 1.1, "학습된 가중치로\n합산 → 거리 d", fc=PURPLE_BG, ec=PURPLE, tc=PURPLE, fs=10, bold=True)
    box(ax, 13.5, 1.7, 1.9, 1.1, "클래스 내 쌍\n평균 = LPIPS", fs=10, ec=DARK, bold=True)
    arrow(ax, 1.9, 3.2, 2.65, 2.4); arrow(ax, 1.9, 1.15, 2.65, 2.0)
    arrow(ax, 5.75, 2.25, 6.55, 2.25); arrow(ax, 9.65, 2.25, 10.45, 2.25); arrow(ax, 12.95, 2.25, 13.45, 2.25)
    ax.text(7.8, 0.35, "d가 클수록 두 이미지가 지각적으로 다름 → 쌍 평균이 높을수록 생성 이미지가 다양함", fontsize=9.5, color=GRAY, ha="center")
    save(fig, "lpips_flow.png")


# 17. 실제 DF 이미지와 클래스 평균 이미지 (2일차 지표 용어 슬라이드용) --------------------------
def fig_metric_mean():
    data = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "practice", "assets", "df_preprocessed.npy"))
    mean = data.mean(axis=0)
    fig, axes = plt.subplots(1, 6, figsize=(6.4, 1.75), gridspec_kw={"width_ratios": [1, 1, 1, 1, 0.45, 1.3]})
    order = np.argsort(-data.reshape(len(data), -1).sum(axis=1))[[3, 25, 50, 75]]  # 병변이 보이는 예시
    for k, i in enumerate(order):
        axes[k].imshow(data[i], cmap="gray", vmin=0, vmax=0.7)
        axes[k].set_title(f"실제 #{i}", fontsize=9, color=INK)
    axes[4].axis("off")
    axes[4].annotate("", xy=(0.95, 0.5), xytext=(0.0, 0.5), arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=1.6), xycoords="axes fraction")
    axes[4].text(0.5, 0.68, "픽셀별\n평균", ha="center", fontsize=8.5, color=GRAY)
    axes[5].imshow(mean, cmap="gray", vmin=0, vmax=0.7)
    axes[5].set_title(f"클래스 평균 이미지\n(DF {len(data)}장)", fontsize=9, color=GREEN, fontweight="bold")
    for i in (0, 1, 2, 3, 5):
        axes[i].set_xticks([]); axes[i].set_yticks([])
        for sp in axes[i].spines.values():
            sp.set_color("#C9C6BE")
    fig.tight_layout(w_pad=0.5)
    save(fig, "metric_real_mean.png")


def _df_data():
    return np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "practice", "assets", "df_preprocessed.npy"))


def _sample_image():
    data = _df_data()
    order = np.argsort(-data.reshape(len(data), -1).sum(axis=1))
    return data[order[25]], int(order[25])


# 18. encoding 비교: 실제 이미지의 2x2 patch 값을 angle / amplitude로 넣는 예 --------------------
def fig_encoding():
    img, idx = _sample_image()
    best, (bi, bj) = -1, (0, 0)
    for i in range(0, 15):
        for j in range(0, 15):
            blk = img[i:i + 2, j:j + 2]
            sc = blk.std()
            if blk.min() > 0.08 * img.max() and sc > best:
                best, (bi, bj) = sc, (i, j)
    patch = img[bi:bi + 2, bj:bj + 2].flatten()
    patch = np.round(patch / img.max(), 2)  # 0 ~ 1로 다시 맞춤(예시용)
    fig = plt.figure(figsize=(11.0, 3.7))
    gs = fig.add_gridspec(1, 4, width_ratios=[1.35, 1.2, 3.1, 3.1], wspace=0.12)
    a = fig.add_subplot(gs[0]); a.imshow(img, cmap="gray", vmin=0, vmax=img.max())
    a.add_patch(plt.Rectangle((bj - 0.5, bi - 0.5), 2, 2, fill=False, ec=ORANGE, lw=2.2))
    a.set_title(f"실제 DF 이미지\n(16×16, #{idx})", fontsize=9.5, color=INK); a.set_xticks([]); a.set_yticks([])
    b = fig.add_subplot(gs[1]); b.imshow(patch.reshape(2, 2), cmap="gray", vmin=0, vmax=1)
    for k, v in enumerate(patch):
        b.text(k % 2, k // 2, f"x{k}\n{v:.2f}", ha="center", va="center", fontsize=9.5, color=ORANGE if v < 0.5 else "#222222", fontweight="bold")
    b.set_title("주황 상자 = 2×2 patch\n(값 4개)", fontsize=9.5, color=INK); b.set_xticks([]); b.set_yticks([])
    for sp in b.spines.values():
        sp.set_color(ORANGE); sp.set_linewidth(2)
    # angle encoding
    c = fig.add_subplot(gs[2]); c.set_xlim(0, 10); c.set_ylim(0, 8); c.axis("off")
    c.text(5, 7.55, "angle encoding: 값 1개 → 큐빗 1개", ha="center", fontsize=10.5, color=GREEN, fontweight="bold")
    for k, v in enumerate(patch):
        y = 6.2 - k * 1.45
        c.plot([0.8, 6.4], [y, y], color=GRAY, lw=1.3); c.text(0.2, y, f"q{k}", ha="right", va="center", fontsize=9.5, color=INK)
        c.add_patch(FancyBboxPatch((2.2, y - 0.5), 3.6, 1.0, boxstyle="round,pad=0.02,rounding_size=0.08", fc="#E4F0EA", ec=GREEN, lw=1.3, zorder=3))
        c.text(4.0, y, f"RY(π·{v:.2f})", ha="center", va="center", fontsize=9.5, color=GREEN2, fontweight="bold", zorder=4)
        c.text(8.1, y, f"P(1)={np.sin(np.pi * v / 2) ** 2:.2f}", ha="center", va="center", fontsize=9, color=GRAY)
    c.text(5, 0.2, "큐빗 4개, 게이트 1층 (깊이 상수)", ha="center", fontsize=9.5, color=INK)
    # amplitude encoding
    d = fig.add_subplot(gs[3]); d.set_xlim(0, 10); d.set_ylim(0, 8); d.axis("off")
    d.text(5, 7.55, "amplitude encoding: 값 2ⁿ개 → 큐빗 n개", ha="center", fontsize=10.5, color=PURPLE, fontweight="bold")
    amp = patch / np.linalg.norm(patch)
    for k in range(2):
        y = 5.4 - k * 1.9
        d.plot([0.8, 6.0], [y, y], color=GRAY, lw=1.3); d.text(0.2, y, f"q{k}", ha="right", va="center", fontsize=9.5, color=INK)
    d.add_patch(FancyBboxPatch((2.4, 3.9), 3.4, 2.6, boxstyle="round,pad=0.02,rounding_size=0.08", fc=PURPLE_BG, ec=PURPLE, lw=1.3, zorder=3))
    d.text(4.1, 5.2, "상태 준비 U(x)\n(깊은 회로)", ha="center", va="center", fontsize=9.5, color=PURPLE, fontweight="bold", linespacing=1.4, zorder=4)
    d.text(8.0, 5.2, "|ψ⟩ = Σ aᵢ|i⟩\naᵢ = xᵢ/‖x‖", ha="center", va="center", fontsize=9.5, color=INK, linespacing=1.5)
    d.text(5, 2.5, "진폭 (a₀ a₁ a₂ a₃) = " + " ".join(f"{v:.2f}" for v in amp), ha="center", fontsize=9.5, color=INK)
    d.text(5, 1.6, "큐빗 2개 = log₂4, 단 U(x)는 일반적으로 게이트가 O(2ⁿ)개", ha="center", fontsize=9.5, color=INK)
    d.text(5, 0.7, "‖x‖ = 1로 정규화하므로 값의 크기 정보는 사라짐", ha="center", fontsize=9.5, color=GRAY)
    save(fig, "encoding_compare.png")


# 19. 학습 불안정성 시각화 -----------------------------------------------------------------------
def fig_mode_collapse():
    rng = np.random.default_rng(11)
    real = np.vstack([rng.normal([-2, 0], 0.5, (150, 2)), rng.normal([2, 0], 0.5, (150, 2))])
    good = np.vstack([rng.normal([-2, 0], 0.55, (150, 2)), rng.normal([2, 0], 0.55, (150, 2))])
    bad = rng.normal([2, 0], 0.4, (300, 2))
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.9), sharex=True, sharey=True)
    for ax, gen, title, col in ((axes[0], good, "정상: 두 mode를 모두 생성", GREEN), (axes[1], bad, "mode collapse: 한 mode만 반복", ORANGE)):
        ax.scatter(real[:, 0], real[:, 1], s=9, color=LGRAY, alpha=0.7, label="실제")
        ax.scatter(gen[:, 0], gen[:, 1], s=9, color=col, alpha=0.7, label="생성")
        ax.set_title(title, fontsize=10, color=INK, pad=6); ax.set_xticks([]); ax.set_yticks([])
        ax.legend(frameon=False, fontsize=8.5, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(w_pad=1.0)
    save(fig, "mode_collapse.png")


def fig_js_w():
    d = np.linspace(0, 2.5, 400)
    js = np.where(d > 0, np.log(2), 0.0)
    fig, ax = plt.subplots(figsize=(4.8, 2.9))
    ax.plot(d, js, color=ORANGE, lw=2.4, label="Jensen-Shannon: 상수 (ln 2)")
    ax.plot(d, d, color=GREEN, lw=2.4, label="Wasserstein-1: 거리에 비례")
    ax.set_xlabel("두 분포 사이의 거리 d (support가 겹치지 않음)"); ax.set_ylabel("거리 척도 값")
    ax.set_ylim(0, 3.3); ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.grid(color="#E6E3DC", lw=0.8); ax.set_axisbelow(True)
    ax.text(1.0, 0.82, "JS는 d가 변해도 평평 → gradient 0", fontsize=9, color=ORANGE)
    save(fig, "js_vs_wasserstein.png")


# 20. Bloch 구 단면 ---------------------------------------------------------------------------------
def fig_bloch():
    th = np.pi / 3
    fig, ax = plt.subplots(figsize=(4.8, 4.2))
    t = np.linspace(0, 2 * np.pi, 300)
    ax.plot(np.cos(t), np.sin(t), color=LGRAY, lw=1.6)
    ax.plot([-1.15, 1.15], [0, 0], color="#E0DDD5", lw=1); ax.plot([0, 0], [-1.15, 1.15], color="#E0DDD5", lw=1)
    ax.text(0, 1.2, "|0⟩ (z)", ha="center", fontsize=10.5, color=INK); ax.text(0, -1.3, "|1⟩", ha="center", fontsize=10.5, color=INK)
    ax.text(1.2, -0.05, "x", fontsize=10, color=GRAY); ax.text(-1.32, -0.05, "−x", fontsize=10, color=GRAY)
    ax.annotate("", xy=(np.sin(th), np.cos(th)), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=2.4))
    arc = np.linspace(0, th, 50)
    ax.plot(0.32 * np.sin(arc), 0.32 * np.cos(arc), color=ORANGE, lw=2)
    ax.text(0.2, 0.42, "θ", fontsize=11, color=ORANGE, fontweight="bold")
    ax.text(np.sin(th) + 0.06, np.cos(th) + 0.06, "RY(θ)|0⟩", fontsize=10, color=GREEN2, fontweight="bold")
    ax.text(0, -1.62, f"θ = π/3:  P(0) = cos²(θ/2) = {np.cos(th/2)**2:.2f},  P(1) = sin²(θ/2) = {np.sin(th/2)**2:.2f}", ha="center", va="top", fontsize=9.5, color=INK)
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.9, 1.45); ax.set_aspect("equal"); ax.axis("off")
    save(fig, "bloch_ry.png")


# 21. patch 분할 예시 (16x16 = 4 patch x 64픽셀) -------------------------------------------------------
def fig_patch():
    img, idx = _sample_image()
    fig = plt.figure(figsize=(10.8, 3.6))
    gs = fig.add_gridspec(1, 4, width_ratios=[1.5, 0.35, 2.0, 1.5], wspace=0.15)
    a = fig.add_subplot(gs[0]); a.imshow(img, cmap="gray", vmin=0, vmax=img.max())
    a.set_title("이어붙인 이미지\n16×16 = 256픽셀", fontsize=10, color=INK); a.set_xticks([]); a.set_yticks([])
    for r in (3.5, 7.5, 11.5):
        a.axhline(r, color=ORANGE, lw=1.6, ls="--")
    ar = fig.add_subplot(gs[1]); ar.axis("off")
    ar.annotate("", xy=(0.95, 0.5), xytext=(0.0, 0.5), arrowprops=dict(arrowstyle="<|-", color=GRAY, lw=1.6), xycoords="axes fraction")
    b = fig.add_subplot(gs[2]); b.set_xlim(0, 10); b.set_ylim(0, 10); b.axis("off")
    for k in range(4):
        y = 7.9 - k * 2.35
        strip = img[4 * k:4 * k + 4]
        b.imshow(strip, cmap="gray", vmin=0, vmax=img.max(), extent=(0.2, 5.4, y, y + 1.7), aspect="auto")
        b.add_patch(plt.Rectangle((0.2, y), 5.2, 1.7, fill=False, ec=GRAY, lw=1.0))
        b.text(5.8, y + 0.85, f"sub-generator {k + 1}\npatch {k + 1}: 16×4 = 64픽셀", va="center", fontsize=9, color=INK, linespacing=1.4)
    c = fig.add_subplot(gs[3]); c.set_xlim(0, 10); c.set_ylim(0, 10); c.axis("off")
    c.text(0.2, 8.4, "patch 하나", fontsize=10.5, color=GREEN, fontweight="bold")
    c.text(0.2, 6.6, "64픽셀 = 2⁶", fontsize=10, color=INK)
    c.text(0.2, 5.0, "→ 데이터 큐빗 6개", fontsize=10, color=INK)
    c.text(0.2, 3.4, "+ ancilla 1개", fontsize=10, color=INK)
    c.text(0.2, 1.8, "= 회로당 7큐빗 (실습)", fontsize=10, color=GREEN2, fontweight="bold")
    save(fig, "patch_split.png")


# 22. parameter-shift rule 예시 ------------------------------------------------------------------------------
def fig_param_shift():
    th0 = np.pi / 3
    t = np.linspace(-1.2, 6.0, 500)
    f = np.cos
    fig, ax = plt.subplots(figsize=(6.4, 3.5))
    ax.plot(t, f(t), color=GREEN, lw=2.4, label="f(θ) = ⟨Z⟩ = cos θ")
    slope = -np.sin(th0)
    tt = np.linspace(th0 - 0.9, th0 + 0.9, 20)
    ax.plot(tt, f(th0) + slope * (tt - th0), color=ORANGE, lw=1.8, ls="--", label=f"θ₀에서의 접선 (기울기 {slope:.3f})")
    for x, name in ((th0, "θ₀"), (th0 + np.pi / 2, "θ₀+π/2"), (th0 - np.pi / 2, "θ₀−π/2")):
        ax.plot([x], [f(x)], "o", color=PURPLE if name != "θ₀" else ORANGE, ms=8, mec="white", mew=1.5)
        ax.text(x + (-0.15 if x < th0 else 0.12), f(x) + (0.18 if x <= th0 else -0.38), f"{name}\nf={f(x):.3f}", fontsize=8.5, color=INK, ha="right" if x < th0 else "left")
    ax.set_xlabel("θ"); ax.set_ylabel("기댓값 f(θ)"); ax.set_ylim(-1.35, 1.45)
    ax.legend(frameon=False, fontsize=9, loc="lower left")
    ax.grid(color="#E6E3DC", lw=0.8); ax.set_axisbelow(True)
    ax.text(-1.1, -0.45, "[f(θ₀+π/2) − f(θ₀−π/2)] / 2\n= (−0.866 − 0.866) / 2 = −0.866\n= f′(θ₀)  (정확히 일치)", fontsize=9.5, color=GREEN2, linespacing=1.5)
    save(fig, "param_shift.png")


if __name__ == "__main__":
    for fn in (fig_gan, fig_ry, fig_bell, fig_shots, fig_loop, fig_memory, fig_state3, fig_taxonomy, fig_interference, fig_layer_compare, fig_roc, fig_lpips, fig_metric_mean, fig_encoding, fig_mode_collapse, fig_js_w, fig_bloch, fig_patch, fig_param_shift, fig_fid, fig_fid_minority, fig_ibm, fig_acc, fig_shapes):
        fn()
    print(sorted(os.listdir(OUT)))
