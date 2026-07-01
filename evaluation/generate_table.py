#!/usr/bin/env python3
"""
Generate results tables comparing computed BOP19 metrics against
the paper's reported values (TABLE V and TABLE VI).

Reads from eval/ directories and outputs:
  1. TABLE V equivalent: Overall AR, ADD, MSPD, MSSD, VSD per method/split
  2. TABLE VI equivalent: Per-object AR per method/split
"""
import json
import glob
import os
import sys
import numpy as np

EVAL_DIR = "eval"

# ============================================================================
# Paper reference values from TABLE V and TABLE VI (image provided by user)
# ============================================================================

# TABLE V: Overall metrics per method
# Format: {eval_name: {metric: value}}
PAPER_TABLE_V = {
    # -- Classic --
    "epos_isclassic":       {"add": 0.64, "mspd": 0.54, "mssd": 0.56, "vsd": 0.41, "ar": 0.51},
    "dope_isclassic":       {"add": 0.13, "mspd": 0.09, "mssd": 0.09, "vsd": 0.05, "ar": 0.08},
    "zebrapose_isclassic":  {"add": 0.61, "mspd": 0.54, "mssd": 0.55, "vsd": 0.40, "ar": 0.50},
    "foundpose_isclassic":  {"add": 0.55, "mspd": 0.31, "mssd": 0.39, "vsd": 0.22, "ar": 0.30},
    "fpmb_isclassic":       {"add": 0.78, "mspd": 0.73, "mssd": 0.74, "vsd": 0.53, "ar": 0.67},
    "fpmf_isclassic":       {"add": 0.44, "mspd": 0.26, "mssd": 0.31, "vsd": 0.18, "ar": 0.25},
    "vagdope_isclassic":    {"add": 0.13, "mspd": 0.09, "mssd": 0.09, "vsd": 0.05, "ar": 0.08},
    "vagbop_isclassic":     {"add": 0.13, "mspd": 0.09, "mssd": 0.09, "vsd": 0.05, "ar": 0.08},
    # -- Extended --
    "epos_isextended":       {"add": None, "mspd": None, "mssd": None, "vsd": None, "ar": None},
    "dope_isextended":       {"add": None, "mspd": None, "mssd": None, "vsd": None, "ar": None},
    "zebrapose_isextended":  {"add": None, "mspd": None, "mssd": None, "vsd": None, "ar": None},
    "foundpose_isextended":  {"add": 0.34, "mspd": 0.41, "mssd": 0.25, "vsd": 0.18, "ar": 0.28},
    "fpmb_isextended":       {"add": 0.81, "mspd": 0.83, "mssd": 0.74, "vsd": 0.50, "ar": 0.69},
    "fpmf_isextended":       {"add": 0.48, "mspd": 0.40, "mssd": 0.37, "vsd": 0.22, "ar": 0.33},
}

# TABLE VI: Per-object AR  (mean of VSD, MSSD, MSPD)
# Format: {eval_name: {obj_id_str: value}}
PAPER_TABLE_VI = {
    # -- Classic --
    "epos_isclassic":       {"1": 0.66, "2": 0.26, "3": 0.59, "4": 0.25, "5": 0.00},
    "dope_isclassic":       {"1": 0.18, "2": 0.05, "3": 0.03, "4": 0.10, "5": 0.00},
    "zebrapose_isclassic":  {"1": 0.84, "2": 0.11, "3": 0.49, "4": 0.39, "5": 0.11},
    "foundpose_isclassic":  {"1": 0.43, "2": 0.34, "3": 0.25, "4": 0.11, "5": 0.15},
    "fpmb_isclassic":       {"1": 0.78, "2": 0.49, "3": 0.64, "4": 0.47, "5": 0.31},
    "fpmf_isclassic":       {"1": 0.53, "2": 0.32, "3": 0.12, "4": 0.09, "5": 0.23},
    "dope_isclassic":       {"1": 0.18, "2": 0.05, "3": 0.03, "4": 0.10, "5": 0.00},
    # -- Extended --
    "foundpose_isextended":  {"1": 0.48, "2": 0.17, "3": 0.13, "4": 0.23, "5": 0.04},
    "fpmb_isextended":       {"1": 0.79, "2": 0.54, "3": 0.42, "4": 0.54, "5": 0.56},
    "fpmf_isextended":       {"1": 0.47, "2": 0.26, "3": 0.07, "4": 0.02, "5": 0.38},
}

# ============================================================================
# Compute metrics from eval directories
# ============================================================================

