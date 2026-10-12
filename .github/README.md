# 피부병변 의료영상 양자 생성모델 - QGAN / MediQ-GAN

**양자 GAN으로 의료영상 데이터를 증강하는 전 과정**(데이터 EDA → 세그멘테이션 전처리 → 양자 인코딩 → 학습 → 평가 → 고전 비교)을, 노트북 두 개로 **Google Colab 무료 CPU에서 끝까지 실행**할 수 있도록 구현한 실습 자료입니다.

> 한국어 | **[English](README.en.md)**

논문 두 편의 서로 다른 하이브리드 전략(**모델 단위** vs **레이어 단위**)을 같은 데이터·같은 지표로 나란히 비교하는 것이 자료의 핵심입니다.

## 한눈에 보기

| 항목 | 내용 |
|---|---|
| **데이터셋** | HAM10000(피부병변 10,015장) 중 DF 115장 · NV 345장 → K-means + Fuzzy C-means 세그멘테이션 후 16×16 그레이스케일 |
| **모델 ①** | Patch QGAN (model-level hybrid) - 서브제너레이터 4개 × 7큐빗(데이터 6 + 보조 1), depth 10, patch 64 |
| **모델 ②** | MediQ-GAN (layer-level hybrid) - 고전 스트림 + 양자 스트림(5개 × 16큐빗, depth 8) 듀얼스트림 생성자 |
| **판별자** | 두 모델 공통 - 원 논문 Table 4의 5층 완전연결 분류기 |
| **스택** | PennyLane(`default.qubit` / `lightning.qubit` + `adjoint`) · PyTorch · scikit-fuzzy · OpenCV |
| **실행 환경** | Google Colab 기본 CPU 런타임 - 설치·GPU·양자 하드웨어 계정 모두 불필요 |
| **평가** | 경량 생성품질 지표 4종(픽셀통계 · 클래스평균 상관 · 최근접 실제거리 · 샘플 다양성) |
| **산출물** | 이론 슬라이드 31장 · 실습 노트북 2종 · 사전학습 체크포인트 3종 · 지표 모듈 · 재생산용 CLI |

### 설계 원칙

1. **양자 회로 스펙은 줄이지 않는다.** 시간을 줄이려고 큐빗 수나 깊이를 깎으면 "논문이 말한 모델"이 아니게 되므로, 대신 **데이터 해상도와 학습 구간**을 줄였습니다(MediQ-GAN 양자 스트림은 원 논문 스펙 그대로).
2. **척도를 통일해 비교한다.** QGAN 출력은 확률(픽셀 합 = 1), MediQ-GAN 출력은 Tanh(-1~1), 전처리 데이터는 0~1로 세 척도가 섞여 있어, 공통 함수로 0~1로 되돌린 뒤에만 지표를 계산합니다. 이 과정을 생략하면 두 모델의 차이가 척도 차이에 묻힙니다.
3. **실패와 한계를 함께 기록한다.** 원 논문과 다른 점, 품질이 무너졌던 설정, 지표가 말해주지 못하는 것을 자료 본문에 고지합니다.

## 실습 자료 열기

| 일차 | 내용 | 자료 |
|---|---|---|
| 1일차 | 이론 - 데이터셋 · 두 논문 아키텍처 · 정량 결과 · VQC 학습 방식(parameter-shift, 계산비용) · QML 연구 방향 | [슬라이드 pptx](../practice/day1_slides/day1_theory_slides.pptx) · [pdf](../practice/day1_slides/day1_theory_slides.pdf) |
| 2일차 | EDA · 세그멘테이션 전처리 · 양자 인코딩 · **QGAN 라이브 학습 → 생성 → 평가** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hyunhp/skin_disease_qml/blob/main/practice/day2_practice.ipynb) |
| 3일차 | **MediQ-GAN 미세조정** → QGAN과 동일 지표 비교 → 생성 모델에서의 양자컴퓨팅 한계·연구 방향 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hyunhp/skin_disease_qml/blob/main/practice/day3_practice.ipynb) |

노트북을 연 뒤 `파일(File) → Drive에 사본 저장`을 먼저 실행하면 실행 결과가 본인 Drive에 남습니다. 노트북은 실행 중 이 저장소를 `git clone`해 [`practice/assets/`](../practice/assets/)의 전처리 데이터·체크포인트와 [`practice/gen_metrics.py`](../practice/gen_metrics.py)를 불러옵니다. HAM10000 원본(약 6GB)만 `kagglehub`로 직접 내려받습니다.

## 두 아키텍처

