# -*- coding: utf-8 -*-
"""
경량 생성품질 지표 4종 + 공통 역정규화 함수 — 2·3일차 공통 모듈.
2026-10-01 커리큘럼 재설계로 CNN 증강 비교를 실습에서 들어내면서, "생성이 잘 됐는지"를
판정할 수단으로 도입한 것(설계 근거는 프로젝트 README "커리큘럼 재설계" 섹션 참고).

지표 4종
  ① 픽셀 강도 통계·히스토그램      pixel_stats() / plot_pixel_histogram()
  ② 클래스 평균 이미지와의 상관계수  mean_image_correlation()
  ③ 최근접 실제 이미지 L2 거리      nearest_neighbor_distance() / plot_nearest_neighbors()
  ④ 샘플 간 다양성 + 손실곡선        sample_diversity() / plot_loss_curves()

⚠ 척도 규약(README와 동일, 어기면 QGAN·MediQ-GAN 비교가 무의미해짐)
  - 전처리 npy: 0~1  / QGAN 출력: 픽셀 합=1(확률 척도)  / MediQ-GAN 출력: Tanh(-1~1)
  - **모양 지표(②③④)는 to_unit_scale()로 0~1로 되돌린 뒤 계산**
  - **픽셀 통계(①)는 되돌리기 전 원 척도에서도 함께 봄** — 척도 차이 자체가 두 모델의
    구조적 차이(QGAN은 밝기 총합까지 학습 대상)를 보여주는 정보이기 때문
"""
import numpy as np

SCALE_MODES = ("unit", "prob", "tanh")


def to_unit_scale(x, mode):
    """생성/실제 이미지를 0~1 척도로 되돌림. 모양 비교 지표는 전부 이 함수를 거쳐야 함.

    mode="unit": 이미 0~1 (전처리 npy) → 그대로
    mode="prob": QGAN 출력(픽셀 합=1) → 이미지별 min-max 정규화
    mode="tanh": MediQ-GAN 출력(-1~1) → (x+1)/2
    """
    if mode not in SCALE_MODES:
        raise ValueError(f"mode는 {SCALE_MODES} 중 하나여야 함 (받은 값: {mode!r})")
    arr = np.asarray(x, dtype=np.float64)
    if mode == "unit":
        return np.clip(arr, 0.0, 1.0)
    if mode == "tanh":
        return np.clip((arr + 1.0) / 2.0, 0.0, 1.0)
    # prob — 이미지별 min-max. 상수 이미지(모드붕괴)는 0으로 두어 NaN을 피함
    flat = arr.reshape(len(arr), -1)
    lo = flat.min(axis=1, keepdims=True)
    hi = flat.max(axis=1, keepdims=True)
    span = hi - lo
    out = np.where(span > 1e-12, (flat - lo) / np.where(span > 1e-12, span, 1.0), 0.0)
    return out.reshape(arr.shape)


def _flat(x):
    arr = np.asarray(x, dtype=np.float64)
    return arr.reshape(len(arr), -1)


# ──────────────────────────── ① 픽셀 강도 통계 ────────────────────────────

def pixel_stats(images):
    """픽셀 강도 평균·표준편차·최소·최대·0 근처 비율(배경 비중)."""
    f = _flat(images)
    return {
        "n": int(len(f)),
        "mean": float(f.mean()),
        "std": float(f.std()),
        "min": float(f.min()),
        "max": float(f.max()),
        "sum_per_image": float(f.sum(axis=1).mean()),
        "near_zero_ratio": float((f < 0.05).mean()),
    }


def plot_pixel_histogram(real, fake, ax=None, bins=30, label_real="실제", label_fake="생성"):
    """실제 vs 생성 픽셀 강도 히스토그램(겹쳐 그림)."""
    import matplotlib.pyplot as plt
    if ax is None:
        _, ax = plt.subplots(figsize=(5, 3))
    ax.hist(_flat(real).ravel(), bins=bins, alpha=0.55, density=True, label=label_real)
    ax.hist(_flat(fake).ravel(), bins=bins, alpha=0.55, density=True, label=label_fake)
    ax.set_xlabel("픽셀 강도"); ax.set_ylabel("밀도"); ax.legend()
    return ax


# ─────────────────── ② 클래스 평균 이미지와의 상관계수 ───────────────────

def class_mean_image(real):
    """실제 이미지들의 평균 이미지(클래스 템플릿)."""
    return np.asarray(real, dtype=np.float64).mean(axis=0)


