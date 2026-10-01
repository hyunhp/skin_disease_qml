# day3/assets

2·3일차 실습 노트북이 `git clone`으로 받아 쓰는 자산 폴더 (하위 폴더 없이 이 위치에 그대로 둠 — 노트북이 최상위 경로로 접근함).

## 현행 자산 (2026-10-01 커리큘럼 재설계, 16×16)

| 파일 | 내용 |
|---|---|
| `df_preprocessed.npy` | DF(피부섬유종) 115장, 16×16, 0~1. 세그멘테이션(K-means+FCM) 후 축소. 2일차 QGAN 학습·3일차 비교의 실제 데이터 |
| `nv_preprocessed.npy` | NV(모반) 345장, 16×16, 0~1. 클래스 대비용 |
| `manifest.json` | 위 두 npy의 생성 조건(해상도·장수·척도·출처) |
| `qgan_df_16px.pt` | QGAN 체크포인트 — 서브제너레이터 4개 × (데이터 6 + 보조 1 = 7큐빗), depth 10, 600스텝. 클래스평균 상관 0.195 |
| `mediqgan_e010.pt` | MediQ-GAN 10에폭 — 3일차 **라이브 미세조정의 출발점**(상관 0.018, 덜 학습된 상태여야 효과가 보임) |
| `mediqgan_final.pt` | MediQ-GAN 25에폭 최종 — 16큐빗 × 5 서브제너레이터, depth 8 (원 논문 스펙). 상관 0.365 |

생성 경로: `prep_step1_16px_npy.ipynb`(Colab, npy) → `train_qgan_checkpoint.py` → `train_mediqgan_checkpoint.py`(둘 다 로컬, Kaggle 불필요).
수치의 측정 방식과 선택 근거는 프로젝트 README의 "서브제너레이터 수 재실험"·"MediQ-GAN 학습 레시피" 섹션 참고.

## 과거 자산 (8×8 시절 — 폴백으로 보존, 현재 노트북은 쓰지 않음)

`qgan_df_8px.pt` · `cnn_before.pt` · `cnn_after.pt` · `comparison_result.json`

CNN 2종과 `comparison_result.json`은 CNN 증강 비교를 실습에서 제거하면서(2026-10-01) 쓰이지 않게 됐다.
1일차 이론에서 인용하는 수치(증강 전/후 AUC 0.970→0.974)의 근거 자료로만 남겨둔다.

HAM10000(CC BY-NC 4.0)에서 파생된 자료 — 비상업적 교육·연구 목적으로만 사용.
