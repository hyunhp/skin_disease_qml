# practice

**실습은 현재 폴더에서만 진행**합니다. Colab 링크는 Readme ([`.github/README.md`](../.github/README.md))에 있다.

| 파일 | 내용 |
|---|---|
| `day1_slides/day1_theory_slides.pptx` · `.pdf` | 이론 강의 슬라이드(31장). |
| `day2_slides/day2_practice_slides.pptx` · `.pdf` | 2일차 실습 설명 슬라이드(25장). 노트북 내용을 PART 순서로 설명하는 코드 중심 자료 + 1일차 복습. 발표자 노트 포함 |
| `day3_slides/day3_practice_slides.pptx` · `.pdf` | 3일차 실습 설명 슬라이드(23장). MediQ-GAN 구조·미세조정·QGAN 비교 + 2일차 복습. 발표자 노트 포함 |
| `day2_practice.ipynb` | Colab 환경·EDA·segmentation·회로 encoding → QGAN 라이브 학습·생성·평가 |
| `day3_practice.ipynb` | MediQ-GAN 미세조정 → QGAN과 동일 지표 비교 → 참고사항·토론 |
| `gen_metrics.py` | 생성품질 지표 4종. 두 노트북이 같은 잣대로 비교할 때 import함 |
| `assets/` | 전처리 데이터(16×16) + 사전학습 checkpoint. 상세는 [`assets/README.md`](assets/README.md) |
| `docs/image/` | Kaggle API 토큰 발급 화면 캡처 |

두 노트북은 실행 시 이 저장소를 `git clone`해서 `practice/assets/`와 `practice/gen_metrics.py`를 쓴다
(`ASSET_DIR`·`sys.path` 설정 셀 참고). HAM10000 원본 이미지(약 6GB)는 저장소에 없고 `kagglehub`로 직접 받는다.

강의 준비용 노트북·학습 스크립트·구 8×8 자산·논문 PDF는 실습 경로를 깔끔하게 두기 위해 [`archive/`](../archive/)로 분리해뒀다.