def mean_image_correlation(fake, mean_img):
    """생성 샘플별 Pearson 상관계수(평균 이미지 대비).

    해석: 1에 가까우면 그 클래스의 전형적 밝기 배치를 재현한 것. 상수 이미지는 NaN이 되므로 0으로 둠.
    """
    f = _flat(fake)
    m = np.asarray(mean_img, dtype=np.float64).ravel()
    m_c = m - m.mean()
    m_norm = np.linalg.norm(m_c)
    out = np.zeros(len(f))
    for i, row in enumerate(f):
        r_c = row - row.mean()
        denom = np.linalg.norm(r_c) * m_norm
        out[i] = 0.0 if denom < 1e-12 else float(r_c @ m_c / denom)
    return out


# ──────────────── ③ 최근접 실제 이미지 L2 거리(암기 검출) ────────────────

def nearest_neighbor_distance(fake, real):
    """생성 샘플별 (최근접 실제 이미지까지의 L2 거리, 그 이미지 인덱스).

    해석: 거리가 0에 가까우면 학습 데이터를 거의 복사한 것(암기), 과도하게 크면 분포를 벗어난 것.
    """
    f, r = _flat(fake), _flat(real)
    # (n_fake, n_real) 거리행렬 — 8x8/16x16 저해상도라 전체를 한 번에 계산해도 가벼움
    d = np.linalg.norm(f[:, None, :] - r[None, :, :], axis=2)
    idx = d.argmin(axis=1)
    return d[np.arange(len(f)), idx], idx


def plot_nearest_neighbors(fake, real, img_size, n_show=4, cmap="gray"):
    """생성 샘플과 그 최근접 실제 이미지를 위/아래로 나란히 표시."""
    import matplotlib.pyplot as plt
    dist, idx = nearest_neighbor_distance(fake, real)
    n_show = min(n_show, len(fake))
    fig, axes = plt.subplots(2, n_show, figsize=(2.2 * n_show, 4.6))
    axes = np.atleast_2d(axes)
    f, r = _flat(fake), _flat(real)
    for c in range(n_show):
        axes[0, c].imshow(f[c].reshape(img_size, img_size), cmap=cmap)
        axes[0, c].set_title(f"생성 #{c}", fontsize=9); axes[0, c].axis("off")
        axes[1, c].imshow(r[idx[c]].reshape(img_size, img_size), cmap=cmap)
        axes[1, c].set_title(f"최근접 실제 (L2 {dist[c]:.2f})", fontsize=9); axes[1, c].axis("off")
    fig.tight_layout()
    return fig, dist


# ──────────────── ④ 샘플 간 다양성 + 판별자 손실곡선 ────────────────

def sample_diversity(fake):
    """생성 샘플끼리 얼마나 다른가 — 쌍별 L2 거리 평균/최솟값, 픽셀별 표준편차 평균.

    해석: 값이 0에 가까우면 모드붕괴(어떤 노이즈를 넣어도 같은 그림만 나옴).
    """
    f = _flat(fake)
    if len(f) < 2:
        return {"pairwise_mean": 0.0, "pairwise_min": 0.0, "pixelwise_std": float(f.std())}
    d = np.linalg.norm(f[:, None, :] - f[None, :, :], axis=2)
    iu = np.triu_indices(len(f), k=1)
    return {
        "pairwise_mean": float(d[iu].mean()),
        "pairwise_min": float(d[iu].min()),
        "pixelwise_std": float(f.std(axis=0).mean()),
    }


def plot_loss_curves(loss_g, loss_d, ax=None):
    """생성자·판별자 손실곡선. 판별자가 일방적으로 이기는(loss_d→0) 구간을 눈으로 확인하는 용도."""
    import matplotlib.pyplot as plt
    if ax is None:
        _, ax = plt.subplots(figsize=(5, 3))
    ax.plot(loss_g, label="생성자 loss_g")
    ax.plot(loss_d, label="판별자 loss_d")
    ax.set_xlabel("스텝"); ax.set_ylabel("loss"); ax.legend()
    return ax


# ──────────────────────── 종합: 모델 간 동일 잣대 비교 ────────────────────────

