# Skin Disease QML - 양자 머신러닝으로 의료 영상 데이터 증강하기

QML 강의 자료 
Lecture materials for the QML course (Quantum GAN for skin-lesion image augmentation).

- **데이터셋 / Dataset**: HAM10000 (피부병변 7종, DF vs NV 이진분류)
- **다루는 논문 / Papers**: HAM10000 QGAN (Andra et al., *Quantum Machine Intelligence* 7, 90, 2025) · MediQ-GAN (Jiao et al., arXiv:2506.21015)
- 모든 실습은 **Google Colab(기본 CPU 런타임)** 에서 진행함 - 개인 PC 설치 불필요. / Everything runs on Google Colab (CPU runtime).
- 생성 품질은 픽셀 통계 · 클래스 평균 상관계수 · 최근접 실제 이미지 거리 · 샘플 다양성 네 가지로 평가함(`practice/gen_metrics.py`). 두 모델을 같은 잣대로 비교함.
- **학생이 여는 것은 [`practice/`](../practice/) 폴더뿐임**(1~3일차 자료 전부 이 안에 있음) - 강의 준비용 스크립트·학습 코드·논문은 [`archive/`](../archive/)에 분리해둠. / Students only need `practice/`.

## 실습 노트북 열기 / Open in Colab

| 일차 | 내용 | 노트북 |
|---|---|---|
| 1일차 (11/13) | 이론 강의 슬라이드 | [`practice/day1_slides/`](../practice/day1_slides/) - [pptx](../practice/day1_slides/day1_theory_slides.pptx) · [pdf](../practice/day1_slides/day1_theory_slides.pdf) |
| 2일차 (11/20) | Colab 환경 · EDA · 세그멘테이션 · 회로 인코딩 → **QGAN 학습 · 생성 · 평가** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hyunhp/skin_disease_qml/blob/main/practice/day2_practice.ipynb) |
| 3일차 (11/27) | **MediQ-GAN 학습(미세조정)** → QGAN과 동일 지표 비교 → 생성에서의 양자컴퓨팅 참고사항 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hyunhp/skin_disease_qml/blob/main/practice/day3_practice.ipynb) |

링크로 연 뒤 **`파일(File) → Drive에 사본 저장(Save a copy in Drive)`** 을 먼저 실행할 것 - 사본을 만들어야 실행 결과가 본인 Drive에 저장됨.

처음 쓰는 경우 2일차 노트북의 "0. Google Colab 시작하기" 섹션 참고.

## 폴더 구성 / Structure

```
practice/                      학생용 - 수업에서 여는 것은 이 폴더뿐
  day1_slides/                 1일차 이론 강의 슬라이드 (pptx + pdf)
  day2_practice.ipynb          2일차 실습 (실행 시 이 저장소를 git clone해 assets/와 지표 모듈을 사용)
  day3_practice.ipynb          3일차 실습 (같은 방식으로 assets/의 체크포인트를 불러옴)
  gen_metrics.py               생성품질 지표 4종 - 2·3일차가 같은 잣대로 비교할 때 사용
  assets/                      전처리 데이터(16×16) + 사전학습 체크포인트 (수 MB)
  docs/image/                  Kaggle API 토큰 발급 화면 캡처 (2일차 인증 안내용)

archive/                       보관용 - 학생 실습에는 쓰지 않음
  prep/                        (강의 준비용) 전처리 npy 재생성·코드 리허설 노트북
  train/                       (강의 준비용) 체크포인트 학습 CLI + 모델·전처리 모듈
  assets_8px/                  2026-10-01 재설계 이전 8×8 자산 (현재 미사용, 근거 자료로 보존)
  paper/                       논문 PDF + 두 논문 서지사항·라이선스·구현 차이 비교표

requirements.txt               로컬 실행용 패키지 목록
```

## 데이터 출처 및 이용 조건 / Data & License

- HAM10000 원본 이미지(약 6GB)는 이 저장소에 포함하지 않으며, 2일차 노트북에서 `kagglehub`로 직접 내려받음.
- `practice/assets/`의 전처리 데이터·체크포인트는 HAM10000에서 파생된 자료임. HAM10000은
  **CC BY-NC 4.0**(비상업적 이용) 조건으로 공개됨 - 교육·연구 목적으로만 사용할 것.
- Tschandl, P., Rosendahl, C. & Kittler, H. *The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions.* Sci. Data 5, 180161 (2018). https://doi.org/10.7910/DVN/DBW86T
- 슬라이드의 MediQ-GAN 그림은 원 논문(CC BY 4.0)에서 출처를 밝혀 인용함. 그 외 도식은 원 논문 구조를 바탕으로 새로 그림.
- **논문 PDF / Papers**: MediQ-GAN(arXiv:2506.21015)은 **CC BY 4.0**이라 [`archive/paper/`](../archive/paper/)에 포함함.
  HAM10000 QGAN 논문(Andra et al., *Quantum Machine Intelligence* 7, 90, 2025)은 출판본이 Springer 독점
  라이선스라, 대신 **CC BY 4.0 저자 프리프린트**(Research Square rs-5191116v1)를 포함함.
  인용은 출판본 기준: https://doi.org/10.1007/s42484-025-00315-y
  실습 구현이 두 논문과 어디서 다른지는 [`archive/paper/README.md`](../archive/paper/README.md)의 비교표 참고.
