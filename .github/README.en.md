# Quantum Generative Models for Dermatoscopic Images - QGAN / MediQ-GAN

A hands-on implementation of the **full quantum-GAN data-augmentation pipeline** for medical imaging - EDA, segmentation-based preprocessing, quantum encoding, training, evaluation, and a classical baseline - built so that **two notebooks run end to end on Google Colab's free CPU runtime**.

> [한국어](README.md) | **English**

The core of the material is a side-by-side comparison of two different hybrid strategies - **model-level** and **layer-level** - on the same data under the same metrics.

## At a glance

| | |
|---|---|
| **Dataset** | HAM10000 (10,015 dermatoscopic images); 115 DF + 345 NV images, segmented with K-means + Fuzzy C-means and reduced to 16×16 grayscale |
| **Model ①** | Patch QGAN (model-level hybrid) - 4 sub-generators × 7 qubits (6 data + 1 ancilla), depth 10, patch size 64 |
| **Model ②** | MediQ-GAN (layer-level hybrid) - dual-stream generator: classical stream + quantum stream (5 × 16 qubits, depth 8) |
| **Discriminator** | Shared by both models - the 5-layer fully connected classifier from Table 4 of the QGAN paper |
| **Stack** | PennyLane (`default.qubit` / `lightning.qubit` + `adjoint`), PyTorch, scikit-fuzzy, OpenCV |
| **Runtime** | Google Colab default CPU runtime - no local install, no GPU, no quantum-hardware account |
| **Evaluation** | Four lightweight generation-quality metrics (pixel statistics, class-mean correlation, nearest-real distance, sample diversity) |
| **License** | MIT for code and docs; CC BY-NC 4.0 for data derivatives (see [Licensing](#licensing)) |
| **Deliverables** | 31 theory slides, Day 2 and Day 3 walkthrough slides (25 and 23), 2 practice notebooks, 3 pretrained checkpoints, a metrics module, and reproduction CLIs |

### Design principles

1. **Never shrink the quantum circuit spec.** Cutting qubit count or depth to save time would mean no longer running the model the papers describe, so **image resolution and training budget** were reduced instead (MediQ-GAN's quantum stream is exactly the published spec).
2. **Put everything on one scale before comparing.** QGAN outputs probabilities (each patch sums to 0-1), MediQ-GAN outputs Tanh values (-1 to 1), and the preprocessed data is 0-1. All three are mapped back to 0-1 by a shared helper before any metric is computed; skip that and the difference between the models disappears into a scale artifact. One limitation remains in QGAN training itself: real images are normalised per image (sum = 1) while generated images are normalised per patch (sum 0-4 per image), so the discriminator can tell them apart by total intensity alone. Section 5 of the day-2 notebook documents this.
3. **Document failures and limits.** Every deviation from the papers, every configuration whose quality collapsed, and everything the metrics cannot tell us is stated in the material itself.

## Open the material

| Day | Content | Link |
|---|---|---|
| Day 1 | Theory - dataset, both architectures, published quantitative results, how VQCs train (parameter-shift rule, cost scaling), research directions in QML | [slides pptx](../practice/day1_slides/day1_theory_slides.pptx) · [pdf](../practice/day1_slides/day1_theory_slides.pdf) |
| Day 2 | EDA · segmentation · quantum encoding · **live QGAN training → generation → evaluation** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hyunhp/skin_disease_qml/blob/main/practice/day2_practice.ipynb) · [walkthrough slides pptx](../practice/day2_slides/day2_practice_slides.pptx) · [pdf](../practice/day2_slides/day2_practice_slides.pdf) |
| Day 3 | **MediQ-GAN fine-tuning** → comparison with QGAN under the same metrics → limits of quantum computing for generative models | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hyunhp/skin_disease_qml/blob/main/practice/day3_practice.ipynb) · [walkthrough slides pptx](../practice/day3_slides/day3_practice_slides.pptx) · [pdf](../practice/day3_slides/day3_practice_slides.pdf) |

Run `File → Save a copy in Drive` first so your outputs persist. At runtime each notebook clones this repository to load the preprocessed data and checkpoints in [`practice/assets/`](../practice/assets/) along with [`practice/gen_metrics.py`](../practice/gen_metrics.py). Only the raw HAM10000 archive (~6 GB) is fetched separately, via `kagglehub`.

## The two architectures

|  | QGAN (Andra et al., 2025) | MediQ-GAN (Jiao et al., 2025) |
|---|---|---|
| Hybrid level | **Model level** - the whole generator is a quantum circuit | **Layer level** - classical and quantum streams run in parallel inside the generator |
| Generation | Sub-generators each produce a patch; patches are concatenated | Input features are split in half, processed separately, then fused by a skip connection |
| Measurement / output | Measure all qubits, keep only the ancilla = 0 outcomes (post-selection) → probability scale | Per-qubit PauliX expectation → 1×1 conv projection → MLP decoder → Tanh |
| How it is trained in class | **From scratch during the session** (400 steps, ~35 min measured on Colab; the instructor checkpoint is 600 steps, ~22 min on a local CPU) | **Fine-tuned from a pretrained checkpoint** (full training exceeds 3 hours because 16-qubit simulation is expensive) |

## Evaluation design

**FID is deliberately not used.** At 16×16 the Inception features it relies on are meaningless (the MediQ-GAN paper works at 64×64 RGB), and the sample sizes here are in the hundreds. Four interpretable metrics are implemented in [`practice/gen_metrics.py`](../practice/gen_metrics.py) and imported by both notebooks.

| Metric | What it checks | How to read it |
|---|---|---|
| ① Pixel-intensity statistics and histogram | Does the brightness distribution match the real data? | Also inspected **before** rescaling - the scale difference itself reveals a structural difference between the models |
| ② Correlation with the class-mean image | Is the overall lesion shape reproduced? | Higher is better. Sensitive to sample count, so fixed at 64 samples for QGAN and 16 for MediQ-GAN |
| ③ L2 distance to the nearest real image | Is the model memorizing the training set? | Values near 0 indicate memorization |
| ④ Pairwise sample distance (diversity) + loss curves | Is it generating the same image over and over? | Values near 0 indicate mode collapse; real DF data scores 2.505 |

## Results

Measured on a local CPU with PennyLane exact state-vector simulation. Generative models draw fresh noise on every call, so read the **gap between models** rather than the decimals.

| Model | Training budget | ② Class-mean correlation ↑ | ③ Nearest-real distance | ④ Sample diversity (real: 2.505) |
|---|---|---|---|---|
| QGAN 16×16 | 600 steps (~22 min) | **0.195 ± 0.012** (64 samples × 10 seeds) | 1.64 | 1.92 |
| MediQ-GAN, 10 epochs (fine-tuning start point) | ~80 min | 0.018 | - | - |
| MediQ-GAN, 25 epochs (final) | 196 min | **0.365** | 3.44 | 0.30 |

- **MediQ-GAN matches the "average lesion shape" far better (0.365 vs 0.195), but its sample diversity is roughly one eighth of the real data (0.30 vs 2.505)** - it keeps producing near-identical images. QGAN reproduces shape less well yet stays much closer to the real distribution in diversity (1.92). Answering "which is the better generative model?" requires both numbers, which is exactly the day-3 discussion.
- Both models sit above 1.6 on nearest-real distance, so neither is simply replaying memorized training images.
- Re-scoring the earlier 8×8 checkpoint (depth 4, 300 steps) with the same metrics gives 0.242, but its resolution and sampling conditions differ, so it is not compared directly against the table above.

### Sub-generator sweep - more parameters did not help

The QGAN sub-generator count was swept over 2, 4, 8 and 16 and retrained under **identical conditions (600 steps, depth 10)**. More sub-generators means more parameters per pixel, yet quality was not monotonic.

| Sub-generators | Qubits | Parameters per pixel | ② Class-mean correlation | ④ Diversity | Wall clock |
|---|---|---|---|---|---|
| 2 | 8 | 0.62 | -0.054 (8 samples) | 1.81 | 17.4 min |
| **4 (adopted)** | 7 | 1.09 | **0.195 ± 0.012** | 1.85 | 22.2 min |
| 8 | 6 | 1.88 | 0.105 ± 0.011 | 2.20 | 34.2 min |
| 16 (as in the paper) | 5 | 3.12 | 0.080 ± 0.004 | 2.40 | 54.9 min |

- In the largest configuration `loss_d` fell to 0.003: **the discriminator won outright and the generator lost its training signal.** A concrete demonstration that adding capacity can tip the GAN balance.
- Fewer sub-generators being **faster** is not a bug - the number of circuit evaluations (`sub-generators × batch`) dominates cost more than state-vector size (2ⁿ).
- Two sub-generators were chosen first, because that configuration matches the paper's qubit count and patch size exactly - and it scored worst. **Measurement was given priority over spec parity** and the adopted setting is four.
- The diversity for the same 4-sub-generator setting differs from the results table (1.92) because every generation call draws fresh noise (separate evaluation runs).

### Training stability - the discriminator winning within 3 epochs

Pretraining MediQ-GAN with a large, QGAN-style learning rate (`lr_g` 0.02) **collapsed within 3 epochs: `loss_d` 0.0027 and sample diversity 0.000** (complete mode collapse). Because MediQ-GAN's final output comes from a classical MLP decoder, a saturated Tanh produces a constant image unrelated to the latent vector.

Switching to conventional GAN settings (`lr` 2e-4, `betas` (0.5, 0.999), `z ~ N(0,1)`) completed 25 epochs without collapse. That recipe is stored inside the checkpoints so the notebook fine-tunes under identical conditions. This is the published motivation for MediQ-GAN's **WGAN-GP critic** - the instability of standard GAN training - reproduced first-hand, so it is kept in the material as a discussion point.

### Appendix - reproducing the paper's evaluation protocol (CNN augmentation)

The original paper evaluates generation quality by classification performance before and after augmentation. That protocol was reproduced at the 8×8 stage: a CNN trained on 92 real DF images plus 184 synthetic ones, evaluated on a held-out split (23 DF / 69 NV).

| | Accuracy | AUC |
|---|---|---|
| Before augmentation | 0.946 | 0.970 |
| After augmentation | 0.913 | **0.974** |

AUC rose by 0.004 while accuracy fell. At a sample size of 92 that difference cannot be called an improvement, so the classroom evaluation was switched from a CNN to the four metrics above; the theory session presents the published figures together with this caveat. The artifacts are preserved in [`archive/assets_8px/`](../archive/assets_8px/).

## Differences from the original papers (stated in class as well)

The code is a **scaled-down teaching implementation**, not a reproduction.

| | Original papers | This material |
|---|---|---|
| QGAN sub-generators | 16 × (7 data + 1 ancilla qubits) | 4 × (6 data + 1 ancilla) - chosen empirically |
| QGAN training budget | 2,000 epochs (1-1.5 h) | 600 steps (~22 min) |
| Resolution | MediQ-GAN: 64×64 RGB | 16×16 grayscale |
| MediQ-GAN quantum stream | 5 × 16 qubits, depth 8 | **identical** |
| MediQ-GAN classical part | conv encoder/decoder | MLP |
| MediQ-GAN discriminator | **WGAN-GP critic** | standard BCE discriminator (see "Training stability") |
| Metrics | FID, classification accuracy / AUC | pixel statistics, class-mean correlation, nearest-real distance, diversity |
| Hardware | GPU | Colab CPU, exact simulation (no shot noise, no hardware error) |

## Repository layout

```
practice/                      For students - the only folder opened in class
  day1_slides/                 Day 1 theory slides (pptx + pdf, 31 slides)
  day2_slides/                 Day 2 walkthrough slides (pptx + pdf, 25 slides)
  day3_slides/                 Day 3 walkthrough slides (pptx + pdf, 23 slides)
  day2_practice.ipynb          Day 2 - EDA, preprocessing, encoding, QGAN training
  day3_practice.ipynb          Day 3 - MediQ-GAN fine-tuning, comparison with QGAN
  gen_metrics.py               The four generation-quality metrics (shared module)
  assets/                      16x16 preprocessed data + 3 pretrained checkpoints (~1 MB)
  docs/image/                  Screenshots of the Kaggle API token flow

archive/                       Preparation and provenance material
  prep/                        Notebooks that regenerate the preprocessed data / rehearse code
  train/                       Checkpoint-training CLIs plus model and preprocessing modules
  assets_8px/                  8x8-era artifacts, including the CNN augmentation study
  paper/                       Paper PDFs, citations, licensing, implementation-difference table

requirements.txt               Packages for local runs
LICENSE                        MIT for code and docs, with the data/paper carve-outs
```

## Reproducing locally

The classroom flow needs nothing but Colab; rebuilding the checkpoints follows the chain below (steps ② and ③ need no Kaggle account).

```bash
python -m venv C:/qmlvenv
C:/qmlvenv/Scripts/pip install -r requirements.txt
```

① **(Colab, Kaggle required)** Regenerate the 16×16 preprocessed `.npy` files from HAM10000: `archive/prep/prep_step1_16px_npy.ipynb`

② QGAN checkpoint (~22 min)

```bash
cd archive/train
C:/qmlvenv/Scripts/python.exe -X utf8 train_qgan_checkpoint.py --npy ../../practice/assets/df_preprocessed.npy --out_dir ../checkpoints --n_generators 4 --epochs 600
```

③ MediQ-GAN pretraining (~8 min per epoch, intermediate checkpoint every 5 epochs)

```bash
C:/qmlvenv/Scripts/python.exe -X utf8 train_mediqgan_checkpoint.py --npy ../../practice/assets/df_preprocessed.npy --out_dir ../checkpoints --epochs 25 --save_every 5
```

Copy the resulting checkpoints into `practice/assets/` and the notebooks pick them up unchanged. See [`archive/README.md`](../archive/README.md) for details.

## Licensing

- **Code and documentation: [MIT](../LICENSE)** - notebooks, Python modules, CLI scripts, README files and the lecture slides. Free to use, including commercially, as long as the notice is kept.
- **Data derivatives: CC BY-NC 4.0** - the preprocessed `.npy` files and checkpoints in `practice/assets/`, and everything in `archive/assets_8px/`, are derived from HAM10000 and inherit its **non-commercial** terms. MIT does not apply to them.
- **Paper PDFs**: governed by each paper's CC BY 4.0 terms (see [`archive/paper/README.md`](../archive/paper/README.md)).

### Sources

- The **HAM10000** images (~6 GB) are not redistributed here; the day-2 notebook downloads them with `kagglehub`. The dataset itself is **CC BY-NC 4.0**, so anything built from it - including the preprocessed data and checkpoints - is for education and research only.
- The **MediQ-GAN** paper (arXiv:2506.21015) is CC BY 4.0, so its PDF is included in [`archive/paper/`](../archive/paper/).
- The **HAM10000 QGAN** paper cannot be included because the published version is under an exclusive Springer Nature license; the **CC BY 4.0 author preprint** (Research Square rs-5191116v1) is provided instead. Cite the published version.
- The MediQ-GAN figure in the slides is quoted from the paper (CC BY 4.0) with attribution; all other diagrams were redrawn from the papers' descriptions.

## References

1. Andra, M. B., Yuliani, A. R., Kadar, J. A., Ramdan, A. & Pardede, H. F. **Data augmentation in cancer image classification problem with quantum GAN.** *Quantum Machine Intelligence* **7**, 90 (2025). https://doi.org/10.1007/s42484-025-00315-y
   (CC BY 4.0 preprint: Research Square, https://doi.org/10.21203/rs.3.rs-5191116/v1 )
2. Jiao, Q., Tang, Y., Zhuang, J., Cong, J. & Shi, Y. **MediQ-GAN: Quantum-Inspired GAN for High Resolution Medical Image Generation.** arXiv:[2506.21015](https://arxiv.org/abs/2506.21015) (2025). Official implementation: https://github.com/QingyueJ-nd/MediQ-GAN
3. Tschandl, P., Rosendahl, C. & Kittler, H. **The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions.** *Scientific Data* **5**, 180161 (2018). https://doi.org/10.7910/DVN/DBW86T
