# assets_8px

재설계(16×16 전환) 이전의 8×8 자산. 현재 노트북은 쓰지 않으며, 1일차에서 인용하는 수치의 근거로 보존한다.

| 파일 | 내용 |
|---|---|
| `qgan_df_8px.pt` | 8×8 QGAN (sub-generator 4개, depth 4, 300 step). 현행 지표로 상관 0.242 |
| `cnn_before.pt` · `cnn_after.pt` | 증강 전/후 CNN. held-out AUC 0.970 → 0.974, 정확도 0.946 → 0.913 |
| `comparison_result.json` | 위 CNN 비교 상세 수치 |

HAM10000(CC BY-NC 4.0) 파생 자료라 비상업 용도로만 쓴다.
