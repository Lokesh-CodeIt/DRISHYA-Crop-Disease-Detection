#!/usr/bin/env python3
"""
zip_image_reader.py — LeafLens ZIP-Aware Image Reader

All LeafLens datasets are stored in ZIP archives (some nested).
This module provides a single function to read any image by its
virtual path (the absolute_path stored in the split CSV files),
which uses the format:

  /path/to/archive.zip#inner/path/to/image.jpg          (single ZIP)
  /path/to/outer.zip#inner.zip#path/to/image.jpg         (2-level nested)
  /path/to/outer.zip#mid/path/inner.zip#path/image.jpg   (nested with prefix)

Thread-safety: open_image_bytes() opens a fresh ZipFile handle each
call, which is safe for use in multi-worker DataLoaders.

For training throughput, outer ZipFile objects are cached (LRU) by
file path so that the ZIP's central directory is not re-parsed on
every sample. Cached handles are read-only.
"""

import os
from pathlib import Path
import io
import zipfile
from functools import lru_cache
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def resolve_zip_path(raw_path: str) -> str:
    """
    Resolve zip file path.
    1. If raw_path exists directly on disk (local Windows environment), use it.
    2. Otherwise, check relative to PROJECT_ROOT / 'DATASET' / filename (Google Colab / Linux).
    3. Otherwise, check os.environ.get('DATASET_DIR') / filename.
    4. Otherwise, check current working directory DATASET / filename.
    """
    if os.path.exists(raw_path):
        return raw_path

    filename = Path(raw_path).name
    colab_path = PROJECT_ROOT / "DATASET" / filename
    if colab_path.exists():
        return str(colab_path)

    env_dataset = os.environ.get("DATASET_DIR")
    if env_dataset:
        env_path = Path(env_dataset) / filename
        if env_path.exists():
            return str(env_path)

    cwd_path = Path.cwd() / "DATASET" / filename
    if cwd_path.exists():
        return str(cwd_path)

    return raw_path


@lru_cache(maxsize=16)
def _open_zip(zip_path: str) -> zipfile.ZipFile:
    """Open and cache a ZipFile handle (read-only). LRU with capacity 16."""
    return zipfile.ZipFile(resolve_zip_path(zip_path), "r")


@lru_cache(maxsize=16)
def _open_inner_zip(outer_zip_path: str, inner_zip_name: str) -> zipfile.ZipFile:
    """Cache inner ZipFile handles in memory to avoid re-extracting and re-parsing inner ZIPs."""
    outer = _open_zip(outer_zip_path)
    inner_bytes = io.BytesIO(outer.read(inner_zip_name))
    return zipfile.ZipFile(inner_bytes, "r")


@lru_cache(maxsize=16)
def _open_nested_zip(outer_zip_path: str, mid_zip_name: str, inner_zip_name: str) -> zipfile.ZipFile:
    """Cache 3-level nested ZipFile handles."""
    mid = _open_inner_zip(outer_zip_path, mid_zip_name)
    inner_bytes = io.BytesIO(mid.read(inner_zip_name))
    return zipfile.ZipFile(inner_bytes, "r")


def open_image_bytes(virtual_path: str) -> bytes:
    """
    Read image bytes from a virtual ZIP path.

    Supports:
      - Single ZIP:   /a.zip#inner/path.jpg
      - Double ZIP:   /a.zip#b.zip#inner/path.jpg        (b.zip is at root of a.zip)
      - Double ZIP:   /a.zip#prefix/b.zip#inner/path.jpg (b.zip has a path prefix in a.zip)

    Returns raw image bytes.
    """
    segs = virtual_path.split(".zip#")
    n = len(segs)

    if n == 2:
        # ── Single ZIP ─────────────────────────────────────────────────
        zip_path = segs[0] + ".zip"
        inner    = segs[1]
        zf = _open_zip(zip_path)
        return zf.read(inner)

    elif n == 3:
        # ── Double ZIP ─────────────────────────────────────────────────
        outer_zip_path = segs[0] + ".zip"
        inner_zip_name = segs[1] + ".zip"   # path of inner zip inside outer
        image_path     = segs[2]

        inner_zf = _open_inner_zip(outer_zip_path, inner_zip_name)
        return inner_zf.read(image_path)

    elif n == 4:
        # ── Triple ZIP ─────────────────────────────────────────────────
        outer_zip_path = segs[0] + ".zip"
        mid_zip_name   = segs[1] + ".zip"
        inner_zip_name = segs[2] + ".zip"
        image_path     = segs[3]

        inner_zf = _open_nested_zip(outer_zip_path, mid_zip_name, inner_zip_name)
        return inner_zf.read(image_path)

    else:
        raise ValueError(
            f"Unsupported ZIP nesting depth ({n - 1} levels): {virtual_path}"
        )


def open_pil_image(virtual_path: str) -> Image.Image:
    """
    Open and return a PIL Image (converted to RGB) from a virtual ZIP path.
    This is the primary entry point for the PyTorch Dataset __getitem__.
    """
    raw = open_image_bytes(virtual_path)
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    return img
