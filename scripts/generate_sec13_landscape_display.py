#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Section 1.3.2 presentation only: reuse saved ENN median/minimum/P90 and AREA-SHAPE bins.

python -B scripts/generate_sec13_landscape_display.py
python -B scripts/generate_sec13_landscape_display.py --check

No landscape metric, bin assignment or prediction is recomputed. Existing
outputs are protected; preserve them before generating another revision.
"""
import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pymupdf
from matplotlib import font_manager

import plot_area_shape_joint_bubbles as bubbles

ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "results/summary/sec13_sec31_foundations"
GRADING = ROOT / "results/summary/sec33_indicator_grading_preparation"
JOINT = ROOT / "results/summary/area_shape_joint_bubbles_v3/area_shape_joint_bins.csv"
SUMMARY = ROOT / "results/summary/sec13_landscape_display"
FIGURES = ROOT / "figures/study_area"
TABLE = ROOT / "tables/sec13_landscape_context_rows.tex"
BUILD = ROOT / "output/build/sec132-square-axes-2026-10-15/figure"
STEM = "fig_sec13_area_shape_joint"
SITES = {"A": "iw_2023", "B": "iw2_2023", "C": "ida_2023", "D": "il_2023"}
CROPS = {"corn": "玉米", "soybean": "大豆"}
PANEL_WIDTH_CM = 7.6
PANEL_HEIGHT_CM = 7.6
PANEL_CANVAS_CM = 8.9
FRAME_HEIGHT_CM = 9.0
FRAME_LEFT_CM = 1.25
FRAME_BOTTOM_CM = .8
AREA_TICKS = ["<10", "10–50", "50–100", "100–200", "200–500", "≥500"]
SHAPE_TICKS = ["1–1.5", "1.5–2", "2–3", "≥3"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return pd.read_csv(path, float_precision="round_trip")


def build_reading():
    classes_path = FOUNDATIONS / "class_background_full_scope.csv"
    landscape_path = FOUNDATIONS / "landscape_background_full_scope.csv"
    support_path = FOUNDATIONS / "crop_patch_support_and_limitations.csv"
    composition_path = FOUNDATIONS / "reference_composition.csv"
    dist_path = GRADING / "indicator_distribution_reading.csv"
    foundation_hashes = {x["path"]: x["sha256"] for x in json.loads(
        (FOUNDATIONS / "manifest.json").read_text(encoding="utf-8"))["outputs"]}
    for path in (classes_path, landscape_path, support_path, composition_path):
        require(digest(path) == foundation_hashes[path.relative_to(ROOT).as_posix()],
                f"Foundation source hash differs: {path}")
    grading_manifest = json.loads((GRADING / "delivery_manifest.json").read_text(encoding="utf-8"))
    require(digest(dist_path) == grading_manifest["files"][dist_path.relative_to(ROOT).as_posix()],
            "Saved quantile source hash differs")
    old = json.loads((JOINT.parent / "manifest.json").read_text(encoding="utf-8"))
    require(digest(JOINT) == old["output_sha256"][JOINT.relative_to(ROOT).as_posix()],
            "Joint-bin source hash differs")
    classes = read(classes_path).set_index(["site", "crop"])
    landscape = read(landscape_path).set_index("site")
    support = read(support_path).set_index(["site", "crop"])
    composition = read(composition_path).set_index(["site", "crop"])
    dist = read(dist_path)
    enn = dist.loc[dist.domain.eq("site_crop") & dist.metric.eq("ENN")
                   & dist.weighting.eq("patch_equal")].set_index(["site", "crop"])
    require(len(enn) == 8 and enn.index.is_unique, "Expected eight ENN groups")
    joint = read(JOINT)
    require(len(joint) == 192 and not joint.duplicated(
        ["site", "crop", "area_bin_order", "shape_bin_order"]).any(), "Joint-bin identities")
    table, reading, closure = [], [], []
    for site, target in SITES.items():
        land = landscape.loc[site]
        require(land.target == target and bool(land.verified)
                and land.scope_note == "whole_landscape_not_crop_specific", "ED scope")
        for crop, label in CROPS.items():
            cls, quant, sup = classes.loc[(site, crop)], enn.loc[(site, crop)], support.loc[(site, crop)]
            require(cls.target == quant.target == target and bool(cls.verified), "Site/class identity")
            require(quant.algorithm == "linear_order_statistics" and quant.unit == "m"
                    and quant.current_status == "Verified", "ENN weighting/algorithm/unit")
            require(quant.n_total == quant.n_valid == cls.patch_count_8n == sup.n_patches
                    and quant.pixels_total == quant.pixels_valid == cls.pixels == sup.pixels
                    and quant.n_missing_or_invalid == quant.pixels_missing_or_invalid == 0,
                    "ENN complete-reference support")
            comp = composition.loc[(site, crop)]
            require(comp.target == target and int(comp.pixels) == int(cls.pixels)
                    and abs(comp.area_share - comp.pixels / comp.total_pixels) < 1e-12,
                    "Composition share/denominator")
            table.append(dict(target=target, site=site, crop=crop, crop_label=label,
                              area_share_pct=float(100 * comp.area_share),
                              site_total_pixels=int(comp.total_pixels),
                              patch_count=int(cls.patch_count_8n), ai_pct=float(cls.aggregation_index),
                              enn_median_m=float(quant['median']), enn_min_m=float(quant.minimum),
                              enn_max_m=float(quant.maximum), enn_p90_m=float(quant.q90),
                              enn_weighting="patch_equal", enn_quantile_algorithm="linear_order_statistics",
                              reference_pixels=int(cls.pixels),
                              landscape_ed_m_per_ha=float(land.edge_density_m_per_ha),
                              ed_scope="whole_landscape_all_three_classes"))
            group = joint.loc[joint.site.eq(site) & joint.crop.eq(crop)]
            require(len(group) == 24 and group.target.eq(target).all(), "Joint-bin coverage")
            require(int(group.patch_count.sum()) == int(cls.patch_count_8n)
                    and int(group.reference_pixels.sum()) == int(cls.pixels)
                    == int(composition.loc[(site, crop), "pixels"]), "Joint count/area closure")
            require(np.allclose(group.area_ha, group.reference_pixels * .09, rtol=0, atol=1e-9)
                    and np.allclose(group.area_share_pct, 100 * group.reference_pixels / cls.pixels,
                                    rtol=0, atol=1e-12)
                    and abs(group.area_share_pct.sum() - 100) < 1e-10, "Joint shares/denominator")
            require(int(group.singleton_patch_count.sum()) == int(sup.singleton_count)
                    and int(group.outer_edge_patch_count.sum()) == int(sup.edge_patches),
                    "Singleton/outer-edge patches must remain included")
            top = group.nlargest(3, "area_share_pct")
            small = group.area_bin_order.eq(0)
            reading.append(dict(site=site, crop=crop,
                shape_below_2_area_pct=float(group.loc[group.shape_bin_order.lt(2), "area_share_pct"].sum()),
                top3_joint_area_pct=float(top.area_share_pct.sum()),
                largest_cell_area_bin=int(top.iloc[0].area_bin_order),
                largest_cell_shape_bin=int(top.iloc[0].shape_bin_order),
                largest_cell_area_pct=float(top.iloc[0].area_share_pct),
                area_below_10_patch_pct=float(100 * group.loc[small, "patch_count"].sum() / cls.patch_count_8n),
                area_below_10_area_pct=float(group.loc[small, "area_share_pct"].sum()),
                area_ge200_shape_ge3_area_pct=float(group.loc[
                    group.area_bin_order.ge(4) & group.shape_bin_order.eq(3), "area_share_pct"].sum())))
            closure.append(dict(site=site, crop=crop, patch_count=int(cls.patch_count_8n),
                                reference_pixels=int(cls.pixels), area_ha=float(cls.pixels * .09),
                                area_share_sum_pct=float(group.area_share_pct.sum()),
                                zero_cells=int(group.patch_count.eq(0).sum()), status="Verified"))
    sources = [classes_path, landscape_path, support_path, composition_path, dist_path, JOINT]
    return pd.DataFrame(table), pd.DataFrame(reading), pd.DataFrame(closure), joint, sources


def table_rows(table):
    lines = ["% Patch level: ENN patch-equal median (minimum to P90); class level: area share, NP, AI;",
             "% landscape level: whole-site three-class ED."]
    for site in SITES:
        for i, crop in enumerate(CROPS):
            row = table.loc[table.site.eq(site) & table.crop.eq(crop)].iloc[0]
            site_cell = rf"\multirow{{2}}{{*}}{{{site}}}" if i == 0 else ""
            ed_cell = rf"\multirow{{2}}{{*}}{{{row.landscape_ed_m_per_ha:.2f}}}" if i == 0 else ""
            lines.append(f"{site_cell} & {CROPS[crop]} & "
                         f"{row.enn_median_m:.2f}（{row.enn_min_m:.2f}～{row.enn_p90_m:.2f}） & "
                         f"{row.area_share_pct:.2f} & {int(row.patch_count)} & {row.ai_pct:.2f} & {ed_cell} " + r"\\")
        if site != "D":
            lines.append(r"\addlinespace[2pt]")
    return "\n".join(lines) + "\n"


def draw_current_frames(summary, path):
    """Use saved bins and bubble scale, with complete axes on both panels."""
    fs = bubbles.fs
    fs.setup()
    baseline = json.loads((JOINT.parent / "manifest.json").read_text(encoding="utf-8"))
    scale = baseline["geometry"]["scatter_s_pt2_per_pct"]
    offsets = baseline["geometry"]["offsets"]
    width = 2 * PANEL_CANVAS_CM
    fig = fs.plt.figure(figsize=(width / 2.54, FRAME_HEIGHT_CM / 2.54))
    axes, panels, gaps, clearances = [], [], [], []
    positive = summary.loc[summary.reference_pixels.gt(0)]
    for j, crop in enumerate(CROPS):
        left = FRAME_LEFT_CM + j * PANEL_CANVAS_CM
        ax = fig.add_axes([left / width, FRAME_BOTTOM_CM / FRAME_HEIGHT_CM,
                           PANEL_WIDTH_CM / width, PANEL_HEIGHT_CM / FRAME_HEIGHT_CM])
        axes.append(ax)
        circles = []
        for site in SITES:
            points = positive.loc[positive.crop.eq(crop) & positive.site.eq(site)]
            dx, dy = offsets[site]
            x = points.area_bin_order.to_numpy() + dx
            y = points.shape_bin_order.to_numpy() + dy
            sizes = points.area_share_pct.to_numpy() * scale
            ax.scatter(x, y, s=sizes, color=bubbles.SITE_COLORS[site],
                       edgecolors="none", linewidths=0, alpha=1, zorder=3)
            circles.extend(zip(x, y, np.sqrt(sizes) / 2))
        ax.set_xlim(-.5, 5.5)
        ax.set_ylim(-.5, 3.5)
        ax.set_xticks(range(6), AREA_TICKS)
        ax.set_yticks(range(4), SHAPE_TICKS)
        ax.tick_params(length=0, pad=2)
        ax.tick_params(axis="y", labelrotation=90)
        for tick in ax.get_yticklabels():
            tick.set_verticalalignment("center")
        ax.set_xlabel("面积区间（ha）", labelpad=3)
        ax.set_ylabel("形状指数（SHAPE）", rotation=90, labelpad=2)
        for x in np.arange(.5, 5.5, 1):
            ax.axvline(x, **fs.GROUPED_BAR_GRID, zorder=0)
        for y in np.arange(.5, 3.5, 1):
            ax.axhline(y, **fs.GROUPED_BAR_GRID, zorder=0)
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        bounds = ax.get_window_extent(renderer)
        centers = ax.transData.transform(np.array([[x, y] for x, y, _ in circles]))
        radii = np.array([r for _, _, r in circles]) * fig.dpi / 72
        for i, (center, radius) in enumerate(zip(centers, radii)):
            x, y, _ = circles[i]
            low = ax.transData.transform((round(x) - .5, round(y) - .5))
            high = ax.transData.transform((round(x) + .5, round(y) + .5))
            clearance = min(center[0] - radius - low[0], high[0] - center[0] - radius,
                            center[1] - radius - low[1], high[1] - center[1] - radius)
            require(clearance > .2 * fig.dpi / 72, "Bubble touches a bin boundary")
            clearances.append(float(clearance / fig.dpi * 25.4))
            for k in range(i):
                gap = np.linalg.norm(center - centers[k]) - radius - radii[k]
                require(gap > 0, "Overlapping bubbles")
                gaps.append(float(gap / fig.dpi * 25.4))
        labels = [t.get_window_extent(renderer) for t in ax.get_xticklabels()]
        require(not any(a.overlaps(b) for i, a in enumerate(labels) for b in labels[i+1:]),
                "Overlapping horizontal labels")
        panels.append(dict(crop=crop, nonzero_bubbles=len(circles),
                           left_cm=left, bottom_cm=FRAME_BOTTOM_CM,
                           width_cm=bounds.width / fig.dpi * 2.54,
                           height_cm=bounds.height / fig.dpi * 2.54,
                           y_axis_label="形状指数（SHAPE）", y_ticks=SHAPE_TICKS,
                           y_axis_label_rotation_deg=90, y_tick_rotation_deg=90))
    for j, ax in enumerate(axes):
        for item in [*ax.get_xticklabels(), *ax.get_yticklabels(), ax.xaxis.label, ax.yaxis.label]:
            box = item.get_window_extent(renderer)
            lo, hi = j * PANEL_CANVAS_CM / 2.54 * fig.dpi, (j+1) * PANEL_CANVAS_CM / 2.54 * fig.dpi
            require(box.x0 >= lo and box.x1 <= hi and box.y0 >= 0 and box.y1 <= fig.bbox.height,
                    f"Axis text outside its panel: {item.get_text()} {box.bounds}")
    with fs.plt.rc_context({"savefig.bbox": None}):
        fig.savefig(path, bbox_inches=None, facecolor="white")
    fs.plt.close(fig)
    return dict(fonts={name: font_manager.findfont(name, fallback_to_default=False)
                       for name in ["Times New Roman", "SimSun"]},
                panels=panels, scatter_s_pt2_per_pct=scale, circle_area_pt2_per_pct=math.pi/4*scale,
                observed_max_share_pct=float(positive.area_share_pct.max()),
                min_circle_gap_mm=min(gaps), min_cell_boundary_clearance_mm=min(clearances),
                offsets=offsets, min_bubble_floor=None, figure_width_cm=width,
                frame_height_cm=FRAME_HEIGHT_CM, panel_canvas_width_cm=PANEL_CANVAS_CM,
                area_tick_labels=AREA_TICKS, shape_tick_labels=SHAPE_TICKS,
                interval_convention="left closed, right open; last includes its lower limit",
                legend=[dict(share_pct=p, diameter_pt=math.sqrt(scale*p),
                             diameter_mm=math.sqrt(scale*p)/72*25.4) for p in [1,5,20]])


def legend_tex(geometry):
    lines = [r"\begin{tikzpicture}[x=1cm,y=1cm,every node/.style={inner sep=0pt,font=\songti\rmfamily\zihao{-5}}]",
             r"\path[use as bounding box] (0,0) rectangle (13.5,0.72);",
             r"\node[anchor=west] at (0,0.36) {站点};"]
    for i, site in enumerate(SITES):
        x = 1.1 + .9 * i
        lines += [rf"\definecolor{{jointsite{site}}}{{HTML}}{{{bubbles.SITE_COLORS[site][1:]}}}",
                  rf"\fill[jointsite{site}] ({x:.4f},0.36) circle[radius=0.09cm];",
                  rf"\node[anchor=west] at ({x + .17:.4f},0.36) {{{site}}};"]
    lines += [r"\node[anchor=west] at (5.0,0.36) {作物面积占比};",
              r"\definecolor{jointbubblegray}{HTML}{777777}"]
    for item, x in zip(geometry["legend"], [7.7, 9.5, 11.5]):
        radius = item["diameter_mm"] / 20
        lines += [rf"\fill[jointbubblegray] ({x:.5f},0.36) circle[radius={radius:.12f}cm];",
                  rf"\node[anchor=west] at ({x + radius + .13:.5f},0.36) {{{item['share_pct']}\%}};"]
    return "\n".join(lines + [r"\end{tikzpicture}", ""])


def figure_body():
    return rf"""% Generated presentation; original bins and v3 plot remain unchanged.
