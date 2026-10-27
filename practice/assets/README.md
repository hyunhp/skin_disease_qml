# practice/assets

2·3일차 실습 노트북이 `git clone`으로 받아 쓰는 자산 폴더 

## 구성 항목

| 파일 | 내용 |
|---|---|
| `df_preprocessed.npy` | DF(피부섬유종) 115장, 16×16, 0 ~ 1. segmentation(K-means+FCM) 후 축소. 2일차 QGAN 학습·3일차 비교의 실제 데이터 |
| `nv_preprocessed.npy` | NV(모반) 345장, 16×16, 0 ~ 1. 클래스 대비용 |
| `manifest.json` | 위 두 npy의 생성 조건(해상도·장수·척도·출처) |
| `qgan_df_16px.pt` | QGAN checkpoint - sub-generator 4개 × (데이터 6 + ancilla 1 = 7큐빗), depth 10, 600 step. 클래스평균 상관 0.195 |
| `mediqgan_e010.pt` | MediQ-GAN 10 epoch - 상관 0.018 |
| `mediqgan_final.pt` | MediQ-GAN 25 epoch 최종 - 16큐빗 × 5 sub-generator, depth 8 (원 논문 스펙). 상관 0.365 |

생성 경로: `archive/prep/prep_step1_16px_npy.ipynb`(Colab, npy) → `archive/train/train_qgan_checkpoint.py` → `archive/train/train_mediqgan_checkpoint.py`(둘 다 로컬, Kaggle 불필요).
수치의 측정 방식과 선택 근거는 프로젝트 README의 "sub-generator 수 재실험"·"MediQ-GAN 학습 레시피" 섹션 참고.
