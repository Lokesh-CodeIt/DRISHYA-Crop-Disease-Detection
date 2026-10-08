#!/usr/bin/env python3
"""extract_book_chapter_results.py - extracts real DRISHYA book chapter values."""
import sys, json, csv, io
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(r".")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

CACHE_DIR = PROJECT_ROOT / "ml" / "calibration" / "cache"
CALIB_DIR = PROJECT_ROOT / "ml" / "calibration"
MODELS_DIR = PROJECT_ROOT / "ml" / "models"
SPLITS_DIR = PROJECT_ROOT / "data" / "metadata" / "splits"
DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_DIR.mkdir(exist_ok=True)

def softmax(x):
    e = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e / np.sum(e, axis=-1, keepdims=True)

def ece_10bin(probs, labels):
    n_bins = 10; edges = np.linspace(0, 1, n_bins + 1)
    conf = np.max(probs, axis=1); preds = np.argmax(probs, axis=1)
    correct = (preds == labels).astype(float); ece = 0.0; bins = []
    for i in range(n_bins):
        lo, hi = edges[i], edges[i + 1]
        mask = (conf >= lo) & (conf < hi if i < n_bins - 1 else conf <= hi)
        n = int(mask.sum())
        if n > 0:
            ba = float(correct[mask].mean()); bc = float(conf[mask].mean())
            gap = abs(ba - bc); ece += (n / len(labels)) * gap
            bins.append({"bin_index": i, "bin_lower": round(lo,4), "bin_upper": round(hi,4),
                         "sample_count": n, "bin_accuracy": round(ba,6), "bin_confidence": round(bc,6), "calibration_gap": round(gap,6)})
        else:
            bins.append({"bin_index": i, "bin_lower": round(lo,4), "bin_upper": round(hi,4),
                         "sample_count": 0, "bin_accuracy": None, "bin_confidence": None, "calibration_gap": 0.0})
    return {"ece": float(ece), "n_bins": 10, "bins": bins}

def metrics_full(logits, labels, classes, T=1.0):
    probs = softmax(logits / T); preds = np.argmax(probs, axis=1)
    acc = float(accuracy_score(labels, preds))
    mf1 = float(f1_score(labels, preds, average="macro", zero_division=0))
    mp = float(precision_score(labels, preds, average="macro", zero_division=0))
    mr = float(recall_score(labels, preds, average="macro", zero_division=0))
    pp = precision_score(labels, preds, average=None, zero_division=0)
    rp = recall_score(labels, preds, average=None, zero_division=0)
    fp = f1_score(labels, preds, average=None, zero_division=0)
    sup = np.bincount(labels, minlength=len(classes))
    per = {c: {"precision": float(pp[i]), "recall": float(rp[i]), "f1": float(fp[i]), "support": int(sup[i])} for i, c in enumerate(classes)}
    return {"accuracy": acc, "macro_f1": mf1, "macro_precision": mp, "macro_recall": mr,
            "per_class": per, "ece_10bin": ece_10bin(probs, labels), "n_samples": len(labels), "T": T}

def make_ser(o):
    if isinstance(o, np.integer): return int(o)
    if isinstance(o, np.floating): return float(o)
    if isinstance(o, np.ndarray): return o.tolist()
    if isinstance(o, dict): return {k: make_ser(v) for k, v in o.items()}
    if isinstance(o, list): return [make_ser(v) for v in o]
    return o

print("="*70); print("DRISHYA Book Chapter Results Extraction"); print("="*70)
R = {}

print("[1] Turmeric cached logits...")
tv = np.load(CACHE_DIR / "turmeric_val_logits.npz", allow_pickle=True)
tt = np.load(CACHE_DIR / "turmeric_test_logits.npz", allow_pickle=True)
tc = list(tv["classes"]); tT = float(json.load(open(CALIB_DIR / "turmeric_temperature.json"))["temperature"])
R["turmeric"] = {"arch": "ConvNeXt-Tiny", "seed": 42, "classes": tc, "T": tT,
    "val": {"raw": metrics_full(tv["logits"], tv["labels"], tc, 1.0), "cal": metrics_full(tv["logits"], tv["labels"], tc, tT)},
    "test": {"raw": metrics_full(tt["logits"], tt["labels"], tc, 1.0), "cal": metrics_full(tt["logits"], tt["labels"], tc, tT)}}
