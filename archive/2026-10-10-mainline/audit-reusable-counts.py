"""Read-only cross-check of archived tile partitions against active full-patch counts."""

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "archive/2026-10-10-mainline/history/results/processed/sec33_crop_spatial_context"
PATCH = ROOT / "results/processed/sec33_reference_patch_types"
ACTIVE = ROOT / "results/processed/sec33_crop_spatial_context"


def load_index(path):
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    index = {}
    for row in rows:
        key = tuple(row[name] for name in ("kind", "model", "source", "target", "fold"))
        if key in index:
            raise AssertionError(f"duplicate prediction identity in {path}: {key}")
        index[key] = row
    return index


def main():
    tile_root = ACTIVE if (ACTIVE / "joint_counts_index.csv").exists() else ARCHIVE
    tiles = load_index(tile_root / "joint_counts_index.csv")
    patches = load_index(PATCH / "prediction_count_index.csv")
    if len(tiles) != 192 or tiles.keys() != patches.keys():
        raise AssertionError("12 within and 180 cross identities do not match")
    for key, tile_row in tiles.items():
        with np.load(tile_root / tile_row["file"]) as tile, np.load(PATCH / patches[key]["file"]) as patch:
            cm = tile["cm"]
            patch_cm = patch["type_band_bit_cm"]
            tile_ids = tile["patch_id"]
            if cm.shape != (400, 7, 8, 3, 3) or patch_cm.shape[1:] != (3, 7, 8, 3):
                raise AssertionError(f"unexpected count shape: {key}")
            if not np.issubdtype(cm.dtype, np.integer) or not np.issubdtype(patch_cm.dtype, np.integer):
                raise AssertionError(f"noninteger count array: {key}")
            if len(np.unique(tile_ids)) != 400 or np.any(cm < 0) or np.any(patch_cm < 0):
                raise AssertionError(f"bad tile identity or negative counts: {key}")
            # The first axis is only a 128x128 storage partition. The reference
            # patch tensor uses a separate full-landscape connected-component ID.
            tiled = cm.astype(np.int64).sum(axis=0)
            full_patch = patch_cm.astype(np.int64).sum(axis=0).transpose(1, 2, 0, 3)
            if not np.array_equal(tiled, full_patch):
                raise AssertionError(f"band/bitmask/true/predicted count mismatch: {key}")
    support_checks = verify_restored_support()
    print(json.dumps({"status": "Verified", "matched_predictions": len(tiles),
                      "within": sum(key[0] == "within" for key in tiles),
                      "cross": sum(key[0] == "cross" for key in tiles),
                      "comparison": "all 7x8x3x3 integer cells, tiled sum vs full-patch sum",
                      **support_checks}))


def read_table(relative):
    return pd.read_csv(ROOT / relative, float_precision="round_trip")


def unique_index(frame):
    if frame.duplicated(["target", "PID"]).any():
        raise AssertionError("duplicate reference identity")
    return frame.set_index(["target", "PID"]).sort_index()


def verify_restored_support():
    features = unique_index(read_table("results/processed/sec33_reference_patch_types/reference_patch_features.csv"))
    frozen = unique_index(read_table("results/processed/sec33_reference_patch_types/frozen_patch_assignments.csv"))
    candidates = unique_index(read_table("results/processed/sec33_reference_patch_types/cluster_candidates.csv"))
    k4 = unique_index(read_table("results/processed/sec33_k4_sensitivity/selected_assignments.csv"))
    grades = unique_index(read_table("results/processed/sec33_common_five_grades/patch_grade_assignments.csv"))
    crops = features[features.crop.isin(["corn", "soybean"])]
    if not frozen.index.equals(features.index):
        raise AssertionError("K2 frozen full reference identity mismatch")
    for frame in (candidates, k4, grades):
        if not frame.index.equals(crops.index):
            raise AssertionError("candidate/grade crop reference identity mismatch")
    for frame in (frozen, k4, grades):
        expected = features.loc[frame.index]
        for column in ("crop", "patch_uid", "reference_pixels", "boundary_pixels", "interior_pixels", "far_interior_pixels"):
            if not np.array_equal(frame[column].to_numpy(), expected[column].to_numpy()):
                raise AssertionError(f"reference attribute mismatch: {column}")
    if not np.array_equal(candidates.k2, frozen.loc[crops.index, "spatial_type"]) or not np.array_equal(candidates.k4, k4.k4):
        raise AssertionError("restored assignments disagree with original candidates")
    tables = [
        (frozen.loc[crops.index], read_table("results/summary/sec33_reference_patch_types/type_reference_support.csv")),
        (k4, read_table("results/summary/sec33_k4_sensitivity/type_reference_support.csv")),
    ]
    checked_type_groups = 0
    for assigned, support in tables:
        if "domain" in support:
            support = support[support.domain == "site_crop"]
        actual = assigned.reset_index().groupby(["target", "crop", "spatial_type"]).agg(n_patches=("PID", "size"), pixels=("reference_pixels", "sum"))
        expected = support.set_index(["target", "crop", "spatial_type"])[["n_patches", "pixels"]].sort_index()
        pd.testing.assert_frame_equal(actual.sort_index(), expected, check_dtype=False)
        checked_type_groups += len(expected)
    support = read_table("results/summary/sec33_common_five_grades/grade_support.csv")
    checked_grade_groups = 0
    for scheme in support.scheme.unique():
        for metric in support.metric.unique():
            column = f"{metric}_{scheme}_number"
            if not grades[column].isin([1, 2, 3, 4, 5]).all():
                raise AssertionError("missing or invalid grade assignment")
            grouped = grades.reset_index().groupby(["target", "crop", column]).agg(
                n_patches=("PID", "size"), pixels=("reference_pixels", "sum"),
                boundary_pixels=("boundary_pixels", "sum"), interior_pixels=("interior_pixels", "sum"),
                far_interior_pixels=("far_interior_pixels", "sum"))
            grouped.index.names = ["target", "crop", "grade_number"]
            selected = support[(support.scheme == scheme) & (support.metric == metric)]
            expected = selected[selected.domain == "site_crop"].set_index(["target", "crop", "grade_number"])[grouped.columns]
            pd.testing.assert_frame_equal(grouped.sort_index(), expected.sort_index(), check_dtype=False)
            whole = selected[selected.domain == "all"].set_index("grade_number")[grouped.columns]
            pd.testing.assert_frame_equal(grouped.groupby(level="grade_number").sum().sort_index(), whole.sort_index(), check_dtype=False)
            if not (selected.scheme_status == "pending_author_review_not_frozen").all():
                raise AssertionError("grade candidate approval status changed")
            checked_grade_groups += len(expected) + len(whole)
    return {"reference_patches": len(features), "crop_patches": len(crops),
            "type_support_groups": checked_type_groups, "grade_support_groups": checked_grade_groups,
            "grade_status": "pending_author_review_not_frozen"}


if __name__ == "__main__":
    main()
