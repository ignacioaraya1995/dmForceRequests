#!/usr/bin/env python3
"""
Real Estate Property Data Consolidation Tool
Main entry point for English version.

This tool consolidates property data from multiple CSV files, applies distress-based
filtering, and generates formatted Excel reports for real estate professionals.
"""

import time
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.config import get_default_config
from src.data_processing.processor import DataProcessor, DataValidator
from src.file_operations.file_handler import (
    FileReader, DuplicateManager, ZipExtractor
)
from src.file_operations.excel_formatter import ExcelFormatter, ReportGenerator
from src.ui.console_interface import ConsoleInterface, DataFilter, ProgressTracker


def main():
    """Main processing pipeline."""
    start_time = time.time()

    # Initialize configuration
    config = get_default_config(language='en', log_level='INFO')
    config.ensure_setup()

    # Initialize logger
    logger = get_logger(__name__, log_level=config.log_level)
    logger.info("=" * 60)
    logger.info("Real Estate Data Processing Tool - STARTED")
    logger.info("=" * 60)

    # Initialize components
    console = ConsoleInterface(config.language)
    progress = ProgressTracker()
    progress.set_total_steps(10)

    # Display welcome message
    console.print_header("Real Estate Data Consolidation Tool")
    console.print_info("Starting data consolidation and cleaning process...")

    try:
        # Step 1: Get client name
        client_name = console.get_client_name()
        console.print_success(f"Client selected: {client_name}")

        # Set client name in configuration to update folder paths
        config.paths.set_client_name(client_name)
        config.ensure_setup()  # Create client-specific directories

        console.print_info(f"📁 Input folder: {config.paths.input_path}")
        console.print_info(f"📁 Output folder: {config.paths.output_path}")

        progress.step_completed("Client name collected")

        # Step 2: Extract ZIP files if present
        logger.info("Checking for ZIP files to extract...")
        zip_extractor = ZipExtractor()
        extracted_count = zip_extractor.extract_zip_files(config.paths.input_path)
        if extracted_count > 0:
            console.print_success(f"Extracted {extracted_count} ZIP file(s)")
        progress.step_completed("ZIP extraction completed")

        # Step 3: Check if input folder exists and has files
        if not config.paths.input_path.exists():
            console.print_error(f"Input folder does not exist: {config.paths.input_path}")
            console.print_info(f"Please create the folder and add your CSV files there")
            logger.error(f"Input folder not found: {config.paths.input_path}")
            return

        folders = [config.paths.input_path]
        console.print_info(f"Processing folder: {config.paths.input_path}")
        progress.step_completed("Folder scanning completed")

        # Step 4: Read CSV files
        console.print_section("Reading CSV Files")
        file_reader = FileReader(config.processing)
        all_dataframes = []

        for folder in folders:
            logger.info(f"Processing folder: {folder.name}")
            console.print_info(f"Processing folder: {folder.name}")

            dfs = file_reader.read_csv_files_from_folder(folder)
            if dfs:
                all_dataframes.extend(dfs)
                console.print_success(f"Read {len(dfs)} CSV file(s) from {folder.name}")
            else:
                console.print_warning(f"No CSV files read from {folder.name}")

        if not all_dataframes:
            console.print_error("No data read from CSV files!")
            logger.error("No dataframes loaded")
            return

        progress.step_completed("CSV files read")

        # Step 5: Initialize data processor and consolidate
        console.print_section("Processing Data")
        processor = DataProcessor(config.columns, config.processing)
        validator = DataValidator()

        logger.info("Consolidating dataframes...")
        df = processor.consolidate_dataframes(all_dataframes)
        console.print_info(f"Consolidated {len(df):,} total rows")
        progress.step_completed("Data consolidated")

        # Step 6: Data cleaning and transformation
        logger.info("Starting data cleaning and transformation...")

        df = processor.select_relevant_columns(df)
        console.print_info(f"Selected {len(df.columns)} relevant columns")

        df = processor.clean_addresses(df)
        console.print_info(f"Removed rows with incomplete addresses: {len(df):,} rows remaining")

        df = processor.calculate_distress_counter(df)
        console.print_info("Calculated distress scores")

        df = processor.remove_duplicates(df)
        console.print_info(f"Removed duplicates: {len(df):,} rows remaining")

        df = processor.filter_top_by_distress(df)
        console.print_info(f"Filtered top {config.processing.percentage_to_retain:.0%}: {len(df):,} rows remaining")

        progress.step_completed("Data cleaning completed")

        # Step 7: Reorder and rename columns
        logger.info("Reordering and renaming columns...")
        df = processor.reorder_columns(df)
        df = processor.rename_columns(df)

        # Merge FIPS data
        df = processor.merge_fips_data(df, config.paths.fips_file_path)

        df = processor.uppercase_columns(df)
        progress.step_completed("Column formatting completed")

        # Step 8: Interactive filtering
        console.print_section("Interactive Filtering")
        data_filter = DataFilter()
        df = data_filter.apply_interactive_filters(df)
        progress.step_completed("Interactive filtering completed")

        # Step 9: Final cleanup
        console.print_section("Final Cleanup")
        df = processor.clean_ltv_values(df)
        df = processor.apply_title_case(df)
        console.print_info("Applied final formatting")
        progress.step_completed("Final cleanup completed")

        # Step 10: Remove duplicates from previous files (optional)
        console.print_section("Duplicate Removal from Previous Files")
        if console.confirm_action("Do you want to remove properties listed in previous files (from 'Dupes' folder)?"):
            dupe_manager = DuplicateManager()
            previous_addresses = dupe_manager.load_previous_addresses(config.paths.dupes_path)

            if previous_addresses:
                df, removed_count = processor.remove_previous_addresses(df, previous_addresses)
                console.print_success(f"Removed {removed_count:,} duplicate properties")
            else:
                console.print_warning("No previous addresses found to compare against")

        progress.step_completed("Duplicate removal completed")

        # Validate final data
        if not validator.validate_dataframe(df, "Final DataFrame"):
            console.print_error("Final data validation failed!")
            return

        # Step 11: Save to Excel
        console.print_section("Saving Results")
        excel_formatter = ExcelFormatter(config.excel, config.columns)
        output_file = excel_formatter.save_formatted_excel(
            df,
            config.paths.output_path,
            client_name
        )
        console.print_success(f"Saved Excel file: {output_file.name}")
        logger.info(f"Output file saved: {output_file}")

        # Step 12: Generate summary report
        console.print_section("Final Summary")
        report_generator = ReportGenerator()
        report_generator.print_summary_report(df)

        # Print completion
        elapsed_time = time.time() - start_time
        progress.print_summary(len(df), elapsed_time)

        console.print_success("Process completed successfully!")
        logger.info(f"Processing completed in {elapsed_time:.2f} seconds")
        logger.info("=" * 60)

    except KeyboardInterrupt:
        console.print_warning("\nProcess interrupted by user")
        logger.warning("Process interrupted by user")

    except Exception as e:
        console.print_error(f"An error occurred: {e}")
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