r = R["turmeric"]["test"]["raw"]
print(f"  Acc={r['accuracy']:.6f} F1={r['macro_f1']:.6f} P={r['macro_precision']:.6f} Rec={r['macro_recall']:.6f} N={r['n_samples']}")

print("[2] Citrus cached logits...")
cv = np.load(CACHE_DIR / "citrus_val_logits.npz", allow_pickle=True)
ct = np.load(CACHE_DIR / "citrus_test_logits.npz", allow_pickle=True)
cc = list(cv["classes"]); cT = float(json.load(open(CALIB_DIR / "citrus_temperature.json"))["temperature"])
R["citrus"] = {"arch": "EfficientNetV2-S", "seed": 42, "classes": cc, "T": cT,
    "val": {"raw": metrics_full(cv["logits"], cv["labels"], cc, 1.0), "cal": metrics_full(cv["logits"], cv["labels"], cc, cT)},
    "test": {"raw": metrics_full(ct["logits"], ct["labels"], cc, 1.0), "cal": metrics_full(ct["logits"], ct["labels"], cc, cT)}}
r = R["citrus"]["test"]["raw"]
print(f"  Acc={r['accuracy']:.6f} F1={r['macro_f1']:.6f} P={r['macro_precision']:.6f} Rec={r['macro_recall']:.6f} N={r['n_samples']}")

print("[3] Cross-dataset: Citrus external test...")
from backend.app.ml.registry import get_active_model_config
from backend.app.ml.model_builder import load_trained_model
from ml.scripts.zip_image_reader import open_pil_image
from backend.app.preprocessing.image_pipeline import preprocess_image_bytes
import time

cc2idx = {c: i for i, c in enumerate(cc)}
ecfg = get_active_model_config("citrus"); cmodel, _ = load_trained_model(ecfg, map_location="cpu"); cmodel.eval()
edf = pd.read_csv(SPLITS_DIR / "citrus_external_test.csv")
elogits, elabels, eseen, eskip = [], [], set(), 0
for _, row in edf.iterrows():
    clsn = str(row["final_class"])
    if clsn not in cc2idx: eskip += 1; continue
    try:
        pil = open_pil_image(str(row["absolute_path"])); buf = io.BytesIO(); pil.save(buf, format="JPEG")
        tens = preprocess_image_bytes(buf.getvalue(), crop="citrus")
        with torch.no_grad(): lg = cmodel(tens).squeeze(0).numpy()
        elogits.append(lg); elabels.append(cc2idx[clsn]); eseen.add(clsn)
    except Exception as ex: eskip += 1
print(f"  External: {len(elogits)} ok, {eskip} skipped")
if len(elogits) > 0:
    elognp = np.array(elogits, dtype=np.float32); elabnp = np.array(elabels, dtype=np.int64)
    sc = sorted(eseen); sidx = [cc2idx[c] for c in sc]
    mask = np.isin(elabnp, sidx); slogs = elognp[mask]; slab_raw = elabnp[mask]
    remap = {old: new for new, old in enumerate(sidx)}
    slab = np.array([remap[l] for l in slab_raw])
    sprobs = softmax(slogs[:, sidx]); spreds = np.argmax(sprobs, axis=1)
    ca = float(accuracy_score(slab, spreds)); cf = float(f1_score(slab, spreds, average="macro", zero_division=0))
    sp2 = precision_score(slab, spreds, average=None, zero_division=0)
    sr2 = recall_score(slab, spreds, average=None, zero_division=0)
    sf2 = f1_score(slab, spreds, average=None, zero_division=0)
    ss2 = np.bincount(slab, minlength=len(sc))
    cpc = {c: {"precision": float(sp2[i]), "recall": float(sr2[i]), "f1": float(sf2[i]), "support": int(ss2[i])} for i, c in enumerate(sc)}
    in_f1 = R["citrus"]["test"]["raw"]["macro_f1"]; drop = (in_f1 - cf) / in_f1 * 100
    print(f"  5-class: Acc={ca:.6f} F1={cf:.6f} Drop={drop:.1f}%")
    R["citrus"]["cross_dataset"] = {"n_external": len(elogits), "shared_classes": sc, "n_shared": int(mask.sum()),
        "accuracy": ca, "macro_f1": cf, "indataset_macro_f1": in_f1, "pct_drop": round(drop, 2), "per_class": cpc}