def evaluate(fake, real, scale_mode, real_scale_mode="unit"):
    """지표 4종을 한 번에 계산해 dict로 반환. 모양 지표는 0~1로 되돌린 뒤 계산함."""
    fake_u = to_unit_scale(fake, scale_mode)
    real_u = to_unit_scale(real, real_scale_mode)
    corr = mean_image_correlation(fake_u, class_mean_image(real_u))
    nn_dist, _ = nearest_neighbor_distance(fake_u, real_u)
    div = sample_diversity(fake_u)
    return {
        "픽셀평균(원척도)": pixel_stats(fake)["mean"],
        "픽셀합/장(원척도)": pixel_stats(fake)["sum_per_image"],
        "픽셀평균(0~1환산)": pixel_stats(fake_u)["mean"],
        "클래스평균 상관계수": float(np.mean(corr)),
        "상관계수 최댓값": float(np.max(corr)),
        "최근접 실제거리 평균": float(np.mean(nn_dist)),
        "최근접 실제거리 최솟값": float(np.min(nn_dist)),
        "샘플간 거리 평균": div["pairwise_mean"],
        "픽셀별 표준편차": div["pixelwise_std"],
    }


def comparison_table(entries, real, real_scale_mode="unit"):
    """여러 모델을 같은 잣대로 비교. entries = {"QGAN": (fake, "prob"), "MediQ-GAN": (fake, "tanh")}

    pandas가 있으면 DataFrame, 없으면 dict of dict를 반환함(노트북에서는 DataFrame으로 표시됨).
    """
    rows = {name: evaluate(fake, real, mode, real_scale_mode) for name, (fake, mode) in entries.items()}
    try:
        import pandas as pd
        return pd.DataFrame(rows).round(4)
    except ImportError:
        return rows


if __name__ == "__main__":
    print("[검증] 지표 4종 — 합성 데이터로 동작·민감도 확인")
    rng = np.random.default_rng(0)
    IMG = 16
    # 실제 데이터 모사: 가운데가 밝은 병변 + 노이즈
    yy, xx = np.mgrid[0:IMG, 0:IMG]
    blob = np.exp(-((yy - IMG / 2) ** 2 + (xx - IMG / 2) ** 2) / (2 * (IMG / 5) ** 2))
    real = np.clip(blob[None] + rng.normal(0, 0.08, (40, IMG, IMG)), 0, 1)

    good = np.clip(blob[None] + rng.normal(0, 0.12, (8, IMG, IMG)), 0, 1)   # 비슷하게 생성
    noise = rng.random((8, IMG, IMG))                                        # 엉뚱한 생성
    collapsed = np.repeat(good[:1], 8, axis=0)                               # 모드붕괴
    memorized = real[:8].copy()                                              # 학습데이터 암기

    for mode in SCALE_MODES:
        probe = {"unit": good, "prob": good / good.reshape(8, -1).sum(1)[:, None, None],
                 "tanh": good * 2 - 1}[mode]
        u = to_unit_scale(probe, mode)
        assert u.shape == good.shape and u.min() >= 0 and u.max() <= 1, mode
    print("OK — to_unit_scale 3개 모드 모두 0~1 복원 확인")

    r_good = mean_image_correlation(good, class_mean_image(real)).mean()
    r_noise = mean_image_correlation(noise, class_mean_image(real)).mean()
    print(f"② 상관계수: 비슷한 생성 {r_good:.3f} vs 무작위 {r_noise:.3f}")
    assert r_good > r_noise + 0.3, "상관계수가 좋은 생성과 무작위를 구분하지 못함"

    d_good = nearest_neighbor_distance(good, real)[0].mean()
    d_mem = nearest_neighbor_distance(memorized, real)[0].mean()
    print(f"③ 최근접거리: 정상 생성 {d_good:.3f} vs 암기 {d_mem:.3f}")
    assert d_mem < 1e-9 < d_good, "암기(거리 0)를 검출하지 못함"

    div_good = sample_diversity(good)["pairwise_mean"]
    div_col = sample_diversity(collapsed)["pairwise_mean"]
    print(f"④ 샘플간 거리: 정상 {div_good:.3f} vs 모드붕괴 {div_col:.3f}")
    assert div_col < 1e-9 < div_good, "모드붕괴를 검출하지 못함"

    table = comparison_table({"정상생성(prob척도)": (good / good.reshape(8, -1).sum(1)[:, None, None], "prob"),
                              "무작위(tanh척도)": (noise * 2 - 1, "tanh")}, real)
    print("\n=== comparison_table 출력 예시 ===")
    print(table)
    print("\nOK — 지표 4종이 좋은 생성/무작위/암기/모드붕괴를 전부 구분함")
