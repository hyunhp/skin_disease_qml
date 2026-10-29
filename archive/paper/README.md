# paper

강의에서 다루는 논문 두 편. 둘 다 CC BY 4.0 판본만 포함했다.

## ① HAM10000 QGAN (1·2일차)

> Andra, M. B., Yuliani, A. R., Kadar, J. A., Ramdan, A. & Pardede, H. F. **Data augmentation in cancer image classification problem with quantum GAN.** *Quantum Machine Intelligence* **7**, 90 (2025). DOI: [10.1007/s42484-025-00315-y](https://doi.org/10.1007/s42484-025-00315-y)

- 출판본은 Springer 독점 라이선스라 포함하지 않음. 대신 저자 프리프린트 [`HAM10000-QGAN_preprint_ResearchSquare_rs-5191116v1.pdf`](HAM10000-QGAN_preprint_ResearchSquare_rs-5191116v1.pdf)를 넣음 (Research Square v1, DOI [10.21203/rs.3.rs-5191116/v1](https://doi.org/10.21203/rs.3.rs-5191116/v1), CC BY 4.0)
- 주의: 동료심사 전 판본임. 인용은 출판본 기준으로 하고, 프리프린트는 본문 확인용으로 씀. Table 3 수치(7 + ancilla 1큐빗, sub-generator 16, depth 10, 학습률 0.1, 2,000 epoch)는 프리프린트에서 대조함
- 출판본 개인 사본을 이 폴더에 두어도 `.gitignore`가 커밋을 막음
- 가져온 것: patch 생성자, 5층 판별자(Table 4), K-means + FCM segmentation(Section 3.1), DF vs NV 설정, 증강 결과(Table 6·10·11), 생성 이미지(Fig. 21, 3일차 노트북)

## ② MediQ-GAN (3일차)

> Jiao, Q., Tang, Y., Zhuang, J., Cong, J. & Shi, Y. **MediQ-GAN: Quantum-Inspired GAN for High Resolution Medical Image Generation.** arXiv:[2506.21015](https://arxiv.org/abs/2506.21015) (v2 2025-11-03).

- [`MediQ-GAN_arXiv-2506.21015v2.pdf`](MediQ-GAN_arXiv-2506.21015v2.pdf) 포함 (CC BY 4.0). 공식 구현: https://github.com/QingyueJ-nd/MediQ-GAN
- 가져온 것: dual-stream 생성자, 양자 stream 스펙(16큐빗 × 5, depth 8), 16 site 중 5개만 양자 처리, `lightning.qubit` + `adjoint` 학습, 생성 이미지(Fig. 2, 3일차 노트북)

원 논문과 실습의 차이는 [저장소 README](../../.github/README.md#원-논문과-다른-점)에 정리했다.

## 데이터셋

> Tschandl, P., Rosendahl, C. & Kittler, H. *The HAM10000 dataset.* Sci. Data **5**, 180161 (2018). https://doi.org/10.7910/DVN/DBW86T (CC BY-NC 4.0)
