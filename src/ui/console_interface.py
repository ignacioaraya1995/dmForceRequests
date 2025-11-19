"""
Console interface module for user interactions.
Provides professional console output and user input handling.
"""

import pandas as pd
from typing import Optional, List, Tuple

from src.utils.logger import get_logger
from src.utils.config import LanguageConfig


logger = get_logger(__name__)


class ConsoleInterface:
    """Handles console user interface and interactions."""

    def __init__(self, language_config: LanguageConfig):
        """
        Initialize the console interface.

        Args:
            language_config: Language configuration for messages
        """
        self.language_config = language_config
        logger.debug("ConsoleInterface initialized")

    def print_header(self, title: str) -> None:
        """
        Print a formatted header.

        Args:
            title: Header title
        """
        width = 60
        print("\n" + "=" * width)
        print(title.center(width))
        print("=" * width + "\n")

    def print_section(self, title: str) -> None:
        """
        Print a section divider.

        Args:
            title: Section title
        """
        print(f"\n--- {title} ---\n")

    def print_info(self, message: str, prefix: str = "INFO") -> None:
        """
        Print an info message.

        Args:
            message: Message to print
            prefix: Prefix for the message
        """
        print(f"[{prefix}] {message}")

    def print_success(self, message: str) -> None:
        """
        Print a success message.

        Args:
            message: Success message
        """
        print(f"[SUCCESS] {message}")

    def print_warning(self, message: str) -> None:
        """
        Print a warning message.

        Args:
            message: Warning message
        """
        print(f"[WARNING] {message}")

    def print_error(self, message: str) -> None:
        """
        Print an error message.

        Args:
            message: Error message
        """
        print(f"[ERROR] {message}")

    def get_client_name(self) -> str:
        """
        Get client name from user with validation.

        Returns:
            Valid client name
        """
        msg = self.language_config.get_message('client_prompt')
        empty_msg = self.language_config.get_message('client_empty')

        while True:
            client_name = input(msg).strip()
            if client_name:
                logger.info(f"Client name entered: {client_name}")
                return client_name
            print(f"[ERROR] {empty_msg}")

    def confirm_action(self, prompt: str) -> bool:
        """
        Get yes/no confirmation from user.

        Args:
            prompt: Prompt message

        Returns:
            True if user confirmed, False otherwise
        """
        response = input(f"{prompt} (yes/no): ").strip().lower()
        confirmed = response == 'yes'
        logger.debug(f"User confirmation for '{prompt}': {confirmed}")
        return confirmed