R["turmeric"]["cross_dataset"] = {"status": "NOT_AVAILABLE",
    "reason": "Source-separated training (TURM_CROSS_B_TO_A, TURM_CROSS_A_TO_B) not run."}

print("[4] Deployment metrics...")
def fsize(p): return round(p.stat().st_size / (1024*1024), 2)
def nparams(m): return sum(p.numel() for p in m.parameters())
def cpu_timing(m, sz, n=50):
    m.eval(); d = torch.randn(1, 3, sz, sz)
    with torch.no_grad(): [m(d) for _ in range(5)]
    ts = []
    with torch.no_grad():
        for _ in range(n): t0 = time.perf_counter(); m(d); ts.append((time.perf_counter()-t0)*1000)
    return {"median_ms": round(float(np.median(ts)),2), "mean_ms": round(float(np.mean(ts)),2),
            "std_ms": round(float(np.std(ts)),2), "n_runs": n}
tpath = MODELS_DIR/"turmeric"/"convnext_tiny"/"seed_42"/"best_model.pt"
cpath = MODELS_DIR/"citrus"/"efficientnet_v2_s"/"seed_42"/"best_model.pt"
tcfg = get_active_model_config("turmeric"); tmodel, _ = load_trained_model(tcfg, map_location="cpu"); tmodel.eval()
tp = nparams(tmodel); cp = nparams(cmodel)
print(f"  Turmeric {tp:,} params; Citrus {cp:,} params")
ttim = cpu_timing(tmodel, 224); ctim = cpu_timing(cmodel, 384)
print(f"  T median={ttim['median_ms']}ms C median={ctim['median_ms']}ms")
R["deployment"] = {
    "turmeric": {"checkpoint": str(tpath), "file_size_mb": fsize(tpath), "total_parameters": tp,
        "total_parameters_M": round(tp/1e6,2), "img_size": 224, "runtime": "PyTorch CPU torch.no_grad()", "cpu_inference_ms": ttim},
    "citrus": {"checkpoint": str(cpath), "file_size_mb": fsize(cpath), "total_parameters": cp,
        "total_parameters_M": round(cp/1e6,2), "img_size": 384, "runtime": "PyTorch CPU torch.no_grad()", "cpu_inference_ms": ctim}}

print("[5] Calibration...")
cr = json.load(open(CALIB_DIR / "calibration_report.json"))
R["calibration"] = {
    "turmeric": {"temperature": tT, "val_ece_before": cr["crops"]["turmeric"]["validation_split"]["ece_before"],
        "val_ece_after": cr["crops"]["turmeric"]["validation_split"]["ece_after"],
        "test_ece_before": cr["crops"]["turmeric"]["test_split"]["ece_before"],
        "test_ece_after": cr["crops"]["turmeric"]["test_split"]["ece_after"],
        "test_nll_before": cr["crops"]["turmeric"]["test_split"]["nll_before"],
        "test_nll_after": cr["crops"]["turmeric"]["test_split"]["nll_after"]},
    "citrus": {"temperature": cT, "val_ece_before": cr["crops"]["citrus"]["validation_split"]["ece_before"],
        "val_ece_after": cr["crops"]["citrus"]["validation_split"]["ece_after"],
        "test_ece_before": cr["crops"]["citrus"]["test_split"]["ece_before"],
        "test_ece_after": cr["crops"]["citrus"]["test_split"]["ece_after"],
        "test_nll_before": cr["crops"]["citrus"]["test_split"]["nll_before"],
        "test_nll_after": cr["crops"]["citrus"]["test_split"]["nll_after"]}}

print("[6] 10-bin reliability...")
fig71 = {}
for key, lgs, lbs, T in [
    ("turmeric_test_uncal", tt["logits"], tt["labels"], 1.0),
    ("turmeric_test_cal", tt["logits"], tt["labels"], tT),
    ("citrus_test_uncal", ct["logits"], ct["labels"], 1.0),
    ("citrus_test_cal", ct["logits"], ct["labels"], cT)]:
    fig71[key] = ece_10bin(softmax(lgs/T), lbs)
    print(f"  {key}: ECE={fig71[key]['ece']:.6f}")
R["figure_7_1"] = fig71

