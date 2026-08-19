#!/usr/bin/env python3
"""Core numerical ideas used in the ammonia-discrepancy analysis.

This compact public module illustrates the guarded NDI calculation and the
weighted statistics used by the monthly and stratified summaries. It is not a
replacement for provider-specific preprocessing of the raw input products.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray


def normalised_discrepancy(
    top_down: ArrayLike,
    bottom_up: ArrayLike,
    *,
    minimum_combined_flux: float = 0.0,
) -> NDArray[np.float64]:
    """Calculate NDI = (TD - BU) / (TD + BU) with validity guards.

    Parameters
    ----------
    top_down, bottom_up
        Matched satellite-constrained (TD) and inventory-derived (BU) values.
        Inputs must be non-negative and broadcast to a common shape.
    minimum_combined_flux
        Values are masked unless ``TD + BU`` is strictly greater than this
        configurable near-zero threshold. It must use the same units as the
        inputs.

    Returns
    -------
    numpy.ndarray
        Float array with invalid cells represented by ``NaN``.
    """

    if minimum_combined_flux < 0:
        raise ValueError("minimum_combined_flux must be non-negative")

    td, bu = np.broadcast_arrays(
        np.asarray(top_down, dtype=np.float64),
        np.asarray(bottom_up, dtype=np.float64),
    )
    total = td + bu
    valid = (
        np.isfinite(td)
        & np.isfinite(bu)
        & (td >= 0.0)
        & (bu >= 0.0)
        & (total > minimum_combined_flux)
    )

    ndi = np.full(td.shape, np.nan, dtype=np.float64)
    np.divide(td - bu, total, out=ndi, where=valid)
    return ndi


def _valid_weighted_values(
    values: ArrayLike, weights: ArrayLike
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    values_array, weights_array = np.broadcast_arrays(
        np.asarray(values, dtype=np.float64),
        np.asarray(weights, dtype=np.float64),
    )
    valid = (
        np.isfinite(values_array)
        & np.isfinite(weights_array)
        & (weights_array > 0.0)
    )
    return values_array[valid], weights_array[valid]


def weighted_mean(values: ArrayLike, weights: ArrayLike) -> float:
    """Return the positive-weight mean, or ``NaN`` when no values remain."""

    valid_values, valid_weights = _valid_weighted_values(values, weights)
    if valid_values.size == 0:
        return float("nan")
    return float(np.average(valid_values, weights=valid_weights))


def weighted_population_sd(values: ArrayLike, weights: ArrayLike) -> float:
    """Return the positive-weight population standard deviation."""

    valid_values, valid_weights = _valid_weighted_values(values, weights)
    if valid_values.size == 0:
        return float("nan")
    mean = np.average(valid_values, weights=valid_weights)
    variance = np.average((valid_values - mean) ** 2, weights=valid_weights)
    return float(np.sqrt(max(float(variance), 0.0)))


def effective_sample_size(weights: ArrayLike) -> float:
    """Return Kish effective sample size for finite positive weights."""

    weights_array = np.asarray(weights, dtype=np.float64)
    valid_weights = weights_array[
        np.isfinite(weights_array) & (weights_array > 0.0)
    ]
    if valid_weights.size == 0:
        return 0.0
    denominator = np.sum(valid_weights**2)
    if denominator <= 0.0:
        return 0.0
    return float(np.sum(valid_weights) ** 2 / denominator)


def weighted_quantile(
    values: ArrayLike,
    weights: ArrayLike,
    quantiles: float | Sequence[float],
) -> float | NDArray[np.float64]:
    """Calculate midpoint-CDF weighted quantiles by linear interpolation."""

    scalar_requested = np.isscalar(quantiles)
    requested = np.atleast_1d(np.asarray(quantiles, dtype=np.float64))
    if np.any(~np.isfinite(requested)) or np.any((requested < 0) | (requested > 1)):
        raise ValueError("quantiles must be finite and lie between 0 and 1")

    valid_values, valid_weights = _valid_weighted_values(values, weights)
    if valid_values.size == 0:
        result = np.full(requested.shape, np.nan, dtype=np.float64)
    else:
        order = np.argsort(valid_values)
        sorted_values = valid_values[order]
        sorted_weights = valid_weights[order]
        cumulative = np.cumsum(sorted_weights) - 0.5 * sorted_weights
        cumulative /= np.sum(sorted_weights)
        result = np.interp(
            requested,
            cumulative,
            sorted_values,
            left=sorted_values[0],
            right=sorted_values[-1],
        )

    return float(result[0]) if scalar_requested else result


def weighted_box_statistics(
    values: ArrayLike, weights: ArrayLike
) -> dict[str, float]:
    """Return the five weighted quantiles and mean used for boxplots."""

    p05, p25, p50, p75, p95 = weighted_quantile(
        values, weights, [0.05, 0.25, 0.50, 0.75, 0.95]
    )
    return {
        "weighted_p05": float(p05),
        "weighted_p25": float(p25),
        "weighted_median": float(p50),
        "weighted_p75": float(p75),
        "weighted_p95": float(p95),
        "weighted_mean": weighted_mean(values, weights),
    }
