# Skin Disease QML — 양자 머신러닝으로 의료 영상 데이터 증강하기

동아대학교 대학원 QML 강의(11/13 · 11/20 · 11/27) 실습 자료 — 메가존클라우드 Quantum Innovation Lab
Lecture materials for the Dong-A University graduate QML course (Quantum GAN for skin-lesion image augmentation).

- **데이터셋 / Dataset**: HAM10000 (피부병변 7종, DF vs NV 이진분류)
- **다루는 논문 / Papers**: HAM10000 QGAN (Andra et al., *Quantum Machine Intelligence* 7, 90, 2025) · MediQ-GAN (Jiao et al., arXiv:2506.21015)
- 모든 실습은 **Google Colab(기본 CPU 런타임)** 에서 진행함 — 개인 PC 설치 불필요. / Everything runs on Google Colab (CPU runtime).

## 실습 노트북 열기 / Open in Colab

| 일차 | 내용 | 노트북 |
|---|---|---|
| 1일차 (11/13) | 이론 강의 슬라이드 | [`day1/day1_theory_slides.pptx`](day1/day1_theory_slides.pptx) |
| 2일차 (11/20) | Colab 환경 · EDA · 세그멘테이션 · 회로 인코딩 기초 (학습 없음) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hyunhp/skin_disease_qml/blob/main/day2/day2_practice.ipynb) |
| 3일차 (11/27) | 사전학습 QGAN 로드 → 생성 · 증강 · CNN 비교 + MediQ-GAN 데모 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hyunhp/skin_disease_qml/blob/main/day3/day3_practice.ipynb) |

링크로 연 뒤 **`파일(File) → Drive에 사본 저장(Save a copy in Drive)`** 을 먼저 실행할 것 — 사본을 만들어야 실행 결과가 본인 Drive에 저장됨.
처음 쓰는 경우 2일차 노트북의 "0. Google Colab 시작하기" 섹션 참고.

## 폴더 구성 / Structure

```
day1/  이론 강의 슬라이드
day2/  day2_practice.ipynb            2일차 실습
       prep_day2_eda_rehearsal.ipynb   (강의 준비용) 2일차 코드 리허설
day3/  day3_practice.ipynb            3일차 실습 — 실행 시 이 저장소를 git clone해 assets/를 사용
       prep_day3_train_checkpoints.ipynb (강의 준비용) QGAN·CNN 사전학습 → assets/ 생성
       assets/                         사전학습 체크포인트 + 전처리 데이터 (수 MB)
       *.py                            노트북과 같은 로직의 모듈·CLI 학습 스크립트 (노트북은 import하지 않음)
requirements.txt                       로컬 실행용 패키지 목록
```

## 데이터 출처 및 이용 조건 / Data & License

- HAM10000 원본 이미지(약 6GB)는 이 저장소에 포함하지 않으며, 2일차 노트북에서 `kagglehub`로 직접 내려받음.
- `day3/assets/`의 전처리 데이터·체크포인트는 HAM10000에서 파생된 자료임. HAM10000은
  **CC BY-NC 4.0**(비상업적 이용) 조건으로 공개됨 — 교육·연구 목적으로만 사용할 것.
  Tschandl, P., Rosendahl, C. & Kittler, H. *The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions.* Sci. Data 5, 180161 (2018). https://doi.org/10.7910/DVN/DBW86T
- 슬라이드의 MediQ-GAN 그림은 원 논문(CC BY 4.0)에서 출처를 밝혀 인용함. 그 외 도식은 원 논문 구조를 바탕으로 새로 그림.
