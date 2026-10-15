#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""独立核查联合汇总和最终PDF；默认只读，--report写入新核查记录。"""

import argparse
from collections import defaultdict
import csv
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path

import pymupdf
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "results/processed/sec33_reference_patch_types/reference_patch_features.csv"
SITES = {"A": "iw_2023", "B": "iw2_2023", "C": "ida_2023", "D": "il_2023"}
COLORS = {"A": "0072B2", "B": "E69F00", "C": "009E73", "D": "CC79A7"}
OFFSETS = {"A": (-.23, .20), "B": (.245, .20), "C": (-.23, -.20), "D": (.245, -.20)}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def verify_recorded_hash(name, expected):
    """历史清单保留原文；移动文件及旧代码按归档映射核对原字节。"""
    candidates = [ROOT / name]
    for ledger_path in [ROOT / "archive/2026-10-12-area-shape-bubbles/archive-manifest.json",
                        ROOT / "verification/output-organization-2026-10-15.json",
                        ROOT / "verification/artifact-locations-2026-10-15.json"]:
        if ledger_path.exists():
            ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
            candidates.extend(ROOT / r["archive_path"] for r in ledger["files"]
                              if r["original_path"] == name and r["sha256"] == expected)
    candidates = [ROOT / p.relative_to(ROOT).as_posix().replace(
        "output/archive/", "archive/manuscript/", 1) for p in candidates]
    require(any(p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == expected
                for p in candidates), f"哈希不符或缺少归档映射：{name}")