|  | QGAN (Andra et al., 2025) | MediQ-GAN (Jiao et al., 2025) |
|---|---|---|
| 하이브리드 수준 | **모델 단위** - 생성자 전체가 양자회로 | **레이어 단위** - 생성자 내부에서 고전·양자 스트림이 병렬로 동작 |
| 생성 방식 | 서브제너레이터가 patch를 나눠 만들고 이어붙임 | 입력 특징을 절반씩 나눠 처리한 뒤 skip-connection으로 융합 |
| 측정·출력 | 전체 측정 후 보조큐빗 = 0인 항목만 선택(post-selection) → 확률 척도 | 큐빗별 PauliX 기댓값 → 1×1 conv 투영 → MLP 디코더 → Tanh |
| 실습 학습 방식 | 수업 중 **처음부터 학습**(600스텝 기준 로컬 CPU 실측 약 22분) | 사전학습 체크포인트에서 **미세조정**(16큐빗 시뮬레이션이 비싸 전체 학습은 3시간 이상) |

## 평가 설계

16×16 저해상도에서는 **FID를 쓰지 않습니다** - Inception 특징이 의미를 갖지 못하는 해상도이고(MediQ-GAN 논문은 64×64 RGB 기준), 표본도 수백 장 규모입니다. 대신 해석 가능한 네 가지를 [`practice/gen_metrics.py`](../practice/gen_metrics.py)에 구현해 2·3일차가 같은 모듈을 import합니다.

| 지표 | 보는 것 | 읽는 법 |
|---|---|---|
| ① 픽셀 강도 통계·히스토그램 | 밝기 분포가 실제와 맞는가 | 척도 변환 **전** 값도 함께 봄 - 척도 차이 자체가 두 모델의 구조적 차이를 보여줌 |
| ② 클래스 평균 이미지와의 상관계수 | 병변의 전체적 형태를 재현했는가 | 높을수록 좋음. 생성 표본 수에 민감해 QGAN은 64장, MediQ-GAN은 16장으로 고정 |
| ③ 최근접 실제 이미지 L2 거리 | 학습 데이터를 외운 것은 아닌가 | 0에 가까우면 암기(과적합) 신호 |
| ④ 샘플 간 거리(다양성) + 손실곡선 | 같은 이미지만 반복 생성하지 않는가 | 0에 가까우면 모드붕괴. 실제 DF 데이터 값(2.505)이 기준점 |

## 결과

로컬 CPU(PennyLane exact 상태벡터 시뮬레이션) 실측값입니다. 생성 모델은 호출마다 새 난수를 쓰므로 소수점 자리보다 **모델 간 격차**를 보는 것이 맞습니다.

| 모델 | 학습량 | ② 클래스평균 상관 ↑ | ③ 최근접 실제거리 | ④ 샘플간 다양성 (실제 2.505) |
|---|---|---|---|---|
| QGAN 16×16 | 600스텝 (약 22분) | **0.195 ± 0.012** (64장×10시드) | 1.64 | 1.92 |
| MediQ-GAN 10에폭 (미세조정 출발점) | 약 80분 | 0.018 | - | - |
| MediQ-GAN 25에폭 (최종) | 196분 | **0.365** | 3.44 | 0.30 |

- **MediQ-GAN은 "평균적인 병변 형태"를 더 잘 맞추지만(상관 0.365 vs 0.195), 샘플 다양성이 실제 데이터의 1/8 수준(0.30 vs 2.505)** 으로 비슷한 이미지를 반복 생성하는 경향이 있습니다. QGAN은 형태 재현이 약한 대신 다양성(1.92)이 실제 분포에 가깝습니다. 두 지표를 함께 봐야 "어느 쪽이 더 좋은 생성모델인가"에 답할 수 있다는 점이 3일차 토론 주제입니다.
- 두 모델 모두 최근접 실제거리가 1.6 이상이어서, 학습 데이터를 외워 되풀이하는 상태는 아닙니다.
- 8×8 시절 체크포인트(depth 4, 300스텝)를 같은 지표로 재평가하면 0.242가 나오지만, 해상도·표본 조건이 달라 위 표와 직접 비교하지는 않았습니다.

### 서브제너레이터 수 실험 - 파라미터를 늘려도 좋아지지 않는다

QGAN의 서브제너레이터 수를 2·4·8·16으로 바꿔 **600스텝 · depth 10 동일 조건**으로 재학습한 결과입니다. 서브제너레이터가 많아질수록 픽셀당 파라미터는 늘지만, 품질은 단조증가하지 않았습니다.

