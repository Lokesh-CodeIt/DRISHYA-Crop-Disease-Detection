# DRISHYA — Manual Website Testing Folder

## Purpose

This folder contains a **small, curated set of real images** for **manually testing and demonstrating the DRISHYA website only**.

It is **NOT** part of any training, validation, retraining, or model-update pipeline.

---

## Important — Data Integrity

| Rule | Status |
|---|---|
| Images are **copies** from the original ZIPs | ✅ |
| Original datasets are **untouched** | ✅ |
| No original file was moved or deleted | ✅ |
| Model checkpoints are **untouched** | ✅ |
| Training / validation manifests are **untouched** | ✅ |
| No synthetic or AI-generated images | ✅ |
| No external downloads | ✅ |

---

## Folder Structure

```
TESTING/
├── README.md                   ← this file
├── testing_manifest.csv        ← expected labels for every test image
│
├── turmeric/
│   ├── healthy/                (3 images — TUR_healthy_01..03.jpg)
│   ├── dry_leaf/               (3 images)
│   ├── leaf_blotch/            (3 images)
│   └── leaf_spot/              (3 images)
│
├── citrus/
│   ├── healthy/                (3 images)
│   ├── algal_leaf_spot/        (3 images)
│   ├── anthracnose/            (3 images)
│   ├── bacterial_blight/       (3 images)
│   ├── black_spot/             (3 images)
│   ├── citrus_canker/          (3 images)
│   ├── citrus_hindu_mite/      (3 images)
│   ├── citrus_leafminer/       (3 images)
│   ├── citrus_pest/            (3 images)
│   ├── citrus_scab/            (3 images)
│   ├── curl_leaf/              (3 images)
│   ├── dry_leaf/               (3 images)
│   ├── greening/               (3 images)
│   ├── lemon_sooty_mold/       (3 images)
│   ├── melanose/               (3 images)
│   ├── spider_mites/           (3 images)
│   ├── swallowtail_larval_herbivory_deficiency/ (3 images)
│   └── yellow_spot/            (3 images)
│
└── edge_cases/
    ├── low_light/              (2 images — genuinely darker exposures)
    ├── blurry/                 (2 images — low Laplacian sharpness variance)
    ├── heavy_background/       (2 images — large non-leaf area in frame)
    ├── poor_composition/       (1 image — leaf heavily cut at border)
    ├── non_leaf/               (2 images — turmeric rhizome + citrus fruit)
    ├── multiple_leaves/        ← NOT_AVAILABLE.txt (no suitable source found)
    └── unsupported_crop/       ← NOT_AVAILABLE.txt (no other crop in dataset)
```

**Total images: 75** (12 turmeric + 54 citrus + 9 edge cases)

---

## Image Naming Convention

| Prefix | Meaning |
|---|---|
| `TUR_<class>_NN.jpg` | Turmeric leaf — known ground-truth class |
| `CIT_<class>_NN.jpg` | Citrus leaf — known ground-truth class |
| `EDGE_<category>_NN.jpg` | Edge-case image for website behaviour testing |

---

## testing_manifest.csv

Every image in this folder (except unavailable edge cases) has a row in `testing_manifest.csv`.

| Column | Description |
|---|---|
| `test_id` | Unique identifier for this test image |
| `crop` | `turmeric` or `citrus` (or `unknown` for some edge cases) |
| `expected_class` | The known ground-truth disease / condition class |
| `source_dataset` | Which dataset ZIP this image came from |
| `source_path` | The original virtual ZIP path |
| `original_filename` | The original filename inside the archive |
| `purpose` | Human-readable description of the test scenario |

> **Note:** For edge-case images, `expected_class` may be empty. These images do not
> necessarily have a meaningful ML prediction — they test **website robustness**, not model accuracy.

---

## Image Source Policy

All test images were selected from the **held-out test split** (`data/metadata/splits/*_test.csv`).
They were **not used during model training or validation**.

Images were identified by:
- Known ground-truth class label in the split manifest
- Clear, non-augmented, non-duplicate originals preferred
- Edge cases identified via automated brightness (mean pixel intensity) and
  sharpness (Laplacian variance) analysis across 250 sampled test images

---

## Step-by-Step Website Testing Guide

### Prerequisites

1. **Start the backend server:**
   ```
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
   ```

2. **Start the frontend development server:**
   ```
   npm --prefix frontend run dev
   ```

3. **Open browser:** [http://localhost:5173](http://localhost:5173)

---

### Testing Workflow

```
Step 1 — Login
   Open the DRISHYA welcome page.
   Register or log in with a test account.

Step 2 — Select Crop
   On the Home screen, tap or click the crop card:
   → "Turmeric" for turmeric test images
   → "Citrus" for citrus test images

Step 3 — Open "Check a Leaf"
   Click the "Check a Leaf" button or card.

Step 4 — Upload Image
   Click "Upload" or drag-and-drop a test image from this TESTING/ folder.
   Use the image filename to identify the class from testing_manifest.csv.

Step 5 — Start Analysis
   Click "Analyse" / "Check Now".
   Watch the analysis animation.

Step 6 — Read the Result
   Note the predicted condition displayed on the Result screen.

Step 7 — Compare with Manifest
   Open testing_manifest.csv.
   Find the row matching your test image's test_id.
   Compare the website's prediction with the expected_class column.

Step 8 — (Optional) Check Journal
   Confirm the scan is saved in My Leaf Journal.
```

---

### Edge Case Testing

Upload images from `TESTING/edge_cases/` to observe website behaviour when:

| Category | What to check |
|---|---|
| `low_light` | Does the website handle darker images without crashing? |
| `blurry` | Does the model still return a result (even if lower confidence)? |
| `heavy_background` | Is the result displayed gracefully? |
| `poor_composition` | Does the upload and analysis complete without error? |
| `non_leaf` | Does the model return any class? (expected: unspecified / low confidence) |

> **Important:** Edge-case images do **not** have a guaranteed correct ML prediction.
> The goal is to verify that the **website does not crash** and **displays a response gracefully**.

---

## Classes Reference

### Turmeric (4 classes)
- Healthy
- Dry Leaf
- Leaf Blotch
- Leaf Spot

### Citrus (18 classes)
- Algal_Leaf_Spot
- Anthracnose
- Bacterial Blight
- Black Spot
- Citrus Canker
- Citrus Hindu Mite
- Citrus Leafminer
- Citrus_Pest
- Citrus_Scab
- Curl Leaf
- Dry Leaf
- Greening
- Healthy
- Lemon_Sooty_Mold
- Melanose
- Spider Mites
- Swallowtail Larval Herbivory (Deficiency)
- Yellow_Spot

---

## Unavailable Edge Cases

The following edge-case categories were **not populated** because no suitable images
exist in the current DRISHYA dataset:

- **`multiple_leaves`** — No images with clearly distinct multiple leaves in frame were found in the test splits after automated scanning.
- **`unsupported_crop`** — The current DRISHYA dataset contains only Turmeric and Citrus images. No other crop types are present in the project.

Per project rules, **no external downloads** and **no synthetic / AI-generated images**
were used to fill these gaps.

---

*Generated automatically by `ml/scripts/create_testing_folder.py`.*
*DRISHYA — Crop Disease Detection System.*
