#!/usr/bin/env python3
"""Plot two compact examples from the public Zenodo source-data tables.

The resulting image is an illustrative repository preview. It uses the exact
archived summary values but does not reproduce the typeset manuscript panels.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd


matplotlib.use("Agg")
import matplotlib.pyplot as plt


BOXPLOT_FILE = "Figure_2_monthly_weighted_boxplot_statistics.csv"
CLIMATOLOGY_FILE = "Figure_3_monthly_climatology_displayed.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot selected monthly summaries from Zenodo record 21509244."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        required=True,
        help="Directory containing the downloaded Zenodo source-data files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Destination PNG.",
    )
    return parser.parse_args()


def require_columns(frame: pd.DataFrame, columns: set[str], source: Path) -> None:
    missing = sorted(columns.difference(frame.columns))
    if missing:
        raise ValueError(f"{source.name} is missing columns: {', '.join(missing)}")


def boxplot_records(frame: pd.DataFrame) -> list[dict[str, object]]:
    return [
        {
            "label": row.month_name,
            "whislo": row.weighted_p05,
            "q1": row.weighted_p25,
            "med": row.weighted_median,
            "q3": row.weighted_p75,
            "whishi": row.weighted_p95,
            "mean": row.weighted_mean,
            "fliers": [],
        }
        for row in frame.itertuples(index=False)
    ]


def create_figure(boxes: pd.DataFrame, climatology: pd.DataFrame, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    months = np.arange(1, 13)

    figure, axes = plt.subplots(1, 2, figsize=(12, 4.4), dpi=180)
    figure.patch.set_facecolor("white")

    artists = axes[0].bxp(
        boxplot_records(boxes),
        showmeans=True,
        patch_artist=True,
        widths=0.62,
        meanprops={
            "marker": "D",
            "markerfacecolor": "#126782",
            "markeredgecolor": "#126782",
            "markersize": 4.0,
        },
        medianprops={"color": "#202020", "linewidth": 1.2},
        whiskerprops={"color": "#555555", "linewidth": 0.9},
        capprops={"color": "#555555", "linewidth": 0.9},
    )
    for box in artists["boxes"]:
        box.set(facecolor="#c7e9e5", edgecolor="#397c78", linewidth=0.9)
    axes[0].axhline(0, color="#777777", linewidth=0.7, linestyle="--")
    axes[0].set_title("Weighted monthly NDI distributions")
    axes[0].set_xlabel("Calendar month")
    axes[0].set_ylabel("Normalised Discrepancy Index")

    ag_colour = "#0f7c78"
    nonag_colour = "#a66f2d"
    axes[1].fill_between(
        months,
        climatology["agricultural_displayed_sd_lower"],
        climatology["agricultural_displayed_sd_upper"],
        color=ag_colour,
        alpha=0.16,
        linewidth=0,
    )
    axes[1].plot(
        months,
        climatology["agricultural_weighted_mean_ndi_displayed"],
        color=ag_colour,
        linewidth=2.0,
        label="Agricultural",
    )
    axes[1].fill_between(
        months,
        climatology["nonagricultural_displayed_sd_lower"],
        climatology["nonagricultural_displayed_sd_upper"],
        color=nonag_colour,
        alpha=0.14,
        linewidth=0,
    )
    axes[1].plot(
        months,
        climatology["nonagricultural_weighted_mean_ndi_displayed"],
        color=nonag_colour,
        linewidth=2.0,
        label="Non-agricultural",
    )
    axes[1].axhline(0, color="#777777", linewidth=0.7, linestyle="--")
    axes[1].set_title("Weighted land-use climatologies")
    axes[1].set_xlabel("Calendar month")
    axes[1].set_ylabel("Normalised Discrepancy Index")
    axes[1].set_xticks(months, boxes["month_name"])
    axes[1].legend(frameon=False, loc="upper right")

    for axis in axes:
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(axis="y", color="#d8d8d8", linewidth=0.55, alpha=0.65)
        axis.set_xlim(0.4, 12.6)

    figure.text(
        0.5,
        0.015,
        "Illustrative replot from public source data: doi:10.5281/zenodo.21509244",
        ha="center",
        va="bottom",
        fontsize=8,
        color="#555555",
    )
    figure.tight_layout(rect=(0, 0.05, 1, 1), w_pad=2.4)
    figure.savefig(output, facecolor="white", bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    args = parse_args()
    data_dir = args.data_dir.expanduser().resolve()
    output = args.output.expanduser().resolve()

    boxplot_path = data_dir / BOXPLOT_FILE
    climatology_path = data_dir / CLIMATOLOGY_FILE
    for path in (boxplot_path, climatology_path):
        if not path.is_file():
            raise FileNotFoundError(f"Required Zenodo file not found: {path}")

    boxes = pd.read_csv(boxplot_path).sort_values("month")
    climatology = pd.read_csv(climatology_path).sort_values("month")
    require_columns(
        boxes,
        {
            "month",
            "month_name",
            "weighted_mean",
            "weighted_p05",
            "weighted_p25",
            "weighted_median",
            "weighted_p75",
            "weighted_p95",
        },
        boxplot_path,
    )
    require_columns(
        climatology,
        {
            "month",
            "agricultural_weighted_mean_ndi_displayed",
            "agricultural_displayed_sd_lower",
            "agricultural_displayed_sd_upper",
            "nonagricultural_weighted_mean_ndi_displayed",
            "nonagricultural_displayed_sd_lower",
            "nonagricultural_displayed_sd_upper",
        },
        climatology_path,
    )
    if len(boxes) != 12 or len(climatology) != 12:
        raise ValueError("Expected exactly twelve calendar-month rows per table")

    create_figure(boxes, climatology, output)
    print(f"Created {output}")


if __name__ == "__main__":
    main()
