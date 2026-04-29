# Data Dictionary

Use this file to document every important field in your dataset. A strong data dictionary makes your cleaning decisions, KPI logic, and dashboard filters much easier to review.

## How To Use This File

1. Add one row for each column used in analysis or dashboarding.
2. Explain what the field means in plain language.
3. Mention any cleaning or standardization applied.
4. Flag nullable columns, derived fields, and known quality issues.

## Dataset Summary

| Item | Details |
|---|---|
| Dataset name | NYC Rolling Sales |
| Source | NYC Department of Finance (via [Kaggle](https://www.kaggle.com/datasets/new-york-city/nyc-property-sales)) |
| Raw file name | `data/raw/nyc-rolling-sales.csv` |
| Last updated | Rolling 12-month window (Sep 1, 2016 – Aug 31, 2017) |
| Granularity | One row per property sale transaction |
| Raw dimensions | 84,548 rows × 21 columns |
| Cleaned dimensions | 57,601 rows × 31 columns |
| Cleaning reference | `notebooks/02_cleaning.ipynb` |

## Column Definitions

### Original Columns (from raw dataset)

| Column Name | Data Type | Description | Example Value | Used In | Cleaning Notes |
|---|---|---|---|---|---|
| `borough` | int | NYC borough code (1=Manhattan, 2=Bronx, 3=Brooklyn, 4=Queens, 5=Staten Island) | 1 | EDA, ANOVA, Tableau | No nulls. Mapped to `borough_name` in Step 9. |
| `neighborhood` | string | Sub-area within the borough | UPPER EAST SIDE | Tableau (neighbourhood drill-down) | Whitespace stripped in Step 5. Used as Tableau filter. |
| `building_class_category` | string | Full property classification label (code + description) | 07 RENTALS - WALKUP APARTMENTS | EDA, Chi-Square, Tableau | Split into `building_class_code` and `building_class_description` in Step 10. |
| `tax_class_at_present` | string | Current tax classification of the property | 2A | EDA | 584 blank values → replaced with NaN in Step 11. |
| `building_class_at_present` | string | Specific building subclass code at time of data pull | C2 | Reference | Whitespace stripped. No further cleaning. |
| `building_class_at_time_of_sale` | string | Specific building subclass code at time of sale | C2 | Reference | Whitespace stripped. No further cleaning. |
| `tax_class_at_time_of_sale` | int | Tax class at time of sale (1, 2, or 4) | 2 | Reference | No cleaning needed. |
| `residential_units` | int | Number of residential units in the building | 5 | T-Test (grouping), Feature engineering | Used to derive `is_residential` flag. |
| `commercial_units` | int | Number of commercial units in the building | 0 | T-Test (grouping) | No cleaning needed. |
| `total_units` | int | Sum of residential + commercial units | 5 | Feature engineering | ~19,762 rows have 0 units (vacant lots). Flagged via `has_units`. |
| `land_square_feet` | float | Area of the land parcel in square feet | 1,633.0 | Feature engineering (FAR) | Stored as string with dash (`" - "`) placeholders → converted to float in Step 6. Zeros → NaN in Step 12. **36,578 nulls after cleaning.** |
| `gross_square_feet` | float | Total interior floor area of the building in square feet | 6,440.0 | KPI (PPSF), Regression, EDA, Tableau | Stored as string → converted to float in Step 6. Zeros → NaN in Step 12. Capped at 99th percentile (27,598 sqft) in Step 16. **29,649 nulls after cleaning.** |
| `year_built` | Int64 (nullable) | Year the building was originally constructed | 1900 | Feature engineering (building age) | 6,970 zero values → replaced with NaN in Step 8. **4,051 nulls after cleaning.** |
| `sale_price` | float | Transaction price in USD | 6,625,000.0 | Primary dependent variable — all KPIs, regression, hypothesis tests, Tableau | Stored as string → converted to float in Step 6. Removed: 14,561 missing, 10,228 $0 sales, 1,002 ≤$100 in Step 14. Filtered to 1st–99th percentile ($25,000–$14,000,000) in Step 15. |
| `sale_date` | datetime | Date of the property transaction | 2017-07-19 | Seasonality analysis, temporal features | Converted from string to datetime in Step 7. Range: 2016-09-01 → 2017-08-31. |

### Dropped Columns (removed in Step 4)

| Column Name | Reason for Removal |
|---|---|
| `ease_ment` | 100% blank (single whitespace in every row — zero information) |
| `address` | Too granular / PII-adjacent — not useful for aggregate analysis |
| `apartment_number` | Too granular — not useful for aggregate analysis |
| `block` | Parcel-level identifier — not analytically meaningful |
| `lot` | Parcel-level identifier — not analytically meaningful |

## Derived Columns

All derived columns were engineered in `notebooks/02_cleaning.ipynb` (Step 17) and are present in `data/processed/cleaned_data.csv`.

| Derived Column | Data Type | Logic | Business Meaning | Null Count |
|---|---|---|---|---|
| `borough_name` | string | Mapped from `borough` code: 1→Manhattan, 2→Bronx, 3→Brooklyn, 4→Queens, 5→Staten Island | Human-readable borough name for all visualisations and reporting | 0 |
| `building_class_code` | string | Extracted leading numeric code from `building_class_category` via regex | Clean classification code for grouping (e.g., "07") | 0 |
| `building_class_description` | string | Extracted text description from `building_class_category` after removing code | Readable property type label (e.g., "RENTALS - WALKUP APARTMENTS") | 0 |
| `sale_year` | Int64 | Extracted year from `sale_date` | Temporal grouping for year-over-year analysis | 0 |
| `sale_month` | Int64 | Extracted month from `sale_date` | Seasonality analysis — identifies peak/trough transaction months | 0 |
| `sale_quarter` | Int64 | Extracted quarter from `sale_date` | Quarterly trend analysis in Tableau | 0 |
| `sale_day_of_week` | string | Day name extracted from `sale_date` | Day-of-week closing pattern analysis (Thursday = peak at 24%) | 0 |
| `price_per_sqft` | float | `sale_price / gross_square_feet` (NaN where sqft is missing or zero) | Primary normalised valuation metric — enables fair comparison across property sizes and types. Median: $350. | 29,649 |
| `price_per_unit` | float | `sale_price / total_units` (NaN where units = 0) | Per-unit investment cost for multi-family evaluation. Median: $491K. | 16,359 |
| `building_age` | float | `sale_year - year_built` (NaN if year_built missing; negative values → NaN) | Property age at time of sale — used in correlation analysis (r = +0.017 with price) | 4,051 |
| `floor_area_ratio` | float | `gross_square_feet / land_square_feet` (NaN where land sqft is missing or zero) | Building density indicator. Higher FAR = more built space per land area. Correlates with price at r = +0.51. | 29,650 |
| `is_residential` | int | 1 if `residential_units > 0`, else 0 | Binary flag for residential vs. non-residential segmentation — used as T-Test grouping variable | 0 |
| `has_units` | int | 1 if `total_units > 0`, else 0 | Identifies properties with zero units (vacant lots, special parcels) | 0 |
| `size_category` | category | Binned `gross_square_feet`: Small (0–1K), Medium (1K–2.5K), Mid-Large (2.5K–5K), Large (5K–10K), Very Large (10K+) | Property size segmentation for comparative analysis | 29,649 |
| `price_bracket` | category | Binned `sale_price`: <250K, 250K–500K, 500K–1M, 1M–2.5M, 2.5M–5M, 5M+ | Price tier segmentation — used in Chi-Square test and Tableau colour encoding | 0 |

## Data Quality Notes

- **$0 Sales:** 10,228 records had $0 sale prices representing non-market transactions (ownership transfers, tax arrangements, intra-family transfers). All removed during cleaning as they do not reflect fair market value.
- **≤$100 Sales:** 1,002 additional records with prices between $1–$100 were identified as non-arm's-length transactions and removed.
- **Missing Square Footage:** 39,029 rows (46% of raw data) had zero or missing `gross_square_feet`. Zeros were converted to NaN. These rows are retained in the dataset for price-based analysis but excluded from any PPSF or FAR calculations.
- **Missing Land Square Footage:** 36,578 rows had zero or missing `land_square_feet`. Same treatment as gross square footage — retained but excluded from FAR calculations.
- **Year Built = 0:** 6,970 rows had `year_built` recorded as 0, which is clearly invalid. These were replaced with NaN and excluded from building age analysis.
- **Negative Building Age:** A small number of rows had `year_built` > `sale_year` (data entry errors). These were set to NaN.
- **Outlier Treatment:** Sale prices were filtered to the 1st–99th percentile range ($25,000–$14,000,000), removing 1,156 extreme values. Gross square footage was capped at the 99th percentile (27,598 sqft) rather than removed.
- **String-Encoded Numerics:** `sale_price`, `land_square_feet`, and `gross_square_feet` were stored as strings in the raw CSV, with dash (`" - "`) placeholders for missing values. All were converted to float64 with errors coerced to NaN.
- **Total Records Removed:** 26,947 rows (31.9% of original 84,548) were removed during the cleaning pipeline. The final cleaned dataset contains 57,601 rows.
- **No External Data:** The dataset lacks external economic indicators (interest rates, inflation), property condition data (renovation status, amenities), and geospatial features (subway proximity, school districts). This limits the regression model's explanatory power (R² ceiling = 0.37).