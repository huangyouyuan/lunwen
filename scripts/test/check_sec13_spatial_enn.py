"""Independently audit the eight table rows and manuscript comparisons; no build."""

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

from PIL import ImageFont


ROOT = Path(__file__).resolve().parents[2]


def read(relative):
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def sha(relative):
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, help="write a new JSON report; never overwrite")
    args = parser.parse_args()
    result = subprocess.run(
        [sys.executable, "-B", str(ROOT / "scripts/generate_sec13_spatial_tables.py"), "--check"],
        capture_output=True, check=True, cwd=ROOT,
    )
    report = json.loads(result.stdout)
    features_path = "results/processed/sec33_reference_patch_types/reference_patch_features.csv"
    groups = defaultdict(list)
    for row in read(features_path):
        if row["crop"] in ("corn", "soybean"):
            groups[(row["site"], row["crop"])].append(row)
    assert len(groups) == 8
    stats = {(row["site"], row["crop"]): row for row in report["extremes"]}
    for key, records in groups.items():
        summary = stats[key]
        pixels = sum(int(row["reference_pixels"]) for row in records)
        assert pixels == summary["reference_pixels"] and len(records) == summary["n_patches"]
        assert sum(int(row["reference_pixels"]) == 1 for row in records) == summary["singleton_count"]
        for metric in ("AREA", "SHAPE", "ENN"):
            # Aggregate tied values first, independently of the producer's row sort.
            frequencies = Counter()
            for row in records:
                frequencies[float(row[metric])] += int(row["reference_pixels"])
            cumulative = 0
            for value in sorted(frequencies):
                cumulative += frequencies[value]
                if 2 * cumulative >= pixels:
                    median = value
                    break
            assert [min(frequencies), median, max(frequencies)] == summary[metric], (key, metric)

    raw_dir = Path("results/raw/sec33_reference_patch_types")
    manifest = json.loads((ROOT / raw_dir / "conversion_manifest.json").read_text(encoding="utf-8"))
    input_hashes = {}
    for filename in {row["input_file"] for records in groups.values() for row in records}:
        path = raw_dir / (Path(filename).stem + "_patch.csv")
        entry = next(row for row in manifest["tables"] if row["output"] == path.as_posix())
        assert sha(path) == entry["output_sha256"]
        input_hashes[path.as_posix()] = sha(path)
        # LID disambiguates the A and duplicate D records in 2023iw_patch.csv.
        raw = {(row["LID"], row["PID"]): row for row in read(path)}
        for row in (row for records in groups.values() for row in records if row["input_file"] == filename):
            original = raw[(row["LID"], row["PID"])]
            assert row["TYPE"] == original["TYPE"]
            assert all(float(row[metric]) == float(original[metric]) for metric in ("AREA", "SHAPE", "ENN"))

    table_path = Path("tables/sec13_spatial_metrics_enn_rows.tex")
    lines = [line for line in (ROOT / table_path).read_text(encoding="utf-8").splitlines() if " & " in line]
    assert len(lines) == 8
    table_cells = []
    for index, (line, summary) in enumerate(zip(lines, report["extremes"])):
        cells = [cell.strip() for cell in line.removesuffix(r"\\").split("&")]
        table_cells.append(cells)
        assert len(cells) == 9
        if index % 2 == 0:
            assert cells[0] == rf"\multirow{{2}}{{*}}{{{summary['site']}}}"
            assert cells[8] == rf"\multirow{{2}}{{*}}{{{summary['ED']:.2f}}}"
        else:
            assert not cells[0] and not cells[8]
        assert cells[1] == {"corn": "玉米", "soybean": "大豆"}[summary["crop"]]
        for column, metric in enumerate(("AREA", "SHAPE", "ENN"), start=2):
            low, median, high = summary[metric]
            assert cells[column] == f"{median:.2f}（{low:.2f}～{high:.2f}）"
        assert cells[5] == str(summary["n_patches"])
        assert cells[6] == f"{summary['PD']:.2f}" and cells[7] == f"{summary['AI']:.2f}"

    ranges = {}
    for field, expected in (
        ("singleton_patch_share", ["44.31", "54.64"]),
        ("singleton_area_share", ["0.23", "0.71"]),
        ("AI", ["91.22", "93.92"]),
    ):
        values = [row[field] * (100 if "share" in field else 1) for row in stats.values()]
        ranges[field] = [min(values), max(values)]
        assert [f"{value:.2f}" for value in ranges[field]] == expected
    spans = {}
    for crop in ("corn", "soybean"):
        values = {site: stats[(site, crop)]["AREA"][1] for site in "ABCD"}
        ranges[crop + "_area"] = [min(values.values()), max(values.values())]
        spans[crop] = max(values.values()) - min(values.values())
        assert min(values, key=values.get) != "C"
        for metric, extremum in (("SHAPE", max), ("PD", max), ("AI", min)):
            values = {
                site: stats[(site, crop)][metric][1] if metric == "SHAPE" else stats[(site, crop)][metric]
                for site in "ABCD"
            }
            assert extremum(values, key=values.get) == "C"
    assert ranges["corn_area"] == [116.91, 130.95]
    assert ranges["soybean_area"] == [63.27, 114.39]
    assert spans["soybean"] > spans["corn"]
    gaps = {site: abs(stats[(site, "corn")]["AREA"][1] - stats[(site, "soybean")]["AREA"][1]) for site in "ABCD"}
    assert max(gaps, key=gaps.get) == "B" and min(gaps, key=gaps.get) == "D"
    assert all(row["ENN"][1] == 60.0 for row in stats.values())
    assert max(stats.values(), key=lambda row: row["ED"])["site"] == "C"

    body = (ROOT / "sections/02_data.tex").read_text(encoding="utf-8")
    old = subprocess.check_output(["git", "show", "HEAD:sections/02_data.tex"], cwd=ROOT).decode("utf-8")
    marker = r"\subsubsection{景观格局}"
    assert body.split(marker)[0] == old.split(marker)[0]
    part = body.split(marker)[1]
    assert len(part.split(r"\clearpage")[0].strip().split("\n\n")) == 3
    assert part.count(r"\captionof{table}") == part.count(r"\label{tab:sec13_spatial_metrics}") == 1
    assert table_path.as_posix() in part
    assert re.search(r"mcgarigal2023fragstats\s*,", (ROOT / "bibliography/references.bib").read_text(encoding="utf-8"))
    for environment in ("strip", "minipage", "tabular"):
        assert part.count(r"\begin{" + environment + "}") == part.count(r"\end{" + environment + "}") == 1
    depth = 0
    for character in part:
        depth += (character == "{") - (character == "}")
        assert depth >= 0
    assert depth == 0

    # Font metrics are a width estimate, explicitly not a LaTeX rendering check.
    latin = ImageFont.truetype("C:/Windows/Fonts/times.ttf", 1050)
    cjk = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 1050)
    def width(text):
        # The table uses xeCJK's half-width punctuation spacing, with unchanged glyphs.
        return sum(525 if char in "（）" else (latin if ord(char) < 128 else cjk).getlength(char)
                   for char in text) / 100
    headings = ["站点", "作物", "AREA/ha", "SHAPE", "ENN/m", "斑块数", "(个/100 ha)", "AI/%", "景观级"]
    widths = [width(heading) for heading in headings]
    for cells in table_cells:
        for column, text in enumerate(cells):
            text = re.sub(r"\\multirow\{2\}\{\*\}\{([^{}]+)\}", r"\1", text)
            widths[column] = max(widths[column], width(text))
    estimated_bp = sum(widths) + 16 * 1.5 * 72 / 72.27
    available_bp = 17.4 / 2.54 * 72
    assert estimated_bp < available_bp

    input_paths = [
        features_path,
        "results/summary/sec33_indicator_grading_preparation/indicator_distribution_reading.csv",
        "results/summary/sec33_reference_patch_types/background_class.csv",
        "results/summary/sec33_reference_patch_types/background_landscape.csv",
    ] + ["results/summary/sec13_sec31_foundations/" + name for name in (
        "reference_composition.csv", "crop_patch_distribution_reading.csv", "crop_patch_support_and_limitations.csv",
        "class_background_full_scope.csv", "landscape_background_full_scope.csv",
    )]
    input_hashes.update({path: sha(path) for path in input_paths})
    report.update({
        "data_status": "derived_from_existing_verified_data",
        "independent_frequency_median_audit": "Verified", "raw_csv_metric_audit": "Verified",
        "raw_crop_records_compared": sum(len(records) for records in groups.values()),
        "narrative_comparisons_unrounded": "Verified", "ranges": ranges, "area_crop_gaps": gaps,
        "latex_source_structure": "Verified", "sections_before_132_unchanged": "Verified",
        "width_estimate_bp": estimated_bp, "available_width_bp": available_bp,
        "layout_status": "Not verified", "compiled_this_task": False,
        "inputs_sha256": input_hashes,
        "outputs_sha256": {path: sha(path) for path in (
            "sections/02_data.tex", "scripts/generate_sec13_spatial_tables.py", table_path.as_posix(),
        )},
    })
    if args.report:
        with args.report.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
    print(json.dumps({key: report[key] for key in (
        "status", "patches", "raw_crop_records_compared", "ranges", "area_crop_gaps",
        "width_estimate_bp", "available_width_bp", "layout_status",
    )}))


if __name__ == "__main__":
    main()
