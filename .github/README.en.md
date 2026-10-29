# Quantum Generative Models for Dermatoscopic Images - QGAN / MediQ-GAN

Hands-on material for quantum-GAN data augmentation in medical imaging (EDA → segmentation → quantum encoding → training → evaluation) that runs end to end on Google Colab's free CPU runtime. It compares two hybrid strategies, model-level and layer-level, on the same data with the same metrics.

> [한국어](README.md) | **English**

## At a glance

| | |
|---|---|
| Data | HAM10000: 115 DF + 345 NV images → K-means + Fuzzy C-means segmentation → 16×16 grayscale |
| Model ① | Patch QGAN (model-level hybrid): 4 sub-generators × 7 qubits (6 data + 1 ancilla), depth 10 |
| Model ② | MediQ-GAN (layer-level hybrid): classical stream + quantum stream (16 qubits × 5, depth 8) |
| Discriminator | Shared, the 5-layer fully connected network from Table 4 of the QGAN paper |
| Evaluation | Four metrics (pixel distribution, class-mean correlation, nearest-real distance, sample diversity). FID is meaningless at 16×16 |
| Runtime | Colab default CPU, PennyLane exact simulation; no install, GPU or quantum hardware |

Design principles
- Keep the quantum circuit spec; reduce resolution and training budget instead
- Map all output scales (probability, Tanh, 0-1) to 0-1 before computing metrics
- State deviations from the papers, failed settings and limits in the material

## Material

| Day | Content | Links |
|---|---|---|
| Day 1 | Theory: dataset, both architectures and their results, VQC training cost | [pptx](../practice/day1_slides/day1_theory_slides.pptx) · [pdf](../practice/day1_slides/day1_theory_slides.pdf) |
| Day 2 | EDA · segmentation · circuit → QGAN training → evaluation | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hyunhp/skin_disease_qml/blob/main/practice/day2_practice.ipynb) · [pptx](../practice/day2_slides/day2_practice_slides.pptx) · [pdf](../practice/day2_slides/day2_practice_slides.pdf) |
| Day 3 | MediQ-GAN fine-tuning → comparison with QGAN on the same metrics | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hyunhp/skin_disease_qml/blob/main/practice/day3_practice.ipynb) · [pptx](../practice/day3_slides/day3_practice_slides.pptx) · [pdf](../practice/day3_slides/day3_practice_slides.pdf) |

Run `File → Save a copy in Drive` first. The notebooks clone this repository at runtime for [`practice/assets/`](../practice/assets/) and [`gen_metrics.py`](../practice/gen_metrics.py); only the HAM10000 originals (~6 GB) come from `kagglehub`.

## Results

Measured on a local CPU. Every generation call draws fresh noise, so compare the gap between models rather than decimals.

| Model | Training | ② Class-mean corr. ↑ | ③ Nearest-real dist. | ④ Diversity (real 2.505) |
|---|---|---|---|---|
| QGAN | 600 steps (~22 min) | 0.195 ± 0.012 (64 samples × 10 seeds) | 1.64 | 1.92 |
| MediQ-GAN | 10 epochs (~80 min) | 0.018 | - | - |
| MediQ-GAN | 25 epochs (196 min) | 0.365 | 3.44 | 0.30 |

- MediQ-GAN matches the average shape better but its diversity is one eighth of the real data, so it repeats similar images. QGAN reproduces shape less well but its diversity is close to real.
- At 16×16 both models stay far from the papers' image quality; the Day 3 notebook shows the papers' samples next to ours.

### Sub-generator sweep (600 steps, depth 10)

| Sub-generators | Qubits | ② Corr. | ④ Diversity | Time |
|---|---|---|---|---|
| 2 | 8 | -0.054 (8 samples) | 1.81 | 17.4 min |
| **4 (adopted)** | 7 | **0.195 ± 0.012** | 1.85 | 22.2 min |
| 8 | 6 | 0.105 ± 0.011 | 2.20 | 34.2 min |
| 16 (paper) | 5 | 0.080 ± 0.004 | 2.40 | 54.9 min |

- With 16, `loss_d` fell to 0.003 and the discriminator won outright; more parameters did not help.
- Fewer sub-generators run faster because circuit calls (sub-generators × batch) dominate the cost.
- The 4-generator diversity (1.85) differs from the results table (1.92) because each evaluation draws fresh noise.

### Training stability

