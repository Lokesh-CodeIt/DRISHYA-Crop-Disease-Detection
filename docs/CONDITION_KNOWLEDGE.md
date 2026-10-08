# DRISHYA — Condition Knowledge Documentation

## Overview

DRISHYA provides a **22-class deterministic condition knowledge layer** that maps each recognized plant condition to structured, source-backed information. This layer is entirely deterministic — it does not use any dynamic text generation, LLMs, or AI-generated advisory content.

---

## Coverage

| Crop | Classes | Total |
|---|---|---|
| Turmeric | Healthy, Dry Leaf, Leaf Blotch, Leaf Spot | 4 |
| Citrus | Algal Leaf Spot, Anthracnose, Bacterial Blight, Black Spot, Citrus Canker, Citrus Hindu Mite, Citrus Leafminer, Citrus Pest, Citrus Scab, Curl Leaf, Dry Leaf, Greening, Healthy, Lemon Sooty Mold, Melanose, Spider Mites, Swallowtail Larval Herbivory (Deficiency), Yellow Spot | 18 |
| **Total** | | **22** |

---

## Knowledge Base

The condition knowledge is stored in `backend/app/knowledge/condition_knowledge.json`.

Each condition entry contains:

| Field | Description |
|---|---|
| `condition_name` | Canonical English class name |
| `display_name` | User-facing display name (may differ from model class label) |
| `condition_type` | `disease`, `pest`, `abiotic`, or `healthy` |
| `description` | Plain-language description of the condition |
| `causes` | Primary causal agents (fungal, bacterial, environmental, etc.) |
| `symptoms` | Visual symptoms on leaf or plant |
| `management` | Cultural, organic, and chemical management guidance |
| `sources` | Source metadata (name, URL where applicable) |
| `severity_range` | Approximate severity classification |
| `translations` | Hindi and Marathi translations of key fields |

---

## Lookup Service

Implemented in `backend/app/knowledge/service.py`.

The `ConditionKnowledgeService`:
1. Loads the JSON knowledge base on startup
2. Accepts `(crop, class_name, language)` as input
3. Returns the structured knowledge entry for the requested condition in the requested language
4. Returns a safe fallback for unrecognized inputs
5. Maintains **cross-crop isolation** — turmeric classes cannot resolve citrus entries and vice versa

---

## Advisory States

The condition knowledge layer has three presentation states:

| State | Trigger | Response |
|---|---|---|
| **Supported** | Model predicts a recognized class, confidence ≥ 0.65 | Full condition knowledge displayed |
| **Rejected** | Confidence < 0.65 | Expert confirmation messaging; no condition knowledge displayed |
| **Unknown** | Model predicts an unrecognized class | Graceful fallback; generic messaging |

---

## Multilingual Support

All 22 conditions have translations for:
- English (`en`) — default
- Hindi (`hi`) — translations of display names, symptom descriptions, and management guidance
- Marathi (`mr`) — translations of display names, symptom descriptions, and management guidance

Language is selected by the user at session start and passed through the API request.

---

## Safety Constraints

The condition knowledge layer is designed with explicit safety constraints:

1. **No dynamic pesticide dosage generation** — specific dosage amounts are not generated dynamically or by AI
2. **No chemical prescription** — management guidance describes categories of intervention, not specific product application schedules
3. **Source-backed only** — every condition entry has associated source metadata
4. **Rejection semantics** — uncertain predictions are explicitly flagged and directed to expert confirmation
5. **No hallucination risk** — all content is fixed, reviewed, and loaded from a static JSON file

---

## Updating the Knowledge Base

To add or update condition entries:

1. Edit `backend/app/knowledge/condition_knowledge.json`
2. Ensure all 22+ entries have required fields: `condition_name`, `description`, `causes`, `symptoms`, `management`, `sources`
3. Update translations in `frontend/src/locales/{hi,mr}.json` for any new UI strings
4. Run `python -m pytest tests/test_condition_knowledge.py -v` to verify coverage and schema

The test suite (`tests/test_condition_knowledge.py`) verifies:
- All 22 classes resolve for both crops
- All three languages are covered for all classes
- No unsafe pesticide dosage strings are present
- Source metadata is present for all supported conditions
- Rejection semantics work correctly
- Cross-crop isolation is maintained
- Schema serialization is valid
