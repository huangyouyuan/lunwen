#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Section 1.3.2 presentation only: reuse saved P90 and AREA-SHAPE bins.

python -B scripts/generate_sec13_landscape_display.py
python -B scripts/generate_sec13_landscape_display.py --check

No landscape metric, bin assignment or prediction is recomputed. Existing
outputs are protected; preserve them before generating another revision.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pymupdf

import plot_area_shape_joint_bubbles as bubbles

ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "results/summary/sec13_sec31_foundations"
GRADING = ROOT / "results/summary/sec33_indicator_grading_preparation"
JOINT = ROOT / "results/summary/area_shape_joint_bubbles_v3/area_shape_joint_bins.csv"
SUMMARY = ROOT / "results/summary/sec13_landscape_display"
FIGURES = ROOT / "figures/study_area"
TABLE = ROOT / "tables/sec13_landscape_context_rows.tex"
BUILD = ROOT / "output/build/sec132-landscape/figure"
STEM = "fig_sec13_area_shape_joint"
SITES = {"A": "iw_2023", "B": "iw2_2023", "C": "ida_2023", "D": "il_2023"}
CROPS = {"corn": "玉米", "soybean": "大豆"}


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
            table.append(dict(target=target, site=site, crop=crop, crop_label=label,
                              patch_count=int(cls.patch_count_8n), ai_pct=float(cls.aggregation_index),
                              enn_p90_m=float(quant.q90), enn_median_m=float(quant['median']),
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
    lines = ["% Complete reference patches; ENN P90 is patch-equal, linear order statistics."]
    for site in SITES:
        for i, crop in enumerate(CROPS):
            row = table.loc[table.site.eq(site) & table.crop.eq(crop)].iloc[0]
            site_cell = rf"\multirow{{2}}{{*}}{{{site}}}" if i == 0 else ""
            ed_cell = rf"\multirow{{2}}{{*}}{{{row.landscape_ed_m_per_ha:.2f}}}" if i == 0 else ""
            lines.append(f"{site_cell} & {CROPS[crop]} & {int(row.patch_count)} & "
                         f"{row.ai_pct:.2f} & {row.enn_p90_m:.2f} & {ed_cell} " + r"\\")
        if site != "D":
            lines.append(r"\addlinespace[2pt]")
    return "\n".join(lines) + "\n"


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
\begin{{subfigure}}{{9.1cm}}\centering
\includegraphics{{study_area/{STEM}_a.pdf}}
\caption{{玉米面积—形状联合分布}}
\end{{subfigure}}%
\begin{{subfigure}}{{8.3cm}}\centering
\includegraphics{{study_area/{STEM}_b.pdf}}
\caption{{大豆面积—形状联合分布}}
\end{{subfigure}}\par\nointerlineskip\vspace{{3pt}}
\input{{figures/study_area/{STEM}_legend.tex}}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="read-only source and output verification")
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
        for group in ("input_sha256", "output_sha256"):
            for name, expected in manifest[group].items():
                candidates = [ROOT / name]
                # Preserve the recorded generation source; path-only maintenance
                # does not retroactively change which script produced the figures.
                if group == "input_sha256" and name.startswith("scripts/"):
                    candidates.extend(ROOT / row["archive_path"] for row in relocations
                                      if row["action"] == "snapshot" and row["original_path"] == name
                                      and row["sha256"] == expected)
                require(any(path.is_file() and digest(path) == expected for path in candidates),
                        f"Recorded hash differs: {name}")
        print(json.dumps(dict(status="Verified", groups=8, joint_cells=192,
                              patches=int(table.patch_count.sum()), enn="reused patch-equal P90")))
        return
    figure_paths = [FIGURES / f"{STEM}{suffix}" for suffix in
                    ["_frames.pdf", "_a.pdf", "_b.pdf", "_legend.tex", ".tex", ".pdf", ".png"]]
    for path in [*texts, *figure_paths, SUMMARY / "manifest.json", BUILD]:
        require(not path.exists(), f"Preserve existing output first: {path}")
    SUMMARY.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=False)
    for path, value in texts.items():
        path.write_text(value, encoding="utf-8", newline="\n")
    geometry = bubbles.draw_frames(joint, FIGURES / f"{STEM}_frames.pdf")
    # Split the existing two-panel vector canvas at 9.1 cm without scaling.
    with pymupdf.open(FIGURES / f"{STEM}_frames.pdf") as frames:
        split = 9.1 / 2.54 * 72
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
\begin{{minipage}}{{17.4cm}}\centering
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
                bubbles.BASELINE_DIR / "manifest.json"]
    manifest = dict(status="Verified", scope="Saved-statistic selection, closure and plot geometry; visual review recorded separately",
        data_status="derived", enn_source=dist_source(),
        enn_algorithm="patch_equal; sort n values; interpolate linearly at zero-based (n-1)*0.9",
        geometry=geometry,
        input_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in sources},
        output_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in [*texts, *figure_paths]})
    (SUMMARY / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(status="Verified", groups=8, patches=int(table.patch_count.sum()),
                          figure=str(final_pdf.relative_to(ROOT))), ensure_ascii=False))


def dist_source():
    return "results/summary/sec33_indicator_grading_preparation/indicator_distribution_reading.csv: site_crop, ENN, patch_equal, q90"


if __name__ == "__main__":
    main()
