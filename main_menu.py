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
        self.customers_dir = Path("customers")
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
                input_dir = item / "input" / "raw_data"
                output_dir = item / "output"

                if input_dir.exists() or output_dir.exists():
                    customers.append(item.name)

        return sorted(customers)

    def select_customer(self):
        """Display customer selection menu and return selected customer."""
        customers = self.get_available_customers()

        if not customers:
            self.print_error("No customer folders found!")
            self.print_info("Please create a customer folder in the 'customers/' directory.")
            self.print_info("Required structure:")
            print("  customers/")
            print("    └── customer_name/")
            print("        ├── input/")
            print("        │   ├── raw_data/      # CSV files")
            print("        │   └── suppressed/    # Suppression files")
            print("        └── output/            # Generated files")
            return None

        self.print_header("SELECT CUSTOMER")

        print("Available customers:\n")
        for i, customer in enumerate(customers, 1):
            customer_path = self.customers_dir / customer
            input_files = list((customer_path / "input" / "raw_data").glob("*.csv")) if (customer_path / "input" / "raw_data").exists() else []
            print(f"  {Fore.CYAN}{i}.{Style.RESET_ALL} {customer}")
            if input_files:
                print(f"     └─ {len(input_files)} CSV file(s) in raw_data")
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
            (customer_path / "input" / "raw_data").mkdir(parents=True, exist_ok=True)
            (customer_path / "input" / "suppressed").mkdir(parents=True, exist_ok=True)
            (customer_path / "output").mkdir(parents=True, exist_ok=True)

            self.print_success(f"Created customer folder: {clean_name}")
            self.print_info(f"Location: {customer_path}")
            self.print_info("Please add CSV files to: input/raw_data/")

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
        raw_data_path = customer_path / "input" / "raw_data"
        suppressed_path = customer_path / "input" / "suppressed"
        output_path = customer_path / "output"

        print(f"{Fore.CYAN}Input Files:{Style.RESET_ALL}")
        if raw_data_path.exists():
            csv_files = list(raw_data_path.glob("*.csv"))
            print(f"\n  Raw Data ({raw_data_path}):")
            if csv_files:
                for csv_file in csv_files:
                    size_mb = csv_file.stat().st_size / (1024 * 1024)
                    print(f"    - {csv_file.name} ({size_mb:.2f} MB)")
            else:
                print(f"    {Fore.YELLOW}No CSV files found{Style.RESET_ALL}")

        if suppressed_path.exists():
            suppressed_files = list(suppressed_path.glob("*.csv"))
            print(f"\n  Suppressed Files ({suppressed_path}):")
            if suppressed_files:
                for file in suppressed_files:
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"    - {file.name} ({size_mb:.2f} MB)")
            else:
                print(f"    {Fore.YELLOW}No suppression files found{Style.RESET_ALL}")

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
        input_path = customer_path / "input" / "raw_data"
        output_path = customer_path / "output"

        # Check if input folder has CSV files
        csv_files = list(input_path.glob("*.csv")) if input_path.exists() else []

        if not csv_files:
            self.print_error(f"No CSV files found in {input_path}")
            self.print_info("Please add CSV files to the input/raw_data/ folder.")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        try:
            generator = DynamicTableGenerator(
                input_folder=str(input_path),
                output_folder=str(output_path),
                customer_name=customer_name
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
        self.print_info("Running main data processing pipeline...")
        self.print_warning("This feature will use the existing main.py workflow")
        self.print_info(f"Customer: {customer}")

        # Import and run the main pipeline
        try:
            import main
            # Note: You may need to modify main.py to accept customer parameter
            main.main()
        except Exception as e:
            self.print_error(f"Error running main pipeline: {e}")
            import traceback
            traceback.print_exc()

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")


if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
