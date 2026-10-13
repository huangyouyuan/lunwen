"""F1 presentation only: raw fractions in, percentages/percentage points out.

Never round before multiplying by 100 or calculate differences from labels.
This module does not read or write scientific results.
"""
import math


def display_number(value):
    """Format an already scaled value; preserve NA and suppress rounded -0.00."""
    if value is None or math.isnan(float(value)):
        return 'NA'
    if not math.isfinite(float(value)):
        raise ValueError('Infinite F1 display value')
    text = f'{float(value):.2f}'
    return '0.00' if text == '-0.00' else text


def f1_number(raw_value):
    """Raw F1, its SD, or a signed F1 difference -> two-decimal display number.

    Callers label F1 and SD with %, and differences with percentage points.
    """
    return display_number(float(raw_value) * 100)


def f1_mean_sd(raw_mean, raw_sd):
    return f'{f1_number(raw_mean)} ± {f1_number(raw_sd)}'