def decimal_bin(value, cutpoints):
    number = Decimal(value)
    require(number.is_finite(), "不允许缺失或无穷值")
    return sum(number >= Decimal(str(cut)) for cut in cutpoints)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", default="area_shape_joint_bubbles_v3")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    require(all(c.isalnum() or c in "_-" for c in args.tag), "非法tag")
    summary_dir = ROOT / "results/summary" / args.tag
    figures = ROOT / "figures/exploratory" / args.tag
    manifest = json.loads((summary_dir / "manifest.json").read_text(encoding="utf-8"))
    baseline_dir = ROOT / "archive/2026-10-12-area-shape-bubbles/history/results/summary/area_shape_joint_bubbles_v2"
    baseline_manifest = json.loads((baseline_dir / "manifest.json").read_text(encoding="utf-8"))
    for filename in ["area_shape_joint_bins.csv", "closure_checks.csv"]:
        require((summary_dir / filename).read_bytes() == (baseline_dir / filename).read_bytes(), "本轮统计CSV与v2字节不一致")
    for kind in ["input_sha256", "output_sha256"]:
        for name, expected in manifest[kind].items():
            verify_recorded_hash(name, expected)

    # 不调用生产分档函数，直接从原CSV按十进制阈值比较。
    feature_rows = [r for r in rows(SOURCE) if r["crop"] in {"corn", "soybean"}]
    raw = {}
    duplicates = 0
    raw_paths = sorted((ROOT / "results/raw/sec33_reference_patch_types").glob("2023*_patch.csv"))
    require(len(raw_paths) == 4, "原始斑块CSV数量不符")
    for path in raw_paths:
        for row in rows(path):
            key = row["LID"], row["PID"]
            if key in raw:
                require(raw[key] == row, "原始重复记录不一致")
                duplicates += 1
            raw[key] = row
    cells = defaultdict(lambda: [0, 0, 0, 0, 0])
    totals = defaultdict(lambda: [0, 0])
    for row in feature_rows:
        require(SITES[row["site"]] == row["target"], "站点映射不符")
        original = raw[(row["LID"], row["PID"])]
        require(original["TYPE"] == row["TYPE"], "原始类别不符")
        for name in ["AREA", "SHAPE"]:
            require(abs(Decimal(row[name]) - Decimal(original[name])) < Decimal("1e-9"), f"原始{name}不符")
        pixels = int(row["reference_pixels"])
        require(Decimal(original["AREA"]) == Decimal(pixels) * Decimal("0.09"), "原始面积与像元不符")
        require(Decimal(row["AREA"]) > 0 and Decimal(row["SHAPE"]) >= 1, "下界未覆盖")
        ai = decimal_bin(row["AREA"], [10, 50, 100, 200, 500])
        si = decimal_bin(row["SHAPE"], [1.5, 2, 3])
        entry = cells[(row["site"], row["crop"], ai, si)]
        entry[0] += 1
        entry[1] += pixels
        entry[2] += pixels == 1
        entry[3] += row["touches_outer_edge"] == "True"
        entry[4] += pixels if row["touches_outer_edge"] == "True" else 0
        totals[(row["site"], row["crop"])][0] += 1
        totals[(row["site"], row["crop"])][1] += pixels
    saved = rows(summary_dir / "area_shape_joint_bins.csv")
    require(len(saved) == 192, "必须保留192个组合，包括零值")
    keys = set()
    group_shares = defaultdict(list)
    for row in saved:
        key = row["site"], row["crop"], int(row["area_bin_order"]), int(row["shape_bin_order"])
        require(key not in keys, "分档汇总重复")
        keys.add(key)
        values = [int(row[n]) for n in ["patch_count", "reference_pixels", "singleton_patch_count", "outer_edge_patch_count", "outer_edge_pixels"]]
        require(values == cells[key], f"独立分档不符：{key}")
        denominator = totals[key[:2]][1]
        require(abs(float(row["area_ha"]) - values[1] * .09) < 1e-8, "面积不符")
        require(abs(float(row["total_crop_area_ha"]) - denominator * .09) < 1e-8, "分母不符")
        require(abs(float(row["area_share_pct"]) - 100 * values[1] / denominator) < 1e-12, "占比不符")
        group_shares[key[:2]].append(float(row["area_share_pct"]))
    require(len(keys) == 192 and len(group_shares) == 8, "覆盖不完整")
    require(all(abs(math.fsum(v) - 100) < 1e-12 for v in group_shares.values()), "八组占比未闭合")

    # 在导出的矢量PDF中读取真实圆路径，而不是只核查传给scatter的参数。
    pdf = figures / "fig_area_shape_joint_bubbles.pdf"
    doc = pymupdf.open(pdf)
    require(len(doc) == 1, "图件应为一页")
    page = doc[0]
    require(not page.get_images(full=True), "矢量PDF不应嵌入位图")
    require(abs(page.rect.width / 72 * 2.54 - 17.4) < .001, "画布宽度变化")
    require(abs(page.rect.height / 72 * 2.54 - 11.2) < .001, "画布高度不符")
    borders = [d for d in page.get_drawings() if d["type"] == "s" and abs(d["width"] - .6) < .001]
    horizontal = [d for d in borders if d["rect"].height < .001 and abs(d["rect"].width / 72 * 2.54 - 7.6) < .001]
    vertical = [d for d in borders if d["rect"].width < .001 and abs(d["rect"].height / 72 * 2.54 - 7.6) < .001]
    require(len(horizontal) == 4 and len(vertical) == 4, "PDF实际绘图区不是两个7.6 cm正方形")
    spans = [s for b in page.get_text("dict")["blocks"] if "lines" in b for l in b["lines"] for s in l["spans"]]
    require(all(abs(s["size"] - 9) < .005 for s in spans), "字体不全为9 pt")
    require(all("SimSun" in s["font"] or "TimesNewRoman" in s["font"] for s in spans), "字体不符")
    for font in page.get_fonts(full=True):
        require(bool(doc.extract_font(font[0])[3]), "存在未嵌入字体")
    require(all(page.rect.contains(pymupdf.Rect(s["bbox"])) for s in spans), "文字超出页面")
    xlabel = [pymupdf.Rect(s["bbox"]) for s in spans if s["text"] == "AREA"]
    captions = [pymupdf.Rect(s["bbox"]) for s in spans if s["text"] in {"a", "b"}]
    require(len(xlabel) == 2 and len(captions) == 2, "双子图文字不完整")
    require(all(a.y1 < b.y0 for a, b in zip(xlabel, captions)), "轴标签与子图题重叠")
    curves = [d for d in page.get_drawings() if d["fill"] is not None and all(i[0] == "c" for i in d["items"])]
    positive = [r for r in saved if int(r["patch_count"]) > 0]
    require(len(curves) == len(positive) + 4 + 3, "气泡、站点图例或大小图例数量不符")
    scale = manifest["geometry"]["scatter_s_pt2_per_pct"]
    require(abs(scale / baseline_manifest["geometry"]["scatter_s_pt2_per_pct"] - 2) < 1e-12, "圆面积缩放不是v2的2倍")
    require(manifest["geometry"]["min_bubble_floor"] is None, "不能额外设置最小气泡下限")
    cm_pt = 72 / 2.54
    diam_errors = []
    matched = set()
    circles_by_crop = defaultdict(list)
    cell_clearances = []
    for row in positive:
        dx, dy = OFFSETS[row["site"]]
        left = 1.5 if row["crop"] == "corn" else 9.6
        # TikZ节点默认outer sep为线宽的一半：0.2 TeX pt。
        # includegraphics的south west锚点因此给整张图框统一平移，不改变分档位置。
        node_outer_sep_bp = .2 * 72 / 72.27
        x = (left + (int(row["area_bin_order"]) + .5 + dx) * 7.6 / 6) * cm_pt + node_outer_sep_bp
        y = page.rect.height - (3.4 + (int(row["shape_bin_order"]) + .5 + dy) * 7.6 / 4) * cm_pt - node_outer_sep_bp
        expected_d = math.sqrt(float(row["area_share_pct"]) * scale)
        options = [(math.hypot((d["rect"].x0 + d["rect"].x1) / 2 - x,
                              (d["rect"].y0 + d["rect"].y1) / 2 - y), i, d)
                   for i, d in enumerate(curves) if i not in matched]
        distance, i, drawing = min(options, key=lambda v: v[0])
        require(distance < .015, "实际气泡偏移位置不符")
        require(drawing["type"] == "f", "气泡不应有放大小值的描边")
        require(abs(drawing["rect"].width - drawing["rect"].height) < .001, "气泡不是圆形")
        error = abs(drawing["rect"].width - expected_d)
        require(error < .002, "实际PDF圆面积未按占比线性缩放")
        rgb = tuple(int(COLORS[row["site"]][j:j+2], 16) / 255 for j in (0, 2, 4))
        require(all(abs(a - b) < .001 for a, b in zip(rgb, drawing["fill"])), "站点颜色不符")
        matched.add(i)
        diam_errors.append(error)
        box = drawing["rect"]
        cell_x0 = (left + int(row["area_bin_order"]) * 7.6 / 6) * cm_pt + node_outer_sep_bp
        cell_x1 = cell_x0 + 7.6 / 6 * cm_pt
        cell_y1 = page.rect.height - (3.4 + int(row["shape_bin_order"]) * 7.6 / 4) * cm_pt - node_outer_sep_bp
        cell_y0 = cell_y1 - 7.6 / 4 * cm_pt
        clearance = min(box.x0-cell_x0, cell_x1-box.x1, box.y0-cell_y0, cell_y1-box.y1)
        require(clearance > .2, "气泡碰到或越过分档网格线")
        cell_clearances.append(clearance)
        circles_by_crop[row["crop"]].append(((box.x0 + box.x1) / 2, (box.y0 + box.y1) / 2, box.width / 2))
    min_gap = math.inf
    for circles in circles_by_crop.values():
        for i, (x, y, r) in enumerate(circles):
            for x2, y2, r2 in circles[:i]:
                min_gap = min(min_gap, math.hypot(x-x2, y-y2) - r - r2)
    require(min_gap > 0, "PDF中气泡相交")
    gray = [d for i, d in enumerate(curves) if i not in matched and max(d["fill"]) - min(d["fill"]) < .001]
    require(len(gray) == 3, "占比图例必须为3个")
    for d, pct in zip(sorted(gray, key=lambda d: d["rect"].width), [1, 5, 20]):
        require(abs(d["rect"].width - math.sqrt(pct * scale)) < .002, "图例与图中气泡比例不一致")
    png = pdf.with_suffix(".png")
    with Image.open(png) as im:
        require(abs(im.width - page.rect.width / 72 * 600) < 1.1, "PNG水平分辨率不符")
        require(abs(im.height - page.rect.height / 72 * 600) < 1.1, "PNG垂直分辨率不符")
        png_size = im.size
    report = dict(status="Verified", scope="independent raw-to-summary checks and exported vector geometry/font checks",
                  raw_duplicates_checked=duplicates, crop_patches_checked=len(feature_rows),
                  cells=len(saved), plotted_nonzero_cells=len(positive), zero_cells=len(saved)-len(positive),
                  area_share_sums={f"{site}/{crop}": math.fsum(v) for (site, crop), v in group_shares.items()},
                  actual_pdf_min_circle_gap_mm=min_gap / 72 * 25.4,
                  actual_pdf_min_cell_boundary_clearance_mm=min(cell_clearances) / 72 * 25.4,
                  plot_frame_cm=[7.6, 7.6], bubble_area_multiplier_vs_v2=2,
                  same_csv_bytes_as_v2=True, min_bubble_floor=None,
                  max_actual_diameter_error_pt=max(diam_errors),
                  all_pdf_text_pt=9, embedded_fonts=sorted(set(s["font"] for s in spans)),
                  pdf_raster_image_count=0, png_pixels=png_size, png_dpi=600,
                  visual_review="Not verified by this automated checker; recorded separately",
                  pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest())
    if args.report:
        out = summary_dir / "verification.json"
        require(not out.exists(), "不覆盖已有核查报告")
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