class DataFilter:
    """Handles interactive data filtering operations."""

    def __init__(self):
        """Initialize the data filter."""
        logger.debug("DataFilter initialized")

    def apply_text_filter(
        self,
        df: pd.DataFrame,
        column_name: str
    ) -> pd.DataFrame:
        """
        Apply text-based filter on a column.

        Args:
            df: DataFrame to filter
            column_name: Column to filter on

        Returns:
            Filtered DataFrame
        """
        initial_count = len(df)

        if initial_count == 0:
            print(f"[WARNING] No data to filter by {column_name}. Skipping.")
            logger.warning(f"Empty dataframe, skipping filter for {column_name}")
            return df

        if column_name not in df.columns:
            print(f"[WARNING] Column '{column_name}' not found. Skipping filter.")
            logger.warning(f"Column {column_name} not found in dataframe")
            return df

        # Show unique values
        unique_items = sorted(df[column_name].dropna().unique())
        print(f"\nAvailable values for '{column_name}':")
        print(f"  {', '.join(map(str, unique_items))}")

        # Get user input
        desired_items_str = input(
            f"Enter desired '{column_name}' values (comma-separated), or press Enter to skip: "
        ).strip().lower()

        if not desired_items_str:
            logger.info(f"User skipped filter for {column_name}")
            return df

        # Parse input
        desired_list = [item.strip() for item in desired_items_str.split(',') if item.strip()]

        if not desired_list:
            logger.warning(f"No valid values provided for {column_name} filter")
            return df

        # Apply filter
        df_filtered = df[df[column_name].str.lower().isin(desired_list)].copy()

        removed = initial_count - len(df_filtered)
        print(f"[INFO] Filter applied. Removed {removed:,} rows. {len(df_filtered):,} rows remaining.\n")
        logger.info(f"Text filter on {column_name}: removed {removed:,} rows")

        return df_filtered

    def apply_numeric_filter(
        self,
        df: pd.DataFrame,
        column_name: str
    ) -> pd.DataFrame:
        """
        Apply numeric range filter on a column.

        Args:
            df: DataFrame to filter
            column_name: Column to filter on

        Returns:
            Filtered DataFrame
        """
        initial_count = len(df)

        if initial_count == 0:
            print(f"[WARNING] No data to filter by {column_name}. Skipping.")
            logger.warning(f"Empty dataframe, skipping filter for {column_name}")
            return df

        if column_name not in df.columns:
            print(f"[WARNING] Column '{column_name}' not found. Skipping filter.")
            logger.warning(f"Column {column_name} not found in dataframe")
            return df

        # Show current range
        current_min = df[column_name].min()
        current_max = df[column_name].max()
        print(f"\nCurrent range for '{column_name}':")
        print(f"  Min = {current_min:,.2f}, Max = {current_max:,.2f}")

        # Get user input
        try:
            min_val_str = input("Enter the minimum value (or press Enter to skip): ").strip()
            max_val_str = input("Enter the maximum value (or press Enter to skip): ").strip()

            # Use current values if not provided
            min_val = float(min_val_str) if min_val_str else current_min
            max_val = float(max_val_str) if max_val_str else current_max

            # Swap if needed
            if min_val > max_val:
                min_val, max_val = max_val, min_val
                print("[WARNING] Minimum is greater than maximum; values have been swapped.")
                logger.warning(f"Swapped min/max values for {column_name}")

            # Apply filter
            df_filtered = df[
                (df[column_name] >= min_val) & (df[column_name] <= max_val)
            ].copy()

            removed = initial_count - len(df_filtered)
            print(f"[INFO] Filter applied. Removed {removed:,} rows. {len(df_filtered):,} rows remaining.\n")
            logger.info(f"Numeric filter on {column_name}: removed {removed:,} rows")

            return df_filtered

        except ValueError as e:
            print(f"[ERROR] Invalid numeric input. Filter not applied: {e}")
            logger.error(f"Invalid numeric input for {column_name} filter: {e}")
            return df

    def apply_interactive_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply interactive filters based on user input.

        Args:
            df: DataFrame to filter

        Returns:
            Filtered DataFrame
        """
        logger.info("Starting interactive filtering")

        print("\n--- Interactive Filters (Optional) ---\n")

        # Owner Type filter
        if input("Do you want to filter by OWNER TYPE? (yes/no): ").strip().lower() == 'yes':
            df = self.apply_text_filter(df, 'OWNER TYPE')

        # Property Type filter
        if input("Do you want to filter by PROPERTY TYPE? (yes/no): ").strip().lower() == 'yes':
            df = self.apply_text_filter(df, 'PROPERTY TYPE')

        # Total Value filter
        if input("Do you want to filter by TOTALVALUE? (yes/no): ").strip().lower() == 'yes':
            df = self.apply_numeric_filter(df, 'TOTALVALUE')

        logger.info("Interactive filtering completed")

        return df


class ProgressTracker:
    """Tracks and displays processing progress."""

    def __init__(self):
        """Initialize the progress tracker."""
        self.steps_completed = 0
        self.total_steps = 0
        logger.debug("ProgressTracker initialized")

    def set_total_steps(self, total: int) -> None:
        """
        Set total number of steps.

        Args:
            total: Total number of processing steps
        """
        self.total_steps = total
        self.steps_completed = 0
        logger.debug(f"Progress tracker set to {total} steps")

    def step_completed(self, message: str) -> None:
        """
        Mark a step as completed and display progress.

        Args:
            message: Description of completed step
        """
        self.steps_completed += 1
        if self.total_steps > 0:
            percentage = (self.steps_completed / self.total_steps) * 100
            print(f"[PROGRESS] Step {self.steps_completed}/{self.total_steps} ({percentage:.1f}%): {message}")
            logger.debug(f"Step {self.steps_completed}/{self.total_steps} completed: {message}")
        else:
            print(f"[PROGRESS] {message}")
            logger.debug(f"Step completed: {message}")

    def print_summary(self, total_records: int, processing_time: Optional[float] = None) -> None:
        """
        Print final processing summary.

        Args:
            total_records: Total number of records processed
            processing_time: Optional processing time in seconds
        """
        print("\n" + "=" * 60)
        print("PROCESSING COMPLETE".center(60))
        print("=" * 60)
        print(f"Total records: {total_records:,}")

        if processing_time:
            print(f"Processing time: {processing_time:.2f} seconds")

        print("=" * 60 + "\n")
        logger.info(f"Processing complete: {total_records:,} records")
