#!/usr/bin/env python3
"""
Data Processing Main Menu
Interactive menu for customer data processing and analysis.
"""

import sys
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama for cross-platform color support
init(autoreset=True)


class MainMenu:
    """Main menu interface for data processing operations."""

    def __init__(self):
        self.customers_dir = Path("data")
        self.customers_dir.mkdir(exist_ok=True)

    def print_header(self, title):
        """Print a formatted header."""
        width = 70
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * width}")
        print(f"  {title.center(width - 4)}")
        print(f"{'=' * width}{Style.RESET_ALL}\n")

    def print_success(self, message):
        """Print a success message."""
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

    def print_error(self, message):
        """Print an error message."""
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

    def print_info(self, message):
        """Print an info message."""
        print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")

    def print_warning(self, message):
        """Print a warning message."""
        print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")

    def get_available_customers(self):
        """Get list of available customer folders."""
        customers = []

        if not self.customers_dir.exists():
            return customers

        for item in self.customers_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name != 'README.md':
                # Check if it has the required structure
                input_dir = item / "input"
                suppress_dir = item / "suppress"
                output_dir = item / "output"

                if input_dir.exists() or suppress_dir.exists() or output_dir.exists():
                    customers.append(item.name)

        return sorted(customers)

    def select_customer(self):
        """Display customer selection menu and return selected customer."""
        customers = self.get_available_customers()

        if not customers:
            self.print_error("No customer folders found!")
            self.print_info("Please create a customer folder in the 'data/' directory.")
            self.print_info("Required structure:")
            print("  data/")
            print("    └── customer_name/")
            print("        ├── input/      # CSV data files")
            print("        ├── suppress/   # Suppression files (address + zip)")
            print("        └── output/     # Generated reports")
            return None

        self.print_header("SELECT CUSTOMER")

        print("Available customers:\n")
        for i, customer in enumerate(customers, 1):
            customer_path = self.customers_dir / customer
            input_files = list((customer_path / "input").glob("*.csv")) if (customer_path / "input").exists() else []
            print(f"  {Fore.CYAN}{i}.{Style.RESET_ALL} {customer}")
            if input_files:
                print(f"     └─ {len(input_files)} CSV file(s) in input/")
            else:
                print(f"     └─ {Fore.YELLOW}No CSV files found{Style.RESET_ALL}")

        print(f"\n  {Fore.CYAN}0.{Style.RESET_ALL} Create new customer")
        print(f"  {Fore.CYAN}Q.{Style.RESET_ALL} Quit\n")

        while True:
            choice = input(f"{Fore.GREEN}Select customer (number or Q to quit): {Style.RESET_ALL}").strip()

            if choice.upper() == 'Q':
                return None

            if choice == '0':
                return self.create_new_customer()

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(customers):
                    selected = customers[idx]
                    self.print_success(f"Selected customer: {selected}")
                    return selected
                else:
                    self.print_error("Invalid selection. Please try again.")
            except ValueError:
                self.print_error("Please enter a valid number or Q to quit.")

    def create_new_customer(self):
        """Create a new customer folder structure."""
        self.print_header("CREATE NEW CUSTOMER")

        customer_name = input(f"{Fore.GREEN}Enter customer name: {Style.RESET_ALL}").strip()

        if not customer_name:
            self.print_error("Customer name cannot be empty.")
            return None

        # Clean customer name (remove special characters)
        clean_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in customer_name)

        customer_path = self.customers_dir / clean_name

        if customer_path.exists():
            self.print_error(f"Customer '{clean_name}' already exists!")
            return clean_name

        # Create folder structure
        try:
            (customer_path / "input").mkdir(parents=True, exist_ok=True)
            (customer_path / "suppress").mkdir(parents=True, exist_ok=True)
            (customer_path / "output").mkdir(parents=True, exist_ok=True)

            self.print_success(f"Created customer folder: {clean_name}")
            self.print_info(f"Location: {customer_path}")
            self.print_info("Folder structure created:")
            self.print_info("  - input/    : Place CSV data files here")
            self.print_info("  - suppress/ : Place suppression files here (address + zip required)")
            self.print_info("  - output/   : Generated reports will be saved here")

            return clean_name
        except Exception as e:
            self.print_error(f"Error creating customer folder: {e}")
            return None

    def show_main_menu(self):
        """Display main menu and return user choice."""
        self.print_header("DATA PROCESSING MAIN MENU")

        print("What would you like to do?\n")
        print(f"  {Fore.CYAN}1.{Style.RESET_ALL} Generate Dynamic Summary Table (Pivot Analysis)")
        print(f"  {Fore.CYAN}2.{Style.RESET_ALL} Process Real Estate Data (Main Pipeline)")
        print(f"  {Fore.CYAN}3.{Style.RESET_ALL} View Customer Information")
        print(f"  {Fore.CYAN}Q.{Style.RESET_ALL} Quit\n")

        while True:
            choice = input(f"{Fore.GREEN}Select operation (1-3 or Q): {Style.RESET_ALL}").strip()

            if choice.upper() == 'Q':
                return None

            if choice in ['1', '2', '3']:
                return choice

            self.print_error("Invalid selection. Please enter 1, 2, 3, or Q.")

    def view_customer_info(self, customer_name):
        """Display information about a customer's data."""
        customer_path = self.customers_dir / customer_name

        self.print_header(f"CUSTOMER INFORMATION: {customer_name}")

        # Check input files
        input_path = customer_path / "input"
        suppress_path = customer_path / "suppress"
        output_path = customer_path / "output"

        print(f"{Fore.CYAN}Input Files:{Style.RESET_ALL}")
        if input_path.exists():
            csv_files = list(input_path.glob("*.csv"))

            print(f"\n  Data Files ({input_path}):")
            if csv_files:
                for csv_file in csv_files:
                    size_mb = csv_file.stat().st_size / (1024 * 1024)
                    print(f"    - {csv_file.name} ({size_mb:.2f} MB)")
            else:
                print(f"    {Fore.YELLOW}No CSV files found{Style.RESET_ALL}")
        else:
            print(f"\n  {Fore.YELLOW}Input folder does not exist{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}Suppression Files:{Style.RESET_ALL}")
        if suppress_path.exists():
            suppress_files = list(suppress_path.glob("*"))
            suppress_files = [f for f in suppress_files if f.is_file()]

            if suppress_files:
                print(f"\n  Suppress Files ({suppress_path}):")
                for supp_file in suppress_files:
                    size_mb = supp_file.stat().st_size / (1024 * 1024)
                    print(f"    - {supp_file.name} ({size_mb:.2f} MB)")
            else:
                print(f"  {Fore.YELLOW}No suppression files found{Style.RESET_ALL}")
        else:
            print(f"  {Fore.YELLOW}Suppress folder does not exist{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}Output Files:{Style.RESET_ALL}")
        if output_path.exists():
            output_files = list(output_path.glob("*"))
            if output_files:
                print(f"\n  Output ({output_path}):")
                for file in sorted(output_files, key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
                    if file.is_file():
                        size_mb = file.stat().st_size / (1024 * 1024)
                        print(f"    - {file.name} ({size_mb:.2f} MB)")
            else:
                print(f"  {Fore.YELLOW}No output files yet{Style.RESET_ALL}")
        else:
            print(f"  {Fore.YELLOW}Output folder does not exist{Style.RESET_ALL}")

        print()

    def run(self):
        """Run the main menu loop."""
        self.print_header("DATA PROCESSING SYSTEM")

        print(f"{Fore.CYAN}Welcome to the Data Processing System{Style.RESET_ALL}\n")

        while True:
            # Show main menu
            operation = self.show_main_menu()

            if operation is None:
                print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}\n")
                sys.exit(0)

            # Select customer
            customer = self.select_customer()

            if customer is None:
                continue

            customer_path = self.customers_dir / customer

            # Execute selected operation
            if operation == '1':
                # Generate Dynamic Summary Table
                self.print_header(f"GENERATE DYNAMIC SUMMARY TABLE: {customer}")
                self.run_dynamic_table_generator(customer_path)

            elif operation == '2':
                # Run main data processing pipeline
                self.print_header(f"PROCESS REAL ESTATE DATA: {customer}")
                self.run_main_pipeline(customer)

            elif operation == '3':
                # View customer information
                self.view_customer_info(customer)
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

            # Ask if user wants to continue
            print()
            continue_choice = input(f"{Fore.GREEN}Process another operation? (Y/n): {Style.RESET_ALL}").strip().lower()
            if continue_choice in ['n', 'no']:
                print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}\n")
                break

    def run_dynamic_table_generator(self, customer_path):
        """Run the dynamic table generator for a customer."""
        from dynamic_table_generator import DynamicTableGenerator

        customer_name = customer_path.name
        input_path = customer_path / "input"
        output_path = customer_path / "output"

        # Check if input folder has CSV files
        csv_files = list(input_path.glob("*.csv")) if input_path.exists() else []

        if not csv_files:
            self.print_error(f"No CSV files found in {input_path}")
            self.print_info("Please add CSV files to the input/ folder.")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        try:
            suppress_path = customer_path / "suppress"
            generator = DynamicTableGenerator(
                input_folder=str(input_path),
                output_folder=str(output_path),
                customer_name=customer_name,
                suppress_folder=str(suppress_path) if suppress_path.exists() else None
            )
            generator.process_csv_files()

            self.print_success("Dynamic table generation completed!")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

        except Exception as e:
            self.print_error(f"Error generating dynamic table: {e}")
            import traceback
            traceback.print_exc()
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def run_main_pipeline(self, customer):
        """Run the main data processing pipeline."""
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

        self.print_info("Running main data processing pipeline...")
        self.print_info(f"Customer: {customer}")

        start_time = time.time()

        # Initialize configuration
        config = get_default_config(language='en', log_level='INFO')
        config.paths.set_client_name(customer)
        config.ensure_setup()

        # Initialize logger
        logger = get_logger(__name__, log_level=config.log_level)
        logger.info("=" * 60)
        logger.info(f"Real Estate Data Processing Tool - STARTED for {customer}")
        logger.info("=" * 60)

        # Initialize components
        console = ConsoleInterface(config.language)
        progress = ProgressTracker()
        progress.set_total_steps(11)  # Increased from 10 to account for suppression step

        try:
            self.print_success(f"Client selected: {customer}")
            self.print_info(f"📁 Input folder: {config.paths.input_path}")
            self.print_info(f"📁 Output folder: {config.paths.output_path}")

            progress.step_completed("Client name collected")

            # Step 2: Extract ZIP files if present
            logger.info("Checking for ZIP files to extract...")
            zip_extractor = ZipExtractor()
            extracted_count = zip_extractor.extract_zip_files(config.paths.input_path)
            if extracted_count > 0:
                self.print_success(f"Extracted {extracted_count} ZIP file(s)")
            progress.step_completed("ZIP extraction completed")

            # Step 3: Check if input folder exists and has files
            if not config.paths.input_path.exists():
                self.print_error(f"Input folder does not exist: {config.paths.input_path}")
                self.print_info(f"Please create the folder and add your CSV files there")
                logger.error(f"Input folder not found: {config.paths.input_path}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            folders = [config.paths.input_path]
            self.print_info(f"Processing folder: {config.paths.input_path}")
            progress.step_completed("Folder scanning completed")

            # Step 4: Read CSV files
            console.print_section("Reading CSV Files")
            file_reader = FileReader(config.processing)
            all_dataframes = []

            for folder in folders:
                logger.info(f"Processing folder: {folder.name}")
                self.print_info(f"Processing folder: {folder.name}")

                dfs = file_reader.read_csv_files_from_folder(folder)
                if dfs:
                    all_dataframes.extend(dfs)
                    self.print_success(f"Read {len(dfs)} CSV file(s) from {folder.name}")
                else:
                    self.print_warning(f"No CSV files read from {folder.name}")

            if not all_dataframes:
                self.print_error("No data read from CSV files!")
                logger.error("No dataframes loaded")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            progress.step_completed("CSV files read")

            # Step 5: Initialize data processor and consolidate
            console.print_section("Processing Data")
            processor = DataProcessor(config.columns, config.processing)
            validator = DataValidator()

            logger.info("Consolidating dataframes...")
            df = processor.consolidate_dataframes(all_dataframes)
            self.print_info(f"Consolidated {len(df):,} total rows")
            progress.step_completed("Data consolidated")

            # Step 5.5: Apply suppression before any processing
            console.print_section("Applying Suppression")
            dupe_manager = DuplicateManager()
            suppression_records = dupe_manager.load_suppression_records(config.paths.suppress_path)

            if suppression_records:
                self.print_info(f"Loaded {len(suppression_records):,} suppression records")
                df, suppressed_count = processor.apply_suppression(df, suppression_records)
                self.print_success(f"Suppressed {suppressed_count:,} properties")
            else:
                self.print_info("No suppression records found - skipping suppression")

            progress.step_completed("Suppression applied")

            # Step 6: Data cleaning and transformation
            logger.info("Starting data cleaning and transformation...")

            df = processor.select_relevant_columns(df)
            self.print_info(f"Selected {len(df.columns)} relevant columns")

            df = processor.clean_addresses(df)
            self.print_info(f"Removed rows with incomplete addresses: {len(df):,} rows remaining")

            df = processor.calculate_distress_counter(df)
            self.print_info("Calculated distress scores")

            df = processor.remove_duplicates(df)
            self.print_info(f"Removed duplicates: {len(df):,} rows remaining")

            df = processor.filter_top_by_distress(df)
            self.print_info(f"Filtered top {config.processing.percentage_to_retain:.0%}: {len(df):,} rows remaining")

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
            self.print_info("Applied final formatting")
            progress.step_completed("Final cleanup completed")

            # Step 10: Remove duplicates from previous files (optional)
            console.print_section("Duplicate Removal from Previous Files")
            if console.confirm_action("Do you want to remove properties listed in previous files (from 'Dupes' folder)?"):
                dupe_manager = DuplicateManager()
                previous_addresses = dupe_manager.load_previous_addresses(config.paths.dupes_path)

                if previous_addresses:
                    df, removed_count = processor.remove_previous_addresses(df, previous_addresses)
                    self.print_success(f"Removed {removed_count:,} duplicate properties")
                else:
                    self.print_warning("No previous addresses found to compare against")

            progress.step_completed("Duplicate removal completed")

            # Validate final data
            if not validator.validate_dataframe(df, "Final DataFrame"):
                self.print_error("Final data validation failed!")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            # Step 11: Save to Excel
            console.print_section("Saving Results")
            excel_formatter = ExcelFormatter(config.excel, config.columns)
            output_file = excel_formatter.save_formatted_excel(
                df,
                config.paths.output_path,
                customer
            )
            self.print_success(f"Saved Excel file: {output_file.name}")
            logger.info(f"Output file saved: {output_file}")

            # Step 12: Generate summary report
            console.print_section("Final Summary")
            report_generator = ReportGenerator()
            report_generator.print_summary_report(df)

            # Print completion
            elapsed_time = time.time() - start_time
            progress.print_summary(len(df), elapsed_time)

            self.print_success("Process completed successfully!")
            logger.info(f"Processing completed in {elapsed_time:.2f} seconds")
            logger.info("=" * 60)

        except KeyboardInterrupt:
            self.print_warning("\nProcess interrupted by user")
            logger.warning("Process interrupted by user")

        except Exception as e:
            self.print_error(f"An error occurred: {e}")
            logger.error(f"Fatal error: {e}", exc_info=True)
            import traceback
            traceback.print_exc()

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")


if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
