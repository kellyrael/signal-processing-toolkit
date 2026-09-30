import numpy as np


def average_frequency(samples, sampling_period, threshold,
                      hysteresis=0.0, interpolate=True):
    """
    Find rising-edge crossings of `threshold` and return the average
    frequency over the span from the first edge to the last edge.

    Data before the first edge and after the last edge is excluded: the
    average is built only from the complete cycles bounded by edges.

    Parameters
    ----------
    samples : array_like
        1-D array of doubles (the time-domain signal).
    sampling_period : float
        Time between consecutive samples, in seconds.
    threshold : float
        Level a rising edge must cross.
    hysteresis : float, optional
        Signal must fall below (threshold - hysteresis) before another
        rising edge can fire. Suppresses retriggering on noise. Default 0.
    interpolate : bool, optional
        Linearly interpolate the sub-sample crossing time of each edge.
        Default True.

    Returns
    -------
    dict with: frequency (Hz), period (s), edge_times, edge_indices,
    cycles, periods, jitter (std of periods), span (trimmed index range).
    """
    x = np.asarray(samples, dtype=np.float64).ravel()

    if sampling_period <= 0:
        raise ValueError("sampling_period must be positive")
    if hysteresis < 0:
        raise ValueError("hysteresis must be non-negative")
    if x.size < 2:
        raise ValueError("samples must contain at least two elements")

    # --- locate rising edges ---------------------------------------------
    above = x >= threshold

    if hysteresis > 0.0:
        rearm = threshold - hysteresis
        edges, armed = [], not above[0]
        for i in range(1, x.size):
            if armed and above[i] and not above[i - 1]:
                edges.append(i)
                armed = False
            elif not armed and x[i] < rearm:
                armed = True
        edge_indices = np.asarray(edges, dtype=np.int64)
    else:
        edge_indices = np.flatnonzero(~above[:-1] & above[1:]) + 1

    if edge_indices.size < 2:
        raise ValueError(
            f"need at least 2 rising edges to measure a frequency, "
            f"found {edge_indices.size}"
        )

    # --- crossing times ---------------------------------------------------
    if interpolate:
        prev, curr = x[edge_indices - 1], x[edge_indices]
        denom = curr - prev
        frac = np.where(denom != 0.0, (threshold - prev) / denom, 0.0)
        edge_times = (edge_indices - 1 + frac) * sampling_period
    else:
        edge_times = edge_indices * sampling_period

    # --- trimmed average ---------------------------------------------------
    periods = np.diff(edge_times)          # only edge-to-edge intervals
    mean_period = periods.mean()

    return {
        "frequency": 1.0 / mean_period,
        "period": mean_period,
        "edge_times": edge_times,
        "edge_indices": edge_indices,
        "cycles": periods.size,
        "periods": periods,
        "jitter": periods.std(ddof=1) if periods.size > 1 else 0.0,
        "span": (int(edge_indices[0]), int(edge_indices[-1])),
    }