"""Read-only metric helpers retained from the directional-confusion analysis."""
from __future__ import annotations

import numpy as np
import pandas as pd

SITES = ("iw_2023", "iw2_2023", "ida_2023", "il_2023")
SITE_LABELS = dict(zip(SITES, "ABCD"))
MODELS = ("convgru", "unet3d", "utae")
CLASSES = ("corn", "other", "soybean")
BANDS = ("0<d<=1", "1<d<=2", "2<d<=3", "3<d<=4", "4<d<=5", "5<d<=6", "d>6")
CM_COLS = [f"cm_{i}_{j}" for i in range(3) for j in range(3)]
RUN = ["kind", "model", "source", "target", "fold"]


def five_stats(values: pd.Series | np.ndarray, prefix: str) -> dict[str, object]:
    a = np.asarray(values, dtype=float)
    good = np.isfinite(a)
    complete = len(a) == 5 and bool(good.all())
    return {
        f"{prefix}_mean": float(a.mean()) if complete else np.nan,
        f"{prefix}_std": float(a.std(ddof=1)) if complete else np.nan,
        f"{prefix}_min": float(a.min()) if complete else np.nan,
        f"{prefix}_max": float(a.max()) if complete else np.nan,
        f"{prefix}_n_valid": int(good.sum()),
        f"{prefix}_positive": int((good & (a > 0)).sum()),
        f"{prefix}_negative": int((good & (a < 0)).sum()),
        f"{prefix}_zero": int((good & (a == 0)).sum()),
        f"{prefix}_direction": (
            "not_calculable" if not complete else
            "all_positive" if (a > 0).all() else
            "all_negative" if (a < 0).all() else
            "all_zero" if (a == 0).all() else "mixed"
        ),
    }


def matrix(row: pd.Series) -> np.ndarray:
    return np.asarray([int(row[c]) for c in CM_COLS], dtype=np.int64).reshape(3, 3)


def f1_from_matrix(m: np.ndarray, cls: int) -> tuple[float, float, float, float, int, int, int]:
    tp = int(m[cls, cls])
    fn = int(m[cls, :].sum() - tp)
    fp = int(m[:, cls].sum() - tp)
    recall = tp / (tp + fn) if tp + fn else np.nan
    precision = tp / (tp + fp) if tp + fp else np.nan
    denominator = 2 * tp + fp + fn
    f1 = 2 * tp / denominator if denominator else np.nan
    return f1, precision, recall, float(1 - recall) if np.isfinite(recall) else np.nan, tp, fn, fp
