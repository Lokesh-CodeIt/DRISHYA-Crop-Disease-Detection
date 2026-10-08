# DRISHYA

## Explainable Disease Detection in Turmeric and Citrus Crops Using Deep Learning

DRISHYA is a web-based decision-support system for turmeric (*Curcuma longa*) and citrus (*Citrus* spp.) leaf disease detection. It is built as a responsible AI prototype designed for practical, transparent, and trustworthy disease identification in high-value Indian agricultural crops.

DRISHYA goes beyond simple classification by combining crop-specific deep learning with post-hoc confidence calibration, Grad-CAM visual explanation, uncertainty-based safety rejection, a 22-class deterministic condition knowledge layer, and multilingual support in English, Hindi, and Marathi. It provides safe agricultural guidance backed by source metadata, while explicitly acknowledging the boundary between computational prediction and field-confirmed diagnosis.

> **Academic / Research Prototype — Feature-Complete Demo Build**
>
> Model outputs are decision support, not a substitute for field inspection or qualified agricultural advice.

---

## Key Features

1. **Crop-Specific Deep Learning** — Dedicated ConvNeXt-Tiny (Turmeric) and EfficientNetV2-S (Citrus) pipelines
2. **Confidence Handling** — Calibrated and raw probabilities reported per crop-specific policy
3. **Crop-Specific Calibration** — Temperature Scaling applied selectively; Citrus active, Turmeric inactive (see Calibration)
4. **Uncertainty Rejection** — Predictions below confidence threshold (0.65) are automatically rejected and routed to expert confirmation messaging
5. **Grad-CAM Explainability** — Visual heatmaps highlighting which image regions influenced the prediction
6. **Attention-Region Inspection** — Real crops of high-activation image regions extracted and displayed
7. **22-Class Condition Knowledge** — Deterministic knowledge lookup with source metadata for every recognized condition
8. **Safe Advisory Layer** — Source-backed cultural, organic, and management guidance; no dynamically generated pesticide prescriptions or dosages
9. **Multilingual Support** — English / Hindi / Marathi via `i18next`
10. **User Authentication + History** — BCrypt-hashed accounts, JWT session cookies, prediction history per user
11. **CPU Inference** — Native PyTorch CPU inference; no GPU required for deployment
12. **Responsive Web Application** — React + Vite frontend with GSAP animations

---

## Current Models

### Turmeric
| Property | Value |
|---|---|
| Architecture | ConvNeXt-Tiny |
| Classes | 4 (Healthy, Dry Leaf, Leaf Blotch, Leaf Spot) |
| Input Resolution | 224 × 224 |
| Active Seed | 42 |
| Checkpoint | `ml/models/turmeric/convnext_tiny/seed_42/best_model.pt` |

### Citrus
| Property | Value |
|---|---|
| Architecture | EfficientNetV2-S |
| Classes | 18 |
| Input Resolution | 384 × 384 |
| Active Seed | 42 |
| Checkpoint | `ml/models/citrus/efficientnet_v2_s/seed_42/best_model.pt` |

> **Note:** Only Seed 42 is currently active. No multi-seed ensemble or mean ± SD statistics are claimed.

---

## Final Results

Results are from Seed 42 test evaluation.

### Turmeric — Internal Test Set

| Metric | Value |
|---|---|
| Accuracy | **98.92%** |
| Macro Precision | 0.9921 |
| Macro Recall | 0.9875 |
| Macro F1 | 0.9897 |

### Citrus — Internal Test Set

| Metric | Value |
|---|---|
| Accuracy | **92.73%** |
| Macro Precision | 0.8822 |
| Macro Recall | 0.8915 |
| Macro F1 | 0.8863 |

---

## Calibration

DRISHYA uses **crop-specific Temperature Scaling** (post-hoc calibration):

### Turmeric — Calibration Inactive
- Temperature `T = 0.101698` artifact retained for reproducibility
- Calibration is **not applied** for farmer-facing inference
- **Reason:** The validation split had zero classification errors, causing a pathological sharpening of an already near-perfect model. Applying this T would produce overconfident calibrated probabilities that are less informative than the raw model output.
- Turmeric inference displays raw softmax confidence.

### Citrus — Calibration Active
- Temperature `T = 2.218093`
- Calibration is **applied** for farmer-facing inference
- ECE improvement: Validation `0.062936 → 0.032162` | Test `0.058998 → 0.026995`
- Citrus inference displays calibrated probability

---

## Explainability

DRISHYA uses **Grad-CAM** (Gradient-weighted Class Activation Mapping):

- **Target layer:** `features.7` (the final feature block in both ConvNeXt-Tiny and EfficientNetV2-S)
- Predicted-class logits are used to generate the gradient signal
- Model parameters remain frozen during Grad-CAM generation
- Real attention-region crops are extracted from the input image using the heatmap

