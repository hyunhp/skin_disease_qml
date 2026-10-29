# 피부병변 의료영상 양자 생성모델 - QGAN / MediQ-GAN

양자 GAN으로 의료영상을 증강하는 과정(EDA → segmentation → 양자 encoding → 학습 → 평가)을 Google Colab 무료 CPU에서 끝까지 실행하는 실습 자료입니다. 두 논문의 hybrid 전략(모델 단위 vs layer 단위)을 같은 데이터·같은 지표로 비교합니다.

> 한국어 | **[English](README.en.md)**

## 한눈에 보기

| 항목 | 내용 |
|---|---|
| 데이터 | HAM10000 중 DF 115장 · NV 345장 → K-means + Fuzzy C-means segmentation → 16×16 그레이스케일 |
| 모델 ① | Patch QGAN (모델 단위 hybrid): sub-generator 4개 × 7큐빗(데이터 6 + ancilla 1), depth 10 |
| 모델 ② | MediQ-GAN (layer 단위 hybrid): 고전 stream + 양자 stream(16큐빗 × 5, depth 8) |
| 판별자 | 두 모델 공통, 논문 Table 4의 5층 완전연결 |
| 평가 | 지표 4종(픽셀 분포 · 클래스 평균 상관 · 최근접 실제 거리 · 샘플 다양성). 16×16에서는 FID를 쓸 수 없음 |
| 환경 | Colab 기본 CPU. PennyLane exact 시뮬레이션, 설치·GPU·양자 하드웨어 불필요 |

설계 원칙
- 양자 회로 스펙은 줄이지 않고, 해상도와 학습량을 줄임
- 출력 척도(확률 · Tanh · 0 ~ 1)를 0 ~ 1로 맞춘 뒤에만 지표를 계산함
- 원 논문과 다른 점, 실패한 설정, 한계를 자료에 함께 적음

## 실습 자료

| 일차 | 내용 | 자료 |
|---|---|---|
| 1일차 | 이론: 데이터셋, 두 논문 아키텍처와 결과, VQC 학습 비용 | [슬라이드 pptx](../practice/day1_slides/day1_theory_slides.pptx) · [pdf](../practice/day1_slides/day1_theory_slides.pdf) |
| 2일차 | EDA · segmentation · 회로 구성 → QGAN 학습 → 평가 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hyunhp/skin_disease_qml/blob/main/practice/day2_practice.ipynb) · [슬라이드 pptx](../practice/day2_slides/day2_practice_slides.pptx) · [pdf](../practice/day2_slides/day2_practice_slides.pdf) |
| 3일차 | MediQ-GAN 미세조정 → QGAN과 같은 지표로 비교 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hyunhp/skin_disease_qml/blob/main/practice/day3_practice.ipynb) · [슬라이드 pptx](../practice/day3_slides/day3_practice_slides.pptx) · [pdf](../practice/day3_slides/day3_practice_slides.pdf) |

노트북을 열면 `파일 → Drive에 사본 저장`을 먼저 실행합니다. 노트북은 실행 중 이 저장소를 clone해 [`practice/assets/`](../practice/assets/)와 [`gen_metrics.py`](../practice/gen_metrics.py)를 씁니다. HAM10000 원본(약 6GB)만 `kagglehub`로 받습니다.

## 결과

로컬 CPU 실측. 생성할 때마다 새 난수를 쓰므로 소수점보다 모델 간 격차를 봅니다.

| 모델 | 학습량 | ② 클래스 평균 상관 ↑ | ③ 최근접 실제 거리 | ④ 다양성 (실제 2.505) |
|---|---|---|---|---|
| QGAN | 600 step (약 22분) | 0.195 ± 0.012 (64장 × 10시드) | 1.64 | 1.92 |
| MediQ-GAN | 10 epoch (약 80분) | 0.018 | - | - |
| MediQ-GAN | 25 epoch (196분) | 0.365 | 3.44 | 0.30 |

- MediQ-GAN은 평균 형태를 더 잘 맞추지만, 다양성이 실제의 1/8이라 비슷한 이미지를 반복합니다. QGAN은 형태가 약한 대신 다양성이 실제에 가깝습니다.
- 두 모델 모두 16×16 축소판이라 생성 이미지가 논문 수준과 거리가 멉니다. 3일차 노트북에서 논문의 생성 이미지와 나란히 보여줍니다.

### sub-generator 수 실험 (600 step · depth 10)

| sub-generator | 큐빗 | ② 상관 | ④ 다양성 | 소요 |
|---|---|---|---|---|
| 2 | 8 | -0.054 (8장) | 1.81 | 17.4분 |
| **4 (채택)** | 7 | **0.195 ± 0.012** | 1.85 | 22.2분 |
| 8 | 6 | 0.105 ± 0.011 | 2.20 | 34.2분 |
| 16 (논문) | 5 | 0.080 ± 0.004 | 2.40 | 54.9분 |

- 16개에서는 `loss_d`가 0.003까지 떨어져 판별자가 완승했습니다. 파라미터를 늘려도 품질이 오르지 않았습니다.
- 개수가 적을수록 빠른 이유는 회로 호출 수(sub-generator 수 × batch)가 비용을 지배하기 때문입니다.
- 4개 설정의 다양성(1.85)이 결과 표(1.92)와 다른 것은 평가 실행마다 난수가 달라서입니다.

