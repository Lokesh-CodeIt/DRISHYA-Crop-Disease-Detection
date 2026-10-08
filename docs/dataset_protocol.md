# LeafLens Dataset & Preprocessing Protocol

## 1. Safety & Data Integrity Rules
- **Non-Destructive Operations**: Raw datasets (`ml/datasets/raw/` and root `DATASET/`) must NEVER be modified, renamed in place, or deleted.
- **Git Separation**: Datasets, uncompressed image folders, and model checkpoint weights are strictly excluded via `.gitignore`.
- **Reproducible Pipeline**: All cleaning, filtering, and splitting operations are performed via tracked scripts using deterministic random seeds.
- **Cryptographic Provenance**: Every cleaned image is tracked with source path, destination path, and SHA-256 cryptographic hashes in `data/metadata/`.

## 2. Directory Separation Lifecycle
1. **Raw (`ml/datasets/raw/`)**: Untouched, original archived images extracted from public sources.
2. **Cleaned (`ml/datasets/cleaned/`)**: Verified readable RGB images with non-destructive format conversions (RGBA/palette -> RGB).
3. **Splits (`ml/datasets/splits/`)**: JSON/CSV manifests containing stratified train (70%), validation (15%), and test (15%) partitions with class balance preservation.
4. **Processed (`ml/datasets/processed/`)**: Normalized inputs or pre-computed feature representations (if needed).

## 3. De-duplication Protocol
To prevent optimistic data leakage between training and testing splits:
- **Exact Matches**: Identified using SHA-256 digest comparisons.
- **Near Duplicates**: Identified via perceptual difference hashing (dHash) with Hamming distance thresholding ($\le 2$).
- Manifests and duplicate reports are saved to `data/reports/`.

## 4. Cross-Dataset Validation Standard
Models must be evaluated on independent, external dataset distributions never encountered during training to measure real-world domain generalizability.