> **Scientific caveat:** Grad-CAM is supporting visual evidence, not proof of biological causation. It shows which image regions statistically influenced the model's decision. Quantitative lesion localization metrics are not claimed.

22-class Grad-CAM validation (all 22 supported conditions produce valid overlays): documented in `docs/explainability_22_class_validation.md`.

---

## Cross-Dataset Evaluation

### Citrus

| Evaluation | Accuracy | Macro F1 |
|---|---|---|
| Internal test set | 92.73% | 0.8863 |
| External (held-out) dataset | 66.01% | 0.4892 |
| **Macro F1 drop** | — | **44.8%** |

This demonstrates significant **domain shift** between training and external field conditions. Citrus external evaluation used a geographically distinct, separately held-out dataset not seen during training or validation.

### Turmeric
Cross-dataset evaluation is **not available** for the current combined-pool model. A valid source-isolated experiment was not performed. This is documented as a known limitation.

---

## Condition Knowledge

- **22 active classes** covered (4 turmeric + 18 citrus)
- **Deterministic lookup** — no dynamic text generation
- Source metadata included for each condition
- Safe agricultural guidance provided; no dynamically generated pesticide dosages or application schedules
- Predictions below the uncertainty threshold receive expert-confirmation messaging
- Fully documented in `docs/CONDITION_KNOWLEDGE.md`

---

## Safety & Responsible AI

- Model predictions are **not** field-confirmed diagnoses
- Confidence values reflect model certainty, **not** biological certainty
- Predictions below `0.65` confidence are automatically rejected
- No dynamically generated pesticide prescriptions are provided
- All advisory content is source-backed and deterministic
- User prediction history is stored locally (SQLite) and protected per-user
- Local agricultural expert confirmation is strongly recommended when predictions are uncertain

---

## System Architecture

```
User
  ↓
React Frontend (Vite, i18next, GSAP)
  ↓
FastAPI Backend
  ↓
Image Validation & Preprocessing
  ↓
Crop-Specific PyTorch Model
  ↓
Raw Softmax Probability
  ↓
Calibration Policy (Crop-Specific)
  ↓
Uncertainty Gate (threshold 0.65)
  ↓
Grad-CAM + Region Extraction
  ↓
Condition Knowledge Lookup
  ↓
Final Result (prediction + confidence + heatmap + knowledge + history)
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite 5, i18next / react-i18next, GSAP |
| Backend | FastAPI, Pydantic v2, Uvicorn |
| ORM & DB | SQLAlchemy 2.0, SQLite |
| Authentication | BCrypt, python-jose (JWT), HttpOnly cookie |
| ML Framework | PyTorch 2.x, torchvision |
| CV & Data | OpenCV, Pillow, scikit-learn, NumPy |
| Explainability | Grad-CAM (custom implementation) |

---

## Project Structure

```
DRISHYA-Crop-Disease-Detection/
├── backend/
│   └── app/
│       ├── main.py                  # FastAPI entrypoint & CORS
│       ├── api/                     # API routers (/diagnose, /advisories, /health, /auth)
│       ├── auth/                    # BCrypt + JWT authentication
│       ├── calibration/             # Temperature Scaling
│       ├── db/                      # SQLAlchemy models, database init, repository
│       ├── explainability/          # Grad-CAM, region extractor, renderer
│       ├── knowledge/               # Condition knowledge service & JSON
│       ├── ml/                      # Model builder & registry
│       ├── models/                  # Pydantic schemas
│       ├── preprocessing/           # Image validation & normalization pipeline
│       ├── services/                # Diagnosis & inference orchestration
│       └── utils/                   # Configuration (pydantic-settings)
├── frontend/
│   ├── src/
│   │   ├── components/              # React components (Home, Analysis, Result, Auth, Journal)
│   │   ├── context/                 # AuthContext, LanguageContext
│   │   ├── locales/                 # en.json, hi.json, mr.json
│   │   ├── services/                # API client modules
│   │   └── utils/                   # Formatters
│   ├── public/                      # Logo assets
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── ml/
│   ├── models/                      # Active production checkpoints (Git LFS)
│   │   ├── turmeric/convnext_tiny/seed_42/best_model.pt
│   │   └── citrus/efficientnet_v2_s/seed_42/best_model.pt
│   ├── calibration/                 # Temperature parameters & calibration reports
│   ├── configs/                     # Training YAML configs
│   ├── scripts/                     # ML pipeline scripts (train, calibrate, evaluate, explain)
│   └── datasets/                    # Gitkeep placeholders (datasets not committed)
├── TESTING/
│   ├── turmeric/                    # Curated test images per class
│   ├── citrus/                      # Curated test images per class
│   ├── edge_cases/                  # Low-light, blurry, non-leaf edge case images
│   ├── README.md
│   └── testing_manifest.csv
├── tests/
│   ├── test_calibration.py
│   ├── test_explainability.py
│   ├── test_inference.py
│   ├── test_condition_knowledge.py
│   ├── test_auth.py
│   ├── test_database.py
│   ├── test_localization.py
│   ├── verify_step_c_real_responses.py
│   └── smoke_validation_22class.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATASETS.md
│   ├── EXPERIMENTS.md
│   ├── MODEL_CARD.md
│   ├── CALIBRATION.md
│   ├── EXPLAINABILITY.md
│   ├── CONDITION_KNOWLEDGE.md
│   ├── DEPLOYMENT.md
│   ├── SECURITY.md
│   └── LIMITATIONS.md
├── data/
│   ├── metadata/                    # Curation manifests & split CSVs
│   └── reports/                     # Phase reports, class mappings, split validation
├── advisory/
│   └── disease_advisories.json      # Vetted advisory registry
├── database/
│   └── .gitkeep                     # SQLite DB created locally at runtime (not committed)
├── .env.example                     # Environment template (no real secrets)
├── .gitattributes                   # Git LFS tracking for *.pt
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git with Git LFS installed (`git lfs install`)

