# -*- coding: utf-8 -*-
"""
HAM10000 로드 + EDA + segmentation 전처리 (Andra et al. Section 3.1, K-means + Fuzzy C-means).
2일차 노트북의 전처리 코드와 같은 로직임 - 한쪽을 고치면 다른 쪽도 맞출 것.
원본: HAM10000_metadata.csv (dx: akiec, bcc, bkl, df, mel, nv, vasc)
"""
import os
import numpy as np
import cv2
import pandas as pd
from pathlib import Path

# 논문 Section 5.1의 이진분류 쌍
# DF(최소 클래스) vs NV(최다 클래스) - 논문에서 가장 좋았던 조합(Table 6)
TARGET_CLASSES = ("df", "nv")
CLASS_NAMES_KR = {"akiec": "광선각화증", "bcc": "기저세포암", "bkl": "양성각화증",
                   "df": "피부섬유종", "mel": "흑색종", "nv": "모반(정상)", "vasc": "혈관병변"}


def load_metadata(csv_path):
    """HAM10000_metadata.csv 로드 - dx(진단 클래스), image_id 컬럼 사용."""
    df = pd.read_csv(csv_path)
    assert "dx" in df.columns and "image_id" in df.columns, "HAM10000_metadata.csv 형식이 아닙니다"
    return df


def class_distribution(df):
    """클래스별 샘플 수 (EDA)."""
    counts = df["dx"].value_counts()
    return counts


def load_image(img_dir, image_id, exts=(".jpg", ".jpeg", ".png")):
    """image_id로 이미지를 찾아 BGR로 로드 (part_1·part_2 두 폴더)."""
    img_dir = Path(img_dir)
    for ext in exts:
        for sub in ["", "HAM10000_images_part_1", "HAM10000_images_part_2"]:
            p = img_dir / sub / f"{image_id}{ext}"
            if p.exists():
                return cv2.imread(str(p))
    raise FileNotFoundError(f"이미지를 찾을 수 없음: {image_id}")


def segment_fcm_kmeans(img_bgr, n_clusters=4, resize_to=None):
    """K-means 사전 clustering + Fuzzy C-means 정제 후 가장 어두운 cluster(병변)만 남김.

    논문 Table 10에서 이 전처리를 거친 이미지만 증강 효과가 있었음. 반환: grayscale uint8.
    """
    import skfuzzy as fuzz

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    if resize_to is not None:
        gray = cv2.resize(gray, resize_to, interpolation=cv2.INTER_AREA)

    h, w = gray.shape
    pixels = gray.reshape(-1, 1).astype(np.float32)

    # 1단계: K-means 사전 clustering (FCM 시간 단축)
    from sklearn.cluster import KMeans
    km = KMeans(n_clusters=n_clusters, n_init=4, random_state=0).fit(pixels)
    # FCM 초기 소속도 = K-means 중심까지 거리의 역제곱
    dist = np.abs(pixels - km.cluster_centers_.reshape(1, -1)) + 1e-6
    u_init = 1.0 / dist ** 2
    u_init = (u_init / u_init.sum(axis=1, keepdims=True)).T  # (cluster 수, 픽셀 수)

    # 2단계: Fuzzy C-means로 정제
    cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(
        pixels.T, c=n_clusters, m=2.0, error=1e-4, maxiter=100, init=u_init
    )
    membership = np.argmax(u, axis=0)
    # 가장 어두운 cluster(병변)만 남기고 배경은 0 (논문 Fig.9)
    lesion_cluster = np.argmin(cntr.flatten())
    mask = (membership == lesion_cluster).reshape(h, w).astype(np.uint8) * 255

    segmented = cv2.bitwise_and(gray, gray, mask=mask)
    return segmented


def resize_for_encoding(img_gray, size):
    """양자 encoding용 축소 (큰 폭 축소라 INTER_AREA)."""
    return cv2.resize(img_gray, size, interpolation=cv2.INTER_AREA)


def normalize_for_amplitude_encoding(img_small):
    """진폭 encoding을 위해 L2 정규화된 실수 벡터로 변환 (합의 제곱=1)."""
    vec = img_small.flatten().astype(np.float64)
    norm = np.linalg.norm(vec)
    if norm == 0:
        vec = np.ones_like(vec)
        norm = np.linalg.norm(vec)
    return vec / norm


# ---------------------------------------------------------------------------
# 로컬 코드 검증 전용 - 실제 강의에는 쓰지 않음 (HAM10000 접근 없이 pipeline만 테스트)
# ---------------------------------------------------------------------------
def _make_synthetic_lesion_bgr(size=(128, 128), seed=0):
    """테스트 전용: 병변 비슷한 원형 얼룩이 있는 합성 이미지 생성. 실제 피부 데이터 아님."""
    rng = np.random.RandomState(seed)
    img = (rng.rand(*size, 3) * 40 + 180).astype(np.uint8)  # 밝은 피부톤 배경
    cx, cy = size[0] // 2 + rng.randint(-10, 10), size[1] // 2 + rng.randint(-10, 10)
    r = rng.randint(15, 30)
    cv2.circle(img, (cx, cy), r, (60, 40, 30), -1)  # 어두운 병변
    img = cv2.GaussianBlur(img, (5, 5), 0)
    return img


if __name__ == "__main__":
    print("[검증] HAM10000 접근 없이 전처리 pipeline 자체 동작만 확인합니다 (합성 이미지 사용).")
    img = _make_synthetic_lesion_bgr()
    seg = segment_fcm_kmeans(img, n_clusters=4)
    print("segmentation 결과 shape:", seg.shape, "dtype:", seg.dtype, "min/max:", seg.min(), seg.max())
    small = resize_for_encoding(seg, (8, 8))
    vec = normalize_for_amplitude_encoding(small)
    print("encoding 벡터 길이:", len(vec), "L2 norm:", np.linalg.norm(vec))
    assert abs(np.linalg.norm(vec) - 1.0) < 1e-6, "정규화 실패"
    print("OK - 전처리 pipeline 정상 동작 확인")
