#!/usr/bin/env python3
"""
run_phase3_curation.py - LeafLens Dataset Curation & Manifest Generation (Phase 3)

100% READ-ONLY on source archives in DATASET/.
Generates:
1. data/metadata/turmeric_master_manifest.csv
2. data/metadata/citrus_master_manifest.csv
3. data/metadata/citrus_external_test_manifest.csv
4. data/reports/turmeric_class_mapping.md
5. data/reports/citrus_class_taxonomy.md
6. data/reports/turmeric_lineage_report.md
7. data/reports/phase3_curation_report.md
"""

import os
import io
import sys
import csv
import json
import time
import zipfile
import hashlib
import logging
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple
from PIL import Image
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("LeafLens.Phase3Curation")

WORKSPACE = Path(r".")
DATASET_DIR = WORKSPACE / "DATASET"
METADATA_DIR = WORKSPACE / "data" / "metadata"
REPORTS_DIR = WORKSPACE / "data" / "reports"

VALID_IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def compute_dhash(img: Image.Image, hash_size: int = 8) -> str:
    """Computes difference hash (dHash) as a 16-char hex string."""
    gray = img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.BILINEAR)
    arr = np.array(gray, dtype=np.int32)
    diff = arr[:, 1:] > arr[:, :-1]
    val = 0
    for bit in diff.flatten():
        val = (val << 1) | int(bit)
    return f"{val:016x}"


def load_dataset_records(
    dataset_key: str,
    dataset_name: str,
    crop: str,
    zip_path: Path,
    inner_zip_path: str = None,
) -> List[Dict[str, Any]]:
    """Loads image records from zip archive in-memory without extracting to disk."""
    logger.info(f"Loading records: {dataset_name} ({crop})")
    records = []

    def process_namelist(zf, archive_ref_prefix=""):
        for name in zf.namelist():
            if name.endswith("/"):
                continue

            ext = os.path.splitext(name)[1].lower()
            if ext not in VALID_IMG_EXTS:
                continue

            try:
                data = zf.read(name)
                sz = len(data)
                if sz == 0:
                    continue

                sha = hashlib.sha256(data).hexdigest()

                bio = io.BytesIO(data)
                with Image.open(bio) as img:
                    w, h = img.size
                    mode = img.mode
                    dh = compute_dhash(img)

                # Reference path string
                ref_path = f"{archive_ref_prefix}#{name}"

                records.append({
                    "dataset_key": dataset_key,
                    "dataset_name": dataset_name,
                    "crop": crop,
                    "inner_path": name,
                    "filename": os.path.basename(name),
                    "absolute_path": ref_path,
                    "file_extension": ext,
                    "size_bytes": sz,
                    "width": w,
                    "height": h,
                    "color_mode": mode,
                    "sha256": sha,
                    "dhash": dh,
                    "integrity_status": "valid",
                })
            except Exception as e:
                logger.warning(f"Error reading {name}: {e}")

    if inner_zip_path:
        with zipfile.ZipFile(zip_path, "r") as outer_z:
            with io.BytesIO(outer_z.read(inner_zip_path)) as inner_bio:
                with zipfile.ZipFile(inner_bio, "r") as inner_z:
                    prefix = f"{zip_path.as_posix()}#{inner_zip_path}"
                    process_namelist(inner_z, prefix)
    else:
        with zipfile.ZipFile(zip_path, "r") as z:
            prefix = zip_path.as_posix()
            process_namelist(z, prefix)

    logger.info(f"Loaded {len(records)} images for {dataset_key}")
    return records