MediQ-GAN with `lr_g` 0.02 collapsed in 3 epochs (`loss_d` 0.0027, diversity 0.000). GAN defaults (`lr` 2e-4, `betas` (0.5, 0.999), `z ~ N(0, 1)`) completed 25 epochs. This is why the paper uses a WGAN-GP critic.

### Reference: CNN augmentation protocol (8×8 stage)

| | Accuracy | AUC |
|---|---|---|
| Before augmentation | 0.946 | 0.970 |
| After augmentation | 0.913 | 0.974 |

With 92 DF images this difference is not an improvement, so the practicals use the four metrics instead. Artifacts are in [`archive/assets_8px/`](../archive/assets_8px/).

## Differences from the papers

| | Paper | This material |
|---|---|---|
| QGAN sub-generators | 16 × (7 data + 1 ancilla) | 4 × (6 data + 1 ancilla) |
| QGAN training | 2,000 epochs (1-1.5 h) | 600 steps (~22 min) |
| Resolution | MediQ-GAN 64×64 RGB | 16×16 grayscale |
| MediQ-GAN quantum stream | 16 qubits × 5, depth 8 | Same |
| MediQ-GAN classical part · discriminator | conv · WGAN-GP critic | MLP · standard BCE |
| Evaluation | FID, classification accuracy/AUC | Four metrics |
| Runtime | GPU | Colab CPU exact simulation |

## Repository layout

```
practice/            for students
  day1_slides/       Day 1 theory (31)
  day2_slides/       Day 2 walkthrough (25)
  day3_slides/       Day 3 walkthrough (11)
  day2_practice.ipynb, day3_practice.ipynb
  gen_metrics.py     the four metrics (shared by Day 2 and 3)
  assets/            16×16 preprocessed data + 3 checkpoints
  docs/image/        notebook screenshots and paper figures
archive/             preparation and reproduction
  prep/              preprocessing notebooks
  train/             checkpoint training CLIs + model modules
  slides/            Day 2 and 3 slide build scripts
  assets_8px/        8×8-era assets
  paper/             paper PDFs + citations
```

## Rebuilding the checkpoints locally

```bash
python -m venv C:/qmlvenv
C:/qmlvenv/Scripts/pip install -r requirements.txt
cd archive/train
# QGAN (~22 min)
C:/qmlvenv/Scripts/python.exe -X utf8 train_qgan_checkpoint.py --npy ../../practice/assets/df_preprocessed.npy --out_dir ../checkpoints --n_generators 4 --epochs 600
# MediQ-GAN (~8 min per epoch)
C:/qmlvenv/Scripts/python.exe -X utf8 train_mediqgan_checkpoint.py --npy ../../practice/assets/df_preprocessed.npy --out_dir ../checkpoints --epochs 25 --save_every 5
```

Kaggle is needed only to regenerate the preprocessed npy (`archive/prep/prep_step1_16px_npy.ipynb`). Copy new checkpoints into `practice/assets/` and the notebooks use them as is. Details in [`archive/README.md`](../archive/README.md).

## Licensing

- Code, docs and slides: [MIT](../LICENSE)
- Data derivatives (`practice/assets/`, `archive/assets_8px/`): inherit HAM10000's CC BY-NC 4.0 (non-commercial)
- Paper PDFs and quoted figures: CC BY 4.0 of each paper. Only the MediQ-GAN PDF and the HAM10000 QGAN author preprint are included (the published version is Springer-licensed); figures in the Day 1 deck and the Day 3 notebook are quoted with attribution. See [`archive/paper/README.md`](../archive/paper/README.md)

## References

1. Andra, M. B., Yuliani, A. R., Kadar, J. A., Ramdan, A. & Pardede, H. F. **Data augmentation in cancer image classification problem with quantum GAN.** *Quantum Machine Intelligence* **7**, 90 (2025). https://doi.org/10.1007/s42484-025-00315-y (preprint: https://doi.org/10.21203/rs.3.rs-5191116/v1)
2. Jiao, Q., Tang, Y., Zhuang, J., Cong, J. & Shi, Y. **MediQ-GAN: Quantum-Inspired GAN for High Resolution Medical Image Generation.** arXiv:[2506.21015](https://arxiv.org/abs/2506.21015) (2025). Official code: https://github.com/QingyueJ-nd/MediQ-GAN
3. Tschandl, P., Rosendahl, C. & Kittler, H. **The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions.** *Scientific Data* **5**, 180161 (2018). https://doi.org/10.7910/DVN/DBW86T
