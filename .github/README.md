# Skin Disease QML - 양자 머신러닝으로 의료 영상 데이터 증강하기

QML 강의 자료 
Lecture materials for the QML course (Quantum GAN for skin-lesion image augmentation).

- **데이터셋 / Dataset**: HAM10000 (피부병변 7종, DF vs NV 이진분류)
- **다루는 논문 / Papers**: HAM10000 QGAN (Andra et al., *Quantum Machine Intelligence* 7, 90, 2025) · MediQ-GAN (Jiao et al., arXiv:2506.21015)
- 모든 실습은 **Google Colab(기본 CPU 런타임)** 에서 진행함 - 개인 PC 설치 불필요. / Everything runs on Google Colab (CPU runtime).
- 생성 품질은 픽셀 통계 · 클래스 평균 상관계수 · 최근접 실제 이미지 거리 · 샘플 다양성 네 가지로 평가함(`day3/gen_metrics.py`). 두 모델을 같은 잣대로 비교함.

## 실습 노트북 열기 / Open in Colab

| 일차 | 내용 | 노트북 |
|---|---|---|
| 1일차 (11/13) | 이론 강의 슬라이드 | [`day1/day1_theory_slides.pptx`](day1/day1_theory_slides.pptx) |
| 2일차 (11/20) | Colab 환경 · EDA · 세그멘테이션 · 회로 인코딩 → **QGAN 학습 · 생성 · 평가** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hyunhp/skin_disease_qml/blob/main/day2/day2_practice.ipynb) |
| 3일차 (11/27) | **MediQ-GAN 학습(미세조정)** → QGAN과 동일 지표 비교 → 생성에서의 양자컴퓨팅 참고사항 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hyunhp/skin_disease_qml/blob/main/day3/day3_practice.ipynb) |

링크로 연 뒤 **`파일(File) → Drive에 사본 저장(Save a copy in Drive)`** 을 먼저 실행할 것 - 사본을 만들어야 실행 결과가 본인 Drive에 저장됨.

처음 쓰는 경우 2일차 노트북의 "0. Google Colab 시작하기" 섹션 참고.

## 폴더 구성 / Structure

```
day1/  이론 강의 슬라이드
day2/  day2_practice.ipynb            2일차 실습 - 실행 시 이 저장소를 git clone해 assets/와 지표 모듈을 사용
       prep_day2_eda_rehearsal.ipynb   (강의 준비용) 2일차 코드 리허설
day3/  day3_practice.ipynb            3일차 실습 - 같은 방식으로 assets/의 체크포인트를 불러옴
       assets/                         사전학습 체크포인트 + 전처리 데이터 (수 MB)
       gen_metrics.py                  생성품질 지표 4종 (2·3일차가 같은 잣대로 비교할 때 사용)
       train_qgan_checkpoint.py        (강의 준비용) QGAN 체크포인트 학습
       train_mediqgan_checkpoint.py    (강의 준비용) MediQ-GAN 사전학습
       prep_day3_train_checkpoints.ipynb (옛 구성) QGAN·CNN 사전학습 - 현재 커리큘럼에서는 쓰지 않음
prep_step1_16px_npy.ipynb              (강의 준비용) HAM10000 → 16×16 전처리 데이터 생성 (Colab)
requirements.txt                       로컬 실행용 패키지 목록
```

## 데이터 출처 및 이용 조건 / Data & License

- HAM10000 원본 이미지(약 6GB)는 이 저장소에 포함하지 않으며, 2일차 노트북에서 `kagglehub`로 직접 내려받음.
- `day3/assets/`의 전처리 데이터·체크포인트는 HAM10000에서 파생된 자료임. HAM10000은
  **CC BY-NC 4.0**(비상업적 이용) 조건으로 공개됨 - 교육·연구 목적으로만 사용할 것.
- Tschandl, P., Rosendahl, C. & Kittler, H. *The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions.* Sci. Data 5, 180161 (2018). https://doi.org/10.7910/DVN/DBW86T
- 슬라이드의 MediQ-GAN 그림은 원 논문(CC BY 4.0)에서 출처를 밝혀 인용함. 그 외 도식은 원 논문 구조를 바탕으로 새로 그림.