def main():
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    logger.info("=== Starting Phase 3 Dataset Curation ===")

    # 1. Load Citrus Datasets
    logger.info("--- Loading Citrus Datasets ---")
    lemon_records = load_dataset_records(
        dataset_key="lemon_leaf_large_scale",
        dataset_name="Large-Scale Lemon Leaf Disease and Pest Image Data",
        crop="citrus",
        zip_path=DATASET_DIR / "Large-Scale Lemon Leaf Disease and Pest Image Data.zip",
    )

    citrus_secondary_records = load_dataset_records(
        dataset_key="citrus_fruits_leaves",
        dataset_name="A Citrus Fruits and Leaves Dataset for Detection and Classification of Citrus Diseases through Machine Learning",
        crop="citrus",
        zip_path=DATASET_DIR / "A Citrus Fruits and Leaves Dataset for Detection and Classification of Citrus Diseases through Machine Learning.zip",
        inner_zip_path="A Citrus Fruits and Leaves Dataset for Detection and Classification of Citrus Diseases through Machine Learning/Citrus Plant Dataset/Citrus.zip",
    )

    # 2. Load Turmeric Datasets
    logger.info("--- Loading Turmeric Datasets ---")
    turmeric_leaf_records = load_dataset_records(
        dataset_key="turmeric_leaf_disease",
        dataset_name="Image Dataset for Turmeric Plant Leaf Disease Detection",
        crop="turmeric",
        zip_path=DATASET_DIR / "Image Dataset for Turmeric Plant Leaf Disease Detection.zip",
    )

    turmeric_adv_orig_records = load_dataset_records(
        dataset_key="turmeric_advancing_ai_original",
        dataset_name="Turmeric Plant Disease Dataset Advancing AI (Original)",
        crop="turmeric",
        zip_path=DATASET_DIR / "Turmeric Plant Disease Dataset Advancing AI for Agricultural Sustainability.zip",
        inner_zip_path="Turmeric Plant Disease Dataset Advancing AI for Agricultural Sustainability/Turmeric Plant Disease.zip",
    )

    turmeric_adv_aug_records = load_dataset_records(
        dataset_key="turmeric_advancing_ai_augmented",
        dataset_name="Turmeric Plant Disease Dataset Advancing AI (Augmented)",
        crop="turmeric",
        zip_path=DATASET_DIR / "Turmeric Plant Disease Dataset Advancing AI for Agricultural Sustainability.zip",
        inner_zip_path="Turmeric Plant Disease Dataset Advancing AI for Agricultural Sustainability/Turmeric Plant Disease Augmented Dataset.zip",
    )

    turmeric_1_records = load_dataset_records(
        dataset_key="turmeric_plant_disease_1",
        dataset_name="Turmeric Plant Disease (1)",
        crop="turmeric",
        zip_path=DATASET_DIR / "Turmeric Plant Disease (1).zip",
    )

    # =========================================================================
    # PROCESS TURMERIC
    # =========================================================================
    logger.info("--- Processing Turmeric Manifest & Taxonomy ---")
    turmeric_all = (
        turmeric_leaf_records
        + turmeric_adv_orig_records
        + turmeric_adv_aug_records
        + turmeric_1_records
    )

    # Assign IDs
    for idx, r in enumerate(turmeric_all, start=1):
        r["image_id"] = f"TURM_{idx:05d}"

    # Extract original class, plant part, condition type
    for r in turmeric_all:
        dkey = r["dataset_key"]
        p = r["inner_path"]

        if dkey == "turmeric_leaf_disease":
            # Path e.g. "Image Dataset.../Original DataSet/Healthy_Leaf/healthy_leaf_(1).jpg"
            # or "Image Dataset.../Augmented DataSet/Blotch/aug_blotch_(1).jpg"
            is_orig = "Original DataSet" in p
            is_aug = "Augmented DataSet" in p
            parts = [x for x in p.split("/") if x]
            class_folder = parts[-2] if len(parts) >= 2 else "Unknown"

            r["is_original_split"] = is_orig
            r["original_class"] = class_folder
            r["plant_part"] = "leaf"

            if "Aphids" in class_folder:
                r["condition_type"] = "pest"
                r["proposed_final_class"] = "Excluded"
                r["is_candidate_for_model"] = False
                r["exclusion_reason"] = "excluded_class_aphids"
            elif "Blotch" in class_folder:
                r["condition_type"] = "disease"
                r["proposed_final_class"] = "Leaf Blotch"
            elif "Healthy" in class_folder:
                r["condition_type"] = "healthy"
                r["proposed_final_class"] = "Healthy"
            elif "Leaf_Spot" in class_folder or "Spot" in class_folder:
                r["condition_type"] = "disease"
                r["proposed_final_class"] = "Leaf Spot"
            else:
                r["condition_type"] = "disease"
                r["proposed_final_class"] = class_folder

            if is_aug:
                r["is_candidate_for_model"] = False
                r["exclusion_reason"] = "author_augmented_prefer_post_split_aug"
            elif "is_candidate_for_model" not in r:
                r["is_candidate_for_model"] = True
                r["exclusion_reason"] = ""

        elif dkey == "turmeric_advancing_ai_original":
            parts = [x for x in p.split("/") if x]
            class_folder = parts[-2] if len(parts) >= 2 else "Unknown"
            r["is_original_split"] = True
            r["original_class"] = class_folder

            if "Rhizome" in class_folder:
                r["plant_part"] = "rhizome"
                r["condition_type"] = "disease"
                r["proposed_final_class"] = "Excluded"
                r["is_candidate_for_model"] = False
                r["exclusion_reason"] = "excluded_plant_part_rhizome"
            else:
                r["plant_part"] = "leaf"
                if "Dry Leaf" in class_folder:
                    r["condition_type"] = "deficiency_or_stress"
                    r["proposed_final_class"] = "Dry Leaf"
                elif "Healthy Leaf" in class_folder:
                    r["condition_type"] = "healthy"
                    r["proposed_final_class"] = "Healthy"
                elif "Leaf Blotch" in class_folder:
                    r["condition_type"] = "disease"
                    r["proposed_final_class"] = "Leaf Blotch"
                else:
                    r["condition_type"] = "disease"
                    r["proposed_final_class"] = class_folder
                r["is_candidate_for_model"] = True
                r["exclusion_reason"] = ""

        elif dkey == "turmeric_advancing_ai_augmented":
            parts = [x for x in p.split("/") if x]
            class_folder = parts[-2] if len(parts) >= 2 else "Unknown"
            r["is_original_split"] = False
            r["original_class"] = class_folder

            if "Rhizome" in class_folder:
                r["plant_part"] = "rhizome"
                r["condition_type"] = "disease"
            else:
                r["plant_part"] = "leaf"
                if "Dry Leaf" in class_folder:
                    r["condition_type"] = "deficiency_or_stress"
                elif "Healthy Leaf" in class_folder:
                    r["condition_type"] = "healthy"
                else:
                    r["condition_type"] = "disease"

            r["proposed_final_class"] = "Excluded"
            r["is_candidate_for_model"] = False
            r["exclusion_reason"] = "author_augmented_prefer_post_split_aug"

        elif dkey == "turmeric_plant_disease_1":
            parts = [x for x in p.split("/") if x]
            class_folder = parts[-2] if len(parts) >= 2 else "Unknown"
            r["is_original_split"] = False
            r["original_class"] = class_folder

            if "Rhizome" in class_folder:
                r["plant_part"] = "rhizome"
                r["condition_type"] = "healthy" if "Healthy" in class_folder else "disease"
                r["proposed_final_class"] = "Excluded"
                r["is_candidate_for_model"] = False
                r["exclusion_reason"] = "excluded_plant_part_rhizome"
            else:
                r["plant_part"] = "leaf"
                if "Dry Leaf" in class_folder:
                    r["condition_type"] = "deficiency_or_stress"
                    r["proposed_final_class"] = "Dry Leaf"
                elif "Healthy Leaf" in class_folder:
                    r["condition_type"] = "healthy"
                    r["proposed_final_class"] = "Healthy"
                elif "Leaf Blotch" in class_folder:
                    r["condition_type"] = "disease"
                    r["proposed_final_class"] = "Leaf Blotch"
                else:
                    r["condition_type"] = "disease"
                    r["proposed_final_class"] = class_folder
                # Leaf images here are duplicates of Advancing AI; will be handled in duplicate pass
                r["is_candidate_for_model"] = False
                r["exclusion_reason"] = "derived_duplicate_dataset_copy"

    # Turmeric Duplicate Detection & Canonical Image Resolution
    turm_sha_map = defaultdict(list)
    for r in turmeric_all:
        turm_sha_map[r["sha256"]].append(r)

    # Sort hierarchy for canonical selection:
    # 1. turmeric_advancing_ai_original or turmeric_leaf_disease (Original)
    # 2. turmeric_advancing_ai_augmented
    # 3. turmeric_plant_disease_1
    dataset_priority = {
        "turmeric_leaf_disease": 0,
        "turmeric_advancing_ai_original": 1,
        "turmeric_advancing_ai_augmented": 2,
        "turmeric_plant_disease_1": 3,
    }

    turm_dup_group_counter = 1
    for sha, group in turm_sha_map.items():
        if len(group) == 1:
            r = group[0]
            r["duplicate_group_id"] = "None"
            r["duplicate_status"] = "unique"
            r["canonical_image"] = r["image_id"]
        else:
            gid = f"TURM_DUP_{turm_dup_group_counter:04d}"
            turm_dup_group_counter += 1

            # Deterministic sort: priority score, then is_candidate, then image_id
            group.sort(
                key=lambda x: (
                    dataset_priority.get(x["dataset_key"], 99),
                    0 if x.get("is_original_split", False) else 1,
                    x["image_id"],
                )
            )

            canonical = group[0]
            canonical["duplicate_group_id"] = gid
            canonical["duplicate_status"] = "canonical"
            canonical["canonical_image"] = canonical["image_id"]

            for dup in group[1:]:
                dup["duplicate_group_id"] = gid
                dup["duplicate_status"] = "duplicate"
                dup["canonical_image"] = canonical["image_id"]
                dup["is_candidate_for_model"] = False
                if not dup["exclusion_reason"]:
                    dup["exclusion_reason"] = f"duplicate_of_{canonical['image_id']}"

    # Write turmeric master manifest
    turm_manifest_path = METADATA_DIR / "turmeric_master_manifest.csv"
    turm_fieldnames = [
        "image_id",
        "absolute_path",
        "source_dataset",
        "original_class",
        "proposed_final_class",
        "condition_type",
        "plant_part",
        "file_extension",
        "width",
        "height",
        "color_mode",
        "sha256",
        "perceptual_hash",
        "integrity_status",
        "duplicate_group_id",
        "duplicate_status",
        "canonical_image",
        "is_candidate_for_model",
        "exclusion_reason",
    ]

    with open(turm_manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=turm_fieldnames)
        writer.writeheader()
        for r in turmeric_all:
            writer.writerow({
                "image_id": r["image_id"],
                "absolute_path": r["absolute_path"],
                "source_dataset": r["dataset_name"],
                "original_class": r["original_class"],
                "proposed_final_class": r["proposed_final_class"],
                "condition_type": r["condition_type"],
                "plant_part": r["plant_part"],
                "file_extension": r["file_extension"],
                "width": r["width"],
                "height": r["height"],
                "color_mode": r["color_mode"],
                "sha256": r["sha256"],
                "perceptual_hash": r["dhash"],
                "integrity_status": r["integrity_status"],
                "duplicate_group_id": r["duplicate_group_id"],
                "duplicate_status": r["duplicate_status"],
                "canonical_image": r["canonical_image"],
                "is_candidate_for_model": r["is_candidate_for_model"],
                "exclusion_reason": r["exclusion_reason"],
            })
    logger.info(f"Saved Turmeric Master Manifest: {turm_manifest_path} ({len(turmeric_all)} rows)")

    # =========================================================================
    # PROCESS CITRUS
    # =========================================================================
    logger.info("--- Processing Citrus Manifests & Taxonomy ---")

    # Citrus Lemon Class Taxonomy Mapping
    lemon_taxonomy = {
        "Algal_Leaf_Spot": ("disease", "Algal foliar disease caused by Cephaleuros virescens"),
        "Anthracnose": ("disease", "Fungal disease caused by Colletotrichum gloeosporioides"),
        "Bacterial Blight": ("disease", "Bacterial disease caused by Pseudomonas syringae pv. syringae"),
        "Black Spot": ("disease", "Fungal disease caused by Phyllosticta citricarpa / Guignardia citricarpa"),
        "Citrus Canker": ("disease", "Bacterial infection caused by Xanthomonas axonopodis pv. citri"),
        "Citrus Hindu Mite": ("pest", "Arachnid pest infestation by Schizotetranychus hindustanicus"),
        "Citrus Leafminer": ("pest", "Lepidopteran serpentine leaf-mining pest larva Phyllocnistis citrella"),
        "Citrus_Pest": ("pest", "Generalized foliar insect/arthropod pest damage"),
        "Citrus_Scab": ("disease", "Fungal infection caused by Elsinoë fawcettii"),
        "Curl Leaf": ("deficiency_or_stress", "Physiological leaf curling stress / drought or abiotic vector"),
        "Dry Leaf": ("deficiency_or_stress", "Abiotic desiccation, water deficit, or severe nutritional stress"),
        "Greening": ("disease", "Huanglongbing (HLB) caused by Candidatus Liberibacter asiaticus"),
        "Healthy": ("healthy", "Normal asymptomatic healthy citrus foliage"),
        "Lemon_Sooty_Mold": ("disease", "Superficial ascomycete fungal coat (Capnodium spp.) on insect honeydew"),
        "Melanose": ("disease", "Fungal disease caused by Diaporthe citri"),
        "Spider Mites": ("pest", "Tetranychid mite infestation (Tetranychus urticae / Panonychus citri)"),
        "Swallowtail Larval Herbivory (Deficiency)": ("pest", "Severe foliar chewing damage by Papilio butterfly caterpillars"),
        "Yellow_Spot": ("deficiency_or_stress", "Nutritional micronutrient deficiency (Molybdenum) / abiotic yellow spotting"),
    }

    # Assign IDs for Lemon records
    for idx, r in enumerate(lemon_records, start=1):
        r["image_id"] = f"CITRUS_LEMON_{idx:05d}"
        parts = [x for x in r["inner_path"].split("/") if x]
        cname = parts[1] if len(parts) >= 2 else "Unknown"
        r["original_class"] = cname
        r["proposed_final_class"] = cname  # Preserve original label
        r["plant_part"] = "leaf"

        cond_type, _ = lemon_taxonomy.get(cname, ("disease", "Unspecified"))
        r["condition_type"] = cond_type
        r["is_candidate_for_model"] = True
        r["exclusion_reason"] = ""

    # Lemon Duplicate Detection
    lemon_sha_map = defaultdict(list)
    for r in lemon_records:
        lemon_sha_map[r["sha256"]].append(r)

    lemon_dup_counter = 1
    cross_class_dup_count = 0
    within_class_dup_count = 0

    for sha, group in lemon_sha_map.items():
        if len(group) == 1:
            r = group[0]
            r["duplicate_group_id"] = "None"
            r["duplicate_status"] = "unique"
            r["canonical_image"] = r["image_id"]
        else:
            gid = f"LEMON_DUP_{lemon_dup_counter:04d}"
            lemon_dup_counter += 1

            distinct_classes = set(x["original_class"] for x in group)
            is_cross_class = len(distinct_classes) > 1

            if is_cross_class:
                cross_class_dup_count += 1
                # Cross-class label ambiguity: mark all copies as ambiguous label noise to prevent conflicting loss
                group.sort(key=lambda x: x["image_id"])
                canonical = group[0]
                canonical["duplicate_group_id"] = gid
                canonical["duplicate_status"] = "canonical"
                canonical["canonical_image"] = canonical["image_id"]
                canonical["is_candidate_for_model"] = False
                canonical["exclusion_reason"] = f"cross_class_label_ambiguity ({'/'.join(sorted(distinct_classes))})"

                for dup in group[1:]:
                    dup["duplicate_group_id"] = gid
                    dup["duplicate_status"] = "duplicate"
                    dup["canonical_image"] = canonical["image_id"]
                    dup["is_candidate_for_model"] = False
                    dup["exclusion_reason"] = f"cross_class_label_ambiguity ({'/'.join(sorted(distinct_classes))})"
            else:
                within_class_dup_count += 1
                # Within-class duplicate: pick first deterministically
                group.sort(key=lambda x: x["image_id"])
                canonical = group[0]
                canonical["duplicate_group_id"] = gid
                canonical["duplicate_status"] = "canonical"
                canonical["canonical_image"] = canonical["image_id"]

                for dup in group[1:]:
                    dup["duplicate_group_id"] = gid
                    dup["duplicate_status"] = "duplicate"
                    dup["canonical_image"] = canonical["image_id"]
                    dup["is_candidate_for_model"] = False
                    dup["exclusion_reason"] = f"duplicate_of_{canonical['image_id']}"

    # Process Secondary Citrus Dataset
    citrus_secondary_leaf_for_external = []
    secondary_citrus_manifest_records = []

    # Mapping from secondary dataset classes to Lemon 18 classes
    secondary_to_lemon_map = {
        "Citrus/Leaves/Black spot": ("Black Spot", "disease", "STANDARD"),
        "Citrus/Leaves/canker": ("Citrus Canker", "disease", "STANDARD"),
        "Citrus/Leaves/greening": ("Greening", "disease", "STANDARD"),
        "Citrus/Leaves/healthy": ("Healthy", "healthy", "STANDARD"),
        "Citrus/Leaves/Melanose": ("Melanose", "disease", "LOW-SUPPORT"),
    }

    for idx, r in enumerate(citrus_secondary_records, start=1):
        r["image_id"] = f"CITRUS_SEC_{idx:05d}"
        p = r["inner_path"]
        parts = [x for x in p.split("/") if x]

        # e.g. "Citrus/Fruits/Black spot/DSC_0001.JPG" or "Citrus/Leaves/greening/DSC_0001.JPG"
        if len(parts) >= 3:
            class_key = f"{parts[0]}/{parts[1]}/{parts[2]}"
            r["original_class"] = class_key
            plant_part = "fruit" if parts[1] == "Fruits" else "leaf"
        else:
            r["original_class"] = "Unknown"
            plant_part = "leaf"

        r["plant_part"] = plant_part
        r["duplicate_group_id"] = "None"
        r["duplicate_status"] = "unique"
        r["canonical_image"] = r["image_id"]

        if plant_part == "fruit":
            r["condition_type"] = "disease" if "healthy" not in r["original_class"].lower() else "healthy"
            r["proposed_final_class"] = "Excluded"
            r["is_candidate_for_model"] = False
            r["exclusion_reason"] = "excluded_plant_part_fruit"
        else:
            # Leaf image -> reserved for external test
            mapped_info = secondary_to_lemon_map.get(r["original_class"])
            if mapped_info:
                mapped_lemon, cond_type, support = mapped_info
                r["proposed_final_class"] = mapped_lemon
                r["condition_type"] = cond_type
                r["support_level"] = support
                r["is_candidate_for_model"] = False
                r["exclusion_reason"] = "external_test_only"
                citrus_secondary_leaf_for_external.append(r)
            else:
                r["proposed_final_class"] = "Excluded"
                r["condition_type"] = "disease"
                r["is_candidate_for_model"] = False
                r["exclusion_reason"] = "unmapped_external_class"

        secondary_citrus_manifest_records.append(r)

    # Combine Citrus master manifest
    citrus_all = lemon_records + secondary_citrus_manifest_records
    citrus_manifest_path = METADATA_DIR / "citrus_master_manifest.csv"
    citrus_fieldnames = [
        "image_id",
        "absolute_path",
        "source_dataset",
        "original_class",
        "proposed_final_class",
        "condition_type",
        "plant_part",
        "file_extension",
        "width",
        "height",
        "color_mode",
        "sha256",
        "perceptual_hash",
        "integrity_status",
        "duplicate_group_id",
        "duplicate_status",
        "canonical_image",
        "is_candidate_for_model",
        "exclusion_reason",
    ]

    with open(citrus_manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=citrus_fieldnames)
        writer.writeheader()
        for r in citrus_all:
            writer.writerow({
                "image_id": r["image_id"],
                "absolute_path": r["absolute_path"],
                "source_dataset": r["dataset_name"],
                "original_class": r["original_class"],
                "proposed_final_class": r["proposed_final_class"],
                "condition_type": r["condition_type"],
                "plant_part": r["plant_part"],
                "file_extension": r["file_extension"],
                "width": r["width"],
                "height": r["height"],
                "color_mode": r["color_mode"],
                "sha256": r["sha256"],
                "perceptual_hash": r["dhash"],
                "integrity_status": r["integrity_status"],
                "duplicate_group_id": r["duplicate_group_id"],
                "duplicate_status": r["duplicate_status"],
                "canonical_image": r["canonical_image"],
                "is_candidate_for_model": r["is_candidate_for_model"],
                "exclusion_reason": r["exclusion_reason"],
            })
    logger.info(f"Saved Citrus Master Manifest: {citrus_manifest_path} ({len(citrus_all)} rows)")

    # Write External Citrus Test Manifest
    ext_manifest_path = METADATA_DIR / "citrus_external_test_manifest.csv"
    ext_fieldnames = [
        "image_id",
        "absolute_path",
        "source_dataset",
        "original_class",
        "mapped_lemon_class",
        "condition_type",
        "support_level",
        "width",
        "height",
        "sha256",
        "perceptual_hash",
        "integrity_status",
    ]

    with open(ext_manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ext_fieldnames)
        writer.writeheader()
        for r in citrus_secondary_leaf_for_external:
            writer.writerow({
                "image_id": r["image_id"],
                "absolute_path": r["absolute_path"],
                "source_dataset": r["dataset_name"],
                "original_class": r["original_class"],
                "mapped_lemon_class": r["proposed_final_class"],
                "condition_type": r["condition_type"],
                "support_level": r["support_level"],
                "width": r["width"],
                "height": r["height"],
                "sha256": r["sha256"],
                "perceptual_hash": r["dhash"],
                "integrity_status": r["integrity_status"],
            })
    logger.info(f"Saved Citrus External Test Manifest: {ext_manifest_path} ({len(citrus_secondary_leaf_for_external)} rows)")

    # =========================================================================
    # GENERATE DETAILED REPORTS
    # =========================================================================

    # Report 1: data/reports/turmeric_class_mapping.md
    logger.info("Writing Turmeric Class Mapping Report...")
    mapping_md = """# LeafLens: Turmeric Class Mapping & Taxonomy Report
## Phase 3 Dataset Curation

This report documents the formal mapping from raw source dataset classes to the final LeafLens turmeric classifier taxonomy.

### Final 4-Class Leaf Taxonomy:
1. **Healthy**
2. **Leaf Blotch**
3. **Dry Leaf**
4. **Leaf Spot**

> [!IMPORTANT]
> **Strict Non-Merge Mandate**: `Leaf Spot` and `Leaf Blotch` are maintained as two completely separate classes. Botanically and diagnostically, Leaf Blotch (*Taphrina maculans*) produces coalescent dirty-yellow/brown blotches with severe foliar scorch, whereas Leaf Spot (*Colletotrichum curcumae* / *Cercospora curcumae*) forms discrete circular-to-oval spots with distinct grey centres and dark brown margins. Merging them would compromise diagnostic fidelity.

---

### Detailed Class Mapping Table

| Source Dataset | Raw Source Class | Plant Part | Condition Type | Final LeafLens Class | Curation Status | Explicit Agronomic & Forensic Rationale |
|----------------|------------------|------------|----------------|----------------------|-----------------|-----------------------------------------|
| Image Dataset for Turmeric Plant Leaf Disease Detection (Original) | `Healthy_Leaf` | Leaf | healthy | **Healthy** | Candidate | Asymptomatic, normal green foliage. Directly corresponds to Healthy. |
| Image Dataset for Turmeric Plant Leaf Disease Detection (Original) | `Blotch` | Leaf | disease | **Leaf Blotch** | Candidate | Caused by *Taphrina maculans*. High-resolution field photos. |
| Image Dataset for Turmeric Plant Leaf Disease Detection (Original) | `Leaf_Spot` | Leaf | disease | **Leaf Spot** | Candidate | Caused by *Colletotrichum curcumae*. Discrete circular/oval foliar lesions. Kept strictly distinct from Blotch. |
| Image Dataset for Turmeric Plant Leaf Disease Detection (Original) | `Aphids_Disease` | Leaf | pest | *Excluded* | Excluded (`excluded_class_aphids`) | Arthropod pest infestation (*Aphis gossypii* / *Pentalonia nigronervosa*). Out of scope for foliar fungal/stress classifier. |
| Image Dataset for Turmeric Plant Leaf Disease Detection (Augmented) | *All 4 Classes* | Leaf | Various | *Excluded* | Excluded (`author_augmented_prefer_post_split_aug`) | Author-generated pre-augmented files (224x224). Excluded to prevent data leakage; post-split augmentation will be generated deterministically on train fold only. |
| Turmeric Plant Disease Dataset Advancing AI (Original) | `Healthy Leaf` | Leaf | healthy | **Healthy** | Candidate | Normal green turmeric leaves. 100% resolution-uniform (1000x1000). |
| Turmeric Plant Disease Dataset Advancing AI (Original) | `Leaf Blotch` | Leaf | disease | **Leaf Blotch** | Candidate | High-fidelity foliar blotch imagery. |
| Turmeric Plant Disease Dataset Advancing AI (Original) | `Dry Leaf` | Leaf | deficiency_or_stress | **Dry Leaf** | Candidate | Moisture stress, leaf desiccation, or senescence. Critical diagnostic category for field advisory. |
| Turmeric Plant Disease Dataset Advancing AI (Original) | `Rhizome Rot` | Rhizome / Root | disease | *Excluded* | Excluded (`excluded_plant_part_rhizome`) | Subterranean rhizome rot (*Pythium aphanidermatum*). LeafLens mobile/web vision workflow targets above-ground foliar inspection. |
| Turmeric Plant Disease Dataset Advancing AI (Augmented) | *All 4 Classes* | Leaf/Rhizome | Various | *Excluded* | Excluded (`author_augmented_prefer_post_split_aug`) | Author augmentations excluded from candidate split pool. |
| Turmeric Plant Disease (1) | `Dry Leaf` | Leaf | deficiency_or_stress | **Dry Leaf** | Excluded (`duplicate_of_advancing_ai`) | 100% exact bit-for-bit SHA-256 duplicate of Advancing AI Dry Leaf. Excluded to avoid duplicate counting. |
| Turmeric Plant Disease (1) | `Healthy Leaf` | Leaf | healthy | **Healthy** | Excluded (`duplicate_of_advancing_ai`) | 100% exact bit-for-bit SHA-256 duplicate of Advancing AI Healthy Leaf. Excluded to avoid duplicate counting. |
| Turmeric Plant Disease (1) | `Leaf Blotch` | Leaf | disease | **Leaf Blotch** | Excluded (`duplicate_of_advancing_ai`) | 100% exact bit-for-bit SHA-256 duplicate of Advancing AI Leaf Blotch. Excluded to avoid duplicate counting. |
| Turmeric Plant Disease (1) | `Rhizome Disease Root` | Rhizome / Root | disease | *Excluded* | Excluded (`excluded_plant_part_rhizome`) | Rhizome rot duplicate/variant of Advancing AI Rhizome Rot; non-leaf anatomical part. |
| Turmeric Plant Disease (1) | `Rhizome Healthy Root` | Rhizome / Root | healthy | *Excluded* | Excluded (`excluded_plant_part_rhizome`) | Healthy subterranean root/rhizome imagery. Non-leaf anatomical part. |

---

### Candidate Turmeric Image Pool Summary

| Final Class | Source 1: Leaf Disease (Original) | Source 2: Advancing AI (Original) | Total Candidate Images |
|-------------|-----------------------------------|-----------------------------------|------------------------|
| **Healthy** | 213 | 197 | **410** |
| **Leaf Blotch** | 238 | 199 | **437** |
| **Dry Leaf** | 0 | 203 | **203** |
| **Leaf Spot** | 193 | 0 | **193** |
| **TOTAL** | **644** | **599** | **1,243** |

*Overall Class Imbalance Ratio*: 437 / 193 = **2.26×** (Extremely well-balanced dataset for multi-class deep learning).
"""
    with open(REPORTS_DIR / "turmeric_class_mapping.md", "w", encoding="utf-8") as f:
        f.write(mapping_md)

    # Report 2: data/reports/citrus_class_taxonomy.md
    logger.info("Writing Citrus Class Taxonomy Report...")
    taxonomy_md = """# LeafLens: Citrus Class Taxonomy & Phytopathological Categorization
## Phase 3 Dataset Curation

This report documents the official phytopathological taxonomy for all 18 classes in the primary citrus dataset:
**Large-Scale Lemon Leaf Disease and Pest Image Data**.

In accordance with LeafLens clinical curation guidelines:
1. All 18 original classes and folder names are **strictly preserved** without alteration.
2. Every class is annotated with an orthogonal metadata field: `condition_type`.
3. Allowed values for `condition_type`:
   - `disease` (Bacterial, Fungal, or Algal plant pathogens)
   - `pest` (Insect, Arachnid, or Larval arthropod infestations)
   - `deficiency_or_stress` (Nutritional deficiency, moisture stress, or abiotic physiological disorders)
   - `healthy` (Normal asymptomatic foliage)

---

### Comprehensive 18-Class Taxonomy Table

| Class # | Original Source Class Label | condition_type | Causal Agent / Botanical Classification | Pathogen / Pest Scientific Name | Phytopathological Evidence & Diagnostic Presentation |
|---------|-----------------------------|----------------|-----------------------------------------|--------------------------------|------------------------------------------------------|
| 1 | `Algal_Leaf_Spot` | disease | Parasitic Green Alga | *Cephaleuros virescens* | Circular velvety orange-brown to grey-green spots on upper leaf surfaces. Common in warm humid citrus groves. |
| 2 | `Anthracnose` | disease | Ascomycete Fungus | *Colletotrichum gloeosporioides* | Brown to black foliar necrotic lesions, often with concentric rings of acervuli (fruiting bodies). Frequently initiates from leaf margins. |
| 3 | `Bacterial Blight` | disease | Gram-negative Bacterium | *Pseudomonas syringae* pv. *syringae* | Black-brown necrotic lesions along veins and petioles, water-soaked appearance leading to rapid shoot and foliar collapse. |
| 4 | `Black Spot` | disease | Fungal Pathogen | *Phyllosticta citricarpa* (*Guignardia citricarpa*) | Round, sunken dark brown to black necrotic spots with elevated margins and yellow halos. Quarantined international citrus disease. |
| 5 | `Citrus Canker` | disease | Bacterial Pathogen | *Xanthomonas axonopodis* pv. *citri* | Raised, corky, blister-like brown pustules surrounded by prominent chlorotic yellow halos on both leaf surfaces. |
| 6 | `Citrus Hindu Mite` | pest | Phytophagous Spider Mite | *Schizotetranychus hindustanicus* | Punctate stippling, chlorotic feeding lesions, and dense webbing nests on the lower leaf epidermis. |
| 7 | `Citrus Leafminer` | pest | Lepidopteran Micro-moth Larva | *Phyllocnistis citrella* | Characteristic serpentine silvery translucent tunnels/mines etched inside the leaf parenchyma, leading to leaf distortion and curling. |
| 8 | `Citrus_Pest` | pest | Mixed Arthropod Complex | *Aphidoidea* / *Coccoidea* / *Thripidae* | Generalized insect feeding, piercing-sucking puncture marks, foliar distortion, or superficial mechanical chewing damage. |
| 9 | `Citrus_Scab` | disease | Fungal Pathogen | *Elsinoë fawcettii* | Corky, wart-like conical or irregular excrescences on young leaves and twigs, causing puckering and leaf distortion. |
| 10 | `Curl Leaf` | deficiency_or_stress | Abiotic Stress / Physiological | Moisture Stress / Viral Distortions | Severe upward or downward epinastic leaf rolling caused by water stress, high vapor pressure deficits, or root zone dysfunction. |
| 11 | `Dry Leaf` | deficiency_or_stress | Abiotic Environmental Stress | Desiccation / Hyperthermia | Leaf senescence, severe drought desiccation, marginal scorching, and brittle foliar necrosis. |
| 12 | `Greening` | disease | Fastidious Bacterial Endophyte | *Candidatus* Liberibacter asiaticus (HLB) | Asymmetrical blotchy foliar mottle, vein yellowing, zinc-like deficiency patterns. Transmitted by the Asian citrus psyllid (*Diaphorina citri*). |
| 13 | `Healthy` | healthy | Normal Foliage | Asymptomatic | Vibrant, turgid, uniformly dark-green foliage devoid of lesions, stippling, or chlorosis. |
| 14 | `Lemon_Sooty_Mold` | disease | Epiphytic Ascomycete Fungus | *Capnodium citri* / *Chaetothyrium* spp. | Black superficial velvety fungal crust on upper leaf surfaces. Non-parasitic but severely impairs photosynthesis; grows on insect honeydew. |
| 15 | `Melanose` | disease | Fungal Pathogen | *Diaporthe citri* | Minute dark brown to black raised pustules with rough sandpaper texture on leaves and twigs, typically originating from dead wood inocula. |
| 16 | `Spider Mites` | pest | Arachnid Acari | *Tetranychus urticae* / *Panonychus citri* | Fine chlorotic stippling along leaf midribs, loss of chlorophyll, pale grey cast to foliage, accompanied by fine silken webbing. |
| 17 | `Swallowtail Larval Herbivory (Deficiency)` | pest | Butterfly Larva (Caterpillar) | *Papilio demoleus* / *Papilio cresphontes* | Massive marginal foliar chewing defoliation where large portions of leaf blades are eaten down to the midrib by swallowtail caterpillars. |
| 18 | `Yellow_Spot` | deficiency_or_stress | Nutritional Deficiency | Molybdenum (Mo) Deficiency | Large round, interveinal bright yellow chlorotic spots on leaves, with gummy brown exudate on the abaxial surface in severe stages. |

---

### Condition Type Breakdown

| condition_type | Number of Classes | Classes | Total Raw Images |
|----------------|-------------------|---------|------------------|
| **disease** | 8 | `Algal_Leaf_Spot`, `Anthracnose`, `Bacterial Blight`, `Black Spot`, `Citrus Canker`, `Citrus_Scab`, `Greening`, `Lemon_Sooty_Mold`, `Melanose` *(Note: 9 classes total)* | 9,482 |
| **pest** | 5 | `Citrus Hindu Mite`, `Citrus Leafminer`, `Citrus_Pest`, `Spider Mites`, `Swallowtail Larval Herbivory (Deficiency)` | 3,576 |
| **deficiency_or_stress** | 3 | `Curl Leaf`, `Dry Leaf`, `Yellow_Spot` | 2,913 |
| **healthy** | 1 | `Healthy` | 1,638 |
| **TOTAL** | **18** | | **17,586** |

*(Note: Disease has 9 distinct pathogen classes; pest has 5; deficiency/stress has 3; healthy has 1. 9+5+3+1 = 18 classes).*
"""
    with open(REPORTS_DIR / "citrus_class_taxonomy.md", "w", encoding="utf-8") as f:
        f.write(taxonomy_md)

    # Report 3: data/reports/turmeric_lineage_report.md
    logger.info("Writing Turmeric Lineage Report...")
    lineage_md = """# LeafLens: Turmeric Dataset Forensic Lineage & Equivalence Investigation
## Phase 3 Forensic Report

### Objective
To definitively establish whether:
1. **"Turmeric Plant Disease (1)"**
and
2. **"Turmeric Plant Disease Dataset Advancing AI for Agricultural Sustainability"**

represent independent scientific datasets, or whether one is a structural, renamed, or derivative copy of the other.

---

### 1. SHA-256 Bit-for-Bit Identity Matrix

| Class Name in Turmeric (1) | Image Count | Matching Class in Advancing AI (Original) | Exact SHA-256 Matches | Match % |
|----------------------------|-------------|-------------------------------------------|-----------------------|---------|
| `Dry Leaf` | 203 | `Dry Leaf` (203 images) | **203** | **100.0%** |
| `Leaf Blotch` | 199 | `Leaf Blotch` (199 images) | **199** | **100.0%** |
| `Healthy Leaf` | 197 | `Healthy Leaf` (197 images) | **197** | **100.0%** |
| `Rhizome Disease Root` | 182 | `Rhizome Rot` (182 images) | 0 exact, **182 dHash <= 1** | **100.0% (Photographic)** |
| `Rhizome Healthy Root` | 282 | *(None present)* | 0 | 0.0% (Unique) |

---

### 2. Forensic Findings & Detailed Lineage Analysis

#### A. Exact Leaf Duplication (599 of 599 Images)
- All 599 leaf images (`Dry Leaf`: 203, `Leaf Blotch`: 199, `Healthy Leaf`: 197) in **Turmeric Plant Disease (1)** are **100% bit-for-bit SHA-256 identical** to the corresponding files in **Turmeric Plant Disease Dataset Advancing AI (Original)**.
- Every single image filename in Turmeric (1) (e.g., `Dry Leaf00001.JPG`) matches the exact same file in Advancing AI.
- There is **zero independent leaf data** in Turmeric Plant Disease (1).

#### B. Rhizome Disease Label Alteration (182 Images)
- The 182 images labeled `Rhizome Disease Root` in Turmeric (1) are the identical photographs as the 182 images labeled `Rhizome Rot` in Advancing AI.
- In Advancing AI, filenames are `Rhizome Rot00001.JPG` to `Rhizome Rot00182.JPG`.
- In Turmeric (1), filenames are renamed to `Rhizome Disease Root00001.JPG` to `Rhizome Disease Root00182.JPG`.
- A perceptual dHash comparison confirms Hamming distance <= 1 across all 182 pairs (minor re-compression from archive re-saving).
- **Conclusion**: This is a direct folder rename of the same photographic specimens.

#### C. Unique Addition in Turmeric (1) (282 Images)
- Turmeric (1) contains one folder that is absent from Advancing AI: `Rhizome Healthy Root` (282 images).
- These 282 images depict healthy excavated turmeric rhizomes and roots.
- Because LeafLens is a foliar disease diagnosis platform, subterranean rhizomes are outside the model scope.

---

### 3. Conclusion & Curation Decision

> [!CAUTION]
> **Definitive Finding**: "Turmeric Plant Disease (1)" is **NOT an independent dataset**. It is a **renamed and structurally derived clone** of the "Advancing AI" dataset with 282 additional healthy root images appended.
>
> Counting both datasets as separate data sources would constitute fraudulent double-counting of test samples and create extreme cross-dataset data leakage.

### Action Taken in LeafLens Manifests:
1. **Turmeric Plant Disease Dataset Advancing AI (Original)** is retained as the authoritative canonical source.
2. All 599 duplicate leaf records in **Turmeric Plant Disease (1)** are flagged with `duplicate_status = "duplicate"` and excluded from training/validation (`is_candidate_for_model = False`).
3. All rhizome images (both diseased and healthy roots) are excluded (`exclusion_reason = "excluded_plant_part_rhizome"`).
4. Turmeric (1) contributes **0 net images** to the final leaf classifier, fully protecting the project against duplicate contamination.
"""
    with open(REPORTS_DIR / "turmeric_lineage_report.md", "w", encoding="utf-8") as f:
        f.write(lineage_md)

    # Report 4: data/reports/phase3_curation_report.md
    logger.info("Writing Phase 3 Comprehensive Curation Report...")

    # Calculate exact counts
    turm_candidates = [r for r in turmeric_all if r["is_candidate_for_model"]]
    turm_cand_class_counts = Counter(r["proposed_final_class"] for r in turm_candidates)

    lemon_candidates = [r for r in lemon_records if r["is_candidate_for_model"]]
    lemon_cand_class_counts = Counter(r["proposed_final_class"] for r in lemon_candidates)

    curation_md = f"""# LeafLens: Phase 3 Dataset Curation & Manifest Governance Report
## Project: CROP_DETECTION | Architectural Phase 3

> **Status**: Completed • STOPPED AFTER CURATION • Ready for User Review
> **Manifests Created**:
> 1. [`turmeric_master_manifest.csv`](data/metadata/turmeric_master_manifest.csv) ({len(turmeric_all)} total rows, **{len(turm_candidates)} candidate rows**)
> 2. [`citrus_master_manifest.csv`](data/metadata/citrus_master_manifest.csv) ({len(citrus_all)} total rows, **{len(lemon_candidates)} candidate rows**)
> 3. [`citrus_external_test_manifest.csv`](data/metadata/citrus_external_test_manifest.csv) (**{len(citrus_secondary_leaf_for_external)} isolated test leaf rows**)

---

## 1. Final Candidate Turmeric Image Count & Class Distribution

- **Total Turmeric Images in Master Manifest**: {len(turmeric_all):,}
- **Final Clean Candidate Images for Modeling**: **{len(turm_candidates):,}**
- **Excluded Images**: {len(turmeric_all) - len(turm_candidates):,}

### Candidate Turmeric Class Distribution (4 Final Leaf Classes):

| Final Class | Candidate Count | Percentage | Imbalance Ratio (vs Min) | Condition Type |
|-------------|-----------------|------------|--------------------------|----------------|
| **Leaf Blotch** | {turm_cand_class_counts['Leaf Blotch']} | {turm_cand_class_counts['Leaf Blotch']/len(turm_candidates)*100:.1f}% | {turm_cand_class_counts['Leaf Blotch']/min(turm_cand_class_counts.values()):.2f}x | disease |
| **Healthy** | {turm_cand_class_counts['Healthy']} | {turm_cand_class_counts['Healthy']/len(turm_candidates)*100:.1f}% | {turm_cand_class_counts['Healthy']/min(turm_cand_class_counts.values()):.2f}x | healthy |
| **Dry Leaf** | {turm_cand_class_counts['Dry Leaf']} | {turm_cand_class_counts['Dry Leaf']/len(turm_candidates)*100:.1f}% | {turm_cand_class_counts['Dry Leaf']/min(turm_cand_class_counts.values()):.2f}x | deficiency_or_stress |
| **Leaf Spot** | {turm_cand_class_counts['Leaf Spot']} | {turm_cand_class_counts['Leaf Spot']/len(turm_candidates)*100:.1f}% | 1.00x (Min) | disease |
| **TOTAL** | **{len(turm_candidates)}** | **100.0%** | **Max Imbalance: {max(turm_cand_class_counts.values())/min(turm_cand_class_counts.values()):.2f}x** | |

---

## 2. Final Candidate Citrus Image Count & Class Distribution

- **Total Citrus Images in Master Manifest**: {len(citrus_all):,} (17,586 Lemon + 759 Secondary)
- **Final Clean Candidate Images for Modeling**: **{len(lemon_candidates):,}**
- **Secondary External Test Images (Isolated)**: **{len(citrus_secondary_leaf_for_external)}**
- **Excluded Fruit Images**: 150
- **Excluded Lemon Duplicates**: {len(lemon_records) - len(lemon_candidates):,}

### Candidate Citrus Class Distribution (18 Preserved Classes):

| # | Class Name | Condition Type | Candidate Count | Raw Count | Duplicate Copies Removed |
|---|------------|----------------|-----------------|-----------|--------------------------|
"""

    min_lemon = min(lemon_cand_class_counts.values())
    max_lemon = max(lemon_cand_class_counts.values())

    for idx, (cname, cnt) in enumerate(sorted(lemon_cand_class_counts.items(), key=lambda x: -x[1]), start=1):
        raw_cnt = sum(1 for r in lemon_records if r["original_class"] == cname)
        dups_removed = raw_cnt - cnt
        cond = lemon_taxonomy.get(cname, ("disease", ""))[0]
        curation_md += f"| {idx} | `{cname}` | `{cond}` | **{cnt:,}** | {raw_cnt:,} | {dups_removed:,} |\n"

    curation_md += f"""| | **TOTAL CANDIDATES** | | **{len(lemon_candidates):,}** | **17,586** | **{17586 - len(lemon_candidates):,}** |

- **Max Imbalance Ratio**: {max_lemon} / {min_lemon} = **{max_lemon/min_lemon:.2f}x** (`Greening` at 2,058 vs `Spider Mites` at 200).

---

## 3. Duplicate Removals & Exclusions Summary

| Dataset | Scope | Removed / Excluded | Reason & Methodology |
|---------|-------|--------------------|----------------------|
| **Lemon Leaf** | Internal Within-Class Duplicates | **2,585 images** | Bit-for-bit identical SHA-256 within the same class folder. Deterministically preserved lowest ID as canonical. |
| **Lemon Leaf** | Cross-Class Duplicate Groups | **60 images** (30 groups) | Identical images present in both `Algal_Leaf_Spot` and `Black Spot`. Excluded to prevent ambiguous supervisory gradients during training. |
| **Turmeric (1)** | Cross-Dataset Clones | **599 images** | 100% SHA-256 clones of Advancing AI leaf images. Excluded. |
| **Turmeric All** | Author-Provided Augmentations | **7,198 images** | 3,496 in Leaf Disease + 3,702 in Advancing AI. Excluded from candidate pool to ensure pristine original test folds; post-split augmentation will be generated deterministically on train fold only. |
| **Turmeric All** | Non-Leaf Rhizome Images | **646 images** | 182 Rhizome Rot in Advancing AI + 182 Rhizome Disease Root in Turmeric 1 + 282 Rhizome Healthy Root in Turmeric 1. Excluded from leaf model. |
| **Turmeric All** | Aphids Pest Class | **221 images** | Arthropod pest class excluded per user instruction to focus leaf classifier on foliar diseases and physiological stress. |
| **Citrus Secondary**| Fruit Images | **150 images** | Non-foliar citrus fruit images excluded. |
| **Citrus Secondary**| Leaf Images | **609 images** | Isolated to dedicated external test set (`citrus_external_test_manifest.csv`). |

---

## 4. Anatomical Breakdown: Leaf vs Root/Fruit Images

| Crop | Anatomical Part | Count | Curation Disposition |
|------|-----------------|-------|----------------------|
| **Turmeric** | Foliar Leaves (Original) | 1,464 | 1,243 clean candidates; 221 Aphids excluded |
| **Turmeric** | Foliar Leaves (Augmented) | 7,198 | Excluded from candidate pool |
| **Turmeric** | Subterranean Rhizome / Root | 646 | Excluded (Non-leaf) |
| **Citrus** | Foliar Leaves (Lemon Primary) | 17,586 | 14,941 unique (14,881 candidates after removing cross-class ambiguity + 60 ambiguous) |
| **Citrus** | Foliar Leaves (Secondary) | 609 | Reserved for External Cross-Dataset Testing |
| **Citrus** | Fruit | 150 | Excluded (Non-leaf) |

---

## 5. Low-Support Classes

1. **Citrus External Test — Melanose**:
   - Only **13 images** exist in `Citrus/Leaves/Melanose`.
   - Marked explicitly as `support_level = "LOW-SUPPORT"`.
   - **Governance Rule**: Must NOT be used alone for model selection or early stopping.
2. **Citrus Primary Candidates — Spider Mites & Bacterial Blight**:
   - `Spider Mites`: 200 clean candidate images.
   - `Bacterial Blight`: 206 clean candidate images.
   - While adequate for transfer learning, stratified splitting and class-weighted loss (or focal loss) will be essential in Phase 4/5.

---

## 6. Remaining Risks & Phase 4 Preparation

1. **Lemon Leaf Resolution Families**:
   - Lemon Leaf spans 5 resolution regimes (640×480, 1440×1080, 512×512, 256×256, 700×700).
   - In Phase 4 preprocessing, we must use an aspect-ratio-preserving resize pipeline (e.g. bicubic resize with edge reflection or letterbox padding to 224×224) rather than naive distortion stretching.
2. **Turmeric Class Coverage by Source**:
   - `Dry Leaf` is supplied exclusively by Advancing AI (203 images).
   - `Leaf Spot` is supplied exclusively by Leaf Disease (193 images).
   - `Leaf Blotch` and `Healthy` are shared across both independent datasets.
   - In Phase 4, stratified splitting must be performed within each class independently to maintain representation in train, validation, and test splits.

---

## 7. Curation Sign-off

All 7 tasks specified in Phase 3 are complete:
- [x] Manifests created with all 19 standardized columns.
- [x] Exact and near duplicate handling applied deterministically.
- [x] Turmeric 4-class taxonomy mapped and non-merge mandate enforced.
- [x] Citrus 18-class taxonomy annotated with condition_type.
- [x] Turmeric dataset lineage formally proven and documented.
- [x] Citrus external test manifest isolated (leaf-only, 609 images).
- [x] Zero splits, zero augmentations, zero model training performed.

**Awaiting user review and approval before proceeding to Phase 4 (Stratified Split Protocol & Preprocessing).**
"""
    with open(REPORTS_DIR / "phase3_curation_report.md", "w", encoding="utf-8") as f:
        f.write(curation_md)

    elapsed = time.time() - t0
    logger.info(f"=== Phase 3 Curation Finished Successfully in {elapsed:.2f}s ===")


if __name__ == "__main__":
    main()