| 서브제너레이터 | 큐빗 | 픽셀당 파라미터 | ② 클래스평균 상관 | ④ 다양성 | 소요 |
|---|---|---|---|---|---|
| 2 | 8 | 0.62 | -0.054 (8장 측정) | 1.81 | 17.4분 |
| **4 (채택)** | 7 | 1.09 | **0.195 ± 0.012** | 1.85 | 22.2분 |
| 8 | 6 | 1.88 | 0.105 ± 0.011 | 2.20 | 34.2분 |
| 16 (논문과 동일) | 5 | 3.12 | 0.080 ± 0.004 | 2.40 | 54.9분 |

- 파라미터가 가장 많은 16개 설정에서 `loss_d`가 0.003까지 떨어져 **판별자가 완승하고 생성자가 학습 신호를 잃었습니다.** 용량을 키우면 GAN의 균형이 판별자 쪽으로 깨진다는 실증 사례입니다.
- 서브제너레이터가 **적을수록 빠른** 것은 버그가 아닙니다 - 회로 호출 횟수(`서브제너레이터 수 × 배치`)가 상태벡터 크기(2ⁿ)보다 비용을 더 지배합니다.
- 처음에는 "큐빗 수·patch 크기가 논문과 정확히 일치한다"는 이유로 2개를 택했지만 실측 품질이 가장 나빴습니다. **스펙 일치보다 실측을 우선**해 4개로 교체했습니다.

### 학습 안정성 - 판별자가 3에폭 만에 이기는 문제

MediQ-GAN 사전학습을 QGAN과 같은 학습률(`lr_g` 0.02)로 시작했을 때 **3에폭 만에 `loss_d`가 0.0027로 붕괴하고 샘플 다양성이 0.000**(완전 모드붕괴)이 됐습니다. MediQ-GAN은 고전 MLP 디코더가 최종 출력을 만들기 때문에, Tanh가 포화되면 잠재벡터와 무관한 상수 이미지가 나옵니다.

GAN 관례값(`lr` 2e-4, `betas` (0.5, 0.999), `z ~ N(0,1)`)으로 바꿔 25에폭을 붕괴 없이 완주했고, 이 레시피를 체크포인트 설정에 함께 저장해 노트북이 같은 조건으로 미세조정하도록 했습니다. 원 논문이 **WGAN-GP critic**을 쓰는 이유(표준 GAN 학습의 불안정성)를 실습에서 그대로 겪은 사례라, 자료에 토론 소재로 남겼습니다.

### 참고 - 논문 평가 프로토콜(CNN 증강) 재현

원 논문은 생성 품질을 **증강 전후 분류 성능**으로 평가합니다. 8×8 단계에서 이 프로토콜을 재현해, 실제 DF 92장에 합성 184장을 더해 CNN을 학습하고 held-out(DF 23 / NV 69)에서 평가했습니다.

| | 정확도 | AUC |
|---|---|---|
| 증강 전 | 0.946 | 0.970 |
| 증강 후 | 0.913 | **0.974** |

AUC는 0.004 올랐고 정확도는 떨어졌습니다 - 표본 92장 규모에서 이 차이를 "개선"으로 단정할 수 없다는 판단에 따라, 실습 평가를 CNN 대신 위의 지표 4종으로 바꿨습니다. 이론 강의에서는 논문 수치와 함께 이 한계를 다룹니다. 당시 산출물은 [`archive/assets_8px/`](../archive/assets_8px/)에 보존돼 있습니다.

## 원 논문과 다른 점 (수업 중에도 고지)

실습 코드는 논문 **재현**이 아니라 구조를 이해하기 위한 **축소판**입니다.

| | 원 논문 | 이 자료 |
|---|---|---|
| QGAN 서브제너레이터 | 16개 × (데이터 7 + 보조 1큐빗) | 4개 × (데이터 6 + 보조 1큐빗) - 실측으로 선택 |
| QGAN 학습량 | 2,000 epoch (1~1.5시간) | 600스텝 (약 22분) |
| 해상도 | MediQ-GAN 64×64 RGB | 16×16 그레이스케일 |
| MediQ-GAN 양자 스트림 | 5개 × 16큐빗, depth 8 | **동일** |
| MediQ-GAN 고전 부분 | conv encoder/decoder | MLP |
| MediQ-GAN 판별자 | **WGAN-GP critic** | 표준 BCE 판별자 (위 "학습 안정성" 참고) |
| 평가 지표 | FID, 분류 정확도·AUC | 픽셀통계·클래스평균 상관·최근접거리·다양성 |
| 실행 환경 | GPU | Colab CPU exact 시뮬레이션 (샷 노이즈·하드웨어 오류 없음) |