### 학습 안정성

MediQ-GAN을 `lr_g` 0.02로 학습하면 3 epoch 만에 `loss_d` 0.0027, 다양성 0.000(mode collapse)이 됐습니다. GAN 관례값(`lr` 2e-4, `betas` (0.5, 0.999), `z ~ N(0, 1)`)으로 바꿔 25 epoch을 완주했습니다. 원 논문이 WGAN-GP critic을 쓰는 이유입니다.

### 참고: CNN 증강 평가 재현 (8×8 단계)

| | 정확도 | AUC |
|---|---|---|
| 증강 전 | 0.946 | 0.970 |
| 증강 후 | 0.913 | 0.974 |

DF 92장 규모에서는 이 차이를 개선으로 볼 수 없어, 실습 평가를 지표 4종으로 바꿨습니다. 산출물은 [`archive/assets_8px/`](../archive/assets_8px/)에 있습니다.

## 원 논문과 다른 점

| | 원 논문 | 이 자료 |
|---|---|---|
| QGAN sub-generator | 16개 × (데이터 7 + ancilla 1) | 4개 × (데이터 6 + ancilla 1) |
| QGAN 학습량 | 2,000 epoch (1 ~ 1.5시간) | 600 step (약 22분) |
| 해상도 | MediQ-GAN 64×64 RGB | 16×16 그레이스케일 |
| MediQ-GAN 양자 stream | 16큐빗 × 5, depth 8 | 동일 |
| MediQ-GAN 고전 부분 · 판별자 | conv · WGAN-GP critic | MLP · 표준 BCE |
| 평가 | FID, 분류 정확도·AUC | 지표 4종 |
| 실행 환경 | GPU | Colab CPU exact 시뮬레이션 |

## 저장소 구성

```
practice/            학생용
  day1_slides/       1일차 이론 슬라이드 (31장)
  day2_slides/       2일차 설명 슬라이드 (25장)
  day3_slides/       3일차 설명 슬라이드 (11장)
  day2_practice.ipynb, day3_practice.ipynb
  gen_metrics.py     지표 4종 (2·3일차 공통)
  assets/            16×16 전처리 데이터 + checkpoint 3종
  docs/image/        노트북 캡처·논문 그림
archive/             준비·재생산용
  prep/              전처리 데이터 재생성 노트북
  train/             checkpoint 학습 CLI + 모델 모듈
  slides/            2·3일차 슬라이드 생성 스크립트
  assets_8px/        8×8 시절 자산
  paper/             논문 PDF + 서지사항
```

## 로컬에서 checkpoint 다시 만들기

```bash
python -m venv C:/qmlvenv
C:/qmlvenv/Scripts/pip install -r requirements.txt
cd archive/train
# QGAN (약 22분)
C:/qmlvenv/Scripts/python.exe -X utf8 train_qgan_checkpoint.py --npy ../../practice/assets/df_preprocessed.npy --out_dir ../checkpoints --n_generators 4 --epochs 600
# MediQ-GAN (epoch당 약 8분)
C:/qmlvenv/Scripts/python.exe -X utf8 train_mediqgan_checkpoint.py --npy ../../practice/assets/df_preprocessed.npy --out_dir ../checkpoints --epochs 25 --save_every 5
```

전처리 npy를 다시 만들 때만 Kaggle이 필요합니다(`archive/prep/prep_step1_16px_npy.ipynb`). 만든 checkpoint를 `practice/assets/`로 옮기면 노트북이 그대로 씁니다. 상세는 [`archive/README.md`](../archive/README.md).

## 라이선스

- 코드·문서·슬라이드: [MIT](../LICENSE)
- 데이터 파생물(`practice/assets/`, `archive/assets_8px/`): HAM10000의 CC BY-NC 4.0을 따름 (비상업)
- 논문 PDF와 인용 그림: 각 논문의 CC BY 4.0. MediQ-GAN PDF와 HAM10000 QGAN 저자 프리프린트만 포함했고(출판본은 Springer 독점 라이선스), 슬라이드와 3일차 노트북의 논문 그림은 출처를 밝혀 인용함. 상세는 [`archive/paper/README.md`](../archive/paper/README.md)

## 참고문헌

1. Andra, M. B., Yuliani, A. R., Kadar, J. A., Ramdan, A. & Pardede, H. F. **Data augmentation in cancer image classification problem with quantum GAN.** *Quantum Machine Intelligence* **7**, 90 (2025). https://doi.org/10.1007/s42484-025-00315-y (프리프린트: https://doi.org/10.21203/rs.3.rs-5191116/v1)
2. Jiao, Q., Tang, Y., Zhuang, J., Cong, J. & Shi, Y. **MediQ-GAN: Quantum-Inspired GAN for High Resolution Medical Image Generation.** arXiv:[2506.21015](https://arxiv.org/abs/2506.21015) (2025). 공식 구현: https://github.com/QingyueJ-nd/MediQ-GAN
3. Tschandl, P., Rosendahl, C. & Kittler, H. **The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions.** *Scientific Data* **5**, 180161 (2018). https://doi.org/10.7910/DVN/DBW86T
