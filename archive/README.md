# archive

강의 준비·재생산·근거 자료. 배포 자료는 [`practice/`](../practice/)에 있다.

| 경로 | 내용 |
|---|---|
| `prep/prep_step1_16px_npy.ipynb` | HAM10000 → 16×16 전처리 npy 재생성 (Colab, Kaggle 인증 필요) |
| `prep/prep_day2_eda_rehearsal.ipynb` | 옛 구성(8×8) 2일차 리허설 |
| `prep/prep_day3_train_checkpoints.ipynb` | 옛 구성(8×8), 실행하지 않음 |
| `train/train_qgan_checkpoint.py` | QGAN checkpoint 학습 CLI (로컬) |
| `train/train_mediqgan_checkpoint.py` | MediQ-GAN 사전학습 CLI (로컬, `--resume` 지원) |
| `train/train_cnn_comparison.py` | 옛 구성. CNN 증강 전/후 비교 (1일차 인용 수치의 근거) |
| `train/*.py` (나머지) | 위 CLI의 모델·전처리 모듈. 노트북 안의 사본과 같은 로직이라 한쪽을 고치면 다른 쪽도 맞춤 |
| `slides/` | 2·3일차 슬라이드 생성 스크립트 ([README](slides/README.md)) |
| `assets_8px/` | 8×8 시절 자산 ([README](assets_8px/README.md)) |
| `paper/` | 논문 PDF와 서지사항 ([README](paper/README.md)) |
| `checkpoints/` | 로컬 학습 산출물 (`.gitignore`로 제외) |

학습 명령은 [저장소 README](../.github/README.md#로컬에서-checkpoint-다시-만들기) 참고. 새 checkpoint는 `practice/assets/`로 복사해 커밋한다.
