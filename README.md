# Global ammonia emission discrepancies

Reproducibility materials for the manuscript **“Spatiotemporal discrepancies between satellite- and inventory-derived estimates of global ammonia emissions.”**

## Repository status

This is a revision-stage repository. It currently provides the planned archive structure, dataset manifest, analysis configuration, variable dictionary, and a pinned description of the final local analysis environment. The manuscript, editorial correspondence, reviewer responses, raw third-party datasets, and sensitive working files are deliberately excluded.

The numerical source data required by the journal will be added after final quality control. The custom code remains private during revision while local paths and HPC-specific configuration details are removed. The permanent data archive DOI will be linked here only after its record is active. Until then, this repository must not be cited as the final data archive.

## Planned contents

- `config/`: portable path and analysis-parameter templates.
- `environment/`: pinned software environment and version provenance.
- `metadata/data_sources.csv`: verified source-product versions, identifiers, and official access locations.
- `metadata/output_manifest.csv`: planned generated-data and figure-source-data archive.
- `metadata/variable_dictionary.csv`: definitions and units for archived variables.
- `scripts/`: revision-stage code-release notes; public code release is not part of the required data deposit.
- `data/source_data/`: small numerical source tables for the main figures, to be added with the permanent archive.

## Data-access policy

Third-party IASI, HTAP, ERA5, GPM IMERG, SPAM, and GSDE soil datasets are not redistributed. Their official access locations and persistent identifiers are listed in `metadata/data_sources.csv`. Users must obtain these inputs from the original providers and comply with the providers’ licences and terms.

The planned permanent archive will contain the numerical source data underlying Figures 1–5, Supplementary Data 1–4, a README, and variable- and unit-level metadata. Full harmonised model-output grids are not included in the mandatory deposit plan. The DOI is intentionally omitted until active.

## Core analysis definition

The analysis compares monthly satellite-constrained and inventory-derived ammonia emissions on a common 0.1° grid for 2008–2016. The Normalised Discrepancy Index is

\[
\mathrm{NDI} = \frac{\mathrm{TD}-\mathrm{BU}}{\mathrm{TD}+\mathrm{BU}},
\]

where TD is the satellite-constrained estimate and BU is the inventory-derived estimate on the same grid cell and month.

## Reproducibility notes

- Paths in the forthcoming scripts will be supplied through configuration files, not hard-coded user directories.
- Monthly all-land summaries use grid-cell area weights.
- Agricultural and non-agricultural summaries use grid-cell area multiplied by agricultural share or its complement.
- Crop- and management-specific summaries use the corresponding SPAM physical-area share.
- Figure 2 uses twelve unsmoothed, area-weighted boxplots calculated from pooled valid 0.1° grid-cell-month observations for 2008–2016; boxes show weighted interquartile ranges, centre lines weighted medians, whiskers weighted 5th–95th percentiles, and diamonds weighted means.
- Figure 3 retains the author-supplied Gaussian-smoothed calendar-month weighted means and weighted population-standard-deviation bands (σ = 0.85 months).

## Citation

A final data citation and DOI will be added after archival release. The provisional citation metadata are provided in `CITATION.cff`.

## Contact

Repository maintainer: Zhonghua Ma ([ORCID 0000-0003-2749-1615](https://orcid.org/0000-0003-2749-1615)).
