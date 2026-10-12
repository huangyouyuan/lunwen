#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Section 1.3 table with patch counts and ENN from full-site data.

Run: python scripts/generate_sec13_spatial_tables.py
Check existing outputs: python scripts/generate_sec13_spatial_tables.py --check
Existing outputs are never overwritten by the generation mode.
"""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results/summary/sec13_sec31_foundations"
UPSTREAM = ROOT / "results/summary/sec33_reference_patch_types"
FEATURES = ROOT / "results/processed/sec33_reference_patch_types/reference_patch_features.csv"
GRADING = ROOT / "results/summary/sec33_indicator_grading_preparation"
# Preserve the preceding AREA/SHAPE-only table at its original path.
COMBINED_TABLE = ROOT / "tables/sec13_spatial_metrics_enn_rows.tex"
SITES = {"A": "iw_2023", "B": "iw2_2023", "C": "ida_2023", "D": "il_2023"}
CATEGORIES = {"corn": "玉米", "soybean": "大豆"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(actual, expected):
    return bool(np.isclose(actual, expected, rtol=0, atol=1e-8))


def pixel_weighted_median(group, metric):
    require(np.isfinite(group[metric]).all(), f"non-finite {metric}")
    require(group.reference_pixels.gt(0).all()
            and group.reference_pixels.eq(group.reference_pixels.astype(np.int64)).all(),
            "weights must be positive integer reference-pixel counts")
    order = np.argsort(group[metric].to_numpy(), kind="stable")
    weights = group.reference_pixels.to_numpy()[order]
    midpoint = (int(weights.sum()) + 1) // 2
    median_index = order[np.searchsorted(np.cumsum(weights), midpoint, side="left")]
    median = float(group[metric].iloc[median_index])
    below = int(group.loc[group[metric].lt(median), "reference_pixels"].sum())
    through = int(group.loc[group[metric].le(median), "reference_pixels"].sum())
    require(2 * below < int(weights.sum()) <= 2 * through,
            f"{metric}: weighted median does not cross 50% at the first value")
    return median, bool(group.touches_outer_edge.iloc[median_index])


def build_tables():
    names = (
        "reference_composition.csv", "class_background_full_scope.csv",
        "landscape_background_full_scope.csv", "crop_patch_distribution_reading.csv",
        "crop_patch_support_and_limitations.csv",
    )
    manifest = json.loads((SOURCE / "manifest.json").read_text(encoding="utf-8"))
    recorded = {entry["path"]: entry["sha256"] for entry in manifest["outputs"]}
    for name in names:
        path = SOURCE / name
        require(digest(path) == recorded[path.relative_to(ROOT).as_posix()],
                f"foundation summary hash differs: {name}")

    grading_manifest = json.loads((GRADING / "delivery_manifest.json").read_text(encoding="utf-8"))
    enn_path = GRADING / "indicator_distribution_reading.csv"
    require(digest(enn_path) == grading_manifest["files"][enn_path.relative_to(ROOT).as_posix()],
            "indicator reading hash differs")
    require(digest(FEATURES) == grading_manifest["inputs"][FEATURES.relative_to(ROOT).as_posix()],
            "complete patch feature hash differs")

    composition, classes, landscape, distributions, support = (
        pd.read_csv(SOURCE / name, float_precision="round_trip") for name in names
    )
    features = pd.read_csv(FEATURES, float_precision="round_trip")
    enn_reading = pd.read_csv(enn_path, float_precision="round_trip")
    raw_classes = pd.read_csv(UPSTREAM / "background_class.csv", float_precision="round_trip")
    raw_landscape = pd.read_csv(UPSTREAM / "background_landscape.csv", float_precision="round_trip")
    raw_classes = raw_classes.loc[raw_classes.scope.eq("full")]
    raw_landscape = raw_landscape.loc[raw_landscape.scope.eq("full")]

    require(len(features) == 187372 and not features.duplicated(["target", "PID"]).any(),
            "complete patch identity/count mismatch")
    require(features.feature_status.eq("valid").all(), "invalid patch feature")
    require(features[["AREA", "SHAPE", "ENN", "reference_pixels"]].notna().all().all(),
            "missing patch feature")
    require(np.allclose(features.AREA, features.reference_pixels * 0.09, rtol=0, atol=1e-8),
            "AREA/pixel mismatch")
    require(len(composition) == len(classes) == len(raw_classes) == 12,
            "expected four sites and three classes")
    require(len(landscape) == len(raw_landscape) == 4, "expected four landscape records")

    feature_groups = features.groupby(["target", "site", "crop"], sort=False)
    comp = composition.set_index(["target", "site", "crop"])
    class_summary = classes.set_index(["target", "site", "crop"])
    raw_class = raw_classes.set_index(["dataset_id", "class_name"])
    whole = landscape.set_index(["target", "site"])
    raw_whole = raw_landscape.set_index("dataset_id")
    dist = distributions.loc[
        distributions.metric.isin(["AREA", "SHAPE"])
        & distributions.weighting.eq("reference_pixel_area")
        & distributions.distribution_level.eq("reference_pixel_area")
        & distributions.algorithm.eq("inverse_weighted_ecdf")
    ].set_index(["target", "site", "crop", "metric"])
    limits = support.set_index(["target", "site", "crop"])
    require(len(dist) == 16 and not dist.index.has_duplicates, "patch distribution keys")
    enn_dist = enn_reading.loc[
        enn_reading.domain.eq("site_crop") & enn_reading.metric.eq("ENN")
        & enn_reading.weighting.eq("reference_pixel_area")
        & enn_reading.algorithm.eq("inverse_weighted_ecdf")
    ].set_index(["target", "site", "crop", "metric"])
    require(len(enn_dist) == 8 and enn_dist.index.is_unique, "ENN distribution keys")
    expected_keys = {(target, site, crop) for site, target in SITES.items()
                     for crop in ("corn", "soybean", "other")}
    require(set(feature_groups.groups) == expected_keys
            and set(comp.index) == expected_keys and comp.index.is_unique
            and set(class_summary.index) == expected_keys and class_summary.index.is_unique
            and raw_class.index.is_unique and whole.index.is_unique,
            "site/class identities or duplicate summary keys")
    expected_edge = (features.row_min.eq(0) | features.col_min.eq(0)
                     | features.row_max.eq(2559) | features.col_max.eq(2559))
    require(features.touches_outer_edge.equals(expected_edge), "outer-edge flag/bounds mismatch")
    for key, group in feature_groups:
        target, site, crop = key
        cls = class_summary.loc[key]
        source_cls = raw_class.loc[(target, crop)]
        pixels = int(group.reference_pixels.sum())
        require(group.TYPE.eq({"corn": "cls_1", "other": "cls_2", "soybean": "cls_3"}[crop]).all(),
                f"{key}: reference class code")
        require(pixels == int(comp.loc[key, "pixels"]) == int(cls.pixels)
                == int(source_cls.class_pixels), f"{key}: composition pixel support")
        require(close(float(comp.loc[key, "area_ha"]), pixels * 0.09)
                and close(float(comp.loc[key, "area_share"]), pixels / 6553600),
                f"{key}: composition area or denominator")
        require(bool(cls.verified) and bool(source_cls.verified)
                and len(group) == int(cls.patch_count_8n) == int(source_cls.patch_count_8n)
                and close(float(cls.patch_density_per_100ha), len(group) / 589824 * 100)
                and close(float(cls.patch_density_per_100ha), float(source_cls.pd_recomputed))
                and close(float(cls.aggregation_index), float(source_cls.ai_recomputed)),
                f"{key}: full-scope class support or metrics")

    combined_rows = ["% AREA、SHAPE、ENN为参考像元面积加权中位数（全体斑块最小值～最大值）；斑块数与斑块属性并列，PD、AI为类别级，ED为整站三类景观级。"]
    extremes = []
    for site, target in SITES.items():
        site_comp = composition.loc[composition.site.eq(site)]
        require(set(site_comp.crop) == {"corn", "soybean", "other"},
                f"{site}: composition classes")
        require(site_comp.pixels.sum() == 6553600, f"{site}: site pixel denominator")
        require(close(site_comp.area_share.sum(), 1), f"{site}: area shares")
        require(close(float(whole.loc[(target, site), "edge_density_m_per_ha"]),
                      float(raw_whole.loc[target, "ed_recomputed"])), f"{site}: ED source")
        require(bool(whole.loc[(target, site), "verified"])
                and bool(raw_whole.loc[target, "verified"]), f"{site}: ED verification")
        for index, (crop, crop_name) in enumerate(CATEGORIES.items()):
            key = (target, site, crop)
            group = feature_groups.get_group(key)
            cls = class_summary.loc[key]
            source_cls = raw_class.loc[(target, crop)]
            require(bool(cls.verified) and bool(source_cls.verified), f"{key}: class verification")
            require(len(group) == int(cls.patch_count_8n) == int(source_cls.patch_count_8n),
                    f"{key}: patch count")
            require(int(group.reference_pixels.sum()) == int(comp.loc[key, "pixels"])
                    == int(cls.pixels), f"{key}: pixel support")
            require(len(group) == int(limits.loc[key, "n_patches"])
                    and int(group.reference_pixels.sum()) == int(limits.loc[key, "pixels"])
                    and int(group.touches_outer_edge.sum()) == int(limits.loc[key, "edge_patches"]),
                    f"{key}: crop patch support")
            singleton_count = int(group.reference_pixels.eq(1).sum())
            singleton_patch_share = singleton_count / len(group)
            singleton_area_share = singleton_count / int(group.reference_pixels.sum())
            require(singleton_count == int(limits.loc[key, "singleton_count"])
                    and close(singleton_patch_share, float(limits.loc[key, "singleton_patch_share"]))
                    and close(singleton_area_share, float(limits.loc[key, "singleton_area_share"])),
                    f"{key}: singleton count or crop-specific denominator")
            pd_value = float(cls.patch_density_per_100ha)
            ai_value = float(cls.aggregation_index)
            require(close(pd_value, len(group) / 589824 * 100)
                    and close(pd_value, float(source_cls.pd_recomputed))
                    and close(ai_value, float(source_cls.ai_recomputed)),
                    f"{key}: class metric/source mismatch")
            stats = {}
            edge_status = {}
            for metric in ("AREA", "SHAPE", "ENN"):
                values = group[metric]
                median, median_touches_edge = pixel_weighted_median(group, metric)
                minimum, maximum = float(values.min()), float(values.max())
                require(minimum <= median <= maximum, f"{key}: {metric} statistic ordering")
                reading = (enn_dist if metric == "ENN" else dist).loc[(*key, metric)]
                require(reading.current_status == "Verified"
                        and reading.unit == {"AREA": "ha", "SHAPE": "dimensionless", "ENN": "m"}[metric]
                        and int(reading.n_total) == len(group)
                        and int(reading.pixels_total) == int(group.reference_pixels.sum())
                        and all(close(actual, float(reading[field])) for actual, field in
                                ((minimum, "minimum"), (median, "median"),
                                 (maximum, "maximum"))),
                        f"{key}: {metric} order statistics differ from summary")
                if metric == "ENN":
                    require(int(reading.n_valid) == len(group)
                            and int(reading.pixels_valid) == int(group.reference_pixels.sum())
                            and int(reading.n_missing_or_invalid) == 0
                            and int(reading.pixels_missing_or_invalid) == 0
                            and minimum >= 60,
                            f"{key}: ENN coverage or 30-m/8-neighbor lower bound")
                stats[metric] = (minimum, median, maximum)
                edge_status[metric] = {
                    "weighted_median_touches_outer_edge": median_touches_edge,
                    "minimum_touches_outer_edge": bool(group.loc[values.eq(minimum),
                                                                  "touches_outer_edge"].any()),
                    "maximum_touches_outer_edge": bool(group.loc[values.eq(maximum),
                                                                  "touches_outer_edge"].any()),
                    "maximum_PIDs": [int(pid) for pid in group.loc[values.eq(maximum), "PID"]],
                }
            extremes.append({"site": site, "crop": crop, "n_patches": len(group),
                             "reference_pixels": int(group.reference_pixels.sum()),
                             "singleton_count": singleton_count,
                             "singleton_patch_share": singleton_patch_share,
                             "singleton_area_share": singleton_area_share,
                             "AREA": stats["AREA"], "SHAPE": stats["SHAPE"],
                             "ENN": stats["ENN"], "PD": pd_value, "AI": ai_value,
                             "ED": float(whole.loc[(target, site), "edge_density_m_per_ha"]),
                             "outer_edge": edge_status})

            site_cell = rf"\multirow{{2}}{{*}}{{{site}}}" if index == 0 else ""
            area_cell = f"{stats['AREA'][1]:.2f}（{stats['AREA'][0]:.2f}～{stats['AREA'][2]:.2f}）"
            shape_cell = f"{stats['SHAPE'][1]:.2f}（{stats['SHAPE'][0]:.2f}～{stats['SHAPE'][2]:.2f}）"
            enn_cell = f"{stats['ENN'][1]:.2f}（{stats['ENN'][0]:.2f}～{stats['ENN'][2]:.2f}）"
            ed_cell = (rf"\multirow{{2}}{{*}}{{{float(whole.loc[(target, site), 'edge_density_m_per_ha']):.2f}}}"
                       if index == 0 else "")
            combined_rows.append(f"{site_cell} & {crop_name} & {area_cell} & {shape_cell} & "
                                 f"{enn_cell} & {len(group)} & "
                                 f"{pd_value:.2f} & {ai_value:.2f} & {ed_cell} " + r"\\")
        if site != "D":
            combined_rows.append(r"\addlinespace[2pt]")
    return {COMBINED_TABLE: "\n".join(combined_rows) + "\n"}, extremes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="check current files without writing")
    args = parser.parse_args()
    tables, extremes = build_tables()
    if not args.check:
        for path in tables:
            if path.exists():
                raise FileExistsError(f"preserve existing output; use --check: {path}")
    for path, content in tables.items():
        if args.check:
            require(path.exists() and path.read_text(encoding="utf-8") == content,
                    f"table differs from verified source: {path}")
        else:
            with path.open("x", encoding="utf-8", newline="\n") as output:
                output.write(content)
    print(json.dumps({"status": "Verified", "check_only": args.check,
                      "patches": sum(row["n_patches"] for row in extremes),
                      "extremes": extremes}, ensure_ascii=False))


if __name__ == "__main__":
    main()
