"""NYC Rolling Sales ETL Pipeline for NST DVA Capstone 2.

This script loads the raw NYC Rolling Sales CSV, standardizes columns,
cleans the data (handles missing values, incorrect types, outliers),
engineers new features (price per sqft, building age), and
exports a processed file for notebook and Tableau use.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import numpy as np


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert column names to a clean snake_case format."""
    cleaned = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    result = df.copy()
    result.columns = cleaned
    return result


def clean_nyc_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply NYC specific cleaning steps."""
    result = df.copy()
    
    # 1. Drop useless/irrelevant columns
    drop_cols = ["ease_ment", "address", "apartment_number", "block", "lot"]
    drop_cols = [c for c in drop_cols if c in result.columns]
    result = result.drop(columns=drop_cols)

    # 2. Strip whitespace from string columns
    for column in result.select_dtypes(include=["object", "string"]).columns:
        result[column] = result[column].astype("string").str.strip()

    # 3. Convert numeric columns stored as strings
    numeric_str_cols = ["sale_price", "land_square_feet", "gross_square_feet"]
    for col in numeric_str_cols:
        if col in result.columns:
            result[col] = result[col].replace(["-", "- ", " -", " - ", " -  "], np.nan)
            result[col] = pd.to_numeric(result[col], errors="coerce")

    # 4. Convert sale_date to datetime
    if "sale_date" in result.columns:
        result["sale_date"] = pd.to_datetime(result["sale_date"], errors="coerce")

    # 5. Fix year_built (0 = invalid -> NaN)
    if "year_built" in result.columns:
        result["year_built"] = result["year_built"].replace(0, np.nan).astype("Int64")

    # 6. Fix blank tax_class_at_present -> NaN
    if "tax_class_at_present" in result.columns:
        result["tax_class_at_present"] = result["tax_class_at_present"].replace("", np.nan)

    # 7. Zero square footage -> NaN
    for col in ["land_square_feet", "gross_square_feet"]:
        if col in result.columns:
            result.loc[result[col] == 0, col] = np.nan

    # 8. Filter invalid sale prices (missing, $0, or <=$100 non-arm's length transfers)
    if "sale_price" in result.columns:
        result = result[result["sale_price"].notna()]
        result = result[result["sale_price"] > 100]

        # Handle outliers (trim at 1st and 99th percentile)
        p01 = result["sale_price"].quantile(0.01)
        p99 = result["sale_price"].quantile(0.99)
        result = result[(result["sale_price"] >= p01) & (result["sale_price"] <= p99)]

    # 9. Cap extreme gross square feet at 99th percentile
    if "gross_square_feet" in result.columns:
        valid_gsf = result["gross_square_feet"].dropna()
        if len(valid_gsf) > 0:
            gsf_p99 = round(valid_gsf.quantile(0.99))
            result.loc[result["gross_square_feet"] > gsf_p99, "gross_square_feet"] = gsf_p99

    return result.reset_index(drop=True)


def transform_nyc_data(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer new features and enrich the dataset."""
    result = df.copy()

    # Borough code to name mapping
    if "borough" in result.columns:
        borough_map = {1: "Manhattan", 2: "Bronx", 3: "Brooklyn", 4: "Queens", 5: "Staten Island"}
        result["borough_name"] = result["borough"].map(borough_map)

    # Split building class category -> code + description
    if "building_class_category" in result.columns:
        result["building_class_code"] = result["building_class_category"].str.extract(r"^(\d+\w?)", expand=False)
        result["building_class_description"] = (
            result["building_class_category"]
            .str.replace(r"^\d+\w?\s+", "", regex=True)
            .str.strip()
        )

    # Temporal features
    if "sale_date" in result.columns:
        result["sale_year"] = result["sale_date"].dt.year.astype("Int64")
        result["sale_month"] = result["sale_date"].dt.month.astype("Int64")
        result["sale_day_of_week"] = result["sale_date"].dt.day_name()
        result["sale_quarter"] = result["sale_date"].dt.quarter.astype("Int64")

    # Price per square foot
    if "sale_price" in result.columns and "gross_square_feet" in result.columns:
        result["price_per_sqft"] = np.where(
            (result["gross_square_feet"].notna()) & (result["gross_square_feet"] > 0),
            result["sale_price"] / result["gross_square_feet"],
            np.nan,
        )

    # Price per unit
    if "sale_price" in result.columns and "total_units" in result.columns:
        result["price_per_unit"] = np.where(
            result["total_units"] > 0,
            result["sale_price"] / result["total_units"],
            np.nan,
        )

    # Building age
    if "year_built" in result.columns and "sale_year" in result.columns:
        result["building_age"] = np.where(
            result["year_built"].notna() & result["sale_year"].notna(),
            result["sale_year"] - result["year_built"],
            np.nan,
        )
        result.loc[result["building_age"] < 0, "building_age"] = np.nan

    # Floor area ratio
    if "gross_square_feet" in result.columns and "land_square_feet" in result.columns:
        result["floor_area_ratio"] = np.where(
            (result["land_square_feet"].notna()) & (result["land_square_feet"] > 0),
            result["gross_square_feet"] / result["land_square_feet"],
            np.nan,
        )

    # Boolean flags
    if "residential_units" in result.columns:
        result["is_residential"] = (result["residential_units"] > 0).astype(int)
    if "total_units" in result.columns:
        result["has_units"] = (result["total_units"] > 0).astype(int)

    # Size category
    if "gross_square_feet" in result.columns:
        result["size_category"] = pd.cut(
            result["gross_square_feet"],
            bins=[0, 1000, 2500, 5000, 10000, float("inf")],
            labels=["Small", "Medium", "Mid-Large", "Large", "Very Large"],
            right=True,
        )

    # Price bracket
    if "sale_price" in result.columns:
        result["price_bracket"] = pd.cut(
            result["sale_price"],
            bins=[0, 250_000, 500_000, 1_000_000, 2_500_000, 5_000_000, float("inf")],
            labels=["<250K", "250K-500K", "500K-1M", "1M-2.5M", "2.5M-5M", "5M+"],
            right=True,
        )

    # Reorder columns logically
    col_order = [
        "borough", "borough_name", "neighborhood", "zip_code",
        "building_class_category", "building_class_code", "building_class_description",
        "building_class_at_present", "building_class_at_time_of_sale",
        "tax_class_at_present", "tax_class_at_time_of_sale",
        "residential_units", "commercial_units", "total_units",
        "land_square_feet", "gross_square_feet", "year_built",
        "sale_date", "sale_price",
        "sale_year", "sale_month", "sale_quarter", "sale_day_of_week",
        "price_per_sqft", "price_per_unit", "building_age", "floor_area_ratio",
        "is_residential", "has_units", "size_category", "price_bracket",
    ]
    col_order = [c for c in col_order if c in result.columns]
    remaining = [c for c in result.columns if c not in col_order]
    
    return result[col_order + remaining]


