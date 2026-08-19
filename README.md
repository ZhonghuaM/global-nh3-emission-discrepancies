# Global ammonia emission discrepancies

[![Source data DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21509244.svg)](https://doi.org/10.5281/zenodo.21509244)

Selected code, workflow documentation and example visualisations accompanying
the manuscript **“Spatiotemporal discrepancies between satellite- and
inventory-derived estimates of global ammonia emissions.”**

## Scope

This public companion repository illustrates the principal analysis ideas:

- aligning satellite-constrained (TD) and inventory-derived (BU) ammonia
  emissions on a common monthly 0.1° grid;
- calculating the Normalised Discrepancy Index (NDI);
- applying area, agricultural-share and crop-area weights;
- calculating weighted monthly distributions and climatologies; and
- plotting selected numerical source data deposited with the paper.

The repository is intentionally selective. It is **not** the complete internal
HPC workflow and does not reproduce provider-specific preprocessing from raw
files. Raw IASI/ANNI, HTAP, ERA5, GPM IMERG, SPAM and GSDE data are not
redistributed. Their official records are listed in
[`metadata/data_sources.csv`](metadata/data_sources.csv).

## Public source data

The numerical source data underlying Figs. 1–5 and Supplementary Data 1–4 are
available without restriction from Zenodo:

> Ma, Z. Source data for “Spatiotemporal discrepancies between
> satellite- and inventory-derived estimates of global ammonia emissions”.
> Zenodo, [https://doi.org/10.5281/zenodo.21509244](https://doi.org/10.5281/zenodo.21509244).

Download the Zenodo files to a local directory before running the plotting
examples. The large third-party inputs used to construct those derived source
data must be obtained separately from their original providers.

## Analysis roadmap

The documented workflow, boundaries of the public release and links between
inputs, calculations and outputs are shown in
[`docs/analysis-roadmap.md`](docs/analysis-roadmap.md).

At matched grid-cell and monthly resolution,

```text
NDI = (TD - BU) / (TD + BU)
```

Positive NDI indicates that TD exceeds BU, negative NDI indicates that BU
exceeds TD, and zero indicates agreement. The implementation masks invalid,
negative or insufficient-denominator inputs before calculating the ratio.

## Included examples

- [`scripts/ndi_core.py`](scripts/ndi_core.py): guarded NDI calculation,
  weighted mean, weighted population standard deviation, effective sample size
  and weighted quantiles.
- [`scripts/plot_public_source_data.py`](scripts/plot_public_source_data.py):
  illustrative replots of the deposited monthly distribution and land-use
  climatology summaries.
- [`scripts/plot_global_ndi_banner.py`](scripts/plot_global_ndi_banner.py): a
  deterministic global NDI banner from the deposited Fig. 1a GeoTIFF.
- [`figures/source_data_examples.png`](figures/source_data_examples.png) and
  [`figures/global_ndi_banner.png`](figures/global_ndi_banner.png): example
  outputs from those scripts. These are repository illustrations, not the
  typeset manuscript figures.

## Quick start

```bash
conda env create -f environment/environment.yml
conda activate global-nh3-emission-discrepancies

python -m unittest discover -s tests

python scripts/plot_public_source_data.py \
  --data-dir /path/to/downloaded/zenodo-record \
  --output figures/source_data_examples.png

python scripts/plot_global_ndi_banner.py \
  --raster /path/to/downloaded/zenodo-record/Figure_1_mean_NDI_2008-2016.tif \
  --output figures/global_ndi_banner.png
```

Cartopy may download the Natural Earth 1:110 million public-domain country
boundaries on first use. Local paths belong in `config/paths.yml`, which is
ignored by Git.

## Repository structure

```text
config/       Portable parameter and path templates
data/         Data-access guidance (no raw provider data)
docs/         Analysis roadmap and release boundaries
environment/  Recorded software environment
figures/      Selected repository-only example outputs
metadata/     Product identifiers, outputs and variable definitions
scripts/      Selected illustrative implementations
tests/        Small numerical checks for the public helper functions
```

## Reproducibility boundary

The scripts demonstrate the published equations, weighting logic and plotting
of archived source data. They do not include credentials, private filesystem
paths, scheduler configuration, unpublished intermediate arrays, manuscript
files or editorial correspondence. Results requiring the original provider
products and full historical HPC workflow are therefore outside this compact
public release.

## Citation

Please cite the paper when its article DOI is assigned and cite the Zenodo
record above when using the numerical source data. Citation metadata for this
repository are provided in [`CITATION.cff`](CITATION.cff).

## Licences

- Code is released under the [MIT License](LICENSE).
- Author-created documentation and repository figures are released under
  [CC BY 4.0](CONTENT_LICENSE.md).
- The Zenodo source-data record has its own CC BY 4.0 licence.
- Third-party inputs retain their providers’ licences and terms.

## Contact

Zhonghua Ma ([ORCID 0000-0003-2749-1615](https://orcid.org/0000-0003-2749-1615)).