def load_overall_scores(eval_name):
    """Load scores_bop19.json for a given eval directory."""
    path = os.path.join(EVAL_DIR, f"{eval_name}-test", "scores_bop19.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        d = json.load(f)
    return {
        "ar":   d.get("bop19_average_recall", 0),
        "add":  d.get("bop19_average_recall_add", 0),
        "mspd": d.get("bop19_average_recall_mspd", 0),
        "mssd": d.get("bop19_average_recall_mssd", 0),
        "vsd":  d.get("bop19_average_recall_vsd", 0),
    }


def load_per_object_ar(eval_name, metrics=("vsd", "mssd", "mspd")):
    """
    Load per-object AR (mean of metrics across thresholds, then mean of metrics).
    Returns dict: {obj_id_str: ar_value}
    """
    eval_path = os.path.join(EVAL_DIR, f"{eval_name}-test")
    if not os.path.isdir(eval_path):
        return None

    # Gather all object IDs
    obj_ids = set()
    for metric in metrics:
        score_files = glob.glob(os.path.join(eval_path, f"error={metric}*", "scores_*.json"))
        for f in score_files:
            with open(f) as fh:
                data = json.load(fh)
                recalls = data.get("obj_recalls") or data.get("scores", {})
                obj_ids.update(recalls.keys())

    obj_ids = sorted(obj_ids, key=int)
    if not obj_ids:
        return None

    # Per-metric AR for each object (mean across thresholds)
    metric_results = {}
    for metric in metrics:
        score_files = glob.glob(os.path.join(eval_path, f"error={metric}*", "scores_*.json"))
        if not score_files:
            continue
        obj_recalls_all = {oid: [] for oid in obj_ids}
        for f in score_files:
            with open(f) as fh:
                data = json.load(fh)
                recalls = data.get("obj_recalls") or data.get("scores", {})
                for oid in obj_ids:
                    if oid in recalls:
                        obj_recalls_all[oid].append(recalls[oid])
        metric_results[metric] = {
            oid: np.mean(obj_recalls_all[oid]) if obj_recalls_all[oid] else 0.0
            for oid in obj_ids
        }

    # Mean across metrics
    per_obj_ar = {}
    for oid in obj_ids:
        vals = [metric_results[m][oid] for m in metric_results if oid in metric_results[m]]
        per_obj_ar[oid] = np.mean(vals) if vals else 0.0

    return per_obj_ar


def load_per_object_per_metric(eval_name, metrics=("add", "mspd", "mssd", "vsd")):
    """
    Load per-object AR for each individual metric.
    Returns dict: {metric: {obj_id_str: value}}
    """
    eval_path = os.path.join(EVAL_DIR, f"{eval_name}-test")
    if not os.path.isdir(eval_path):
        return None

    obj_ids = set()
    for metric in metrics:
        score_files = glob.glob(os.path.join(eval_path, f"error={metric}*", "scores_*.json"))
        for f in score_files:
            with open(f) as fh:
                data = json.load(fh)
                recalls = data.get("obj_recalls") or data.get("scores", {})
                obj_ids.update(recalls.keys())

    obj_ids = sorted(obj_ids, key=int)
    if not obj_ids:
        return None

    result = {}
    for metric in metrics:
        score_files = glob.glob(os.path.join(eval_path, f"error={metric}*", "scores_*.json"))
        if not score_files:
            continue
        obj_recalls_all = {oid: [] for oid in obj_ids}
        for f in score_files:
            with open(f) as fh:
                data = json.load(fh)
                recalls = data.get("obj_recalls") or data.get("scores", {})
                for oid in obj_ids:
                    if oid in recalls:
                        obj_recalls_all[oid].append(recalls[oid])
        result[metric] = {
            oid: np.mean(obj_recalls_all[oid]) if obj_recalls_all[oid] else 0.0
            for oid in obj_ids
        }
    return result, obj_ids


# ============================================================================
# Formatting helpers
# ============================================================================

def fmt(val, paper_val=None, precision=2):
    """Format a value, optionally with paper reference in parentheses."""
    if val is None:
        return "-"
    s = f"{val:.{precision}f}"
    if paper_val is not None:
        s += f" ({paper_val:.{precision}f})"
    return s


# ============================================================================
# Main
# ============================================================================

def main():
    # Discover all eval directories
    eval_dirs = sorted([
        d for d in os.listdir(EVAL_DIR)
        if os.path.isdir(os.path.join(EVAL_DIR, d))
    ])
    eval_names = [d.replace("-test", "") for d in eval_dirs]

    # All methods we want to show (computed + reported-only)
    ALL_CLASSIC = ["epos_isclassic", "dope_isclassic", "vagdope_isclassic", "vagbop_isclassic", "zebrapose_isclassic",
                   "foundpose_isclassic", "fpmb_isclassic", "fpmf_isclassic"]
    ALL_EXTENDED = ["foundpose_isextended", "fpmb_isextended", "fpmf_isextended"]

    def fmtv(val, precision=2):
        """Format a single value."""
        if val is None:
            return "-"
        return f"{val:.{precision}f}"

    # ============================
    # TABLE V: Overall Metrics
    # ============================
    print("=" * 110)
    print("TABLE V: Performance of baseline methods on IndustryShapes dataset")
    print("=" * 110)

    header = f"{'Method':<20} {'':>10} {'ADD':>8} {'MSPD':>8} {'MSSD':>8} {'VSD':>8} {'AR':>8}"
    sep = "-" * 78

    for split_label, all_methods in [("IndustryShapes Classic", ALL_CLASSIC),
                                      ("IndustryShapes Extended", ALL_EXTENDED)]:
        print(f"\n--- {split_label} ---")
        print(header)
        print(sep)
        for name in all_methods:
            method_label = name.split("_")[0]
            scores = load_overall_scores(name)
            paper = PAPER_TABLE_V.get(name, {})

            # Computed row
            if scores is not None:
                print(f"{method_label:<20} {'Computed':>10} "
                      f"{fmtv(scores['add']):>8} "
                      f"{fmtv(scores['mspd']):>8} "
                      f"{fmtv(scores['mssd']):>8} "
                      f"{fmtv(scores['vsd']):>8} "
                      f"{fmtv(scores['ar']):>8}")
            # Reported row
            if paper:
                print(f"{'':>20} {'Reported':>10} "
                      f"{fmtv(paper.get('add')):>8} "
                      f"{fmtv(paper.get('mspd')):>8} "
                      f"{fmtv(paper.get('mssd')):>8} "
                      f"{fmtv(paper.get('vsd')):>8} "
                      f"{fmtv(paper.get('ar')):>8}")
            if scores is None and not paper:
                print(f"{method_label:<20} {'':>10} {'(no data)':>8}")
            print()

    # ============================
    # TABLE VI: Per-Object AR
    # ============================
    print("\n" + "=" * 110)
    print("TABLE VI: Per-object Average Recall (AR = mean of VSD, MSSD, MSPD)")
    print("=" * 110)

    obj_ids_default = ["1", "2", "3", "4", "5"]

    for split_label, all_methods in [("IndustryShapes Classic", ALL_CLASSIC),
                                      ("IndustryShapes Extended", ALL_EXTENDED)]:
        print(f"\n--- {split_label} ---")

        obj_ids = obj_ids_default
        obj_header = f"{'Method':<20} {'':>10}" + "".join(f"{'Obj '+oid:>10}" for oid in obj_ids)
        print(obj_header)
        print("-" * (30 + 10 * len(obj_ids)))

        for name in all_methods:
            method_label = name.split("_")[0]
            ar = load_per_object_ar(name)
            paper = PAPER_TABLE_VI.get(name, {})

            if ar is not None:
                row = f"{method_label:<20} {'Computed':>10}"
                for oid in obj_ids:
                    row += f"{fmtv(ar.get(oid)):>10}"
                print(row)
            if paper:
                row = f"{'':>20} {'Reported':>10}"
                for oid in obj_ids:
                    row += f"{fmtv(paper.get(oid)):>10}"
                print(row)
            if ar is None and not paper:
                print(f"{method_label:<20} {'':>10} {'(no data)':>8}")
            print()

    # ============================
    # DETAILED: Per-Object Per-Metric
    # ============================
    print("\n" + "=" * 120)
    print("DETAILED: Per-object metrics (ADD, MSPD, MSSD, VSD) for each method")
    print("=" * 120)

    for split_label, all_methods in [("IndustryShapes Classic", ALL_CLASSIC),
                                      ("IndustryShapes Extended", ALL_EXTENDED)]:
        print(f"\n{'='*60}")
        print(f"  {split_label}")
        print(f"{'='*60}")

        for name in all_methods:
            result = load_per_object_per_metric(name)
            if result is None:
                continue
            per_metric, obj_ids = result
            method_label = name.split("_")[0]

            print(f"\n  --- {method_label} ---")
            metric_header = f"  {'Metric':<10}" + "".join(f"{'Obj '+oid:>10}" for oid in obj_ids) + f"{'Mean':>10}"
            print(metric_header)
            print(f"  " + "-" * (10 + 10 * (len(obj_ids) + 1)))

            for metric in ("add", "mspd", "mssd", "vsd"):
                if metric not in per_metric:
                    continue
                vals = [per_metric[metric].get(oid, 0.0) for oid in obj_ids]
                row = f"  {metric.upper():<10}"
                for v in vals:
                    row += f"{v:>10.2f}"
                row += f"{np.mean(vals):>10.2f}"
                print(row)

            # AR (mean of vsd, mssd, mspd)
            ar_vals = []
            for oid in obj_ids:
                mv = []
                for m in ("vsd", "mssd", "mspd"):
                    if m in per_metric:
                        mv.append(per_metric[m].get(oid, 0.0))
                ar_vals.append(np.mean(mv) if mv else 0.0)
            row = f"  {'AR':<10}"
            for v in ar_vals:
                row += f"{v:>10.2f}"
            row += f"{np.mean(ar_vals):>10.2f}"
            print(row)

            # Reported AR row from paper
            paper = PAPER_TABLE_VI.get(name, {})
            if paper:
                row = f"  {'Rep. AR':<10}"
                rep_vals = []
                for oid in obj_ids:
                    pv = paper.get(oid)
                    row += f"{fmtv(pv):>10}"
                    if pv is not None:
                        rep_vals.append(pv)
                if rep_vals:
                    row += f"{np.mean(rep_vals):>10.2f}"
                print(row)

    print()


if __name__ == "__main__":
    main()
