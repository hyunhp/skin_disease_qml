# assets_8px - 재설계 이전(8×8) 자산

2026-10-01 커리큘럼 재설계(16×16 전환 + CNN 증강 비교를 실습에서 제거)로 **현재 노트북은 이 파일들을 쓰지 않는다.**
1일차 이론에서 인용하는 수치의 근거 자료 겸 폴백으로 보존한다.

| 파일 | 내용 |
|---|---|
| `qgan_df_8px.pt` | 8×8 QGAN checkpoint(sub-generator 4개 · depth 4 · 300 step). 현행 지표로 재평가하면 클래스평균 상관 0.242 - 16×16 재실험의 기준선이 된 값 |
| `cnn_before.pt` · `cnn_after.pt` | 증강 전/후 CNN 분류기(2026-09-22 학습). held-out(DF 23 / NV 69) AUC 0.970 → 0.974, 정확도 0.946 → 0.913 |
| `comparison_result.json` | 위 CNN 비교의 상세 수치 |

현행 자산은 [`practice/assets/`](../../practice/assets/)에 있다. HAM10000(CC BY-NC 4.0)에서 파생된 자료 - 비상업적 교육·연구 목적으로만 사용.
