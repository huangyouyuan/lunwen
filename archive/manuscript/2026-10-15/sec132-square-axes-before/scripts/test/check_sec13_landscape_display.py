#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only independent audit of current Table 1 and the joint figure."""
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pymupdf

ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "results/summary/sec13_landscape_display"
FIGURES = ROOT / "figures/study_area"
STEM = "fig_sec13_area_shape_joint"
SITES = {"A": "iw_2023", "B": "iw2_2023", "C": "ida_2023", "D": "il_2023"}
COLORS = {"A": "0072B2", "B": "E69F00", "C": "009E73", "D": "CC79A7"}


def require(value, message):
    if not value:
        raise AssertionError(message)


def read(path):
    return pd.read_csv(ROOT / path, float_precision="round_trip")


def main():
    features_path = ROOT / "results/processed/sec33_reference_patch_types/reference_patch_features.csv"
    recorded = json.loads((ROOT / "results/summary/area_shape_joint_bubbles_v3/manifest.json").read_text(encoding="utf-8"))
    require(hashlib.sha256(features_path.read_bytes()).hexdigest() == recorded["input_sha256"][
        features_path.relative_to(ROOT).as_posix()], "Complete feature source changed")
    features = read(features_path)
    require(not features.duplicated(["target", "PID"]).any(), "Duplicate reference identity")
    table = read(SUMMARY / "table1_landscape_context.csv")
    classes = read("results/summary/sec33_reference_patch_types/background_class.csv")
    classes = classes.loc[classes.scope.eq("full")].set_index(["dataset_id", "class_name"])
    landscape = read("results/summary/sec33_reference_patch_types/background_landscape.csv")
    landscape = landscape.loc[landscape.scope.eq("full")].set_index("dataset_id")
    p90 = {}
    for row in table.itertuples():
        group = features.loc[features.target.eq(row.target) & features.crop.eq(row.crop)]
        require(row.target == SITES[row.site] and group.site.eq(row.site).all(), "Identity mismatch")
        require(group.feature_status.eq("valid").all() and np.isfinite(group.ENN).all(), "ENN NA/invalid")
        require(len(group) == row.patch_count and group.reference_pixels.sum() == row.reference_pixels,
                "Full reference support differs")
        # Explicit order-statistic interpolation; no weights and no quantile library call.
        ordered = sorted(float(x) for x in group.ENN)
        position = (len(ordered) - 1) * .9
        lower = math.floor(position)
        quantile = ordered[lower] + (position - lower) * (ordered[math.ceil(position)] - ordered[lower])
        require(abs(quantile - row.enn_p90_m) < 1e-9, "P90 not patch-equal linear interpolation")
        cls = classes.loc[(row.target, row.crop)]
        require(cls.patch_count_8n == row.patch_count and abs(cls.ai_recomputed - row.ai_pct) < 1e-10,
                "Full-scope NP/AI differ")
        require(abs(landscape.loc[row.target, "ed_recomputed"] - row.landscape_ed_m_per_ha) < 1e-10,
                "Full-landscape ED differs")
        p90[f"{row.site}/{row.crop}"] = quantile
    joint = read("results/summary/area_shape_joint_bubbles_v3/area_shape_joint_bins.csv")
    a = joint.loc[joint.site.eq("A")]
    require(all(a.groupby("crop").apply(lambda x: x.nlargest(1, "area_share_pct").iloc[0].area_bin_order,
                                       include_groups=False).eq(3)), "A leading AREA cell")
    top_d = [set(map(tuple, g.nlargest(3, "area_share_pct")[["area_bin_order", "shape_bin_order"]].to_numpy()))
             for _, g in joint.loc[joint.site.eq("D")].groupby("crop")]
    require(top_d[0] == top_d[1], "D's top three combinations differ")
    table_tex = (ROOT / "tables/sec13_landscape_context_rows.tex").read_text(encoding="utf-8")
    require(len([x for x in table_tex.splitlines() if x.endswith(r"\\")]) == 8, "Expected eight table rows")
    for line in table_tex.splitlines():
        if line.endswith(r"\\"):
            require(line.count("&") == 5, "Expected six table columns")

    current = json.loads((SUMMARY / "manifest.json").read_text(encoding="utf-8"))
    scale = recorded["geometry"]["scatter_s_pt2_per_pct"]
    require(current["geometry"]["scatter_s_pt2_per_pct"] == scale, "Original bubble scale changed")
    cm = 72 / 2.54
    offsets = recorded["geometry"]["offsets"]
    with pymupdf.open(FIGURES / f"{STEM}_frames.pdf") as frames:
        page = frames[0]
        curves = [x for x in page.get_drawings() if x["type"] == "f" and x["items"][0][0] == "c"]
        require(len(curves) == len(joint.loc[joint.reference_pixels.gt(0)]) == 169, "Nonzero bubbles")
        points, clearances, errors = [], [], []
        for row in joint.loc[joint.reference_pixels.gt(0)].itertuples():
            left = .85 if row.crop == "corn" else 9.55
            dx, dy = offsets[row.site]
            x = (left + (row.area_bin_order + .5 + dx) * 7.8 / 6) * cm
            y = page.rect.height - (.8 + (row.shape_bin_order + .5 + dy) * 7.6 / 4) * cm
            drawing = min(curves, key=lambda d: math.hypot((d["rect"].x0+d["rect"].x1)/2-x,
                                                         (d["rect"].y0+d["rect"].y1)/2-y))
            box = drawing["rect"]
            require(math.hypot((box.x0+box.x1)/2-x, (box.y0+box.y1)/2-y) < .001, "Circle offset")
            error = abs(box.width - math.sqrt(scale * row.area_share_pct))
            require(error < .002 and abs(box.width-box.height) < .001, "Circle area proportionality")
            rgb = tuple(int(COLORS[row.site][i:i+2], 16)/255 for i in (0, 2, 4))
            require(max(abs(a-b) for a,b in zip(rgb,drawing["fill"])) < .001, "Station color")
            cell_left = (left + row.area_bin_order * 7.8/6) * cm
            cell_bottom = page.rect.height - (.8 + row.shape_bin_order * 7.6/4) * cm
            clearance = min(box.x0-cell_left, cell_left+7.8/6*cm-box.x1,
                            box.y0-(cell_bottom-7.6/4*cm), cell_bottom-box.y1)
            require(clearance > .2, "Circle touches a bin boundary")
            clearances.append(clearance / cm * 10)
            points.append((row.crop, x, y, box.width/2))
            errors.append(error)
        gaps = [math.hypot(x-x2,y-y2)-r-r2 for i,(crop,x,y,r) in enumerate(points)
                for crop2,x2,y2,r2 in points[:i] if crop==crop2]
        require(min(gaps) > 0, "Overlapping bubbles")
    for suffix in ["a", "b"]:
        with pymupdf.open(FIGURES / f"{STEM}_{suffix}.pdf") as doc:
            page = doc[0]
            require(abs(page.rect.width / cm - 8.7) < .001, "Panel canvas width")
            text = page.get_text()
            for label in ["形状指数（SHAPE）", "面积区间（ha）", "1–1.5", "1.5–2", "2–3", "≥3",
                          "<10", "10–50", "50–100", "100–200", "200–500", "≥500"]:
                require(label in text, f"Missing axis label on panel {suffix}: {label}")
            require("–<" not in text, "Old mixed interval notation")
    with pymupdf.open(FIGURES / f"{STEM}.pdf") as doc:
        page = doc[0]
        gray = [d for d in page.get_drawings() if d["type"] == "f" and d["items"][0][0] == "c"
                and max(d["fill"])-min(d["fill"]) < .001]
        require(len(gray) == 3, "Three shared size legend circles")
        for d,pct in zip(sorted(gray,key=lambda d:d["rect"].width),[1,5,20]):
            require(abs(d["rect"].width-math.sqrt(scale*pct)) < .002, "Legend size mismatch")
        require(not page.get_images(), "Figure must remain vector")
        spans = [s for b in page.get_text("dict")["blocks"] if "lines" in b
                 for line in b["lines"] for s in line["spans"]]
        require(all(abs(s["size"]-9) < .02 for s in spans), "Figure font size must remain 9pt")
    report = dict(status="Verified", scope="Independent saved-statistic, P90 and exported vector checks",
                  patches=int(table.patch_count.sum()), enn_p90_m=p90,
                  plotted_nonzero_cells=169, zero_cells=23,
                  max_circle_diameter_error_pt=max(errors),
                  min_circle_gap_mm=min(gaps)/cm*10,
                  min_cell_boundary_clearance_mm=min(clearances),
                  legend_matches_circle_area_scale=True, vector_only=True, text_size_pt=9)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
