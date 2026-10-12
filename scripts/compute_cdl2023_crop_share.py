#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1.1研究区概况：2023年CDL中玉米与大豆占各站农作物面积的比例。

输入为仓库外的原始数据，只读：
- 四站2023年CDL原始类别裁剪栅格 D:\\标签\\2023<代码>cdl.tif；
- 正式三类标签 G:\\2560图像\\标签GeoTIFF\\<代码>.tif（1=玉米、2=其它地类、3=大豆）。

脚本先核对两者行列数、地理变换和投影一致，原始CDL按“1→玉米、5→大豆、其余→其它地类”
重分类后与正式标签逐像元相同，且正式标签与图1源栅格的SHA-256一致；再统计CDL类别代码
像元数。农作物取CDL作物类别代码1–61、66–77、204–254（含牧草、休耕地和双季作物），
这是CDL中最宽的作物口径，分母最大、比例最低。分子只计代码1（玉米）和5（大豆），与正式
标签一致；甜玉米、爆裂玉米和含玉米或大豆的双季作物只进入分母。

用法（需含GDAL的环境，例如conda环境tnt）：
    python -B scripts/compute_cdl2023_crop_share.py          # 计算并与已有输出逐字核对
    python -B scripts/compute_cdl2023_crop_share.py --write  # 写出；已有文件内容不同则报错，不覆盖
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from osgeo import gdal, osr

gdal.UseExceptions()

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = Path(r"D:\标签")
LABEL_DIR = Path(r"G:\2560图像\标签GeoTIFF")
FIGURE_VERIFICATION = ROOT / "legacy" / "figures" / "four_site_classification" / "verification.json"
PROCESSED = ROOT / "results" / "processed" / "sec11_cdl2023_crop_share" / "cdl2023_code_counts.csv"
SUMMARY = ROOT / "results" / "summary" / "sec11_cdl2023_crop_share" / "crop_share_2023.csv"

SITES = (("A", "iw"), ("B", "iw2"), ("C", "ida"), ("D", "il"))
SHAPE = (2560, 2560)
CORN, SOYBEAN = 1, 5
CROP_CODES = frozenset(range(1, 62)) | frozenset(range(66, 78)) | frozenset(range(204, 255))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_raster(path: Path):
    dataset = gdal.Open(str(path), gdal.GA_ReadOnly)
    if dataset is None or dataset.RasterCount != 1:
        raise RuntimeError(f"无法读取单波段栅格: {path}")
    array = dataset.GetRasterBand(1).ReadAsArray()
    geotransform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()
    dataset = None
    return array, geotransform, projection


def same_projection(left_wkt: str, right_wkt: str) -> bool:
    left, right = osr.SpatialReference(), osr.SpatialReference()
    if left.ImportFromWkt(left_wkt) != 0 or right.ImportFromWkt(right_wkt) != 0:
        return False
    return bool(left.IsSame(right))


def compute():
    figure_sources = json.loads(FIGURE_VERIFICATION.read_text(encoding="utf-8"))["sites"]
    figure_sha = {item["site"]: item["raster_sha256"] for item in figure_sources}
    code_rows, summary_rows = [], []
    for site, code in SITES:
        raw_path = RAW_DIR / f"2023{code}cdl.tif"
        label_path = LABEL_DIR / f"{code}.tif"
        raw, raw_gt, raw_wkt = read_raster(raw_path)
        label, label_gt, label_wkt = read_raster(label_path)
        if raw.shape != SHAPE or label.shape != SHAPE:
            raise ValueError(f"{site}站栅格尺寸不是2560×2560: {raw.shape}, {label.shape}")
        if not np.allclose(raw_gt, label_gt, rtol=0.0, atol=1e-6):
            raise ValueError(f"{site}站原始CDL与正式标签地理变换不同")
        if not same_projection(raw_wkt, label_wkt):
            raise ValueError(f"{site}站原始CDL与正式标签投影不同")
        reclassified = np.full(SHAPE, 2, dtype=np.int16)
        reclassified[raw == CORN] = 1
        reclassified[raw == SOYBEAN] = 3
        mismatch = int(np.count_nonzero(reclassified != label))
        if mismatch:
            raise ValueError(f"{site}站原始CDL重分类后与正式标签有{mismatch}个像元不同")
        label_sha = sha256(label_path)
        if label_sha != figure_sha[site]:
            raise ValueError(f"{site}站正式标签与图1源栅格SHA-256不一致")

        counts = np.bincount(raw.ravel().astype(np.int64), minlength=256)
        present = [int(value) for value in np.flatnonzero(counts)]
        for value in present:
            code_rows.append({
                "site": site,
                "dataset_id": f"{code}_2023",
                "cdl_code": value,
                "pixels": int(counts[value]),
                "crop": "true" if value in CROP_CODES else "false",
            })
        total = int(counts.sum())
        corn, soybean = int(counts[CORN]), int(counts[SOYBEAN])
        crop = int(sum(int(counts[value]) for value in present if value in CROP_CODES))
        other_crops = sorted(
            ((int(counts[value]), value) for value in present
             if value in CROP_CODES and value not in (CORN, SOYBEAN)),
            reverse=True,
        )
        top_pixels, top_code = other_crops[0] if other_crops else (0, "")
        summary_rows.append({
            "site": site,
            "dataset_id": f"{code}_2023",
            "raw_cdl": str(raw_path),
            "raw_cdl_sha256": sha256(raw_path),
            "label_tif": str(label_path),
            "label_sha256": label_sha,
            "label_pixel_match": "true",
            "total_pixels": total,
            "corn_pixels": corn,
            "soybean_pixels": soybean,
            "crop_pixels": crop,
            "corn_soybean_share_of_crop": f"{(corn + soybean) / crop:.6f}",
            "crop_share_of_site": f"{crop / total:.6f}",
            "corn_soybean_share_of_site": f"{(corn + soybean) / total:.6f}",
            "largest_other_crop_code": top_code,
            "largest_other_crop_pixels": top_pixels,
        })
    return code_rows, summary_rows


def to_csv(rows) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def emit(path: Path, text: str, write: bool) -> str:
    if path.exists():
        if path.read_text(encoding="utf-8") == text:
            return "与已有文件逐字一致"
        raise SystemExit(f"{path} 已存在且内容不同；不覆盖，请人工核查")
    if not write:
        return "未写出（加 --write 写出）"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    return "已写出"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    code_rows, summary_rows = compute()
    for row in summary_rows:
        print(
            f"{row['site']}站：玉米+大豆占农作物 {float(row['corn_soybean_share_of_crop']):.2%}，"
            f"农作物占全站 {float(row['crop_share_of_site']):.2%}，"
            f"玉米+大豆占全站 {float(row['corn_soybean_share_of_site']):.2%}，"
            f"其余作物中最大为代码{row['largest_other_crop_code']}（{row['largest_other_crop_pixels']}像元）"
        )
    print("processed:", emit(PROCESSED, to_csv(code_rows), args.write))
    print("summary:", emit(SUMMARY, to_csv(summary_rows), args.write))


if __name__ == "__main__":
    main()