% Center the wider canvas without scaling the square plotting frames.
\noindent\makebox[\linewidth][c]{{%
\begin{{subfigure}}{{{PANEL_CANVAS_CM:.1f}cm}}\centering
\includegraphics{{study_area/{STEM}_a.pdf}}
\caption{{玉米面积—形状联合分布}}
\end{{subfigure}}%
\begin{{subfigure}}{{{PANEL_CANVAS_CM:.1f}cm}}\centering
\includegraphics{{study_area/{STEM}_b.pdf}}
\caption{{大豆面积—形状联合分布}}
\end{{subfigure}}%
}}\par\nointerlineskip\vspace{{3pt}}
\input{{figures/study_area/{STEM}_legend.tex}}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="read-only source and output verification")
    parser.add_argument("--figure-only", action="store_true", help="verify and preserve saved tables; generate figure only")
    parser.add_argument("--table-only", metavar="ARCHIVE_DIR",
                        help="rewrite table/CSV outputs only after byte-identical archiving; figure untouched")
    args = parser.parse_args()
    table, reading, closure, joint, sources = build_reading()
    texts = {TABLE: table_rows(table)}
    for name, data in [("table1_landscape_context.csv", table), ("joint_distribution_reading.csv", reading),
                       ("closure_checks.csv", closure)]:
        texts[SUMMARY / name] = data.to_csv(index=False, float_format="%.17g", lineterminator="\n")
    if args.check:
        for path, value in texts.items():
            require(path.read_text(encoding="utf-8") == value, f"Display output differs: {path}")
        manifest = json.loads((SUMMARY / "manifest.json").read_text(encoding="utf-8"))
        relocation_path = ROOT / "verification/output-organization-2026-10-15.json"
        relocations = json.loads(relocation_path.read_text(encoding="utf-8"))["files"] if relocation_path.exists() else []
        routing_path = ROOT / "verification/artifact-locations-2026-10-15.json"
        if routing_path.exists():
            relocations += json.loads(routing_path.read_text(encoding="utf-8"))["files"]
        for group in ("input_sha256", "output_sha256"):
            for name, expected in manifest[group].items():
                candidates = [ROOT / name]
                # Preserve the recorded generation source; path-only maintenance
                # does not retroactively change which script produced the figures.
                if group == "input_sha256" and name.startswith("scripts/"):
                    candidates.extend(ROOT / row["archive_path"].replace("output/archive/", "archive/manuscript/", 1)
                                      for row in relocations
                                      if row["action"] in ("snapshot", "reuse_snapshot") and row["original_path"] == name
                                      and row["sha256"] == expected)
                require(any(path.is_file() and digest(path) == expected for path in candidates),
                        f"Recorded hash differs: {name}")
        print(json.dumps(dict(status="Verified", groups=8, joint_cells=192,
                              patches=int(table.patch_count.sum()), enn="reused patch-equal median, minimum and P90")))
        return
    figure_paths = [FIGURES / f"{STEM}{suffix}" for suffix in
                    ["_frames.pdf", "_a.pdf", "_b.pdf", "_legend.tex", ".tex", ".pdf", ".png"]]
    if args.table_only:
        # Rewrite text outputs only; figure 3 must stay byte-identical and every
        # replaced file must already have a byte-identical copy in the archive.
        archive = ROOT / args.table_only
        manifest_path = SUMMARY / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for path in figure_paths:
            name = path.relative_to(ROOT).as_posix()
            require(digest(path) == manifest["output_sha256"][name], f"Figure changed: {name}")
        for path in [*texts, manifest_path]:
            if path.exists():
                kept = archive / path.relative_to(ROOT)
                require(kept.is_file() and digest(kept) == digest(path), f"Archive first: {path}")
        old_script = manifest["input_sha256"]["scripts/generate_sec13_landscape_display.py"]
        for path, value in texts.items():
            path.write_text(value, encoding="utf-8", newline="\n")
        manifest["figure_generation_script_sha256"] = old_script
        manifest["table_revision"] = dict(
            date="2026-10-16", archive=args.table_only,
            change="Table 1 ENN column shows patch-equal median (minimum to P90); maximum kept in CSV only",
            script_sha256=digest(Path(__file__)))
        manifest["input_sha256"]["scripts/generate_sec13_landscape_display.py"] = digest(Path(__file__))
        manifest["output_sha256"].update({p.relative_to(ROOT).as_posix(): digest(p) for p in texts})
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(dict(status="Verified", groups=8, table_only=True,
                              patches=int(table.patch_count.sum())), ensure_ascii=False))
        return
    if args.figure_only:
        for path, value in texts.items():
            require(path.read_text(encoding="utf-8") == value, f"Saved display data differs: {path}")
    for path in [*([] if args.figure_only else texts), *figure_paths, SUMMARY / "manifest.json", BUILD]:
        require(not path.exists(), f"Preserve existing output first: {path}")
    SUMMARY.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=False)
    if not args.figure_only:
        for path, value in texts.items():
            path.write_text(value, encoding="utf-8", newline="\n")
    geometry = draw_current_frames(joint, FIGURES / f"{STEM}_frames.pdf")
    # Equal canvas widths; each panel includes its own y-axis and labels.
    with pymupdf.open(FIGURES / f"{STEM}_frames.pdf") as frames:
        split = PANEL_CANVAS_CM / 2.54 * 72
        for suffix, rect in [("a", pymupdf.Rect(0, 0, split, frames[0].rect.height)),
                             ("b", pymupdf.Rect(split, 0, frames[0].rect.width, frames[0].rect.height))]:
            with pymupdf.open() as out:
                page = out.new_page(width=rect.width, height=rect.height)
                page.show_pdf_page(page.rect, frames, 0, clip=rect)
                out.save(FIGURES / f"{STEM}_{suffix}.pdf")
    (FIGURES / f"{STEM}_legend.tex").write_text(legend_tex(geometry), encoding="utf-8", newline="\n")
    (FIGURES / f"{STEM}.tex").write_text(figure_body(), encoding="utf-8", newline="\n")
    wrapper = rf"""\documentclass[border=0pt]{{standalone}}
\usepackage{{ctex,graphicx,subcaption,tikz}}
\setCJKmainfont{{SimSun}}\setmainfont{{Times New Roman}}
\graphicspath{{{{figures/}}}}
\DeclareCaptionLabelFormat{{cnparen}}{{（#2）}}
\DeclareCaptionFont{{jointfont}}{{\songti\rmfamily\zihao{{-5}}}}
\captionsetup[sub]{{font=jointfont,labelformat=cnparen,labelsep=none,skip=3pt}}
\begin{{document}}
\begin{{minipage}}{{{2 * PANEL_CANVAS_CM:.1f}cm}}\centering
\captionsetup{{type=figure}}\songti\rmfamily\zihao{{-5}}
\input{{figures/study_area/{STEM}.tex}}
\end{{minipage}}
\end{{document}}
"""
    tex_path = BUILD / f"{STEM}.tex"
    tex_path.write_text(wrapper, encoding="utf-8", newline="\n")
    log = bubbles.run_command(["xelatex", "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error",
                               f"-output-directory={BUILD.relative_to(ROOT).as_posix()}",
                               tex_path.relative_to(ROOT).as_posix()], ROOT)
    (BUILD / "compile-output.txt").write_text(log, encoding="utf-8")
    final_pdf = FIGURES / f"{STEM}.pdf"
    shutil.copyfile(BUILD / final_pdf.name, final_pdf)
    bubbles.run_command(["pdftoppm", "-r", "600", "-png", "-singlefile", str(final_pdf),
                         str(FIGURES / STEM)], ROOT)
    sources += [Path(__file__), Path(bubbles.__file__), ROOT / "scripts/figstyle.py",
                JOINT.parent / "manifest.json"]
    manifest = dict(status="Verified", scope="Saved-statistic selection, closure and plot geometry; visual review recorded separately",
        data_status="derived", enn_source=dist_source(),
        enn_algorithm="patch_equal median and P90 (linear order statistics) with observed minimum; maximum kept in CSV only",
        geometry=geometry,
        input_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in sources},
        output_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in [*texts, *figure_paths]})
    (SUMMARY / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(status="Verified", groups=8, patches=int(table.patch_count.sum()),
                          figure=str(final_pdf.relative_to(ROOT))), ensure_ascii=False))


def dist_source():
    return "results/summary/sec33_indicator_grading_preparation/indicator_distribution_reading.csv: site_crop, ENN, patch_equal, median/minimum/q90 (maximum retained in CSV)"


if __name__ == "__main__":
    main()
