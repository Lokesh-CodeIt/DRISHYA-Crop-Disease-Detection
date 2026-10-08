# DRISHYA — Security Documentation

## Overview

This document describes the security design of the DRISHYA system, including authentication, session management, data handling, and repository safety practices.

---

## Authentication

| Property | Implementation |
|---|---|
| Password hashing | BCrypt (via `bcrypt` library, cost factor 12) |
| Token format | JWT (JSON Web Token) |
| Signing algorithm | HS256 |
| Token expiry | 7 days (configurable via `AUTH_TOKEN_EXPIRE_MINUTES`) |
| Token storage | HttpOnly cookie — not accessible by client-side JavaScript |
| Cookie name | `drishya_session` (configurable) |
| Cookie flags | `HttpOnly=true`, `SameSite=Lax` |
| HTTPS enforcement | `Secure=true` in production (set `AUTH_COOKIE_SECURE=true` in `.env`) |

**SameSite=Lax** prevents CSRF from third-party cross-site form submissions while allowing same-site navigation.

**HttpOnly** ensures the session token cannot be exfiltrated via XSS attacks targeting `document.cookie`.

---

## Secret Key

The JWT signing secret (`AUTH_SECRET_KEY`) is loaded from the `.env` file via `pydantic-settings`.

- The `.env` file is **never committed to Git** (enforced by `.gitignore`)
- An `.env.example` file with placeholder values is provided
- The default value in `config.py` is clearly marked as insecure and for development only

> **Production requirement:** Set `AUTH_SECRET_KEY` to a minimum 32-character cryptographically random string before any exposed deployment.

---

## User Ownership

- All database records are associated with the authenticated user's `user_id`
- Prediction history queries are filtered by `user_id` — users cannot access each other's history
- There is no administrative UI — user management is backend-only

---

## Data Storage

| Data | Storage | Notes |
|---|---|---|
| Passwords | BCrypt hashes in SQLite | Plaintext never stored |
| Session tokens | HttpOnly cookies only | Not stored in database |
| Prediction history | SQLite (metadata only) | Class, confidence, timestamp, user_id |
| Uploaded images | Memory only (per-request) | Raw bytes are **not persisted** to database or disk |
| Grad-CAM overlays | Memory only | Not written to disk during normal operation |

The SQLite database file (`database/leaflens.db`) contains:
- User accounts (hashed passwords, email, username)
- Prediction history metadata

It does **not** contain raw image bytes or original file content.

---

## Repository Security

| Practice | Status |
|---|---|
| `.env` excluded from Git | ✅ `.gitignore` enforced |
| Runtime database excluded from Git | ✅ `database/*.db` ignored |
| Personal machine paths sanitized | ✅ Removed from all documentation |
| No secrets in source code | ✅ All secrets via `.env` |
| No API keys committed | ✅ Verified |
| SSH keys not committed | ✅ Not present |
| Repository visibility | ✅ PRIVATE |

---

## CORS Configuration

The backend allows cross-origin requests from:
- `http://localhost:3000`
- `http://localhost:5173`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

For production, restrict `CORS_ORIGINS` to the actual deployment domain.

---

## Input Validation

- Uploaded files are validated for MIME type and file extension
- Images are validated for minimum and maximum dimensions
- File size is validated
- All input is processed through Pydantic schemas before reaching business logic

---

## Image SHA-256 Metadata

The `ml/scripts/` pipeline generates SHA-256 hashes for all dataset images, stored in manifest CSVs. These hashes:
- Confirm dataset integrity during re-runs
- Enable deduplication
- Are **not** exposed via any API endpoint

---

## Known Security Limitations

- DRISHYA is a **research prototype** — no formal security audit has been performed
- SQLite is not suitable for multi-user production workloads — replace with PostgreSQL for scale
- No rate limiting is implemented on the `/diagnose` endpoint
- No IP-based blocking or bot mitigation
- HTTPS is not handled by DRISHYA itself — a reverse proxy (nginx, Caddy) is required for HTTPS in deployment