def build_clean_dataset(input_path: Path) -> pd.DataFrame:
    """Read a raw CSV file and return a cleaned, transformed dataframe."""
    print(f"Loading raw dataset from {input_path}...")
    
    # The first column in NYC dataset is an unnamed index, so we drop it if it exists.
    df = pd.read_csv(input_path)
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
        
    print(f"Initial shape: {df.shape[0]:,} rows | {df.shape[1]} columns")
    
    print("Normalizing columns...")
    df = normalize_columns(df)
    
    print("Applying data cleaning rules...")
    df = clean_nyc_data(df)
    
    print("Engineering features and transforming data...")
    df = transform_nyc_data(df)
    
    return df


def save_processed(df: pd.DataFrame, output_path: Path) -> None:
    """Write the cleaned dataframe to disk, creating the parent folder if needed."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Capstone 2 NYC Rolling Sales ETL pipeline.")
    parser.add_argument(
        "--input",
        required=False,
        default=Path("data/raw/nyc-rolling-sales.csv"),
        type=Path,
        help="Path to the raw CSV file in data/raw/.",
    )
    parser.add_argument(
        "--output",
        required=False,
        default=Path("data/processed/cleaned_data.csv"),
        type=Path,
        help="Path to the cleaned CSV file in data/processed/.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    
    # Resolve to absolute paths relative to the current working directory
    input_path = args.input.resolve()
    output_path = args.output.resolve()
    
    print("Starting ETL pipeline...")
    cleaned_df = build_clean_dataset(input_path)
    
    save_processed(cleaned_df, output_path)
    print(f"\nProcessed dataset saved to: {output_path}")
    print(f"Final shape: {len(cleaned_df):,} rows | {len(cleaned_df.columns)} columns")


if __name__ == "__main__":
    main()
