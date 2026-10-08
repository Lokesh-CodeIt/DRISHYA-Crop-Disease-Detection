# LeafLens: Google Colab Training Guide

This self-contained package allows full reproduction of the **LeafLens** multi-seed training experiments in Google Colab on GPU (NVIDIA T4 or A100).

---

## Step 1: Upload & Unzip in Colab

In Google Colab, create a new notebook, select **Runtime > Change runtime type > T4 GPU**, and run:

```bash
# Upload CROP_DETECTION_COLAB_READY.zip to Colab files or Google Drive, then:
!unzip -q /content/CROP_DETECTION_COLAB_READY.zip -d /content/
%cd /content/CROP_DETECTION
```

---

## Step 2: Install Dependencies & Verify Setup

```bash
!pip install -q -r requirements.txt
!python colab_setup.py
```

This verifies:
- GPU device recognition (CUDA available)
- Integrity of all 4 dataset ZIP archives
- Integrity and row counts of all 7 split CSV files
- ZIP-native image loader functionality
- ConvNeXt-Tiny & EfficientNetV2-S model builders

---

## Step 3: Run Smoke Test

Run a fast forward/backward verification on actual batches from both crops:

```bash
!python ml/scripts/train_pipeline.py --smoke-test
```

---

## Step 4: Execute Experiments

### Option A: Run Full Sequence (Recommended for overnight GPU execution)
Runs all 6 experiments sequentially (Turmeric seeds 42, 123, 7 then Citrus seeds 42, 123, 7):

```bash
!python ml/scripts/train_pipeline.py --run-all
```

### Option B: Run Experiments Individually

**Turmeric (ConvNeXt-Tiny, 4 classes, 224×224, 50 epochs, batch 16):**
```bash
!python ml/scripts/train_pipeline.py --crop turmeric --seed 42
!python ml/scripts/train_pipeline.py --crop turmeric --seed 123
!python ml/scripts/train_pipeline.py --crop turmeric --seed 7
```

**Citrus (EfficientNetV2-S, 18 classes, 384×384, 40 epochs, batch 32):**
```bash
!python ml/scripts/train_pipeline.py --crop citrus --seed 42
!python ml/scripts/train_pipeline.py --crop citrus --seed 123
!python ml/scripts/train_pipeline.py --crop citrus --seed 7
```

---

## Output Artifacts

All training artifacts are saved to:
```
ml/experiments/{crop}/{model}/seed_{seed}/
  ├── best_model.pt               # Best checkpoint by validation Macro F1
  ├── final_model.pt              # Checkpoint at final epoch
  ├── training_history.csv        # Per-epoch losses and metrics
  └── experiment_summary.json     # Full evaluation metrics and confusion matrix
```
Additionally, `ml/experiments/experiment_summary.csv` aggregates metrics across all executed runs.