### 1. Clone Repository

```bash
git clone https://github.com/Lokesh-CodeIt/DRISHYA-Crop-Disease-Detection.git
cd DRISHYA-Crop-Disease-Detection
git lfs pull
```

### 2. Create Python Environment

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env and set AUTH_SECRET_KEY to a strong random string
```

### 5. Start FastAPI Backend

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Backend will be available at: `http://127.0.0.1:8000`
API documentation: `http://127.0.0.1:8000/docs`

### 6. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 7. Start Vite Development Server

```bash
npm run dev
```

Frontend will be available at: `http://localhost:5173`

---

## Running the Application

**Backend:**
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

**Frontend:**
```bash
cd frontend && npm run dev
```

The frontend proxies `/api` requests to the backend automatically via `vite.config.js`.

---

## Testing

All tests require a running or importable backend (models must be available via Git LFS).

```bash
# Core test suite
python -m pytest tests/test_calibration.py -v
python -m pytest tests/test_explainability.py -v
python -m pytest tests/test_inference.py -v
python -m pytest tests/test_condition_knowledge.py -v

# Step C real-response verification
python tests/verify_step_c_real_responses.py

# Frontend build verification
cd frontend && npm run build
```

**Verified passing (Seed 42 checkpoint):** 73 / 73 tests pass.

---

## Dataset & Model Artifact Policy

Large raw datasets and backup archives are **intentionally not committed** to this repository.

| Artifact | Status |
|---|---|
| Raw dataset ZIPs (>7 GB total) | Not committed — place locally in `DATASET/` |
| Colab backup archives | Not committed |
| Active model checkpoints (`*.pt`) | Tracked via **Git LFS** |
| Calibration artifacts (`.json`) | Committed |
| Split manifests (`.csv`) | Committed |
| TESTING images | Committed (curated small set) |

**Model checkpoints** require Git LFS: `git lfs pull` after cloning.

Expected local dataset directory structure (not committed):
```
DATASET/
├── Image Dataset for Turmeric Plant Leaf Disease Detection.zip
├── Turmeric Plant Disease Dataset Advancing AI for Agricultural Sustainability.zip
├── Turmeric Plant Disease (1).zip
├── Large-Scale Lemon Leaf Disease and Pest Image Data.zip
└── A Citrus Fruits and Leaves Dataset for Detection and Classification of Citrus Diseases through Machine Learning.zip
```

---

## Completed Development Stages

| Stage | Status |
|---|---|
| A — Confidence Calibration (crop-specific Temperature Scaling) | ✅ Complete |
| B — Grad-CAM Explainability | ✅ Complete |
| B.1 — 22-Class Grad-CAM Validation | ✅ Complete |
| C — Result Screen Redesign | ✅ Complete |
| C.1 — Calibration Safety Policy | ✅ Complete |
| D — Condition Knowledge & Safe Advisory Layer | ✅ Complete |

---

## Limitations

- Only **Seed 42** is currently active; no multi-seed mean ± SD statistics are available
- **Turmeric cross-dataset evaluation** is not available for the current combined-pool model
- Quantitative lesion-level **Grad-CAM localization metrics** (IoU, etc.) are not claimed
- **Citrus external performance** shows significant domain shift (Macro F1 drop of 44.8%)
- System output is **decision support**, not a confirmed field diagnosis

---

## Future Scope

- Support for additional crops (rice, wheat, banana)
- Geographically diverse field image collection and retraining
- Disease severity estimation
- Offline / mobile deployment (TFLite, ONNX)
- Farmer feedback loop for active learning
- Field-scale monitoring integration (drone / satellite)
- Stronger external cross-dataset validation

---

## Academic Disclaimer

DRISHYA is an academic and research prototype for plant-health decision support. Model outputs are **not** a substitute for field inspection or qualified agricultural advice. Predictions should be verified by a local agricultural extension officer or subject-matter expert before any field intervention.

---

## License

License: Not yet specified.
