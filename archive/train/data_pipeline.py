# -*- coding: utf-8 -*-
"""
HAM10000 로드 + EDA + 전처리(세그멘테이션) 파이프라인
동아대 대학원 QML 강의 2일차 실습용 — HAM10000 QGAN 논문(arXiv 기반 재현, Andra et al. 2024/2025)
Section 3.1의 K-means + Fuzzy C-means 하이브리드 세그멘테이션을 그대로 구현.

실제 강의에서는 학생들이 Colab에서 Kaggle API로 HAM10000을 직접 받는다:
    !pip install kaggle
    from google.colab import files
    files.upload()  # kaggle.json 업로드
    !mkdir -p ~/.kaggle && cp kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json
    !kaggle datasets download -d kmader/skin-cancer-mnist-ham10000
    !unzip -q skin-cancer-mnist-ham10000.zip -d ham10000

원본: HAM10000_metadata.csv (dx 컬럼에 7개 클래스: akiec, bcc, bkl, df, mel, nv, vasc)
"""
import os
import numpy as np
import cv2
import pandas as pd
from pathlib import Path

# 논문(HAM10000 QGAN, Section 5.1)에서 실제 사용한 이진분류 쌍 — 이 강의도 그대로 재현
# DF(피부섬유종, 소수클래스) vs NV(모반, 최다수클래스) — 논문에서 가장 성능이 좋았던 조합(Table 6)
TARGET_CLASSES = ("df", "nv")
CLASS_NAMES_KR = {"akiec": "광선각화증", "bcc": "기저세포암", "bkl": "양성각화증",
                   "df": "피부섬유종", "mel": "흑색종", "nv": "모반(정상)", "vasc": "혈관병변"}


def load_metadata(csv_path):
    """HAM10000_metadata.csv 로드 — dx(진단 클래스), image_id 컬럼 사용."""
    df = pd.read_csv(csv_path)
    assert "dx" in df.columns and "image_id" in df.columns, "HAM10000_metadata.csv 형식이 아닙니다"
    return df


def class_distribution(df):
    """EDA용 — 클래스별 샘플 수. 강의 1일차/2일차에서 그대로 시각화에 사용."""
    counts = df["dx"].value_counts()
    return counts


def load_image(img_dir, image_id, exts=(".jpg", ".jpeg", ".png")):
    """image_id로 실제 이미지 파일을 찾아 BGR로 로드. HAM10000은 이미지가 2개 폴더에 나뉘어 있을 수 있음."""
    img_dir = Path(img_dir)
    for ext in exts:
        for sub in ["", "HAM10000_images_part_1", "HAM10000_images_part_2"]:
            p = img_dir / sub / f"{image_id}{ext}"
            if p.exists():
                return cv2.imread(str(p))
    raise FileNotFoundError(f"이미지를 찾을 수 없음: {image_id}")


def segment_fcm_kmeans(img_bgr, n_clusters=4, resize_to=None):
    """
    HAM10000 QGAN 논문 Section 3.1 — K-means로 1차 클러스터링 후 Fuzzy C-means로 정제하는
    하이브리드 세그멘테이션. 논문 결과(Table 10)상 이 전처리를 거친 이미지에서만 QGAN 증강이
    실제로 성능을 개선시켰으므로(raw 이미지는 오히려 악화), 이 강의의 핵심 전처리 단계다.

    Returns: 세그멘테이션된 grayscale 이미지 (0~255 uint8)
    """
    import skfuzzy as fuzz

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    if resize_to is not None:
        gray = cv2.resize(gray, resize_to, interpolation=cv2.INTER_AREA)

    h, w = gray.shape
    pixels = gray.reshape(-1, 1).astype(np.float32)

    # 1단계: K-means로 대략적인 클러스터 중심 초기화 (논문: "pre-clustering to reduce FCM 처리시간")
    from sklearn.cluster import KMeans
    km = KMeans(n_clusters=n_clusters, n_init=4, random_state=0).fit(pixels)
    # K-means 중심까지의 거리로 FCM 초기 소속도 행렬 구성 (m=2 → 소속도 ∝ 1/거리²)
    dist = np.abs(pixels - km.cluster_centers_.reshape(1, -1)) + 1e-6
    u_init = 1.0 / dist ** 2
    u_init = (u_init / u_init.sum(axis=1, keepdims=True)).T  # (클러스터 수, 픽셀 수)

    # 2단계: Fuzzy C-means로 정제 (K-means 결과에서 출발 → 무작위 시작보다 빨리 수렴, 매번 같은 결과)
    cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(
        pixels.T, c=n_clusters, m=2.0, error=1e-4, maxiter=100, init=u_init
    )
    membership = np.argmax(u, axis=0)
    # 병변(가장 어두운 클러스터)만 남기고 나머지는 배경 처리 — 논문 Fig.9의 세그멘테이션 결과와 동일한 컨셉
    lesion_cluster = np.argmin(cntr.flatten())
    mask = (membership == lesion_cluster).reshape(h, w).astype(np.uint8) * 255

    segmented = cv2.bitwise_and(gray, gray, mask=mask)
    return segmented


def resize_for_encoding(img_gray, size):
    """양자 인코딩용 초저해상도 축소. 예: (8,8)이면 64픽셀=6큐빗 진폭인코딩, (4,4)면 16픽셀=4큐빗."""
    return cv2.resize(img_gray, size, interpolation=cv2.INTER_AREA)


def normalize_for_amplitude_encoding(img_small):
    """진폭 인코딩을 위해 L2 정규화된 실수 벡터로 변환 (합의 제곱=1)."""
    vec = img_small.flatten().astype(np.float64)
    norm = np.linalg.norm(vec)
    if norm == 0:
        vec = np.ones_like(vec)
        norm = np.linalg.norm(vec)
    return vec / norm


# ---------------------------------------------------------------------------
# 로컬 코드 검증 전용 — 실제 강의에는 쓰지 않음 (HAM10000 접근 없이 파이프라인만 테스트)
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
    print("[검증] HAM10000 접근 없이 전처리 파이프라인 자체 동작만 확인합니다 (합성 이미지 사용).")
    img = _make_synthetic_lesion_bgr()
    seg = segment_fcm_kmeans(img, n_clusters=4)
    print("세그멘테이션 결과 shape:", seg.shape, "dtype:", seg.dtype, "min/max:", seg.min(), seg.max())
    small = resize_for_encoding(seg, (8, 8))
    vec = normalize_for_amplitude_encoding(small)
    print("인코딩 벡터 길이:", len(vec), "L2 norm:", np.linalg.norm(vec))
    assert abs(np.linalg.norm(vec) - 1.0) < 1e-6, "정규화 실패"
    print("OK — 전처리 파이프라인 정상 동작 확인")
