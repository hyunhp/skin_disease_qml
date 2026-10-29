# practice/assets

2·3일차 노트북이 clone해서 쓰는 자산.

| 파일 | 내용 |
|---|---|
| `df_preprocessed.npy` | DF 115장, 16×16, 0 ~ 1 (segmentation 후 축소) |
| `nv_preprocessed.npy` | NV 345장, 16×16, 0 ~ 1 (클래스 비교용) |
| `manifest.json` | 두 npy의 생성 조건 |
| `qgan_df_16px.pt` | QGAN, sub-generator 4개 × 7큐빗, depth 10, 600 step. 상관 0.195 |
| `mediqgan_e010.pt` | MediQ-GAN 10 epoch (미세조정 출발점). 상관 0.018 |
| `mediqgan_final.pt` | MediQ-GAN 25 epoch, 16큐빗 × 5, depth 8. 상관 0.365 |

생성 경로: `archive/prep/prep_step1_16px_npy.ipynb`(Colab) → `archive/train/train_qgan_checkpoint.py` → `archive/train/train_mediqgan_checkpoint.py`(로컬).
