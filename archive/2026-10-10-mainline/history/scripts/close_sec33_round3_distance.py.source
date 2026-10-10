#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Close out round-three distance analysis from existing derived tables and CMs."""
from __future__ import annotations

import hashlib
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

import explore_sec33_round3_distance as base


ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "results/processed/sec33_round3_distance"
SUM = ROOT / "results/summary/sec33_round3_distance"
OUT_PROC = ROOT / "results/processed/sec33_round3_closeout"
OUT_SUM = ROOT / "results/summary/sec33_round3_closeout"
OUT_FIG = ROOT / "figures/exploratory/sec33_round3_closeout"
KEY = ["model", "source", "target", "fold", "population"]
GROUP = ["model", "source", "target", "population"]
NEAR, FAR = base.BANDS[0], base.BANDS[-1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unique(frame: pd.DataFrame, columns: list[str], name: str) -> None:
    require(not frame[columns].isna().any().any(), f"{name}: missing identity")
    require(not frame.duplicated(columns).any(), f"{name}: duplicate identity")


def direction(value: float) -> str:
    if not np.isfinite(value):
        return "not_calculable"
    return "gt6_higher" if value > 0 else "near_higher" if value < 0 else "equal"


def validate_cached_metrics(within: pd.DataFrame, cross: pd.DataFrame,
                            within_cm: pd.DataFrame, cross_cm: pd.DataFrame) -> list[dict]:
    """Independently reconstruct all reused band rates from integer CMs, in memory."""
    checks = []
    target_support = {}
    for name, cm_frame, metrics in (("within", within_cm, within), ("cross", cross_cm, cross)):
        keys = ["model", "target", "band"] if name == "within" else KEY[:-1] + ["band"]
        unique(cm_frame, keys, name + " CMs")
        unique(metrics, keys + ["population"], name + " metrics")
        if name == "within":
            expected = set(itertools.product(base.MODELS, base.SITES, base.BANDS))
        else:
            expected = {(m, s, t, k, b) for m in base.MODELS for s in base.SITES
                        for t in base.SITES if s != t for k in range(1, 6) for b in base.BANDS}
        require(set(cm_frame[keys].itertuples(index=False, name=None)) == expected,
                name + " CM identity coverage")
        expected_metrics = {(*key, p) for key in expected for p in base.POPULATIONS}
        require(set(metrics[keys + ["population"]].itertuples(index=False, name=None)) == expected_metrics,
                name + " metric identity coverage")
        indexed = metrics.set_index(keys + ["population"])
        errors = []
        for _, row in cm_frame.iterrows():
            cm = base.matrix(row)
            support_key = (row.target, row.band)
            support = cm.sum(axis=1)
            if support_key in target_support:
                require(np.array_equal(target_support[support_key], support),
                        f"same-target band reference support: {name}, {support_key}")
            else:
                target_support[support_key] = support
            for population in base.POPULATIONS:
                calculated = base.metrics(cm, population)
                key = tuple(row[k] for k in keys) + (population,)
                saved = indexed.loc[key]
                require(saved.pixels == calculated["pixels"] and saved.errors == calculated["errors"]
                        and saved.status == calculated["status"], f"metric counts/status mismatch: {key}")
                a, b = float(saved.error_rate), float(calculated["error_rate"])
                require((np.isnan(a) and np.isnan(b)) or abs(a - b) <= 1e-12,
                        f"matrix-derived rate mismatch: {key}")
                if np.isfinite(a):
                    errors.append(abs(a - b))
        checks.append({"check": name + " matrix identities, reference support and cached rates",
                       "status": "Verified", "records": len(metrics), "max_abs_error": max(errors, default=0)})
    return checks


def pair_deltas(within: pd.DataFrame, cross: pd.DataFrame,
                band_summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    wk = ["model", "target", "population", "band"]
    ck = KEY + ["band"]
    unique(within, wk, "within metrics")
    unique(cross, ck, "cross metrics")
    unique(band_summary, ["model", "source", "target", "population", "band"], "band summary")
    require(set(cross.fold.unique()) == {1, 2, 3, 4, 5}, "unexpected fold identifiers")
    joined = cross.merge(within[wk + ["pixels", "error_rate", "status"]], on=wk,
                         how="left", validate="many_to_one", indicator=True,
                         suffixes=("_cross", "_within"))
    require(joined._merge.eq("both").all() and len(joined) == len(cross), "missing within band")
    require(joined.pixels_cross.eq(joined.pixels_within).all(), "target support mismatch")
    require(joined.groupby(["model", "source", "target", "population", "band"]).fold.apply(
        lambda x: set(x) == {1, 2, 3, 4, 5}).all(), "incomplete five predictions")
    joined["delta_e"] = joined.error_rate_cross - joined.error_rate_within
    near = joined[joined.band.eq(NEAR)].rename(columns={
        "pixels_within": "near_pixels", "error_rate_within": "near_within_e",
        "error_rate_cross": "near_cross_e", "delta_e": "near_delta_e",
        "status_within": "near_within_status", "status_cross": "near_cross_status"})
    far = joined[joined.band.eq(FAR)].rename(columns={
        "pixels_within": "gt6_pixels", "error_rate_within": "gt6_within_e",
        "error_rate_cross": "gt6_cross_e", "delta_e": "gt6_delta_e",
        "status_within": "gt6_within_status", "status_cross": "gt6_cross_status"})
    cols = ["near_pixels", "near_within_e", "near_cross_e", "near_delta_e",
            "near_within_status", "near_cross_status"]
    fcols = ["gt6_pixels", "gt6_within_e", "gt6_cross_e", "gt6_delta_e",
             "gt6_within_status", "gt6_cross_status"]
    paired = near[KEY + cols].merge(far[KEY + fcols], on=KEY, how="outer",
                                     validate="one_to_one", indicator=True)
    require(paired._merge.eq("both").all() and len(paired) > 0, "incomplete band pairing")
    paired = paired.drop(columns="_merge")
    paired["d_gt6_minus_near"] = paired.gt6_delta_e - paired.near_delta_e
    paired["direction"] = paired.d_gt6_minus_near.map(direction)
    paired["status"] = np.where(paired.direction.eq("not_calculable"),
                                "not_calculable", "defined")
    paired = paired.sort_values(KEY).reset_index(drop=True)

    rows = []
    s = band_summary.set_index(["model", "source", "target", "population", "band"])
    for key, x in paired.groupby(GROUP, sort=True):
        x = x.sort_values("fold")
        require(x.fold.tolist() == [1, 2, 3, 4, 5], f"missing fold in {key}")
        vals = x.d_gt6_minus_near.to_numpy(dtype=float)
        valid = np.isfinite(vals)
        mean = float(vals.mean()) if valid.all() else np.nan
        near_mean = float(x.near_delta_e.mean()) if x.near_delta_e.notna().all() else np.nan
        far_mean = float(x.gt6_delta_e.mean()) if x.gt6_delta_e.notna().all() else np.nan
        for band, actual in ((NEAR, near_mean), (FAR, far_mean)):
            expected = s.loc[(*key, band), "delta_error_rate"]
            require((np.isnan(actual) and np.isnan(expected)) or
                    (np.isfinite(actual) and abs(actual - expected) <= 1e-12),
                    f"mean delta differs from original summary: {key}, {band}")
        require((np.isnan(mean) and (np.isnan(near_mean) or np.isnan(far_mean))) or
                (np.isfinite(mean) and abs(mean - (far_mean - near_mean)) <= 1e-12),
                f"paired mean closure failed: {key}")
        counts = x.direction.value_counts()
        n_far, n_near, n_equal, n_na = [int(counts.get(label, 0)) for label in
                                         ("gt6_higher", "near_higher", "equal", "not_calculable")]
        all_direction = ("not_calculable" if n_na else "all_gt6_higher" if n_far == 5 else
                         "all_near_higher" if n_near == 5 else "all_equal" if n_equal == 5 else "mixed")
        rows.append(dict(zip(GROUP, key)) | {
            "near_delta_e_mean": near_mean, "gt6_delta_e_mean": far_mean,
            "d_mean": mean, "d_std": float(vals.std(ddof=1)) if valid.all() else np.nan,
            "d_min": float(vals.min()) if valid.all() else np.nan,
            "d_max": float(vals.max()) if valid.all() else np.nan,
            "n_predictions": len(x), "n_defined": int(valid.sum()),
            "n_gt6_higher": n_far, "n_near_higher": n_near,
            "n_equal": n_equal, "n_not_calculable": n_na,
            "mean_direction": direction(mean), "five_direction": all_direction,
            "status": "defined" if valid.all() else "undefined_one_or_more_predictions"})
    summary = pd.DataFrame(rows).sort_values(GROUP).reset_index(drop=True)
    return paired, summary


def soybean_components(wc: np.ndarray, cm: np.ndarray) -> dict[str, object]:
    n, wn = int(cm[2].sum()), int(wc[2].sum())
    require(n == wn, "D soybean support mismatch")
    result = {"soybean_pixels": n, "within_to_corn_errors": int(wc[2, 0]),
              "cross_to_corn_errors": int(cm[2, 0]),
              "within_to_other_errors": int(wc[2, 1]),
              "cross_to_other_errors": int(cm[2, 1])}
    for label, index in (("corn", 0), ("other", 1)):
        wr = float(wc[2, index] / n) if n else np.nan
        cr = float(cm[2, index] / n) if n else np.nan
        result.update({f"within_to_{label}_rate": wr, f"cross_to_{label}_rate": cr,
                       f"delta_to_{label}_rate": cr - wr})
    result["component_sum"] = result["delta_to_corn_rate"] + result["delta_to_other_rate"]
    result["status"] = "defined" if n else "undefined_zero_support"
    return result


def soybean_folds(within_cm: pd.DataFrame, cross_cm: pd.DataFrame,
                  paired: pd.DataFrame, summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    wk = ["model", "target", "band"]
    ck = ["model", "source", "target", "fold", "band"]
    unique(within_cm, wk, "within CMs")
    unique(cross_cm, ck, "cross CMs")
    target = "il_2023"
    w = within_cm[within_cm.target.eq(target) & within_cm.band.eq(FAR)].set_index(wk)
    c = cross_cm[cross_cm.target.eq(target) & cross_cm.band.eq(FAR)]
    p = paired[paired.target.eq(target) & paired.population.eq("soybean")].set_index(KEY)
    rows = []
    for row in c.itertuples(index=False):
        key = (row.model, row.source, row.target, int(row.fold), "soybean")
        require(key in p.index, f"missing paired record: {key}")
        cm = np.asarray([getattr(row, col) for col in base.CM], dtype=np.int64).reshape(3, 3)
        wc = base.matrix(w.loc[(row.model, row.target, FAR)])
        components = soybean_components(wc, cm)
        delta = float(p.loc[key, "gt6_delta_e"])
        total = components["component_sum"]
        require((np.isnan(total) and np.isnan(delta)) or abs(total - delta) <= 1e-12,
                f"D soybean component closure: {key}")
        rows.append(dict(zip(KEY, key)) | {"band": FAR, **components,
            "gt6_delta_e": delta, "component_closure_error": total - delta,
            "d_gt6_minus_near": float(p.loc[key, "d_gt6_minus_near"]),
            "direction": p.loc[key, "direction"]})
    folds = pd.DataFrame(rows).sort_values(KEY).reset_index(drop=True)
    require(len(folds) == 45, "D soybean needs 3 models x 3 sources x 5 folds")
    ps = paired[paired.target.eq(target) & paired.population.eq("soybean")]
    ss = summary[summary.target.eq(target) & summary.population.eq("soybean")]
    compact = []
    for key, x in folds.groupby(["model", "source", "target", "population"], sort=True):
        x = x.sort_values("fold")
        require(x.fold.tolist() == [1, 2, 3, 4, 5], f"D soybean fold coverage: {key}")
        q = ps[(ps.model == key[0]) & (ps.source == key[1])].sort_values("fold")
        s = ss[(ss.model == key[0]) & (ss.source == key[1])].iloc[0]
        vals = x.gt6_delta_e.to_numpy(dtype=float)
        compact.append(dict(zip(GROUP, key)) | {
            "near_delta_e_mean": float(s.near_delta_e_mean),
            "gt6_delta_e_mean": float(s.gt6_delta_e_mean),
            "gt6_delta_e_std": float(vals.std(ddof=1)),
            "gt6_delta_e_min": float(vals.min()),
            "gt6_delta_e_max": float(vals.max()),
            **{f"gt6_delta_e_fold_{i}": float(v) for i, v in zip(range(1, 6), vals)},
            **{f"delta_to_corn_fold_{int(r.fold)}": float(r.delta_to_corn_rate) for r in x.itertuples()},
            **{f"delta_to_other_fold_{int(r.fold)}": float(r.delta_to_other_rate) for r in x.itertuples()},
            **{f"d_fold_{int(r.fold)}": float(r.d_gt6_minus_near) for r in x.itertuples()},
            **{f"d_direction_fold_{int(r.fold)}": r.direction for r in x.itertuples()},
            "d_mean": float(s.d_mean), "n_gt6_higher": int(s.n_gt6_higher),
            "n_near_higher": int(s.n_near_higher), "n_equal": int(s.n_equal),
            "n_not_calculable": int(s.n_not_calculable),
            "mean_direction": s.mean_direction,
            "five_direction": s.five_direction,
            "delta_to_corn_mean": base.mean_or_nan(x.delta_to_corn_rate.to_numpy(dtype=float)),
            "delta_to_other_mean": base.mean_or_nan(x.delta_to_other_rate.to_numpy(dtype=float)),
            "n_gt6_positive": int((vals > 0).sum()), "n_gt6_negative": int((vals < 0).sum()),
            "n_gt6_zero": int((vals == 0).sum()), "n_gt6_defined": int(np.isfinite(vals).sum()),
            "n_predictions": 5, "status": s.status})
        require(np.allclose(q.gt6_delta_e.to_numpy(dtype=float), vals, rtol=0, atol=1e-12, equal_nan=True),
                f"D fold identity mismatch: {key}")
    return folds, pd.DataFrame(compact)


def validate_overview(overview: pd.DataFrame, source_summary: pd.DataFrame) -> None:
    keys = ["model", "target", "population", "band"]
    unique(overview, keys, "overview")
    unique(source_summary, keys + ["source"], "source summary")
    expected = set(itertools.product(base.MODELS, base.SITES, base.POPULATIONS, base.BANDS))
    require(set(overview[keys].itertuples(index=False, name=None)) == expected,
            "overview identity coverage")
    for key, r in source_summary.groupby(keys):
        require(set(r.source) == set(base.SITES) - {key[1]} and len(r) == 3,
                f"three source identity: {key}")
    calculated = source_summary.groupby(keys).delta_error_rate.agg(
        lambda v: float(np.mean(v.to_numpy(dtype=float))))
    actual = overview.set_index(keys).delta_error_rate_three_source_mean
    require(set(calculated.index) == set(actual.index), "overview keys mismatch")
    require(np.allclose(calculated.to_numpy(), actual.loc[calculated.index].to_numpy(),
                        rtol=0, atol=1e-12, equal_nan=True), "overview mean mismatch")


def plot_delta(overview: pd.DataFrame, source_summary: pd.DataFrame) -> Path:
    import matplotlib.pyplot as plt
    from matplotlib import font_manager, ticker
    from matplotlib.lines import Line2D

    fonts = {f.name for f in font_manager.fontManager.ttflist}
    chinese_font = next((f for f in ("Microsoft YaHei", "SimHei", "SimSun", "Noto Sans CJK SC")
                         if f in fonts), None)
    require(chinese_font is not None, "a Chinese font is required for the overview")
    plt.rcParams.update({"font.family": [chinese_font, "DejaVu Sans"],
                         "axes.unicode_minus": False})
    validate_overview(overview, source_summary)
    x = np.asarray([1, 2, 3, 4, 5, 6, 7.6])
    labels = ["(0,1]", "(1,2]", "(2,3]", "(3,4]", "(4,5]", "(5,6]", ">6"]
    colors = {"convgru": "#2869A0", "unet3d": "#D05A35", "utae": "#16856D"}
    order = ["convgru", "unet3d", "utae"]
    crops = {"corn": "玉米", "soybean": "大豆"}
    unique(overview, ["model", "target", "population", "band"], "overview")
    fig, axes = plt.subplots(4, 2, figsize=(12.5, 13.2), sharex=True, sharey=True)
    compared = 0
    for ri, target in enumerate(base.SITES):
        for ci, population in enumerate(("corn", "soybean")):
            ax = axes[ri, ci]
            ax.axhline(0, color="#666666", lw=0.9, zorder=0)
            ax.axvline(6.8, color="#B3B3B3", lw=0.8, linestyle=":")
            for model in order:
                q = overview[(overview.target == target) &
                             (overview.population == population) &
                             (overview.model == model)].set_index("band").reindex(base.BANDS)
                require(len(q) == 7 and q.delta_error_rate_three_source_mean.notna().all(),
                        f"incomplete overview curve: {target}, {population}, {model}")
                values = q.delta_error_rate_three_source_mean.to_numpy(dtype=float)
                src = source_summary[(source_summary.target == target) &
                                     (source_summary.population == population) &
                                     (source_summary.model == model)]
                for band, value in zip(base.BANDS, values):
                    r = src[src.band == band]
                    require(len(r) == 3 and abs(value - r.delta_error_rate.mean()) <= 1e-12,
                            f"plot does not match three-source mean: {target}, {population}, {model}, {band}")
                    compared += 1
                ax.plot(x[:6], values[:6], marker="o", markersize=3.5,
                        lw=1.5, color=colors[model])
                ax.plot(x[-1], values[-1], marker="o", markersize=5,
                        color=colors[model], linestyle="None")
            ax.set_title(f"{base.SITE_LABELS[target]}站 · {crops[population]}", fontsize=10)
            ax.grid(axis="y", alpha=0.22)
            ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))
            ax.set_xlim(0.7, 8.0)
            if ci == 0:
                ax.set_ylabel("漏分率差 Δe（原尺度）")
            if ri == 3:
                ax.set_xticks(x, labels)
                ax.tick_params(axis="x", labelrotation=25)
                ax.set_xlabel("距类别边界的距离带（像元）\n>6为开放区间，与前六带断开")
    require(compared == 168, "plot requires 4 sites x 2 crops x 3 models x 7 bands")
    handles = [Line2D([0], [0], color=colors[m], marker="o", lw=1.5,
                      label=base.MODEL_LABELS[m]) for m in order]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 0.956))
    fig.suptitle("跨站相对本站的额外漏分率随边界距离变化", fontsize=14, y=0.995)
    fig.text(0.5, 0.938, "每点为三个来源的等权均值；前六带连接仅表示组间变化",
             ha="center", fontsize=9)
    fig.subplots_adjust(top=0.90, bottom=0.07, left=0.10, right=0.97,
                        hspace=0.35, wspace=0.24)
    OUT_FIG.mkdir(parents=True, exist_ok=True)
    path = OUT_FIG / "delta_e_distance_overview.png"
    fig.savefig(path, dpi=210, bbox_inches="tight")
    plt.close(fig)
    return path


