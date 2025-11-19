"""
Excel formatting module for generating professional reports.
Handles Excel file generation with custom formatting and styling.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Set

from src.utils.logger import get_logger
from src.utils.config import ExcelFormatConfig, ColumnConfig


logger = get_logger(__name__)


class ExcelFormatter:
    """Handles Excel file creation with professional formatting."""

    def __init__(
        self,
        excel_config: ExcelFormatConfig,
        column_config: ColumnConfig
    ):
        """
        Initialize the Excel formatter.

        Args:
            excel_config: Excel formatting configuration
            column_config: Column configuration for identifying distress columns
        """
        self.excel_config = excel_config
        self.column_config = column_config
        self.distress_headers_set: Set[str] = {
            col.upper() for col in column_config.distress_columns
        }
        logger.info("ExcelFormatter initialized")

    def save_formatted_excel(
        self,
        df: pd.DataFrame,
        output_path: Path,
        client_name: str
    ) -> Path:
        """
        Save DataFrame to formatted Excel file.

        Args:
            df: DataFrame to save
            output_path: Directory path for output file
            client_name: Client name for filename

        Returns:
            Path to the created Excel file
        """
        # Generate filename with timestamp
        today_date = datetime.now().strftime('%m-%d-%Y')
        filename = f"{client_name} Consolidated {today_date}.xlsx"
        full_path = output_path / filename

        logger.info(f"Saving formatted Excel file to: {full_path}")

        try:
            # Create Excel writer with xlsxwriter engine
            with pd.ExcelWriter(full_path, engine='xlsxwriter') as writer:
                # Write DataFrame without header (we'll add custom header)
                df.to_excel(
                    writer,
                    sheet_name=self.excel_config.sheet_name,
                    index=False,
                    header=False,
                    startrow=1
                )

                # Get workbook and worksheet objects
                workbook = writer.book
                worksheet = writer.sheets[self.excel_config.sheet_name]

                # Apply formatting
                self._format_headers(workbook, worksheet, df)
                self._adjust_column_widths(worksheet, df)

            logger.info(f"Successfully saved Excel file: {full_path}")
            logger.info(f"File size: {full_path.stat().st_size / 1024:.2f} KB")

            return full_path

        except Exception as e:
            logger.error(f"Error saving Excel file: {e}", exc_info=True)
            raise

    def _format_headers(
        self,
        workbook,
        worksheet,
        df: pd.DataFrame
    ) -> None:
        """
        Format header row with different styles for main and distress columns.

        Args:
            workbook: xlsxwriter workbook object
            worksheet: xlsxwriter worksheet object
            df: DataFrame being written
        """
        logger.debug("Formatting header row")

        # Create header formats
        main_format = workbook.add_format(self.excel_config.main_header_format)
        distress_format = workbook.add_format(self.excel_config.distress_header_format)

        # Write headers with appropriate formatting
        for col_num, column_name in enumerate(df.columns.values):
            if column_name in self.distress_headers_set:
                worksheet.write(0, col_num, column_name, distress_format)
            else:
                worksheet.write(0, col_num, column_name, main_format)

        logger.debug(f"Formatted {len(df.columns)} header cells")

    def _adjust_column_widths(
        self,
        worksheet,
        df: pd.DataFrame
    ) -> None:
        """
        Adjust column widths based on content.

        Args:
            worksheet: xlsxwriter worksheet object
            df: DataFrame being written
        """
        logger.debug("Adjusting column widths")

        for col_num, column_name in enumerate(df.columns.values):
            # Calculate column width based on header and max content length
            header_length = len(str(column_name))
            max_content_length = df[column_name].astype(str).str.len().max()
            column_width = max(header_length, max_content_length)

            # Apply width with padding, capped at maximum
            final_width = min(
                column_width + self.excel_config.column_width_padding,
                self.excel_config.max_column_width
            )
            worksheet.set_column(col_num, col_num, final_width)

        logger.debug(f"Adjusted widths for {len(df.columns)} columns")


class ReportGenerator:
    """Generates summary reports and statistics."""

    def __init__(self):
        """Initialize the report generator."""
        logger.debug("ReportGenerator initialized")

    def generate_summary_report(self, df: pd.DataFrame) -> str:
        """
        Generate a text summary report of the data.

        Args:
            df: DataFrame to summarize

        Returns:
            Formatted summary report string
        """
        logger.info("Generating summary report")

        report_lines = []
        report_lines.append("=" * 50)
        report_lines.append("FINAL PROCESS SUMMARY".center(50))
        report_lines.append("=" * 50)

        # Total records
        total_records = len(df)
        report_lines.append(f"TOTAL FINAL RECORDS: {total_records:,}")
        report_lines.append("-" * 50)

        # Counties
        if 'COUNTY' in df.columns and not df['COUNTY'].dropna().empty:
            counties = sorted(df['COUNTY'].dropna().unique())
            counties_str = ', '.join(counties)
            report_lines.append(f"COUNTIES PRESENT: {counties_str}")
        else:
            report_lines.append("COUNTY: Not available or no data")
        report_lines.append("-" * 50)

        # Property types
        if 'PROPERTY TYPE' in df.columns and not df['PROPERTY TYPE'].dropna().empty:
            prop_types = sorted(df['PROPERTY TYPE'].dropna().unique())
            prop_types_str = ', '.join(prop_types)
            report_lines.append(f"PROPERTY TYPES: {prop_types_str}")
        else:
            report_lines.append("PROPERTY TYPE: Not available or no data")
        report_lines.append("-" * 50)

        # Owner types
        if 'OWNER TYPE' in df.columns and not df['OWNER TYPE'].dropna().empty:
            owner_types = sorted(df['OWNER TYPE'].dropna().unique())
            owner_types_str = ', '.join(owner_types)
            report_lines.append(f"OWNER TYPES: {owner_types_str}")
        else:
            report_lines.append("OWNER TYPE: Not available or no data")
        report_lines.append("-" * 50)

        # Total value range
        if 'TOTALVALUE' in df.columns and not df['TOTALVALUE'].dropna().empty:
            min_value = df['TOTALVALUE'].min()
            max_value = df['TOTALVALUE'].max()
            report_lines.append(f"TOTAL VALUE RANGE: ${min_value:,.2f} - ${max_value:,.2f}")
        else:
            report_lines.append("TOTALVALUE: Not available or no data")
        report_lines.append("=" * 50)

        report = "\n".join(report_lines)
        logger.debug("Summary report generated")

        return report

    def print_summary_report(self, df: pd.DataFrame) -> None:
        """
        Print summary report to console.

        Args:
            df: DataFrame to summarize
        """
        report = self.generate_summary_report(df)
        print(f"\n{report}")
        logger.info("Summary report printed to console")

    def get_processing_statistics(self, df: pd.DataFrame) -> dict:
        """
        Get detailed processing statistics.

        Args:
            df: DataFrame to analyze

        Returns:
            Dictionary of statistics
        """
        stats = {
            'total_records': len(df),
            'total_columns': len(df.columns),
            'null_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100),
        }

        # Add distress counter statistics if available
        if 'DISTRESSCOUNTER' in df.columns:
            stats['avg_distress_score'] = df['DISTRESSCOUNTER'].mean()
            stats['max_distress_score'] = df['DISTRESSCOUNTER'].max()
            stats['min_distress_score'] = df['DISTRESSCOUNTER'].min()

        # Add value statistics if available
        if 'TOTALVALUE' in df.columns:
            stats['avg_property_value'] = df['TOTALVALUE'].mean()
            stats['median_property_value'] = df['TOTALVALUE'].median()

        logger.debug(f"Processing statistics calculated: {stats}")

        return stats
