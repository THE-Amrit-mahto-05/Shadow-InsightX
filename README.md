# NYC Real Estate Sales Analysis

### Quick Start

If you are working locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

If you are working in Google Colab:

- Upload or sync the notebooks from `notebooks/`
- Keep the final `.ipynb` files committed to GitHub
- Export any cleaned datasets into `data/processed/`

---

## Project Overview

| Field | Details |
|---|---|
| **Project Title** | NYC Real Estate Sales Analysis |
| **Sector** | Real Estate / Finance |
| **Team ID** | Shadow-InsightX |
| **Institute** | Newton School of Technology |
| **Submission Date** | 28-04-2026 |

### Team Members

| Role | Name | GitHub Username |
|---|---|---|
| Project/Visualization Lead | Amrit Mahto | [THE-Amrit-mahto-05](https://github.com/THE-Amrit-mahto-05) |
| Data/Analysis Lead | Anuj Chhajed | [Anuj-Chhajed](https://github.com/Anuj-Chhajed) |
| ETL Lead | Ayush Kumar | [Ayush123-e](https://github.com/Ayush123-e) |
| Strategy Lead | Parth Tandalwade | [parth-tandalwade](https://github.com/parth-tandalwade) |
| PPT and Quality Lead | Nakul Sharma | [29naks2005](https://github.com/29naks2005) |

---

## Business Problem

The New York City real estate market — one of the world's largest — processes tens of thousands of property transactions annually across five boroughs with vastly different pricing dynamics. Despite this scale, most market participants — investors, developers, lenders, and policymakers — rely on city-wide averages that mask critical borough-level disparities. Property valuations are influenced by subjective appraisals and inconsistent comparables, leading to mispricing, missed investment windows, and inequitable tax assessments. This project uses the NYC Rolling Sales dataset (84,548 transactions) to build a data-driven decision-support framework that replaces guesswork with statistically validated insights.

**Core Business Question**

> What property attributes (location, size, building class, density, seasonality) most significantly drive sale prices in NYC, and how do these drivers vary across boroughs and property types?

**Decision Supported**

> This analysis enables investors to identify undervalued boroughs and optimal transaction timing, developers to choose between renovation and new construction based on density and age metrics, lenders to adopt segmented valuation models for collateral assessment, and policymakers to benchmark equitable property tax assessments using statistically validated price disparities.

---

## Dataset

| Attribute | Details |
|---|---|
| **Source Name** | NYC Property Sales (via Kaggle) |
| **Direct Access Link** | [https://www.kaggle.com/datasets/new-york-city/nyc-property-sales](https://www.kaggle.com/datasets/new-york-city/nyc-property-sales) |
| **Row Count** | 84,548 (raw) → 57,601 (cleaned) |
| **Column Count** | 21 (raw) → 31 (after feature engineering) |
| **Time Period Covered** | September 1, 2016 – August 31, 2017 |
| **Format** | CSV |

**Key Columns Used**

| Column Name | Description | Role in Analysis |
|---|---|---|
| `sale_price` | Transaction price in USD | Primary dependent variable; used in all KPIs, regression, and hypothesis tests |
| `gross_square_feet` | Total interior floor area of the building | Strongest single predictor (r = +0.59); used for PPSF calculation |
| `borough` / `borough_name` | NYC borough code (1–5) and mapped name | Key segmentation variable; ANOVA grouping factor |
| `building_class_category` | Property type classification (e.g., "01 ONE FAMILY DWELLINGS") | Chi-Square test variable; Tableau building class comparison |
| `sale_date` | Date of property transaction | Extracted `sale_month`, `sale_quarter` for seasonality analysis |
| `year_built` | Year the building was originally constructed | Used to engineer `building_age`; correlation analysis |
| `land_square_feet` | Area of the land parcel | Used to engineer `floor_area_ratio` (building density) |
| `residential_units` / `commercial_units` | Number of residential and commercial units | Used to engineer `is_residential` flag; T-Test grouping |
| `price_per_sqft` | Engineered: `sale_price / gross_square_feet` | Primary normalised valuation metric across all borough/type comparisons |
| `floor_area_ratio` | Engineered: `gross_square_feet / land_square_feet` | Building density indicator; moderate positive correlation with price (r = +0.51) |

For full column definitions, see [`docs/data_dictionary.md`](docs/data_dictionary.md).

---

## KPI Framework

| KPI | Definition | Formula / Computation |
|---|---|---|
| **Median Sale Price** | The middle value of all property transactions — represents what a "typical" buyer actually pays ($636K). More reliable than mean for right-skewed markets. | `df["sale_price"].median()` → Computed in `notebooks/03_exploratory_data_analysis.ipynb` |
| **Price Per Square Foot (PPSF)** | Normalised property value by size, enabling fair comparison across different property types and boroughs. Median: $350. | `sale_price / gross_square_feet` → Engineered in `notebooks/02_cleaning.ipynb` (Step 17a) |
| **Price Per Unit** | Per-unit investment cost for multi-family properties — critical for rental income evaluation. Median: $491K. | `sale_price / total_units` → Engineered in `notebooks/02_cleaning.ipynb` (Step 17b) |
| **Monthly Transaction Volume** | Count of sales per month (Range: 4,276 – 5,841) — tracks market liquidity and seasonal demand cycles. | `df.groupby("sale_month")["sale_price"].count()` → Computed in `notebooks/03_exploratory_data_analysis.ipynb` |
| **Borough Market Share** | Percentage of total transactions per borough — identifies where activity is concentrated vs. underserved. Queens: 31%, Brooklyn: 26%, Manhattan: 24%. | `df["borough_name"].value_counts(normalize=True)` → Computed in `notebooks/03_exploratory_data_analysis.ipynb` |
| **Floor Area Ratio (FAR)** | Building density indicator — higher FAR correlates with higher property value (r = +0.51). | `gross_square_feet / land_square_feet` → Engineered in `notebooks/02_cleaning.ipynb` (Step 17g) |
| **Model R² Score** | Proportion of sale price variance explained by the regression model — quantifies predictive accuracy. Best: R² = 0.37. | `r2_score(y_test, y_pred)` → Computed in `notebooks/04_statistical_analysis.ipynb` |

Document KPI logic clearly in `notebooks/04_statistical_analysis.ipynb` and `notebooks/05_final_load_prep.ipynb`.

---

## Tableau Dashboard

| Item | Details |
|---|---|
| **Dashboard URL** | https://public.tableau.com/views/NYCproperty/Dashboard2?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link |
| **Executive View** | **Sales by Borough** — Stacked horizontal bar chart showing total sales value across all 5 boroughs, colour-segmented by price bracket (<250K through 5M+). Manhattan dominates at $26.6B total value. **Sales Trend by Year** — Multi-line chart tracking year-over-year sales value per borough, revealing Manhattan's steep growth from $8.7B to $18.7B. |
| **Operational View** | **Avg Price/Sqft by Building Class** — Bar chart comparing average PPSF across 28 building class categories (Condo Hotels lead at $2,789/sqft). **Neighbourhood Sales Volume** — Top 10 neighbourhoods ranked by total sales value (Upper East Side leads at $2.67B). **Price Bracket Count by Quarter** — Multi-line trend showing quarterly transaction counts across 6 price tiers, validating the Q2 seasonal volume peak. |
| **Main Filters** | Borough Name, Neighbourhood, Sale Year, Price Bracket (colour encoding), Tooltips (SUM Sale Price, AVG PPSF, CNT Total Units) |

Store dashboard screenshots in [`tableau/screenshots/`](tableau/screenshots/) and document the public links in [`tableau/dashboard_links.md`](tableau/dashboard_links.md).

---

## Key Insights

1. **The "average" NYC property doesn't exist.** The mean sale price ($1.07M) is 67% higher than the median ($636K), revealing a market heavily distorted by luxury transactions in the upper tail.
2. **Manhattan charges 3× the Bronx for the same square footage.** Median PPSF is $695 in Manhattan vs. $226 in the Bronx — a gap confirmed as statistically significant by ANOVA (F = 2,607.62, p ≈ 0).
3. **62% of all transactions fall in the $250K–$1M band.** The luxury segment (>$2.5M) represents only ~8% of transactions but disproportionately skews market averages.
4. **Summer drives volume, not price.** June sees 37% more transactions than February (5,841 vs. 4,276), yet median prices remain stable year-round ($600K–$714K). Sellers hold through slow months rather than discounting.
5. **Building age has near-zero impact on property value.** 42.5% of properties are over 80 years old, yet age correlation with price is r = +0.017 — pre-war buildings in prime locations retain and often command luxury premiums.
6. **Manhattan's building density (FAR) is 5.6× Staten Island's.** Manhattan's median FAR is 2.86 vs. 0.51 for Staten Island, and FAR correlates positively with sale price (r = +0.51) — denser buildings are worth more.
7. **Non-residential properties sell at lower medians but far higher extremes.** Residential median ($694K) exceeds non-residential ($465K), but commercial outliers push the non-residential mean ($2.89M) far higher — two fundamentally different markets sharing one dataset (T-Test p = 1.35e-81).
8. **Square footage is the strongest single predictor of price (r = +0.59).** However, R² = 0.35 confirms that size alone explains only 35% of variance — any practical model must incorporate location, building class, and density.
9. **Building class directly predicts price tier.** Chi-Square test (χ² = 8,054.63, p ≈ 0) confirmed a statistically significant association between building class category and price bracket.
10. **The Upper East Side alone accounts for $5.2B+ in total sales value.** 7 of the top 10 highest-value neighbourhoods are in Manhattan, with Flushing-North (Queens) being the only outer-borough entry in the top 5.

---

## Recommendations

| # | Insight | Recommendation | Expected Impact |
|---|---|---|---|
| 1 | Manhattan charges 3× the Bronx per sqft (Insight 2) | **Adopt borough-specific pricing models** instead of city-wide averages. A property at $400/sqft is underpriced in Manhattan but overpriced in the Bronx. | Reduces valuation error by aligning benchmarks with statistically validated borough-level PPSF ranges ($226–$695). |
| 2 | Summer drives volume, not price (Insight 4) | **Time property listings for April–July** to capture peak buyer demand. Buyers seeking leverage should target January–February for reduced competition. | Sellers gain 37% more buyer exposure; buyers gain faster closing timelines in low-competition months. |
| 3 | Building age doesn't reduce value (Insight 5) | **Invest in pre-war building renovation** over new mid-tier construction. 42.5% of stock is 80+ years old and commands luxury pricing in prime locations. | Redirects development capital toward cost-effective renovation with proven market premiums. |
| 4 | Residential ≠ Commercial (Insight 7) | **Separate residential and commercial portfolios** in all analysis, valuation, and risk assessment. | Eliminates cross-contamination between markets with a $1.97M mean price gap (p = 1.35e-81). |
| 5 | Density correlates with value (Insight 6) | **Prioritise high-FAR parcels for land acquisition** in demand boroughs — density (r = +0.51) is a stronger value predictor than age, unit count, or land area. | Targets properties with the highest value-add potential through density-driven development. |

---

## Repository Structure

```text
Shadow-InsightX/
|
|-- README.md
|
|-- data/
|   |-- raw/                         # Original dataset (never edited)
|   `-- processed/                   # Cleaned output from ETL pipeline
|
|-- notebooks/
|   |-- 01_extraction.ipynb
|   |-- 02_cleaning.ipynb
|   |-- 03_eda.ipynb
|   |-- 04_statistical_analysis.ipynb
|   `-- 05_final_load_prep.ipynb
|
|-- scripts/
|   `-- etl_pipeline.py
|
|-- tableau/
|   |-- screenshots/
|   `-- dashboard_links.md
|
|-- reports/
|   |-- README.md
|   |-- project_report_template.md
|   `-- presentation_outline.md
|
|-- docs/
|   `-- data_dictionary.md
```

---

## Analytical Pipeline

The project follows a structured 7-step workflow:

1. **Define** - Real estate sector selected; problem statement scoped around NYC borough-level price disparities and investment timing; mentor approval obtained.
2. **Extract** - NYC Rolling Sales dataset (84,548 records) sourced from Kaggle/NYC Department of Finance and committed to `data/raw/`; data dictionary drafted in `docs/data_dictionary.md`.
3. **Clean and Transform** - 20-step cleaning pipeline built in `notebooks/02_cleaning.ipynb`: removed 26,947 invalid/outlier rows, converted data types, engineered 10 new features (PPSF, FAR, building age, price brackets, size categories). Output: `data/processed/cleaned_data.csv` (57,601 × 31).
4. **Analyze** - EDA (`notebooks/03_exploratory_data_analysis.ipynb`): 10+ visualisations covering distributions, borough comparisons, seasonality, and correlations. Statistical analysis (`notebooks/04_statistical_analysis.ipynb`): ANOVA, T-Test, Chi-Square (all significant at p < 0.05), Simple & Multiple Linear Regression (R² = 0.37).
5. **Visualize** - 5-view Tableau dashboard built and published: Sales by Borough, Sales Trend, PPSF by Building Class, Neighbourhood Sales Volume, Price Bracket by Quarter.
6. **Recommend** - 5 data-backed business recommendations delivered, each linked to a specific statistical finding.
7. **Report** - Final project report and presentation deck completed and exported to PDF in `reports/`.

---

## Tech Stack

| Tool | Status | Purpose |
|---|---|---|
| Python 3.13 + Jupyter Notebooks | Mandatory | ETL, cleaning, analysis, and KPI computation |
| Google Colab | Supported | Cloud notebook execution environment |
| Tableau Public | Mandatory | Dashboard design, publishing, and sharing |
| GitHub | Mandatory | Version control, collaboration, contribution audit |
| SQL | Optional | Not used in this project |

**Python libraries used:** `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, `scikit-learn`

---

## Evaluation Rubric

| Area | Marks | Focus |
|---|---|---|
| Problem Framing | 10 | Is the business question clear and well-scoped? |
| Data Quality and ETL | 15 | Is the cleaning pipeline thorough and documented? |
| Analysis Depth | 25 | Are statistical methods applied correctly with insight? |
| Dashboard and Visualization | 20 | Is the Tableau dashboard interactive and decision-relevant? |
| Business Recommendations | 20 | Are insights actionable and well-reasoned? |
| Storytelling and Clarity | 10 | Is the presentation professional and coherent? |
| **Total** | **100** | |

> Marks are awarded for analytical thinking and decision relevance, not chart quantity, visual decoration, or code length.

---

## Submission Checklist

**GitHub Repository**

- [x] Public repository created with the correct naming convention (`SectionName_TeamID_ProjectName`)
- [x] All notebooks committed in `.ipynb` format
- [x] `data/raw/` contains the original, unedited dataset
- [x] `data/processed/` contains the cleaned pipeline output
- [x] `tableau/screenshots/` contains dashboard screenshots
- [x] `tableau/dashboard_links.md` contains the Tableau Public URL
- [x] `docs/data_dictionary.md` is complete
- [x] `README.md` explains the project, dataset, and team
- [x] All members have visible commits and pull requests

**Tableau Dashboard**

- [x] Published on Tableau Public and accessible via public URL
- [x] At least one interactive filter included
- [x] Dashboard directly addresses the business problem

**Project Report**

- [x] Final report exported as PDF into `reports/`
- [x] Cover page, executive summary, sector context, problem statement
- [x] Data description, cleaning methodology, KPI framework
- [x] EDA with written insights, statistical analysis results
- [x] Dashboard screenshots and explanation
- [x] 8-12 key insights in decision language
- [x] 3-5 actionable recommendations with impact estimates
- [x] Contribution matrix matches GitHub history

**Presentation Deck**

- [x] Final presentation exported as PDF into `reports/`
- [x] Title slide through recommendations, impact, limitations, and next steps

---

## Contribution Matrix

This table must match evidence in GitHub Insights, PR history, and committed files.

| Team Member | Dataset and Sourcing | ETL and Cleaning | EDA and Analysis | Statistical Analysis | Tableau Dashboard | Report Writing | PPT and Viva |
|---|---|---|---|---|---|---|---|
| Amrit Kumar Mahto | Owner | Support | Support | Support | Owner | Support | Support |
| Anuj Chhajed | Support | Support | Owner | Support | Support | Owner | Support |
| Nakul Sharma | Support | Support | Support | Support | Support | Owner | Owner |
| Ayush Kumar | Support | Owner | Support | Support | Support | Support | Support |
| Parth Tandalwade | Support | Support | Support | Owner | Support | Support | Support |

_Declaration: We confirm that the above contribution details are accurate and verifiable through GitHub Insights, PR history, and submitted artifacts._

**Team Lead Name:** Amrit Kumar Mahto

**Date:** April 28, 2026

---

*Newton School of Technology - Data Visualization & Analytics | Capstone 2*