def record(path: Path) -> dict[str, object]:
    return {"path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size}


def main() -> None:
    inputs = [PROC / "band_metrics_within.csv", PROC / "band_metrics_cross_fold.csv",
              SUM / "band_metrics_summary.csv", SUM / "three_source_overview.csv",
              PROC / "boundary_within_cm_reused.csv", PROC / "boundary_cross_fold_cm_reused.csv"]
    within, cross, source_summary, overview, within_cm, cross_cm = map(base.read_csv, inputs)
    within_cm = base.cm_frame(within_cm, "within CMs")
    cross_cm = base.cm_frame(cross_cm, "cross CMs")
    checks = validate_cached_metrics(within, cross, within_cm, cross_cm)
    paired, summary = pair_deltas(within, cross, source_summary)
    require(len(paired) == 720 and len(summary) == 144, "paired coverage")
    folds, compact = soybean_folds(within_cm, cross_cm, paired, summary)
    require((summary[summary.population.isin(("corn", "soybean"))].shape[0]) == 72,
            "crop comparisons need 72 combinations")
    checks.extend([
        {"check": "explicit-key endpoint pairing and five-prediction coverage", "status": "Verified",
         "records": len(paired)},
        {"check": "mean D equals mean gt6 delta minus mean near delta", "status": "Verified",
         "records": len(summary),
         "max_abs_error": float((summary.d_mean - (summary.gt6_delta_e_mean - summary.near_delta_e_mean)).abs().max())},
        {"check": "D soybean per-prediction component closure", "status": "Verified",
         "records": len(folds), "max_abs_error": float(folds.component_closure_error.abs().max())},
        {"check": "NA not treated as equal; negative near and gt6 deltas retained", "status": "Verified",
         "records": len(paired), "detail": json.dumps({
             "n_undefined_D": int(paired.status.ne("defined").sum()),
             "n_negative_near_delta": int((paired.near_delta_e < 0).sum()),
             "n_negative_gt6_delta": int((paired.gt6_delta_e < 0).sum())})},
    ])
    # Plot validates all overview values against exactly three distinct source means.
    fig = plot_delta(overview, source_summary)
    checks.append({"check": "plotted crop values equal three-source means", "status": "Verified", "records": 168})
    outputs = {OUT_PROC / "nearest_vs_gt6_delta_e_per_fold.csv": paired,
               OUT_PROC / "d_soybean_gt6_delta_e_components_per_fold.csv": folds,
               OUT_SUM / "nearest_vs_gt6_delta_e_summary.csv": summary,
               OUT_SUM / "d_soybean_five_prediction_diagnostic.csv": compact,
               OUT_SUM / "checks.csv": pd.DataFrame(checks)}
    for path, frame in outputs.items():
        base.write_csv(path, frame)
    manifest = {"data_status": "derived", "analysis_status": "exploratory",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "spatial_metric_status": "Partially verified",
                "distance_arrays_rerun": False,
                "pair_rule": "D_k=(cross_gt6_k-within_gt6)-(cross_near_k-within_near)",
                "source_overview": "equal weight of three source means, not fifteen repetitions",
                "inputs": [record(p) for p in inputs],
                "script": record(Path(__file__)),
                "dependencies": [record(Path(base.__file__))],
                "outputs": [record(p) for p in [*outputs, fig]]}
    OUT_SUM.mkdir(parents=True, exist_ok=True)
    (OUT_SUM / "run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    crops = summary[summary.population.isin(("corn", "soybean"))]
    print("crop five-direction:", crops.five_direction.value_counts().to_dict())
    print("crop mean-direction:", crops.mean_direction.value_counts().to_dict())
    print("D soybean:")
    print(compact[["model", "source", "near_delta_e_mean", "gt6_delta_e_mean",
                   "gt6_delta_e_min", "gt6_delta_e_max", "gt6_delta_e_std",
                   "n_gt6_higher", "n_near_higher"]].to_string(index=False))


if __name__ == "__main__":
    main()
