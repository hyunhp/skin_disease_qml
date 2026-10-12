# archive 

배포 자료(1일차 슬라이드 + 2·3일차 노트북)는 모두 [`practice/`](../practice/)에 있다. 폴더는 **강의 준비·재생산·근거 자료**를 모아둔 곳이다.

| 경로 | 내용 |
|---|---|
| `prep/prep_step1_16px_npy.ipynb` | (현행) HAM10000 → 16×16 전처리 npy 재생성. Kaggle 인증 필요, Colab에서 실행 |
| `prep/prep_day2_eda_rehearsal.ipynb` | (현행) 2일차 코드 리허설 |
| `prep/prep_day3_train_checkpoints.ipynb` | **(옛 구성, 실행 금지)** QGAN·CNN 사전학습용 |
| `train/train_qgan_checkpoint.py` | QGAN 체크포인트 학습 CLI (로컬, Kaggle 불필요) |
| `train/train_mediqgan_checkpoint.py` | MediQ-GAN 사전학습 CLI (로컬 밤샘, `--resume` 지원) |
| `train/train_cnn_comparison.py` | (옛 구성) CNN 증강 전/후 비교 학습. 실습에서는 제거됐고 1일차 인용 수치의 근거로만 남김 |
| `train/{qgan_model,mediqgan_toy,data_pipeline,cnn_classifier}.py` | 위 CLI가 쓰는 모델·전처리 모듈. 노트북 인라인 사본과 로직이 같으니 **한쪽을 고치면 다른 쪽도 맞출 것** |
| `assets_8px/` | 8×8 assets. 상세는 [`assets_8px/README.md`](assets_8px/README.md) |
| `paper/` | 논문 PDF + 서지사항·라이선스·구현 차이 비교표 ([`paper/README.md`](paper/README.md)) |
| `checkpoints/` | 로컬 학습 산출물(`.gitignore`로 제외 - 저장소에는 올라가지 않음) |

## 학습 스크립트 실행 (로컬 venv)

```bash
cd archive/train
C:/qmlvenv/Scripts/python.exe -X utf8 train_qgan_checkpoint.py \
    --npy ../../practice/assets/df_preprocessed.npy --out_dir ../checkpoints --epochs 600
```

`train_mediqgan_checkpoint.py`는 품질 모니터링에 `practice/gen_metrics.py`를 쓰므로 스크립트 안에서 `practice/`를 `sys.path`에 추가한다.
생성된 체크포인트를 배포할 때는 `practice/assets/`로 복사해 커밋한다.