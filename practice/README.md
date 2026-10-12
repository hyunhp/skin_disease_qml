# practice

**실제로 실행하는 것은 해당 폴더뿐**이다. Colab 링크는 저장소 첫 화면([`.github/README.md`](../.github/README.md))에 있다.

| 파일 | 내용 |
|---|---|
| `day1_slides/day1_theory_slides.pptx` · `.pdf` | 이론 강의 슬라이드(31장). 수정 전 백업은 `day1_slides/_backup/`(gitignore) |
| `day2_practice.ipynb` | Colab 환경·EDA·세그멘테이션·회로 인코딩 → QGAN 라이브 학습·생성·평가 |
| `day3_practice.ipynb` | MediQ-GAN 미세조정 → QGAN과 동일 지표 비교 → 참고사항·토론 |
| `gen_metrics.py` | 생성품질 지표 4종. 두 노트북이 같은 잣대로 비교할 때 import함 |
| `assets/` | 전처리 데이터(16×16) + 사전학습 체크포인트. 상세는 [`assets/README.md`](assets/README.md) |
| `docs/image/` | Kaggle API 토큰 발급 화면 캡처 |

두 노트북은 실행 시 이 저장소를 `git clone`해서 `practice/assets/`와 `practice/gen_metrics.py`를 쓴다
(`ASSET_DIR`·`sys.path` 설정 셀 참고). HAM10000 원본 이미지(약 6GB)는 저장소에 없고 `kagglehub`로 직접 받는다.

강의 준비용 노트북·학습 스크립트·구 8×8 자산·논문 PDF는 실습 경로를 깔끔하게 두기 위해 [`archive/`](../archive/)로 분리해뒀다.
