#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build verified reading tables for Sections 1.3 and 3.1.

This script only reads existing verified results. It does not run training,
inference, FRAGSTATS, distance calculations, clustering, or manuscript builds.
All outputs are created once in an independent summary directory so historical
scientific products are never overwritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


SITES = ("iw_2023", "iw2_2023", "ida_2023", "il_2023")
SITE_CODES = {"iw_2023": "A", "iw2_2023": "B", "ida_2023": "C", "il_2023": "D"}
MODELS = ("convgru", "unet3d", "utae")
CLASSES = ("corn", "other", "soybean")
CROPS = ("corn", "soybean")
CLASS_INDEX = {name: index for index, name in enumerate(CLASSES)}
FULL_SITE_PIXELS = 6_553_600
PIXEL_AREA_HA = 0.09
OUT_DIR = "results/summary/sec13_sec31_foundations"

INPUTS = {
    "reference_support": "results/summary/sec33_indicator_grading_preparation/all_class_reference_support.csv",
    "background_class": "results/summary/sec33_reference_patch_types/background_class.csv",
    "background_landscape": "results/summary/sec33_reference_patch_types/background_landscape.csv",
    "distribution": "results/summary/sec33_indicator_grading_preparation/indicator_distribution_reading.csv",
    "support_reading": "results/summary/sec33_indicator_grading_preparation/reference_support_reading.csv",
    "formal_within_f1": "results/summary/f1_raw_scale/within_site_crop_f1.csv",
    "within_metrics": "results/processed/sec33_directional_confusion_closeout/crop_metrics_per_prediction.csv",
    "directional_summary": "results/summary/sec33_directional_confusion_closeout/directional_summary.csv",
    "within_raw_cm": "results/raw/within_site_confusion_matrices.csv",
    "whole_cm": "results/processed/sec33_crop_spatial_context/whole_cm.csv",
    "f1_difference": "results/summary/f1_raw_scale/crop_f1_difference_36paths.csv",
    "case_crop_metrics": "results/summary/sec33_directional_confusion_closeout/case_B_D_ConvGRU_crop_metrics.csv",
    "case_distance": "results/summary/sec33_directional_confusion_closeout/case_D_distance_all_sources.csv",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def close(a, b, tolerance: float = 1e-12) -> bool:
    return bool(np.allclose(a, b, rtol=0, atol=tolerance, equal_nan=True))


def read_csv(root: Path, relative: str) -> pd.DataFrame:
    return pd.read_csv(root / relative, float_precision="round_trip")


def int_values(frame: pd.DataFrame, columns: list[str], label: str) -> pd.DataFrame:
    result = frame.copy()
    for column in columns:
        values = pd.to_numeric(result[column], errors="raise").to_numpy(dtype=float)
        require(np.isfinite(values).all() and (values >= 0).all() and (values == np.floor(values)).all(),
                f"{label}: {column} must contain nonnegative integers")
        result[column] = values.astype(np.int64)
    return result


def file_record(path: Path, root: Path) -> dict[str, object]:
    resolved = path.resolve()
    return {
        "path": resolved.relative_to(root.resolve()).as_posix(),
        "sha256": hashlib.sha256(resolved.read_bytes()).hexdigest(),
        "bytes": resolved.stat().st_size,
    }


def string_bool(value: object) -> bool:
    return str(value).strip().lower() == "true"


def sorted_sites(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    result = frame.copy()
    result["_site_order"] = result["target"].map({site: index for index, site in enumerate(SITES)})
    result["_model_order"] = result.get("model", pd.Series("", index=result.index)).map(
        {model: index for index, model in enumerate(MODELS)}
    ).fillna(-1)
    result["_crop_order"] = result.get("crop", result.get("true_class", pd.Series("", index=result.index))).map(
        {name: index for index, name in enumerate(CLASSES)}
    ).fillna(-1)
    return result.sort_values(["_site_order", "_model_order", "_crop_order", *columns], kind="stable").drop(
        columns=["_site_order", "_model_order", "_crop_order"], errors="ignore"
    )


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    with path.open("x", encoding="utf-8", newline="") as handle:
        frame.to_csv(handle, index=False, float_format="%.17g", lineterminator="\n")


def matrix_from_row(row: pd.Series, style: str) -> np.ndarray:
    if style == "raw":
        columns = [f"cm_{i}{j}" for i in range(3) for j in range(3)]
    elif style == "processed":
        columns = [f"cm_{i}_{j}" for i in range(3) for j in range(3)]
    else:
        raise ValueError(f"Unknown matrix style: {style}")
    values = np.asarray([row[column] for column in columns], dtype=np.int64)
    return values.reshape(3, 3)


def metric_values(matrix: np.ndarray, class_index: int) -> tuple[int, int, int, float, float, float]:
    tp = int(matrix[class_index, class_index])
    fn = int(matrix[class_index, :].sum() - tp)
    fp = int(matrix[:, class_index].sum() - tp)
    f1_denominator = 2 * tp + fn + fp
    precision_denominator = tp + fp
    recall_denominator = tp + fn
    f1 = (2 * tp / f1_denominator) if f1_denominator else np.nan
    precision = (tp / precision_denominator) if precision_denominator else np.nan
    recall = (tp / recall_denominator) if recall_denominator else np.nan
    return tp, fn, fp, f1, precision, recall


def build_reference_tables(tables: dict[str, pd.DataFrame], checks: list[dict[str, object]]) -> dict[str, pd.DataFrame]:
    support = int_values(tables["reference_support"], ["n_patches", "pixels", "boundary_pixels", "interior_pixels", "far_interior_pixels"],
                         "reference support")
    expected_support = {(site, crop) for site in SITES for crop in CLASSES}
    require(len(support) == 12 and not support.duplicated(["target", "crop"]).any(),
            "reference support: expected 12 unique target/crop rows")
    require(set(support[["target", "crop"]].itertuples(index=False, name=None)) == expected_support,
            "reference support: target/crop identities are incomplete")
    require((support["site"] == support["target"].map(SITE_CODES)).all(), "reference support: site code mismatch")
    require(close(support["area_ha"], support["pixels"] * PIXEL_AREA_HA), "reference support: area/pixel mismatch")
    support_totals = support.groupby("target", as_index=False).agg(total_pixels=("pixels", "sum"), total_area_ha=("area_ha", "sum"))
    require((support_totals["total_pixels"] == FULL_SITE_PIXELS).all(), "reference support: site total is not 6,553,600 pixels")
    require(close(support_totals["total_area_ha"], FULL_SITE_PIXELS * PIXEL_AREA_HA), "reference support: site area mismatch")
    composition = support.merge(support_totals, on="target", validate="many_to_one")
    composition["pixel_share"] = composition["pixels"] / composition["total_pixels"]
    composition["area_share"] = composition["area_ha"] / composition["total_area_ha"]
    composition["data_status"] = "derived_from_verified_summary"
    composition = composition[["target", "site", "crop", "pixels", "area_ha", "total_pixels", "total_area_ha", "pixel_share", "area_share", "data_status"]]
    composition = sorted_sites(composition, [])
    checks.append({"check": "four_sites_three_reference_classes_unique", "status": "Verified", "detail": "12 unique target/crop rows"})
    checks.append({"check": "reference_composition_restores_full_site", "status": "Verified", "detail": "4 site totals each equal 6553600 pixels"})

    background_class = tables["background_class"].copy()
    background_class = background_class[background_class["scope"].eq("full")].copy()
    require(len(background_class) == 12 and not background_class.duplicated(["dataset_id", "class_name"]).any(),
            "background class: expected 12 unique full-scope records")
    require(set(background_class[["dataset_id", "class_name"]].itertuples(index=False, name=None)) == expected_support,
            "background class: target/class identities are incomplete")
    require(background_class["verified"].map(string_bool).all(), "background class: source records are not verified")
    background_class = background_class.rename(columns={
        "dataset_id": "target", "class_name": "crop", "class_pixels": "pixels",
        "patch_count_8n": "patch_count_8n", "pd_recomputed": "patch_density_per_100ha",
        "area_mn_recomputed": "mean_patch_area_ha", "ai_recomputed": "aggregation_index",
    })
    background_class["site"] = background_class["target"].map(SITE_CODES)
    support_pixels = support.set_index(["target", "crop"])["pixels"]
    require((background_class.apply(lambda row: int(row["pixels"]) == int(support_pixels[(row["target"], row["crop"])]), axis=1)).all(),
            "background class: pixels do not match reference support")
    class_background = background_class[["target", "site", "crop", "pixels", "patch_count_8n", "patch_density_per_100ha", "mean_patch_area_ha", "aggregation_index", "verified"]]
    class_background = sorted_sites(class_background, [])
    checks.append({"check": "class_background_reference_support_match", "status": "Verified", "detail": "12 class pixel supports match composition"})

    landscape = tables["background_landscape"].copy()
    landscape = landscape[landscape["scope"].eq("full")].copy()
    require(len(landscape) == 4 and not landscape.duplicated("dataset_id").any(),
            "landscape background: expected four unique full-scope records")
    require(set(landscape["dataset_id"]) == set(SITES), "landscape background: site set mismatch")
    require(landscape["verified"].map(string_bool).all(), "landscape background: source records are not verified")
    landscape = landscape.rename(columns={"dataset_id": "target", "ed_recomputed": "edge_density_m_per_ha"})
    landscape["site"] = landscape["target"].map(SITE_CODES)
    landscape["scope_note"] = "whole_landscape_not_crop_specific"
    landscape_background = sorted_sites(landscape[["target", "site", "edge_density_m_per_ha", "scope_note", "verified"]], [])
    checks.append({"check": "landscape_edge_density_kept_at_landscape_level", "status": "Verified", "detail": "4 full-scope ED records, not copied to crop rows"})

    distribution = tables["distribution"].copy()
    distribution = distribution[
        distribution["domain"].eq("site_crop")
        & distribution["crop"].isin(CROPS)
        & distribution["metric"].isin(["AREA", "SHAPE"])
        & distribution["weighting"].isin(["patch_equal", "reference_pixel_area"])
    ].copy()
    require(len(distribution) == 32 and not distribution.duplicated(["target", "crop", "metric", "weighting"]).any(),
            "distribution: expected 32 unique site/crop/metric/weighting rows")
    expected_distribution = {(site, crop, metric, weight)
                             for site in SITES for crop in CROPS for metric in ("AREA", "SHAPE")
                             for weight in ("patch_equal", "reference_pixel_area")}
    require(set(distribution[["target", "crop", "metric", "weighting"]].itertuples(index=False, name=None)) == expected_distribution,
            "distribution: identity set is incomplete")
    support_counts = support.set_index(["target", "crop"])[["n_patches", "pixels"]]
    require((distribution.apply(lambda row: int(row["n_total"]) == int(support_counts.loc[(row["target"], row["crop"]), "n_patches"])
                                        and int(row["pixels_total"]) == int(support_counts.loc[(row["target"], row["crop"]), "pixels"]), axis=1)).all(),
            "distribution: support does not match reference inventory")
    distribution["site"] = distribution["target"].map(SITE_CODES)
    distribution["distribution_level"] = np.where(distribution["weighting"].eq("patch_equal"), "patch_count", "reference_pixel_area")
    distribution["data_status"] = "reused_verified_summary"
    distribution_reading = distribution[[
        "target", "site", "crop", "metric", "unit", "weighting", "distribution_level", "n_total", "pixels_total",
        "minimum", "q05", "q10", "q25", "median", "q75", "q90", "q95", "q99", "maximum", "algorithm",
        "current_status", "data_status",
    ]]
    distribution_reading = sorted_sites(distribution_reading, ["metric", "weighting"])
    checks.append({"check": "eight_crop_groups_area_shape_distributions_complete", "status": "Verified", "detail": "8 site/crop groups x AREA/SHAPE x two weightings = 32 rows"})

    support_reading = tables["support_reading"].copy()
    support_reading = support_reading[support_reading["domain"].eq("site_crop") & support_reading["crop"].isin(CROPS)].copy()
    require(len(support_reading) == 8 and not support_reading.duplicated(["target", "crop"]).any(),
            "support reading: expected eight site/crop rows")
    require(set(support_reading[["target", "crop"]].itertuples(index=False, name=None)) == {(site, crop) for site in SITES for crop in CROPS},
            "support reading: identity set is incomplete")
    require((support_reading.apply(lambda row: int(row["n_patches"]) == int(support_counts.loc[(row["target"], row["crop"]), "n_patches"])
                                       and int(row["pixels"]) == int(support_counts.loc[(row["target"], row["crop"]), "pixels"]), axis=1)).all(),
            "support reading: support does not match reference inventory")
    support_reading["site"] = support_reading["target"].map(SITE_CODES)
    support_reading["data_status"] = "reused_verified_summary"
    support_limitations = support_reading[[
        "target", "site", "crop", "n_patches", "pixels", "area_ha", "singleton_count", "singleton_patch_share",
        "singleton_area_share", "no_interior_patches", "no_interior_patch_share", "no_interior_pixels",
        "no_interior_area_share", "edge_patches", "edge_patch_share", "edge_pixels", "edge_area_share",
        "boundary_pixels", "boundary_area_share", "data_status",
    ]]
    support_limitations = sorted_sites(support_limitations, [])
    checks.append({"check": "micro_patch_and_window_limitation_support_complete", "status": "Verified", "detail": "8 crop rows retain count and area shares"})

    return {
        "reference_composition.csv": composition,
        "class_background_full_scope.csv": class_background,
        "landscape_background_full_scope.csv": landscape_background,
        "crop_patch_distribution_reading.csv": distribution_reading,
        "crop_patch_support_and_limitations.csv": support_limitations,
    }


def build_within_tables(tables: dict[str, pd.DataFrame], reference_tables: dict[str, pd.DataFrame], checks: list[dict[str, object]]) -> tuple[dict[str, pd.DataFrame], dict[tuple[str, str], np.ndarray]]:
    formal_f1 = tables["formal_within_f1"].copy()
    require(len(formal_f1) == 12 and not formal_f1.duplicated(["model", "target"]).any(),
            "formal within F1: expected 12 unique records")
    expected_runs = {(model, target) for model in MODELS for target in SITES}
    require(set(formal_f1[["model", "target"]].itertuples(index=False, name=None)) == expected_runs,
            "formal within F1: model/target identities are incomplete")
    require((pd.to_numeric(formal_f1["valid_pixels"], errors="raise") == FULL_SITE_PIXELS).all(),
            "formal within F1: invalid full-site support")

    metrics = tables["within_metrics"].copy()
    metrics = metrics[
        metrics["kind"].eq("within") & metrics["source"].eq(metrics["target"]) & metrics["fold"].eq(0)
    ].copy()
    metric_keys = ["model", "target", "crop"]
    require(len(metrics) == 36 and not metrics.duplicated(metric_keys).any(),
            "within metrics: expected 36 unique model/target/class rows")
    require(set(metrics[["model", "target"]].itertuples(index=False, name=None)) == expected_runs,
            "within metrics: model/target identities are incomplete")
    require(set(metrics["crop"]) == set(CLASSES), "within metrics: class set mismatch")
    metrics = int_values(metrics, ["pixels", "predicted_pixels", "tp", "fn", "fp", "f1_denominator"], "within metrics")
    require(metrics[["f1_status", "precision_status", "recall_status"]].eq("defined").all().all(),
            "within metrics: an undefined metric is outside the expected full-site result")
    require((metrics["pixels"].groupby([metrics["model"], metrics["target"]]).sum() == FULL_SITE_PIXELS).all(),
            "within metrics: class supports do not restore full site")

    f1_long = formal_f1.melt(
        id_vars=["model", "target"], value_vars=["corn_f1", "soybean_f1"],
        var_name="metric_name", value_name="formal_f1",
    )
    f1_long["crop"] = f1_long["metric_name"].str.replace("_f1", "", regex=False)
    metrics = metrics.merge(f1_long[["model", "target", "crop", "formal_f1"]], on=metric_keys, how="left", validate="one_to_one")
    computed = 2 * metrics["tp"] / (2 * metrics["tp"] + metrics["fp"] + metrics["fn"])
    require(close(metrics["f1"], computed), "within metrics: F1 does not match TP/FN/FP formula")
    crop_metrics = metrics[metrics["crop"].isin(CROPS)].copy()
    require(close(crop_metrics["f1"], crop_metrics["formal_f1"]), "within metrics: F1 does not match formal summary")
    crop_metrics["site"] = crop_metrics["target"].map(SITE_CODES)
    crop_metrics["f1_agreement_absolute_error"] = np.abs(crop_metrics["f1"] - crop_metrics["formal_f1"])
    crop_metrics["data_status"] = "derived_from_integer_within_matrices"
    crop_metrics = crop_metrics[[
        "model", "target", "site", "crop", "pixels", "predicted_pixels", "tp", "fn", "fp", "f1_denominator",
        "f1", "precision", "recall", "formal_f1", "f1_agreement_absolute_error", "f1_status", "precision_status",
        "recall_status", "data_status",
    ]]
    crop_metrics = sorted_sites(crop_metrics, [])
    checks.append({"check": "twenty_four_within_crop_metric_rows_complete", "status": "Verified", "detail": "12 independent model/target baselines x corn and soybean"})
    checks.append({"check": "within_f1_matches_formal_summary_within_1e12", "status": "Verified", "detail": "24 crop F1 values agree with f1_raw_scale"})

    raw = tables["within_raw_cm"].copy()
    raw_columns = [f"cm_{i}{j}" for i in range(3) for j in range(3)]
    raw = int_values(raw, raw_columns, "raw within confusion matrices")
    require(len(raw) == 72, "raw within confusion matrices: expected 72 records")
    raw["fold"] = pd.to_numeric(raw["fold"], errors="coerce")
    raw_folds = raw[raw["result_type"].eq("fold")].copy()
    raw_pooled = raw[raw["result_type"].eq("oof_pooled")].copy()
    require(len(raw_folds) == 60 and len(raw_pooled) == 12, "raw within confusion matrices: 60 folds plus 12 pooled records required")
    require(raw_pooled["fold"].isna().all(), "raw within confusion matrices: pooled records must have empty fold")
    require(set(raw_folds["fold"].dropna().astype(int)) == {1, 2, 3, 4, 5}, "raw within confusion matrices: invalid folds")
    require(not raw_folds.duplicated(["model", "target", "fold"]).any() and not raw_pooled.duplicated(["model", "target"]).any(),
            "raw within confusion matrices: duplicate identities")
    require(set(raw_pooled[["model", "target"]].itertuples(index=False, name=None)) == expected_runs,
            "raw within confusion matrices: pooled identities incomplete")
    require((raw_folds[raw_columns].sum(axis=1) == FULL_SITE_PIXELS // 5).all(), "raw within confusion matrices: fold support mismatch")
    require((raw_pooled[raw_columns].sum(axis=1) == FULL_SITE_PIXELS).all(), "raw within confusion matrices: pooled support mismatch")
    raw_sum = raw_folds.groupby(["model", "target"], as_index=False)[raw_columns].sum()
    raw_pooled_ordered = raw_pooled[["model", "target", *raw_columns]].sort_values(["model", "target"]).reset_index(drop=True)
    raw_sum_ordered = raw_sum.sort_values(["model", "target"]).reset_index(drop=True)
    require((raw_sum_ordered[raw_columns].to_numpy() == raw_pooled_ordered[raw_columns].to_numpy()).all(),
            "raw within confusion matrices: fold sum does not equal pooled matrix")

    whole = tables["whole_cm"].copy()
    processed_columns = [f"cm_{i}_{j}" for i in range(3) for j in range(3)]
    whole = int_values(whole, processed_columns, "processed whole matrices")
    require(len(whole) == 192 and not whole.duplicated(["kind", "model", "source", "target", "fold"]).any(),
            "processed whole matrices: expected 192 unique run records")
    within_whole = whole[whole["kind"].eq("within") & whole["source"].eq(whole["target"]) & whole["fold"].eq(0)].copy()
    require(len(within_whole) == 12 and not within_whole.duplicated(["model", "target"]).any(),
            "processed whole matrices: expected 12 within records")
    require((within_whole[processed_columns].sum(axis=1) == FULL_SITE_PIXELS).all(),
            "processed whole matrices: full-site support mismatch")
    require(set(within_whole[["model", "target"]].itertuples(index=False, name=None)) == expected_runs,
            "processed whole matrices: within identities incomplete")

    matrices: dict[tuple[str, str], np.ndarray] = {}
    matrix_rows: list[dict[str, object]] = []
    reference_support = reference_tables["reference_composition.csv"].set_index(["target", "crop"])["pixels"]
    metrics_indexed = metrics.set_index(metric_keys)
    for model in MODELS:
        for target in SITES:
            raw_row = raw_pooled[(raw_pooled["model"] == model) & (raw_pooled["target"] == target)].iloc[0]
            processed_row = within_whole[(within_whole["model"] == model) & (within_whole["target"] == target)].iloc[0]
            raw_matrix = matrix_from_row(raw_row, "raw")
            processed_matrix = matrix_from_row(processed_row, "processed")
            matrices[(model, target)] = raw_matrix
            raw_processed_equal = bool(np.array_equal(raw_matrix, processed_matrix))
            require(raw_processed_equal, f"matrix {model}/{target}: raw pooled and processed values differ")
            class_support_ok = True
            metric_ok = True
            for class_name, class_index in CLASS_INDEX.items():
                expected_pixels = int(reference_support[(target, class_name)])
                class_support_ok = class_support_ok and int(raw_matrix[class_index, :].sum()) == expected_pixels
                row = metrics_indexed.loc[(model, target, class_name)]
                tp, fn, fp, f1, precision, recall = metric_values(raw_matrix, class_index)
                metric_ok = metric_ok and (
                    tp == int(row["tp"]) and fn == int(row["fn"]) and fp == int(row["fp"])
                    and close(f1, row["f1"]) and close(precision, row["precision"]) and close(recall, row["recall"])
                )
            require(class_support_ok, f"matrix {model}/{target}: row support differs from reference support")
            require(metric_ok, f"matrix {model}/{target}: TP/FN/FP or metrics do not reconstruct")
            matrix_rows.append({
                "model": model, "target": target, "site": SITE_CODES[target], "full_site_pixels": int(raw_matrix.sum()),
                "raw_fold_sum_equals_raw_pooled": True, "raw_pooled_equals_processed_whole_cm": raw_processed_equal,
                "reference_class_row_sums_match": class_support_ok, "tp_fn_fp_and_metrics_reconstruct": metric_ok,
                "matrix_status": "Verified",
            })
    matrix_checks = sorted_sites(pd.DataFrame(matrix_rows), [])
    checks.append({"check": "twelve_raw_fold_sums_equal_pooled_matrices", "status": "Verified", "detail": "5 fold matrices restore every pooled within-site matrix"})
    checks.append({"check": "twelve_raw_and_processed_whole_matrices_identical", "status": "Verified", "detail": "integer 3x3 matrices agree for all baselines"})
    checks.append({"check": "twelve_matrices_restore_reference_support_and_tp_fn_fp", "status": "Verified", "detail": "all 12 matrices contain 6553600 pixels and close against class support"})

    gap_rows: list[dict[str, object]] = []
    crop_metrics_indexed = crop_metrics.set_index(["model", "target", "crop"])
    for model in MODELS:
        for target in SITES:
            corn = crop_metrics_indexed.loc[(model, target, "corn")]
            soybean = crop_metrics_indexed.loc[(model, target, "soybean")]
            precision_gap = float(corn["precision"] - soybean["precision"])
            recall_gap = float(corn["recall"] - soybean["recall"])
            larger_difference = "recall" if abs(recall_gap) > abs(precision_gap) else "precision"
            gap_rows.append({
                "model": model, "target": target, "site": SITE_CODES[target],
                "corn_f1": corn["f1"], "soybean_f1": soybean["f1"], "corn_minus_soybean_f1": corn["f1"] - soybean["f1"],
                "corn_minus_soybean_precision": precision_gap, "corn_minus_soybean_recall": recall_gap,
                "larger_absolute_crop_difference": larger_difference,
                "corn_precision_below_soybean": precision_gap < 0,
            })
    crop_gap = sorted_sites(pd.DataFrame(gap_rows), [])
    require((crop_gap["corn_minus_soybean_f1"] > 0).all(), "within crop gaps: corn F1 is not higher in every baseline")
    checks.append({"check": "within_crop_gap_precision_recall_diagnostic_complete", "status": "Verified", "detail": "12 baselines retain both recall and precision differences"})

    return {
        "within_site_crop_metrics.csv": crop_metrics,
        "within_site_crop_gap_diagnostic.csv": crop_gap,
        "within_site_matrix_checks.csv": matrix_checks,
    }, matrices


def build_directional_tables(tables: dict[str, pd.DataFrame], matrices: dict[tuple[str, str], np.ndarray], checks: list[dict[str, object]]) -> dict[str, pd.DataFrame]:
    summary = tables["directional_summary"].copy()
    directional_keys = ["model", "target", "true_class", "predicted_class"]
    expected_directions = {(model, target, true_class, predicted_class)
                           for model in MODELS for target in SITES
                           for true_class in CLASSES for predicted_class in CLASSES if true_class != predicted_class}
    require(set(summary[directional_keys].itertuples(index=False, name=None)) == expected_directions,
            "directional summary: model/target/direction identities are incomplete")
    rows: list[dict[str, object]] = []
    repeated_fields = ["within_pixels", "within_errors", "within_rate", "within_delta_rate", "rate_status"]
    for key, group in summary.groupby(directional_keys, sort=False):
        model, target, true_class, predicted_class = key
        expected_sources = set(SITES).difference({target})
        require(len(group) == 3 and set(group["source"]) == expected_sources,
                f"directional summary: {key} does not have the three expected source repetitions")
        for field in repeated_fields:
            require(group[field].nunique(dropna=False) == 1, f"directional summary: repeated within records disagree for {key}/{field}")
        true_index = CLASS_INDEX[true_class]
        predicted_index = CLASS_INDEX[predicted_class]
        matrix = matrices[(model, target)]
        errors = int(group["within_errors"].iloc[0])
        pixels = int(group["within_pixels"].iloc[0])
        rate = float(group["within_rate"].iloc[0])
        require(errors == int(matrix[true_index, predicted_index]), f"directional summary: matrix error mismatch for {key}")
        require(pixels == int(matrix[true_index, :].sum()), f"directional summary: reference support mismatch for {key}")
        require(close(rate, errors / pixels), f"directional summary: rate mismatch for {key}")
        require(close(group["within_delta_rate"].iloc[0], 0.0), f"directional summary: within delta rate is nonzero for {key}")
        require(group["rate_status"].eq("defined").all(), f"directional summary: undefined within rate for {key}")
        rows.append({
            "model": model, "target": target, "site": SITE_CODES[target], "true_class": true_class,
            "predicted_class": predicted_class, "direction": f"{true_class}_to_{predicted_class}",
            "reference_pixels": pixels, "errors": errors, "error_rate": rate,
            "repeated_source_record_count": len(group), "repeated_source_records_identical": True,
            "data_status": "derived_from_integer_within_matrices",
        })
    directional = pd.DataFrame(rows)
    require(len(directional) == 72 and not directional.duplicated(directional_keys).any(), "directional table: expected 72 unique records")
    directional = sorted_sites(directional, ["true_class", "predicted_class"])

    directional_indexed = directional.set_index(directional_keys)
    dominant_rows: list[dict[str, object]] = []
    matrix_check: dict[tuple[str, str], bool] = {}
    for model in MODELS:
        for target in SITES:
            matrix = matrices[(model, target)]
            closure_ok = True
            for true_class, true_index in CLASS_INDEX.items():
                outgoing = directional[
                    (directional["model"] == model) & (directional["target"] == target) & (directional["true_class"] == true_class)
                ]
                closure_ok = closure_ok and int(outgoing["errors"].sum()) == int(matrix[true_index, :].sum() - matrix[true_index, true_index])
            for predicted_class, predicted_index in CLASS_INDEX.items():
                incoming = directional[
                    (directional["model"] == model) & (directional["target"] == target) & (directional["predicted_class"] == predicted_class)
                ]
                closure_ok = closure_ok and int(incoming["errors"].sum()) == int(matrix[:, predicted_index].sum() - matrix[predicted_index, predicted_index])
            require(closure_ok, f"directional closure fails for {model}/{target}")
            matrix_check[(model, target)] = closure_ok
            for crop in CROPS:
                choices = directional[
                    (directional["model"] == model) & (directional["target"] == target) & (directional["true_class"] == crop)
                ].sort_values(["errors", "predicted_class"], ascending=[False, True], kind="stable")
                require(len(choices) == 2, f"dominant direction: missing alternatives for {model}/{target}/{crop}")
                primary, alternate = choices.iloc[0], choices.iloc[1]
                dominant_rows.append({
                    "model": model, "target": target, "site": SITE_CODES[target], "crop": crop,
                    "dominant_predicted_class": primary["predicted_class"], "dominant_direction": primary["direction"],
                    "dominant_errors": primary["errors"], "dominant_error_rate": primary["error_rate"],
                    "other_predicted_class": alternate["predicted_class"], "other_errors": alternate["errors"],
                    "other_error_rate": alternate["error_rate"], "unique_dominant_direction": primary["errors"] > alternate["errors"],
                })
    dominant = sorted_sites(pd.DataFrame(dominant_rows), [])
    require(len(dominant) == 24, "dominant direction: expected 24 crop-level records")
    checks.append({"check": "within_directional_source_repetitions_identical_before_collapse", "status": "Verified", "detail": "each of 72 directions has three identical within-site records"})
    checks.append({"check": "seventy_two_directional_errors_close_to_fn_and_fp", "status": "Verified", "detail": "two outgoing directions restore FN and two incoming directions restore FP for each class"})

    return {
        "within_site_directional_errors.csv": directional,
        "within_site_dominant_error_direction.csv": dominant,
    }


def build_bridge(tables: dict[str, pd.DataFrame], checks: list[dict[str, object]]) -> pd.DataFrame:
    difference = tables["f1_difference"].copy()
    require(len(difference) == 36 and not difference.duplicated(["model", "source", "target"]).any(),
            "F1 difference: expected 36 unique model/path records")
    expected_paths = {(model, source, target) for model in MODELS for source in SITES for target in SITES if source != target}
    require(set(difference[["model", "source", "target"]].itertuples(index=False, name=None)) == expected_paths,
            "F1 difference: model/path identity set is incomplete")

    case_metrics = tables["case_crop_metrics"].copy()
    case_metrics = case_metrics[(case_metrics["model"] == "convgru") & (case_metrics["source"] == "iw2_2023")
                                & (case_metrics["target"] == "il_2023") & (case_metrics["crop"] == "soybean")]
    require(len(case_metrics) == 1, "case metrics: selected B-to-D soybean record is missing or duplicated")
    case = case_metrics.iloc[0]
    b_to_d = difference[(difference["model"] == "convgru") & (difference["source"] == "iw2_2023") & (difference["target"] == "il_2023")].iloc[0]
    c_to_d = difference[(difference["model"] == "convgru") & (difference["source"] == "ida_2023") & (difference["target"] == "il_2023")].iloc[0]
    conv_d_to_b = difference[(difference["model"] == "convgru") & (difference["source"] == "il_2023") & (difference["target"] == "iw2_2023")].iloc[0]
    unet_b_to_d = difference[(difference["model"] == "unet3d") & (difference["source"] == "iw2_2023") & (difference["target"] == "il_2023")].iloc[0]
    unet_d_to_b = difference[(difference["model"] == "unet3d") & (difference["source"] == "il_2023") & (difference["target"] == "iw2_2023")].iloc[0]
    require(close(case["delta_f1"], b_to_d["soybean_f1_difference"]), "case metrics: soybean F1 difference mismatch")

    distance = tables["case_distance"].copy()
    far = distance[(distance["model"] == "convgru") & (distance["source"] == "iw2_2023") & (distance["target"] == "il_2023")
                   & (distance["band"] == "d>6") & (distance["true_class"] == "soybean") & (distance["predicted_class"] == "corn")]
    require(len(far) == 1, "distance case: B-to-D soybean-to-corn far-interior record is missing or duplicated")
    far = far.iloc[0]

    bridge = pd.DataFrame([
        {
            "bridge_id": "B1", "comparison_scope": "ConvGRU; B_to_D; soybean", "section_32_comparison": "target D, source B versus target-site within baseline",
            "f1_difference": b_to_d["soybean_f1_difference"], "error_change": "soybean_to_corn directional error rate increased",
            "error_rate_increment_pp": b_to_d["soybean_f1_difference"] * np.nan,
            "directional_rate_increment_pp": np.nan, "spatial_condition": "far interior d>6",
            "spatial_rate_increment_pp": far["delta_rate_pp"], "all_five_direction_positive": far["delta_rate_direction"] == "all_positive",
            "metric_link": "soybean recall change and corn precision change are consistent with this directional error path",
            "soybean_recall_change_pp": case["delta_recall"] * 100, "corn_precision_change_pp": np.nan,
            "scope_and_limitation": "descriptive correspondence for one model/path; it does not identify a causal landscape mechanism",
            "counterexample_or_boundary": "soybean precision mean change has mixed five-prediction signs; do not state a precision increase",
            "new_statistics_needed_now": "no; existing stored five-prediction evidence supports only conditional description",
        },
        {
            "bridge_id": "B2", "comparison_scope": "ConvGRU; C_to_D versus B_to_D; soybean", "section_32_comparison": "same target D, different source sites",
            "f1_difference": c_to_d["soybean_f1_difference"], "error_change": "contrast in F1 gap motivates path-specific directional inspection",
            "error_rate_increment_pp": np.nan, "directional_rate_increment_pp": np.nan, "spatial_condition": "same target reference layout",
            "spatial_rate_increment_pp": np.nan, "all_five_direction_positive": pd.NA,
            "metric_link": "B_to_D soybean Delta F1 exceeds C_to_D; target layout alone cannot explain source contrast",
            "soybean_recall_change_pp": np.nan, "corn_precision_change_pp": np.nan,
            "scope_and_limitation": "source composition, imagery/phenology and model-source interaction remain inseparable in current evidence",
            "counterexample_or_boundary": "fixed target does not prove which source condition produces the difference",
            "new_statistics_needed_now": "no; no causal separation is justified from these paths",
        },
        {
            "bridge_id": "B3", "comparison_scope": "B_to_D and D_to_B; ConvGRU and 3D U-Net; soybean", "section_32_comparison": "opposite transfer directions with two models",
            "f1_difference": b_to_d["soybean_f1_difference"], "error_change": "directional F1-gap ordering differs by model",
            "error_rate_increment_pp": np.nan, "directional_rate_increment_pp": np.nan, "spatial_condition": "target layouts exchange across direction",
            "spatial_rate_increment_pp": np.nan, "all_five_direction_positive": pd.NA,
            "metric_link": "ConvGRU B_to_D/D_to_B and 3D U-Net B_to_D/D_to_B are retained as model-conditional contrasts",
            "soybean_recall_change_pp": np.nan, "corn_precision_change_pp": np.nan,
            "scope_and_limitation": "the two directions do not establish a universal directional rule",
            "counterexample_or_boundary": "ConvGRU: %.17g vs %.17g; 3D U-Net: %.17g vs %.17g" % (
                b_to_d["soybean_f1_difference"], conv_d_to_b["soybean_f1_difference"],
                unet_b_to_d["soybean_f1_difference"], unet_d_to_b["soybean_f1_difference"],
            ),
            "new_statistics_needed_now": "no; retain as a counterexample to generalization",
        },
    ])

    directional = tables.get("directional_summary")
    b_direction = directional[(directional["model"] == "convgru") & (directional["source"] == "iw2_2023")
                              & (directional["target"] == "il_2023") & (directional["true_class"] == "soybean")
                              & (directional["predicted_class"] == "corn")]
    require(len(b_direction) == 1, "directional summary: B-to-D soybean-to-corn record is missing or duplicated")
    b_direction = b_direction.iloc[0]
    bridge.loc[bridge["bridge_id"] == "B1", "directional_rate_increment_pp"] = b_direction["delta_rate_pp"]
    bridge.loc[bridge["bridge_id"] == "B1", "error_rate_increment_pp"] = b_direction["delta_rate_pp"]
    corn_case = tables["case_crop_metrics"]
    corn_case = corn_case[(corn_case["model"] == "convgru") & (corn_case["source"] == "iw2_2023")
                          & (corn_case["target"] == "il_2023") & (corn_case["crop"] == "corn")]
    require(len(corn_case) == 1, "case metrics: selected B-to-D corn record is missing or duplicated")
    bridge.loc[bridge["bridge_id"] == "B1", "corn_precision_change_pp"] = float(corn_case.iloc[0]["delta_precision"]) * 100
    require(b_direction["delta_rate_direction"] == "all_positive" and far["delta_rate_direction"] == "all_positive",
            "selected B-to-D evidence: not all five prediction changes are positive")
    checks.append({"check": "sec32_to_sec33_bridge_selected_case_linked", "status": "Verified", "detail": "B-to-D ConvGRU soybean path links F1, directional error and d>6 evidence"})
    checks.append({"check": "sec32_direction_and_model_counterexamples_retained", "status": "Verified", "detail": "B/D ordering is kept separately for ConvGRU and 3D U-Net"})
    return bridge


def build_readme() -> str:
    return """# 1.3 与 3.1 基础证据阅读入口

本目录是对既有结果的只读整理，不是新实验。它为 1.3 的四站参考空间背景和 3.1 的本站分类基准提供可追溯阅读表，也为 3.2 到 3.3 的最小衔接保留一条已验证的条件性线索。

## 范围

- `reference_composition.csv`：四站三类参考像元、面积及整站占比。
- `class_background_full_scope.csv` 与 `landscape_background_full_scope.csv`：只保留 `scope=full` 的类别级和景观级背景；景观级 ED 不属于作物专属指标。
- `crop_patch_distribution_reading.csv` 与 `crop_patch_support_and_limitations.csv`：八个站点—作物组的 AREA、SHAPE 两种权重分布，以及微小斑块、无内部区域和研究窗口外框截断的支持量。
- `within_site_crop_metrics.csv`、`within_site_crop_gap_diagnostic.csv`、`within_site_directional_errors.csv`、`within_site_dominant_error_direction.csv`：12 个独立本站模型—目标站基准的两作物指标、作物差异和六向错分。
- `within_site_matrix_checks.csv` 与 `verification_checks.csv`：原始五折矩阵、已处理整图矩阵、参考支持、TP/FN/FP、方向性闭合和正式 F1 的本次核对。
- `sec32_to_sec33_evidence_bridge.csv`：用于决定后续 3.3 必要证据的内部衔接表，不是正文结论。

本站基准由五折测试混淆矩阵逐元素求和后计算；跨站结果仍按五次完整目标站预测分别计算后取均值。本站方向性记录在上游汇总中按三个来源站重复，本次先验证其数值一致，再折叠为 72 条方向记录，绝不把它们当作 36 次独立本站实验。

所有输出均为 `derived` 或 `reused_verified_summary`。输入、脚本和输出 SHA-256 见 `manifest.json`。`paragraph_evidence_outline.md` 仅为正文作者提供证据路由，不替代正文，也不赋予景观指标因果解释。
"""


def build_outline(reference_tables: dict[str, pd.DataFrame], within_tables: dict[str, pd.DataFrame], directional_tables: dict[str, pd.DataFrame]) -> str:
    composition = reference_tables["reference_composition.csv"]
    composition_text = "；".join(
        f"{site}：玉米 {composition[(composition.site == site) & (composition.crop == 'corn')].iloc[0].pixel_share * 100:.2f}%，"
        f"大豆 {composition[(composition.site == site) & (composition.crop == 'soybean')].iloc[0].pixel_share * 100:.2f}%，"
        f"其他 {composition[(composition.site == site) & (composition.crop == 'other')].iloc[0].pixel_share * 100:.2f}%"
        for site in ("A", "B", "C", "D")
    )
    gap = within_tables["within_site_crop_gap_diagnostic.csv"]
    recall_count = int(gap["larger_absolute_crop_difference"].eq("recall").sum())
    precision_count = int(gap["larger_absolute_crop_difference"].eq("precision").sum())
    precision_exceptions = gap[gap["corn_precision_below_soybean"]]
    exception_text = "、".join(f"{row.site}站{row.model}" for row in precision_exceptions.itertuples())
    dominant = directional_tables["within_site_dominant_error_direction.csv"]
    other_count = int(dominant[dominant["dominant_predicted_class"].eq("other")].shape[0])
    non_other = dominant[~dominant["dominant_predicted_class"].eq("other")]
    non_other_text = "；".join(f"{row.site}站{row.model}的{row.crop}主要误分为{row.dominant_predicted_class}" for row in non_other.itertuples())
    return f"""# 1.3 与 3.1 段落—证据提纲

本文件是内部证据路由，不是论文正文。下列陈述仅使用本目录核验后的表；它们描述参考空间背景、本站错误基准或具体条件下的对应关系，不构成跨站退化的因果解释。

## 1.3.1 地物组成

- 论述任务：用同一整站有效参考像元分母交代四站三类地物组成，为后文的目标站条件提供背景。
- 证据：`reference_composition.csv`。2023 年整站占比分别为：{composition_text}。
- 边界：不将组成差异提前解释为本站错误或跨站 F1 差距；不与 1.1 的年际农作物面积分母混用。

## 1.3.2 参考斑块与整站景观背景

- 论述任务：区分类别级斑块数量、平均面积和聚合度，与整站景观级 ED；明确对象是 8 邻域完整参考斑块，不是实际农业田块，也不是 128×128 训练图块。
- 证据：`class_background_full_scope.csv`、`landscape_background_full_scope.csv`、`crop_patch_distribution_reading.csv`。AREA 与 SHAPE 同时保留斑块等权和参考像元面积加权分布，避免把大量微小斑块按数量的中位数直接当作主要作物面积的典型情形。
- 支持与限制：`crop_patch_support_and_limitations.csv`。微小和无内部区域斑块可在数量上常见，但必须同时报告其面积份额；外框截断相关面积只作为研究窗口限制，不能被删除或写成分类误差原因。
- 边界：本节仅描述空间背景。较大的斑块、较低的 ED 或不同的形状分布本身都不足以推断跨站退化更小。

## 3.1 本站分类性能

- 论述任务：保留现有 F1 主体与正式图，补足 12 个独立模型—目标站基准中 F1、精确率、召回率及六向错分的全域证据。
- 证据：`within_site_crop_metrics.csv` 与 `within_site_crop_gap_diagnostic.csv`。12 个基准中玉米 F1 均高于大豆 F1；作物间 F1 差异伴随更大的召回率差异 {recall_count}/12 次、精确率差异 {precision_count}/12 次。这只是并行的指标差异，不是 F1 贡献分解。{exception_text} 的玉米精确率低于大豆，必须保留，不能将玉米 F1 较高概括为普遍精确率优势。
- 方向性证据：`within_site_directional_errors.csv` 与 `within_site_dominant_error_direction.csv`。24 个作物基准中有 {other_count} 个以误分为其他类为较大 FN 方向；例外为 {non_other_text}。方向性率的分母为真实来源类别参考像元，不能跨来源类别直接当作 F1 作用大小相加。
- 核验边界：`within_site_matrix_checks.csv` 证明本站三类 TP、FN、FP、六个非对角元素和全矩阵闭合。D 站局部图仍仅作示例，不替代这套整站统计。

## 3.2 到 3.3 的衔接

- 证据：`sec32_to_sec33_evidence_bridge.csv`。优先选择一个明确的模型—源站—目标站—作物差异，先报告方向性错误变化，再说明该变化在既有空间条件统计中的位置，并保留模型和方向反例。
- 边界：目标站参考格局不随源站而变化，因此它不能单独解释来源差异；面积、形状、组成、邻接、物候和影像条件的独立作用尚未分离。现有材料支持条件性对应描述，不支持因果机制结论。
"""


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="Repository root")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    output_dir = root / OUT_DIR
    require(not output_dir.exists(), f"Refusing to overwrite existing output directory: {output_dir}")
    input_paths = {name: root / relative for name, relative in INPUTS.items()}
    for name, path in input_paths.items():
        require(path.is_file(), f"Missing required input {name}: {path}")
    input_records = [file_record(path, root) for path in input_paths.values()]
    tables = {name: read_csv(root, relative) for name, relative in INPUTS.items()}
    checks: list[dict[str, object]] = []
    reference_tables = build_reference_tables(tables, checks)
    within_tables, matrices = build_within_tables(tables, reference_tables, checks)
    directional_tables = build_directional_tables(tables, matrices, checks)
    bridge = build_bridge(tables, checks)
    all_tables = {**reference_tables, **within_tables, **directional_tables, "sec32_to_sec33_evidence_bridge.csv": bridge}
    checks_frame = pd.DataFrame(checks)
    all_tables["verification_checks.csv"] = checks_frame
    readme = build_readme()
    outline = build_outline(reference_tables, within_tables, directional_tables)
    before_write_records = [file_record(path, root) for path in input_paths.values()]
    require(before_write_records == input_records, "Input hashes changed while validations were running; no outputs written")

    output_dir.mkdir(parents=True, exist_ok=False)
    output_records: list[dict[str, object]] = []
    for name, frame in all_tables.items():
        destination = output_dir / name
        write_csv(destination, frame)
        output_records.append({**file_record(destination, root), "rows": int(len(frame))})
    for name, text in {"README.md": readme, "paragraph_evidence_outline.md": outline}.items():
        destination = output_dir / name
        with destination.open("x", encoding="utf-8", newline="") as handle:
            handle.write(text)
        output_records.append({**file_record(destination, root), "rows": None})
    manifest = {
        "data_status": "derived_and_reused_verified_summary",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Reading tables and integrity checks for Sections 1.3 and 3.1; no new experiment or manuscript edit.",
        "site_mapping": SITE_CODES,
        "class_order_for_confusion_matrices": list(CLASSES),
        "within_baseline": "pooled integer CM from five independent test folds",
        "cross_site_context": "five full-target predictions per model/path; used only in the explicit Section 3.2-to-3.3 bridge",
        "f1_formula": "2TP / (2TP + FP + FN); undefined only when denominator is zero",
        "directional_rate_denominator": "reference pixels of the true source class",
        "inputs": input_records,
        "script": file_record(Path(__file__), root),
        "outputs": output_records,
        "verification": "Verified",
    }
    manifest_path = output_dir / "manifest.json"
    with manifest_path.open("x", encoding="utf-8", newline="") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(f"Verified: wrote {len(all_tables)} CSV tables, two internal reading documents, and {OUT_DIR}/manifest.json")


if __name__ == "__main__":
    main()
