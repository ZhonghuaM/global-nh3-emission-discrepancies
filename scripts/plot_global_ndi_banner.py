#!/usr/bin/env python3
"""Render the public Fig. 1a mean-NDI GeoTIFF as a wide global banner.

This is deterministic scientific plotting, not image synthesis. The default
crop (55° S to 70° N) preserves most inhabited land while leaving modest,
equal side margins in a 1400 × 400 canvas. Geographic proportions are not
stretched.
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib
import numpy as np
import rasterio
from PIL import Image, PngImagePlugin
from shapely.geometry import box


matplotlib.use("Agg")
import matplotlib.pyplot as plt


WIDTH_PX = 1400
HEIGHT_PX = 400
DPI = 100
OCEAN_COLOUR = "#e5e5e3"
NO_DATA_LAND_COLOUR = "#f7f7f4"
BOUNDARY_COLOUR = "#252525"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot the deposited global mean-NDI GeoTIFF as an RGB banner."
    )
    parser.add_argument(
        "--raster",
        type=Path,
        required=True,
        help="Downloaded Figure_1_mean_NDI_2008-2016.tif.",
    )
    parser.add_argument("--output", type=Path, required=True, help="Destination PNG.")
    parser.add_argument("--lat-min", type=float, default=-55.0)
    parser.add_argument("--lat-max", type=float, default=70.0)
    parser.add_argument("--vmin", type=float, default=-1.0)
    parser.add_argument("--vmax", type=float, default=1.0)
    return parser.parse_args()


def read_raster(path: Path) -> tuple[np.ma.MaskedArray, tuple[float, ...]]:
    if not path.is_file():
        raise FileNotFoundError(f"Mean-NDI raster not found: {path}")
    with rasterio.open(path) as dataset:
        if dataset.count != 1:
            raise ValueError(f"Expected one raster band, found {dataset.count}")
        if dataset.crs is None or dataset.crs.to_epsg() != 4326:
            raise ValueError(f"Expected EPSG:4326, found {dataset.crs}")
        values = np.ma.masked_invalid(dataset.read(1, masked=True).astype(np.float32))
        bounds = dataset.bounds

    finite = values.compressed()
    if finite.size == 0:
        raise ValueError("The raster contains no finite NDI values")
    if finite.min() < -1.0 or finite.max() > 1.0:
        raise ValueError("NDI values fall outside the theoretical [-1, 1] range")
    return values, (bounds.left, bounds.right, bounds.bottom, bounds.top)


def country_geometries() -> list[object]:
    boundary_file = shpreader.natural_earth(
        resolution="110m", category="cultural", name="admin_0_countries"
    )
    return list(shpreader.Reader(boundary_file).geometries())


def create_banner(
    values: np.ma.MaskedArray,
    extent: tuple[float, ...],
    output: Path,
    *,
    lat_min: float,
    lat_max: float,
    vmin: float,
    vmax: float,
) -> None:
    if not (-90 <= lat_min < lat_max <= 90):
        raise ValueError("Latitude limits must satisfy -90 <= min < max <= 90")
    if not vmin < 0 < vmax:
        raise ValueError("Colour limits must bracket zero")

    output.parent.mkdir(parents=True, exist_ok=True)
    projection = ccrs.PlateCarree()
    figure = plt.figure(
        figsize=(WIDTH_PX / DPI, HEIGHT_PX / DPI),
        dpi=DPI,
        facecolor=OCEAN_COLOUR,
    )
    axis = figure.add_axes([0, 0, 1, 1], projection=projection)
    axis.set_extent([-180, 180, lat_min, lat_max], crs=projection)
    axis.set_aspect("equal", adjustable="box", anchor="C")
    axis.set_facecolor(OCEAN_COLOUR)
    axis.set_axis_off()

    geometries = country_geometries()
    axis.add_geometries(
        geometries,
        crs=projection,
        facecolor=NO_DATA_LAND_COLOUR,
        edgecolor="none",
        linewidth=0,
        zorder=1,
    )

    colour_map = plt.get_cmap("BrBG").copy()
    colour_map.set_bad((0, 0, 0, 0))
    axis.imshow(
        values,
        origin="upper",
        extent=extent,
        transform=projection,
        cmap=colour_map,
        vmin=vmin,
        vmax=vmax,
        interpolation="nearest",
        zorder=2,
    )

    antimeridian_clip = box(-179.98, -89.98, 179.98, 89.98)
    boundaries = [
        clipped
        for geometry in geometries
        if not (clipped := geometry.boundary.intersection(antimeridian_clip)).is_empty
    ]
    axis.add_geometries(
        boundaries,
        crs=projection,
        facecolor="none",
        edgecolor=BOUNDARY_COLOUR,
        linewidth=0.42,
        zorder=3,
    )

    with tempfile.NamedTemporaryFile(
        prefix="ndi_banner_", suffix=".png", dir=output.parent, delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)

    try:
        figure.savefig(
            temporary_path,
            dpi=DPI,
            facecolor=OCEAN_COLOUR,
            edgecolor="none",
            transparent=False,
            bbox_inches=None,
            pad_inches=0,
        )
    finally:
        plt.close(figure)

    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Title", "Global distribution of mean NDI, 2008–2016")
    metadata.add_text("Creator", "Zhonghua Ma")
    metadata.add_text("Source", "https://doi.org/10.5281/zenodo.21509244")
    metadata.add_text("Boundary data", "Natural Earth, public domain")
    try:
        with Image.open(temporary_path) as rendered:
            rendered.convert("RGB").save(
                output, format="PNG", pnginfo=metadata, optimize=True
            )
    finally:
        temporary_path.unlink(missing_ok=True)

    with Image.open(output) as rendered:
        if rendered.size != (WIDTH_PX, HEIGHT_PX) or rendered.mode != "RGB":
            raise RuntimeError(
                f"Unexpected output: size={rendered.size}, mode={rendered.mode}"
            )


def main() -> None:
    args = parse_args()
    values, extent = read_raster(args.raster.expanduser().resolve())
    output = args.output.expanduser().resolve()
    create_banner(
        values,
        extent,
        output,
        lat_min=args.lat_min,
        lat_max=args.lat_max,
        vmin=args.vmin,
        vmax=args.vmax,
    )
    print(f"Created {output} ({WIDTH_PX} × {HEIGHT_PX}, RGB)")


if __name__ == "__main__":
    main()
