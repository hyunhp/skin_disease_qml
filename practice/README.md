# practice

실습 자료 폴더. Colab 링크는 [저장소 README](../.github/README.md)에 있다.

| 파일 | 내용 |
|---|---|
| `day1_slides/` | 1일차 이론 슬라이드 (31장) |
| `day2_slides/` | 2일차 설명 슬라이드 (25장, 발표자 노트 포함) |
| `day3_slides/` | 3일차 설명 슬라이드 (11장, 발표자 노트 포함) |
| `day2_practice.ipynb` | EDA · segmentation · 회로 구성 → QGAN 학습 · 평가 |
| `day3_practice.ipynb` | MediQ-GAN 미세조정 → QGAN과 같은 지표로 비교 |
| `gen_metrics.py` | 생성품질 지표 4종 (두 노트북 공통) |
| `assets/` | 16×16 전처리 데이터 + checkpoint ([README](assets/README.md)) |
| `docs/image/` | 노트북에 쓰는 캡처와 논문 그림 |

노트북은 실행 중 이 저장소를 clone해 `assets/`와 `gen_metrics.py`를 쓴다. HAM10000 원본(약 6GB)만 `kagglehub`로 받는다.
