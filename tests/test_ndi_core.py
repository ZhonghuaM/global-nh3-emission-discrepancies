"""Small numerical checks for the public NDI and weighting helpers."""

from __future__ import annotations

import unittest

import numpy as np

from scripts.ndi_core import (
    effective_sample_size,
    normalised_discrepancy,
    weighted_mean,
    weighted_population_sd,
    weighted_quantile,
)


class NormalisedDiscrepancyTests(unittest.TestCase):
    def test_known_values_and_invalid_inputs(self) -> None:
        actual = normalised_discrepancy(
            [3.0, 1.0, 0.0, 0.0, -1.0],
            [1.0, 3.0, 2.0, 0.0, 1.0],
        )
        np.testing.assert_allclose(actual[:3], [0.5, -0.5, -1.0])
        self.assertTrue(np.isnan(actual[3]))
        self.assertTrue(np.isnan(actual[4]))

    def test_configurable_near_zero_threshold(self) -> None:
        actual = normalised_discrepancy(
            [1e-12, 2.0], [1e-12, 1.0], minimum_combined_flux=1e-10
        )
        self.assertTrue(np.isnan(actual[0]))
        self.assertAlmostEqual(actual[1], 1.0 / 3.0)


class WeightedStatisticsTests(unittest.TestCase):
    def test_equal_weights_match_unweighted_results(self) -> None:
        values = np.array([1.0, 2.0, 3.0])
        weights = np.ones(3)
        self.assertAlmostEqual(weighted_mean(values, weights), 2.0)
        self.assertAlmostEqual(
            weighted_population_sd(values, weights), np.std(values, ddof=0)
        )
        self.assertAlmostEqual(effective_sample_size(weights), 3.0)

    def test_invalid_and_nonpositive_weights_are_excluded(self) -> None:
        result = weighted_mean([1.0, 100.0, 3.0], [1.0, 0.0, 1.0])
        self.assertAlmostEqual(result, 2.0)

    def test_weighted_quantile_is_monotonic(self) -> None:
        result = weighted_quantile(
            [0.0, 1.0, 2.0, 3.0], [1.0, 1.0, 2.0, 6.0], [0.05, 0.5, 0.95]
        )
        self.assertTrue(np.all(np.diff(result) >= 0))
        self.assertTrue(np.all((result >= 0) & (result <= 3)))


if __name__ == "__main__":
    unittest.main()