R["not_available"] = {
    "Table_7_4_turmeric": {"reason": "No source-separated checkpoint. Need TURM_CROSS_B_TO_A and TURM_CROSS_A_TO_B experiments."},
    "Table_7_1_3seed_mean_sd": {"reason": "Only seed=42 present. Seeds 123,7 not in ml/models/."},
    "Table_7_6_gradcam": {"reason": "Grad-CAM++ not implemented. No lesion GT annotations. No pointing-game or background-masking experiment."}}

print("[7] Saving...")
out_json = DOCS_DIR / "book_chapter_results.json"
json.dump(make_ser(R), open(out_json, "w", encoding="utf-8"), indent=2)
print(f"  {out_json}")
rel_out = DOCS_DIR / "book_chapter_reliability_data.json"
json.dump({"generated_at": datetime.now(timezone.utc).isoformat(),
           "description": "10-bin reliability for Figure 7.1",
           "data": make_ser(fig71)}, open(rel_out, "w", encoding="utf-8"), indent=2)
print(f"  {rel_out}")

csv_rows = []
def ar(tab, crop, arch, seed, spl, metric, raw, rnd, unit, src, T=None):
    row = {"table": tab, "crop": crop, "architecture": arch, "seed": seed, "split": spl,
           "metric": metric, "raw_value": raw, "rounded_value": rnd, "unit": unit, "source": src}
    if T is not None: row["temperature"] = T
    csv_rows.append(row)
for crop, arch in [("turmeric","ConvNeXt-Tiny"),("citrus","EfficientNetV2-S")]:
    r = R[crop]["test"]["raw"]; s = f"ml/calibration/cache/{crop}_test_logits.npz"
    ar("7.1",crop,arch,42,"test","accuracy",r["accuracy"],round(r["accuracy"]*100,2),"%",s,1.0)
    ar("7.1",crop,arch,42,"test","macro_f1",r["macro_f1"],round(r["macro_f1"],4),"score",s,1.0)
    ar("7.1",crop,arch,42,"test","macro_precision",r["macro_precision"],round(r["macro_precision"],4),"score",s,1.0)
    ar("7.1",crop,arch,42,"test","macro_recall",r["macro_recall"],round(r["macro_recall"],4),"score",s,1.0)
for cls, m in R["turmeric"]["test"]["raw"]["per_class"].items():
    s = "ml/calibration/cache/turmeric_test_logits.npz"
    ar("7.2","turmeric","ConvNeXt-Tiny",42,"test",f"{cls}_precision",m["precision"],round(m["precision"],4),"score",s,1.0)
    ar("7.2","turmeric","ConvNeXt-Tiny",42,"test",f"{cls}_recall",m["recall"],round(m["recall"],4),"score",s,1.0)
    ar("7.2","turmeric","ConvNeXt-Tiny",42,"test",f"{cls}_f1",m["f1"],round(m["f1"],4),"score",s,1.0)
    ar("7.2","turmeric","ConvNeXt-Tiny",42,"test",f"{cls}_support",m["support"],m["support"],"count",s,1.0)
for cls, m in R["citrus"]["test"]["raw"]["per_class"].items():
    s = "ml/calibration/cache/citrus_test_logits.npz"
    ar("7.3","citrus","EfficientNetV2-S",42,"test",f"{cls}_precision",m["precision"],round(m["precision"],4),"score",s,1.0)
    ar("7.3","citrus","EfficientNetV2-S",42,"test",f"{cls}_recall",m["recall"],round(m["recall"],4),"score",s,1.0)
    ar("7.3","citrus","EfficientNetV2-S",42,"test",f"{cls}_f1",m["f1"],round(m["f1"],4),"score",s,1.0)
    ar("7.3","citrus","EfficientNetV2-S",42,"test",f"{cls}_support",m["support"],m["support"],"count",s,1.0)
if "cross_dataset" in R["citrus"] and "macro_f1" in R["citrus"]["cross_dataset"]:
    xd = R["citrus"]["cross_dataset"]
    ar("7.4","citrus","EfficientNetV2-S",42,"test_indataset","macro_f1",xd["indataset_macro_f1"],round(xd["indataset_macro_f1"],4),"score","cache/citrus_test_logits.npz")
    ar("7.4","citrus","EfficientNetV2-S",42,"ext_5class","macro_f1",xd["macro_f1"],round(xd["macro_f1"],4),"score","data/metadata/splits/citrus_external_test.csv")
    ar("7.4","citrus","EfficientNetV2-S",42,"ext_5class","pct_drop",xd["pct_drop"],round(xd["pct_drop"],1),"%","computed")