## 저장소 구성

```
practice/                      학생용 - 수업에서 여는 것은 이 폴더뿐
  day1_slides/                 1일차 이론 강의 슬라이드 (pptx + pdf, 31장)
  day2_practice.ipynb          2일차 실습 - EDA·전처리·인코딩 → QGAN 학습·평가
  day3_practice.ipynb          3일차 실습 - MediQ-GAN 미세조정 → QGAN과 비교
  gen_metrics.py               생성품질 지표 4종 (2·3일차 공통 모듈)
  assets/                      16×16 전처리 데이터 + 사전학습 체크포인트 3종 (약 1MB)
  docs/image/                  Kaggle API 토큰 발급 화면 캡처

archive/                       보관용 - 강의 준비·재생산·근거 자료
  prep/                        전처리 데이터 재생성·코드 리허설 노트북
  train/                       체크포인트 학습 CLI + 모델·전처리 모듈
  assets_8px/                  8×8 시절 자산 (CNN 증강 비교 포함, 현재 미사용)
  paper/                       논문 PDF + 서지사항·라이선스·구현 차이 비교표

requirements.txt               로컬 실행용 패키지 목록
```

## 로컬에서 재현하기

실습은 Colab만으로 끝나지만, 체크포인트를 다시 만들려면 아래 순서를 따릅니다(②③은 Kaggle 계정이 필요 없습니다).

```bash
python -m venv C:/qmlvenv
C:/qmlvenv/Scripts/pip install -r requirements.txt
```

① **(Colab · Kaggle 필요)** HAM10000 → 16×16 전처리 npy 재생성: `archive/prep/prep_step1_16px_npy.ipynb`

② QGAN 체크포인트 (약 22분)

```bash
cd archive/train
C:/qmlvenv/Scripts/python.exe -X utf8 train_qgan_checkpoint.py --npy ../../practice/assets/df_preprocessed.npy --out_dir ../checkpoints --epochs 600
```

③ MediQ-GAN 사전학습 (에폭당 약 8분, 5에폭마다 중간 저장)

```bash
C:/qmlvenv/Scripts/python.exe -X utf8 train_mediqgan_checkpoint.py --npy ../../practice/assets/df_preprocessed.npy --out_dir ../checkpoints --epochs 25 --save_every 5
```

생성된 체크포인트를 `practice/assets/`로 옮기면 노트북이 그대로 불러 씁니다. 상세는 [`archive/README.md`](../archive/README.md) 참고.

## 데이터·논문 라이선스

- **HAM10000** 원본 이미지는 이 저장소에 포함하지 않으며, 2일차 노트북에서 `kagglehub`로 직접 내려받습니다. `practice/assets/`의 전처리 데이터·체크포인트는 HAM10000 파생물이므로 **CC BY-NC 4.0**(비상업적 이용) 조건이 그대로 적용됩니다 - 교육·연구 목적으로만 사용하십시오.
- **MediQ-GAN** 논문(arXiv:2506.21015)은 CC BY 4.0이라 PDF를 [`archive/paper/`](../archive/paper/)에 포함했습니다.
- **HAM10000 QGAN** 논문은 출판본이 Springer Nature 독점 라이선스라 포함할 수 없어, **CC BY 4.0 저자 프리프린트**(Research Square rs-5191116v1)를 대신 넣었습니다. 인용은 출판본 기준으로 하십시오.
- 슬라이드의 MediQ-GAN 그림은 원 논문(CC BY 4.0)에서 출처를 밝혀 인용했고, 그 외 도식은 논문 구조를 바탕으로 새로 그렸습니다.

## 참고문헌

1. Andra, M. B., Yuliani, A. R., Kadar, J. A., Ramdan, A. & Pardede, H. F. **Data augmentation in cancer image classification problem with quantum GAN.** *Quantum Machine Intelligence* **7**, 90 (2025). https://doi.org/10.1007/s42484-025-00315-y
   (CC BY 4.0 프리프린트: Research Square, https://doi.org/10.21203/rs.3.rs-5191116/v1 )
2. Jiao, Q., Tang, Y., Zhuang, J., Cong, J. & Shi, Y. **MediQ-GAN: Quantum-Inspired GAN for High Resolution Medical Image Generation.** arXiv:[2506.21015](https://arxiv.org/abs/2506.21015) (2025). 공식 구현: https://github.com/QingyueJ-nd/MediQ-GAN
3. Tschandl, P., Rosendahl, C. & Kittler, H. **The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions.** *Scientific Data* **5**, 180161 (2018). https://doi.org/10.7910/DVN/DBW86T
