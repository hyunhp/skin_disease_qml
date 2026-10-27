# paper - 강의에서 다루는 원 논문

이 강의는 논문 두 편을 다룹니다. 두 편 모두 **CC BY 4.0로 공개된 판본**을 저장소에 포함했습니다. 한 편은 출판본이 아니라 저자 프리프린트라는 점에 주의하세요.

## ① HAM10000 QGAN (1·2일차 실습의 기반)

> M. Bagus Andra, Asri R. Yuliani, Jimmy A. Kadar, Ade Ramdan, Hilman F. Pardede.
> **"Data augmentation in cancer image classification problem with quantum GAN."**
> *Quantum Machine Intelligence* **7**, 90 (2025). 온라인 공개 2025-09-15.
> DOI: [10.1007/s42484-025-00315-y](https://doi.org/10.1007/s42484-025-00315-y)

- **출판본 PDF는 미포함** - Springer Nature 독점 라이선스(오픈액세스 아님)라 이 공개 저장소에 올릴 수 없습니다.
- **대신 저자 프리프린트를 포함합니다**: [`HAM10000-QGAN_preprint_ResearchSquare_rs-5191116v1.pdf`](HAM10000-QGAN_preprint_ResearchSquare_rs-5191116v1.pdf) (38쪽)
  > Research Square, v1 (2024-11-14 공개). DOI: [10.21203/rs.3.rs-5191116/v1](https://doi.org/10.21203/rs.3.rs-5191116/v1) - **CC BY 4.0**
  >
  > ⚠ **동료심사 전 버전**입니다. 2025-09-15 출판본과 내용이 다를 수 있으니, 인용할 때는 출판본(위 Springer DOI)을 기준으로 하고 프리프린트는 본문 확인용으로만 쓰세요.
  > 강의자료의 Table 3 수치(큐빗 7 + ancilla 1, Sub-generator 16, PQC depth 10, 학습률 0.1, epoch 2,000)는 이 프리프린트에서 대조 확인했습니다(2026-10-12).
- 소속 기관 구독으로 받은 출판본 개인 사본을 이 폴더에 두더라도 `.gitignore`가 커밋을 막아둡니다(실수로 공개되지 않도록).
- 이 논문에서 가져온 것: patch 방식 생성자(sub-generator ensemble), 5층 완전연결 판별자(Table 4), K-means+Fuzzy C-means segmentation(Section 3.1), DF vs NV 이진분류 설정, 증강 전/후 비교 결과(Table 6·10·11).

## ② MediQ-GAN (3일차 실습의 기반)

> Qingyue Jiao, Yongcan Tang, Jun Zhuang, Jason Cong, Yiyu Shi.
> **"MediQ-GAN: Quantum-Inspired GAN for High Resolution Medical Image Generation."**
> arXiv:[2506.21015](https://arxiv.org/abs/2506.21015) (v1 2025-06-26, **v2 2025-11-03**).

- **PDF 포함**: [`MediQ-GAN_arXiv-2506.21015v2.pdf`](MediQ-GAN_arXiv-2506.21015v2.pdf) (28쪽, 1.35MB)
- 라이선스 **CC BY 4.0** - 출처를 밝히면 재배포 가능해 저장소에 포함했습니다. 위 서지사항이 그 출처 표기입니다.
- 공식 구현: https://github.com/QingyueJ-nd/MediQ-GAN
- 이 논문에서 가져온 것: dual-stream 생성자(고전 stream + 양자 stream을 skip-connection으로 융합), 양자 stream 스펙(**sub-generator 5개 × 16큐빗, 8층 깊이** - 본문 그대로), 16 site 중 5개만 양자 처리하는 방식, exact 상태벡터 시뮬레이션 학습(`lightning.qubit` + `adjoint`).

## 우리 구현이 원 논문과 다른 점 (수업 중에도 고지)

실습 코드는 재현이 아니라 **구조를 이해하기 위한 축소판**입니다.

| | 원 논문 | 우리 실습 |
|---|---|---|
| QGAN sub-generator | 16개 × (데이터 7 + ancilla 1큐빗) | 4개 × (데이터 6 + ancilla 1큐빗) - 실측으로 선택 |
| QGAN 학습량 | 2,000 epoch (1~1.5시간) | 600 step (약 20분) |
| 이미지 해상도 | QGAN 논문 기준 저해상도 / MediQ-GAN 64×64 RGB | 16×16 흑백 |
| MediQ-GAN 양자 stream | 5개 × 16큐빗, depth 8 | **동일** |
| MediQ-GAN 고전 부분 | conv 기반 encoder/decoder | MLP |
| **MediQ-GAN 판별자** | **WGAN-GP critic**(gradient penalty로 Lipschitz 조건 강제) | **표준 BCE 판별자** |
| 평가 지표 | FID, 분류 정확도·AUC | 픽셀통계·클래스평균 상관·최근접거리·다양성 |

마지막 두 줄이 수업에서 직접 드러났습니다. 원 논문이 WGAN-GP를 쓰는 이유가 **표준 GAN 학습이 불안정하기 때문**인데, 우리가 표준 BCE 판별자로 사전학습을 돌렸을 때 실제로 판별자가 3 epoch 만에 완승해 학습이 무너졌습니다(학습률을 GAN 관례인 2e-4로 낮춰 해결). 또 16×16에서는 FID가 의미를 갖지 못해 다른 지표를 써야 했습니다.

## 데이터셋

> Tschandl, P., Rosendahl, C. & Kittler, H. *The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions.* Sci. Data **5**, 180161 (2018).
> https://doi.org/10.7910/DVN/DBW86T - **CC BY-NC 4.0**(비상업적 이용)
