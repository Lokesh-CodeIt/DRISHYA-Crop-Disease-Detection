# DRISHYA — Deployment Documentation

## Overview

DRISHYA is designed for **CPU-only local deployment** using native PyTorch inference. No GPU, ONNX Runtime, TensorFlow, or external inference server is required.

---

## Current Deployment Runtime

**Native PyTorch CPU inference**

Models are loaded as standard PyTorch `nn.Module` objects set to `eval()` mode. Inference runs synchronously within the FastAPI request handler via `torch.no_grad()`.

> Note: ONNX Runtime is **not** used in the current production configuration. `ml/scripts/export_onnx.py` exists as a future export pipeline but is not active.

---

## CPU Benchmark Results

Measured on CPU (50 timed forward passes + 2 warm-up runs, single-sample batch).

| Model | File Size | Parameters | Median Latency | Std Dev |
|---|---|---|---|---|
| ConvNeXt-Tiny (Turmeric, 224×224) | 106.20 MB | 27.82M | 168.39 ms | ±39.46 ms |
| EfficientNetV2-S (Citrus, 384×384) | 77.92 MB | 20.20M | 336.16 ms | ±22.86 ms |

Total Grad-CAM overhead adds approximately 50–100 ms per request.

---

## System Requirements

| Requirement | Minimum |
|---|---|
| Python | 3.10+ |
| RAM | 4 GB (8 GB recommended) |
| Disk (models via Git LFS) | ~200 MB |
| GPU | Not required |
| OS | Windows / Linux / macOS |
| Node.js (frontend) | 18+ |

---

## Running the Application

### Backend

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

On startup, the application:
1. Initializes the SQLite database (`database/leaflens.db`)
2. Loads both model checkpoints into memory from `ml/models/`
3. Loads calibration artifacts from `ml/calibration/`
4. Loads the condition knowledge JSON

The backend API is available at:
- Root: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`
- API v1: `http://127.0.0.1:8000/api/v1/`

### Frontend

```bash
cd frontend
npm install       # first time only
npm run dev
```

Frontend is available at: `http://localhost:5173/`

Vite proxies all `/api` requests to `http://127.0.0.1:8000` automatically.

---

## Environment Configuration

Copy `.env.example` to `.env` and configure:

```env
AUTH_SECRET_KEY=<your-strong-random-secret-key>
AUTH_ALGORITHM=HS256
AUTH_TOKEN_EXPIRE_MINUTES=10080
AUTH_COOKIE_NAME=drishya_session
AUTH_COOKIE_SECURE=false
AUTH_COOKIE_SAMESITE=lax
UNCERTAINTY_REJECTION_THRESHOLD=0.65
```

> **Security:** `AUTH_SECRET_KEY` must be set to a strong random value in production environments. The default value in `.env.example` is insecure and must not be used in any exposed deployment.

---

## Model Checkpoint Loading

Model checkpoints are stored in:
- `ml/models/turmeric/convnext_tiny/seed_42/best_model.pt`
- `ml/models/citrus/efficientnet_v2_s/seed_42/best_model.pt`

These files are tracked via **Git LFS**. After cloning, run:

```bash
git lfs pull
```

to download the checkpoint files.

The model builder (`backend/app/ml/model_builder.py`) instantiates the architecture using `torchvision` and loads the checkpoint with `torch.load(..., map_location="cpu")`.

---

## Database

The application uses **SQLite** for local user and history storage.

- File location: `database/leaflens.db` (created automatically on first startup)
- This file is **not committed to Git** (ignored by `.gitignore`)
- To reset: delete `database/leaflens.db` and restart the backend

---

## Production Deployment Notes

For production use:

1. Set `AUTH_COOKIE_SECURE=true` and use HTTPS
2. Change `AUTH_SECRET_KEY` to a cryptographically random value
3. Consider replacing SQLite with PostgreSQL for multi-user workloads
4. Add a reverse proxy (nginx, Caddy) in front of Uvicorn
5. Build the frontend: `cd frontend && npm run build` (serves static files)
6. Consider rate limiting on the `/api/v1/diagnose` endpoint

> DRISHYA is currently a research prototype. Production hardening is future work.

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Root health check |
| `/api/v1/health` | GET | Backend health status |
| `/api/v1/diagnose` | POST | Leaf image diagnosis |
| `/api/v1/advisories` | GET | Advisory listing |
| `/auth/register` | POST | User registration |
| `/auth/login` | POST | User login (sets HttpOnly cookie) |
| `/auth/logout` | POST | User logout |
| `/auth/me` | GET | Current user info |
| `/auth/history` | GET | Current user prediction history |
| `/docs` | GET | Swagger interactive API docs |