for crop in ["turmeric","citrus"]:
    c = R["calibration"][crop]; s = "ml/calibration/calibration_report.json"
    ar("7.5",crop,"",42,"test","temperature_T",c["temperature"],round(c["temperature"],6),"scalar",f"ml/calibration/{crop}_temperature.json")
    ar("7.5",crop,"",42,"test","ece_before",c["test_ece_before"],round(c["test_ece_before"],4),"score",s)
    ar("7.5",crop,"",42,"test","ece_after",c["test_ece_after"],round(c["test_ece_after"],4),"score",s)
    ar("7.5",crop,"",42,"val","ece_before",c["val_ece_before"],round(c["val_ece_before"],4),"score",s)
    ar("7.5",crop,"",42,"val","ece_after",c["val_ece_after"],round(c["val_ece_after"],4),"score",s)
for crop in ["turmeric","citrus"]:
    d = R["deployment"][crop]
    ar("7.7",crop,"",42,"production","file_size_mb",d["file_size_mb"],d["file_size_mb"],"MB",d["checkpoint"])
    ar("7.7",crop,"",42,"production","parameters_M",d["total_parameters_M"],d["total_parameters_M"],"M",d["checkpoint"])
    ar("7.7",crop,"",42,"production","cpu_median_ms",d["cpu_inference_ms"]["median_ms"],d["cpu_inference_ms"]["median_ms"],"ms","live 50-run benchmark")
    ar("7.7",crop,"",42,"production","cpu_std_ms",d["cpu_inference_ms"]["std_ms"],d["cpu_inference_ms"]["std_ms"],"ms","live 50-run benchmark")
csv_out = DOCS_DIR / "book_chapter_results.csv"
with open(csv_out,"w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys())); w.writeheader(); w.writerows(csv_rows)
print(f"  {csv_out}")

print("="*70); print("SUMMARY"); print("="*70)
for crop in ["turmeric","citrus"]:
    r = R[crop]["test"]["raw"]
    print(f"{crop.upper()}: Acc={r['accuracy']*100:.2f}% F1={r['macro_f1']:.4f} P={r['macro_precision']:.4f} Rec={r['macro_recall']:.4f} N={r['n_samples']}")
print("\nTURMERIC per-class:")
for cls,m in R["turmeric"]["test"]["raw"]["per_class"].items():
    print(f"  {cls}: P={m['precision']:.4f} R={m['recall']:.4f} F1={m['f1']:.4f} N={m['support']}")
print("\nCITRUS per-class:")
for cls,m in R["citrus"]["test"]["raw"]["per_class"].items():
    print(f"  {cls}: P={m['precision']:.4f} R={m['recall']:.4f} F1={m['f1']:.4f} N={m['support']}")
if "cross_dataset" in R["citrus"] and "macro_f1" in R["citrus"]["cross_dataset"]:
    xd = R["citrus"]["cross_dataset"]
    print(f"\nCITRUS cross-dataset: in={xd['indataset_macro_f1']:.4f} cross={xd['macro_f1']:.4f} drop={xd['pct_drop']:.1f}% N={xd['n_shared']}")
    for cls,m in xd["per_class"].items():
        print(f"  {cls}: P={m['precision']:.4f} R={m['recall']:.4f} F1={m['f1']:.4f} N={m['support']}")
print("\nCalibration:")
for crop in ["turmeric","citrus"]:
    c = R["calibration"][crop]
    print(f"  {crop}: T={c['temperature']:.6f} ECE_before={c['test_ece_before']:.4f} ECE_after={c['test_ece_after']:.4f}")
print("\nDeployment:")
for crop in ["turmeric","citrus"]:
    d = R["deployment"][crop]; t = d["cpu_inference_ms"]
    print(f"  {crop}: {d['file_size_mb']}MB {d['total_parameters_M']}M params CPU {t['median_ms']}ms +/-{t['std_ms']}ms")
print("\nFig 7.1 10-bin ECE:")
for k,v in fig71.items():
    print(f"  {k}: ECE={v['ece']:.6f}")
print("\nNOT AVAILABLE:")
for k,v in R["not_available"].items():
    print(f"  {k}: {v['reason']}")
print("\nDone.")
