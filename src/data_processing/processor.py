"""
Data processing module for real estate property data.
Handles data cleaning, transformation, filtering, and deduplication.
"""

import pandas as pd
from typing import List, Set, Optional, Tuple
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.config import ColumnConfig, ProcessingConfig


logger = get_logger(__name__)


class DataProcessor:
    """Handles all data processing operations for real estate property data."""

    def __init__(self, column_config: ColumnConfig, processing_config: ProcessingConfig):
        """
        Initialize the data processor.

        Args:
            column_config: Column configuration settings
            processing_config: Processing parameter configuration
        """
        self.column_config = column_config
        self.processing_config = processing_config
        logger.info("DataProcessor initialized")

    def consolidate_dataframes(self, dataframes: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Consolidate multiple dataframes into one.

        Args:
            dataframes: List of pandas DataFrames to consolidate

        Returns:
            Consolidated DataFrame

        Raises:
            ValueError: If no dataframes provided
        """
        if not dataframes:
            logger.error("No dataframes provided for consolidation")
            raise ValueError("Cannot consolidate empty list of dataframes")

        logger.info(f"Consolidating {len(dataframes)} dataframes")
        consolidated = pd.concat(dataframes, ignore_index=True)
        logger.info(f"Consolidated into {len(consolidated):,} total rows")

        return consolidated

    def select_relevant_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Select only relevant columns that exist in the dataframe.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with only relevant columns
        """
        all_columns = self.column_config.get_all_columns()
        existing_columns = [col for col in all_columns if col in df.columns]

        logger.info(f"Selecting {len(existing_columns)} relevant columns out of {len(df.columns)} total")
        logger.debug(f"Selected columns: {existing_columns}")

        return df[existing_columns].copy()

    def clean_addresses(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove rows with incomplete address information.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with complete addresses only
        """
        initial_rows = len(df)
        columns_to_check = self.column_config.address_validation_columns
        existing_check_cols = [col for col in columns_to_check if col in df.columns]

        if not existing_check_cols:
            logger.warning("No address columns found for validation")
            return df

        df_cleaned = df.dropna(subset=existing_check_cols, how='any').copy()
        rows_removed = initial_rows - len(df_cleaned)

        logger.info(f"Address cleaning: Removed {rows_removed:,} rows with incomplete addresses")
        logger.info(f"Remaining rows: {len(df_cleaned):,}")

        return df_cleaned

    def calculate_distress_counter(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the DistressCounter column (sum of active distress indicators).

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with DistressCounter column added
        """
        distress_existing = [
            col for col in self.column_config.distress_columns
            if col in df.columns
        ]

        if not distress_existing:
            logger.warning("No distress columns found, DistressCounter will be 0")
            df['DistressCounter'] = 0
            return df

        logger.info(f"Calculating DistressCounter using {len(distress_existing)} distress indicators")

        # Fill NaN with 0 and count boolean True values
        distress_df = df[distress_existing].fillna(0)
        df['DistressCounter'] = distress_df.apply(lambda row: row.astype(bool).sum(), axis=1)

        logger.debug(f"DistressCounter range: {df['DistressCounter'].min()} to {df['DistressCounter'].max()}")

        return df

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate records based on mailing and property addresses.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with duplicates removed
        """
        initial_rows = len(df)

        # Remove duplicates based on unique1 columns (mailing address)
        unique1_existing = [
            col for col in self.column_config.unique1_columns
            if col in df.columns
        ]
        if unique1_existing:
            df = df.drop_duplicates(subset=unique1_existing).copy()
            logger.debug(f"Removed duplicates based on {unique1_existing}")

        # Remove duplicates based on unique2 columns (property address)
        unique2_existing = [
            col for col in self.column_config.unique2_columns
            if col in df.columns
        ]
        if unique2_existing:
            df = df.drop_duplicates(subset=unique2_existing).copy()
            logger.debug(f"Removed duplicates based on {unique2_existing}")

        rows_removed = initial_rows - len(df)
        logger.info(f"Duplicate removal: Removed {rows_removed:,} duplicate records")
        logger.info(f"Remaining rows: {len(df):,}")

        return df

    def filter_top_by_distress(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter to keep only the top percentage of records by distress score.

        Args:
            df: Input DataFrame with DistressCounter column

        Returns:
            DataFrame with top records retained
        """
        if 'DistressCounter' not in df.columns:
            logger.warning("DistressCounter column not found, skipping distress-based filtering")
            return df

        initial_rows = len(df)

        # Sort by DistressCounter in descending order
        df_sorted = df.sort_values(by='DistressCounter', ascending=False).copy()

        # Calculate cutoff index
        cutoff_index = max(1, int(initial_rows * self.processing_config.percentage_to_retain))
        df_filtered = df_sorted.iloc[:cutoff_index].copy()

        rows_kept = len(df_filtered)
        rows_removed = initial_rows - rows_kept

        logger.info(
            f"Distress filtering: Kept top {self.processing_config.percentage_to_retain:.0%} "
            f"({rows_kept:,} rows, removed {rows_removed:,})"
        )

        return df_filtered

    def reorder_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Reorder columns according to display order configuration.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with columns reordered
        """
        display_order = self.column_config.display_order
        distress_columns = self.column_config.distress_columns

        # Get existing distress columns
        existing_distress = [col for col in distress_columns if col in df.columns]

        # Combine display order with distress columns
        final_order = display_order + existing_distress

        # Filter to only existing columns
        existing_order = [col for col in final_order if col in df.columns]

        logger.info(f"Reordering {len(existing_order)} columns")
        logger.debug(f"Column order: {existing_order[:10]}...")  # Show first 10

        return df[existing_order].copy()

    def rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rename columns to standardized display names.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with renamed columns
        """
        rename_map = self.column_config.rename_mapping
        renamed_count = sum(1 for col in df.columns if col in rename_map)

        df_renamed = df.rename(columns=rename_map).copy()

        logger.info(f"Renamed {renamed_count} columns to standardized names")

        return df_renamed

    def uppercase_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert all column names to uppercase.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with uppercase column names
        """
        df.columns = df.columns.str.upper()
        logger.debug("Converted all column names to uppercase")

        return df

    def clean_ltv_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and filter LTV (Loan-to-Value) column.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with cleaned LTV values
        """
        if 'LTV' not in df.columns:
            logger.warning("LTV column not found, skipping LTV cleaning")
            return df

        initial_rows = len(df)

        # Convert to string for pattern matching
        ltv_str = df['LTV'].astype(str)

        # Keep rows where LTV is 'unknown' or <= threshold
        mask = (
            ltv_str.str.lower().str.contains('unknown', na=False) |
            (pd.to_numeric(df['LTV'], errors='coerce') <= self.processing_config.ltv_max_threshold)
        )
        df_cleaned = df[mask | df['LTV'].isna()].copy()

        # Convert to numeric
        df_cleaned['LTV'] = pd.to_numeric(df_cleaned['LTV'], errors='coerce')

        rows_removed = initial_rows - len(df_cleaned)
        logger.info(
            f"LTV cleaning: Removed {rows_removed:,} rows with LTV > "
            f"{self.processing_config.ltv_max_threshold}"
        )

        return df_cleaned

    def apply_title_case(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply title case formatting to text columns.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with title-cased text columns
        """
        title_cols = self.column_config.title_case_columns
        existing_title_cols = [col for col in title_cols if col in df.columns]

        for col in existing_title_cols:
            if pd.api.types.is_string_dtype(df[col]):
                df[col] = df[col].str.title()

        logger.info(f"Applied title case to {len(existing_title_cols)} text columns")

        return df

    def merge_fips_data(self, df: pd.DataFrame, fips_file: Path) -> pd.DataFrame:
        """
        Merge FIPS county data into the dataframe.

        Args:
            df: Input DataFrame
            fips_file: Path to FIPS Excel file

        Returns:
            DataFrame with county information merged
        """
        if not fips_file.exists():
            logger.warning(f"FIPS file not found at {fips_file}, skipping county merge")
            return df

        try:
            logger.info(f"Reading FIPS data from {fips_file}")
            fips_df = pd.read_excel(fips_file)

            # Verify required columns exist
            if not all(col in fips_df.columns for col in ['FIPS Code', 'County']):
                logger.error("FIPS file missing required columns: 'FIPS Code', 'County'")
                return df

            # Merge on FIPS code
            df_merged = pd.merge(
                df,
                fips_df[['FIPS Code', 'County']],
                left_on='FIPS',
                right_on='FIPS Code',
                how='left'
            )

            # Drop redundant FIPS Code column
            df_merged.drop('FIPS Code', axis=1, inplace=True)

            # Rename County column
            df_merged.rename(columns={'County': 'COUNTY'}, inplace=True)

            # Reorder to place COUNTY after PROPERTY STATE
            if 'PROPERTY STATE' in df_merged.columns and 'COUNTY' in df_merged.columns:
                cols = df_merged.columns.tolist()
                prop_state_idx = cols.index('PROPERTY STATE')
                county_idx = cols.index('COUNTY')
                cols.insert(prop_state_idx + 1, cols.pop(county_idx))
                df_merged = df_merged[cols]

            logger.info("Successfully merged COUNTY data from FIPS file")

            return df_merged

        except Exception as e:
            logger.error(f"Error processing FIPS file: {e}", exc_info=True)
            return df

    def remove_previous_addresses(
        self,
        df: pd.DataFrame,
        previous_addresses: Set[str]
    ) -> Tuple[pd.DataFrame, int]:
        """
        Remove properties that appear in the previous addresses set.

        Args:
            df: Input DataFrame
            previous_addresses: Set of addresses to filter out (lowercase)

        Returns:
            Tuple of (filtered DataFrame, count of rows removed)
        """
        if not previous_addresses:
            logger.info("No previous addresses provided, skipping duplicate removal")
            return df, 0

        initial_rows = len(df)

        # Create lowercase version of property addresses for matching
        if 'PROPERTY ADDRESS' not in df.columns:
            logger.warning("PROPERTY ADDRESS column not found, cannot remove duplicates")
            return df, 0

        consolidated_addresses = df['PROPERTY ADDRESS'].str.strip().str.lower()

        # Filter out addresses that are in the previous set
        mask = ~consolidated_addresses.isin(previous_addresses)
        df_filtered = df[mask].copy()

        rows_removed = initial_rows - len(df_filtered)

        logger.info(f"Removed {rows_removed:,} properties found in previous files")
        logger.info(f"Remaining properties: {len(df_filtered):,}")

        return df_filtered, rows_removed


class DataValidator:
    """Validates data quality and completeness."""

    def __init__(self):
        """Initialize the data validator."""
        logger.debug("DataValidator initialized")

    def validate_dataframe(self, df: pd.DataFrame, name: str = "DataFrame") -> bool:
        """
        Validate basic DataFrame properties.

        Args:
            df: DataFrame to validate
            name: Name for logging purposes

        Returns:
            True if valid, False otherwise
        """
        if df is None:
            logger.error(f"{name} is None")
            return False

        if df.empty:
            logger.warning(f"{name} is empty")
            return False

        logger.info(f"{name} validation passed: {len(df):,} rows, {len(df.columns)} columns")
        return True

    def check_required_columns(
        self,
        df: pd.DataFrame,
        required_columns: List[str],
        name: str = "DataFrame"
    ) -> bool:
        """
        Check if required columns exist in the DataFrame.

        Args:
            df: DataFrame to check
            required_columns: List of required column names
            name: Name for logging purposes

        Returns:
            True if all required columns exist, False otherwise
        """
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            logger.warning(f"{name} missing required columns: {missing_columns}")
            return False

        logger.debug(f"{name} has all required columns")
        return True

    def get_data_summary(self, df: pd.DataFrame) -> dict:
        """
        Get a summary of the DataFrame for logging and reporting.

        Args:
            df: DataFrame to summarize

        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'null_counts': df.isnull().sum().to_dict()
        }

        logger.debug(f"Data summary: {summary['total_rows']:,} rows, {summary['total_columns']} columns")

        return summary
