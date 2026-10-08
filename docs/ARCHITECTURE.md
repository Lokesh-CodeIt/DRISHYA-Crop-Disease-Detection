# DRISHYA — System Architecture

## Overview

DRISHYA is a layered web application consisting of a React frontend, a FastAPI backend, crop-specific PyTorch inference, post-hoc calibration, Grad-CAM explainability, a deterministic condition knowledge layer, and a local SQLite user database.

---

## Component Map

```
┌─────────────────────────────────────────────┐
│               React Frontend                 │
│  (Vite, i18next, GSAP, 3 languages)          │
│  ┌──────────┐ ┌────────────┐ ┌───────────┐  │
│  │  Upload  │ │  Results   │ │  Journal  │  │
│  │  Screen  │ │  Screen    │ │  Screen   │  │
│  └──────────┘ └────────────┘ └───────────┘  │
└─────────────────────┬───────────────────────┘
                      │ HTTP (proxied /api)
┌─────────────────────▼───────────────────────┐
│              FastAPI Backend                  │
│  /api/v1/diagnose  /api/v1/health  /auth     │
└─────────────────────┬───────────────────────┘
                      │
        ┌─────────────┼──────────────┐
        ▼             ▼              ▼
  Image Pipeline   Inference     Auth / DB
  (validation,     Service       (SQLite,
   normalization)  (PyTorch)      BCrypt, JWT)
        │
        ▼
  Crop-Specific Model
  ┌─────────────┐   ┌─────────────────┐
  │ConvNeXt-Tiny│   │EfficientNetV2-S │
  │ (Turmeric)  │   │    (Citrus)     │
  └──────┬──────┘   └───────┬─────────┘
         │                  │
         ▼                  ▼
    Raw Softmax Probabilities
         │
         ▼
  Calibration Policy
  ┌──────────────────────────────────┐
  │ Turmeric: inactive (raw output)  │
  │ Citrus:   T = 2.218093 applied   │
  └──────────────────────────────────┘
         │
         ▼
  Uncertainty Gate (threshold 0.65)
  ├── below threshold → REJECTED → expert messaging
  └── above threshold → ACCEPTED
         │
         ▼
  Grad-CAM (target layer: features.7)
  + Region Extractor
         │
         ▼
  Condition Knowledge Lookup (22 classes)
         │
         ▼
  Final API Response → Frontend Result Screen
```

---

## Frontend Architecture

**Framework:** React 18 with Vite 5

**Key screens:**
- `WelcomeScreen` — Language selection and entry
- `HomeScreen` — Crop selection (Turmeric / Citrus)
- `CheckLeafScreen` — Image upload, preview, photo tips
- `AnalysisScreen` — Inference progress display
- `ResultScreen` — Full result with confidence arc, Grad-CAM overlay, condition knowledge, history
- `JournalScreen` — Per-user prediction history
- `AboutScreen` — Project information
- `GuideScreen` — Usage guidance

**Internationalisation:** `i18next` + `react-i18next` with locale JSON files (`en.json`, `hi.json`, `mr.json`)

**Animations:** GSAP for transitions and interactive elements

**Authentication state:** `AuthContext` (React context) + `authApi.js` service module

**API proxy:** Vite dev server proxies `/api` → `http://127.0.0.1:8000`

---

## Backend Architecture

**Framework:** FastAPI with Uvicorn

**Key modules:**

| Module | Responsibility |
|---|---|
| `main.py` | App factory, CORS, lifespan events, router mounting |
| `api/routes.py` | `/diagnose`, `/health`, `/advisories` routing |
| `api/auth_routes.py` | `/auth/register`, `/auth/login`, `/auth/logout`, `/auth/me`, `/auth/history` |
| `services/inference_service.py` | Model loading, per-request prediction orchestration |
| `services/diagnosis_service.py` | End-to-end diagnosis pipeline coordinator |
| `ml/model_builder.py` | Architecture instantiation and checkpoint loading |
| `ml/registry.py` | Active model configuration registry |
| `calibration/temperature_scaler.py` | Crop-specific Temperature Scaling |
| `explainability/gradcam.py` | Grad-CAM hook registration and gradient computation |
| `explainability/region_extractor.py` | Heatmap-based region bounding box extraction |
| `explainability/renderer.py` | Heatmap-to-image compositing |
| `knowledge/service.py` | Deterministic condition knowledge lookup |
| `preprocessing/image_pipeline.py` | Input validation, resize, normalization |
| `auth/security.py` | BCrypt + JWT token generation and verification |
| `db/database.py` | SQLAlchemy engine, session factory, table init |
| `db/models.py` | User and PredictionHistory ORM models |
| `db/repository.py` | Database read/write operations |
| `utils/config.py` | Pydantic-Settings configuration with `.env` support |

---

## Inference Flow (per request)

1. Client uploads JPEG/PNG image with crop selection
2. `image_pipeline.py` validates, decodes to RGB, resizes to crop-specific resolution
3. `inference_service.py` selects the active checkpoint for the requested crop
4. PyTorch model runs forward pass → raw logits + softmax probabilities
5. `temperature_scaler.py` applies calibration per crop policy
6. Uncertainty gate checks calibrated (or raw) confidence vs threshold (0.65)
7. If rejected: response returns `rejected=True` with expert referral messaging
8. If accepted: `gradcam_service.py` registers backward hooks on `features.7`, runs backward pass, generates heatmap
9. `region_extractor.py` extracts bounding boxes of high-activation regions
10. `renderer.py` composites the heatmap overlay
11. `knowledge/service.py` looks up condition knowledge for the predicted class
12. Full response returned to frontend

---

## Calibration Layer

Temperature Scaling divides logits by a learned scalar `T` before softmax.

- **Turmeric:** `T = 0.101698` — calibration **inactive** (raw softmax used)
- **Citrus:** `T = 2.218093` — calibration **active**

See `docs/CALIBRATION.md` for full policy rationale.

---

## Authentication & Session System

- Passwords hashed with BCrypt (cost factor 12)
- JWT tokens signed with HS256 (secret from `.env`)
- Session stored in HttpOnly, SameSite=Lax cookie (`drishya_session`)
- Per-user prediction history stored in SQLite `prediction_history` table
- Raw image bytes are **not** persisted in the database

---

## Multilingual System

- Three locale files: `frontend/src/locales/{en,hi,mr}.json`
- All user-facing strings are keyed through i18next
- Language selection persists in `LanguageContext`
- Condition knowledge JSON (`backend/app/knowledge/condition_knowledge.json`) stores translated field names for all 22 conditions

---

## Database Schema

**SQLite** (local file: `database/leaflens.db`)

**Tables:**
- `users` — `id`, `username`, `email`, `hashed_password`, `created_at`, `is_active`
- `prediction_history` — `id`, `user_id`, `crop`, `predicted_class`, `confidence`, `rejected`, `created_at`, plus Grad-CAM metadata fields

The database file is created automatically on first startup. It is not committed to Git.
