#!/usr/bin/env python3
"""
ZIP File Extraction Utility
Extracts ZIP files from customer input folders.
"""
import os
import zipfile
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama for cross-platform color support
init(autoreset=True)


def get_customer_folders():
    """Get list of available customer folders."""
    customers_dir = Path("customers")

    if not customers_dir.exists():
        return []

    customers = []
    for item in customers_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.') and item.name != 'README.md':
            customers.append(item.name)

    return sorted(customers)


def extract_zips_from_folder(folder_path):
    """
    Extract all ZIP files from a specific folder.

    Args:
        folder_path: Path to folder containing ZIP files

    Returns:
        Number of ZIP files extracted
    """
    folder_path = Path(folder_path)

    if not folder_path.exists():
        print(f"{Fore.RED}✗ Folder does not exist: {folder_path}{Style.RESET_ALL}")
        return 0

    # Get all ZIP files in the folder
    zip_files = list(folder_path.glob("*.zip"))

    if not zip_files:
        print(f"{Fore.YELLOW}No ZIP files found in {folder_path}{Style.RESET_ALL}")
        return 0

    print(f"{Fore.CYAN}Found {len(zip_files)} ZIP file(s) to extract...{Style.RESET_ALL}\n")

    extracted_count = 0

    # Process each ZIP file
    for zip_path in zip_files:
        try:
            print(f"{Fore.BLUE}Extracting {zip_path.name}...{Style.RESET_ALL}")

            # Extract the ZIP file contents to the same folder
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(folder_path)

            # Delete the ZIP file after extraction
            zip_path.unlink()
            print(f"{Fore.GREEN}✓ {zip_path.name} extracted and removed{Style.RESET_ALL}")
            extracted_count += 1

        except Exception as e:
            print(f"{Fore.RED}✗ Error processing {zip_path.name}: {str(e)}{Style.RESET_ALL}")

    print(f"\n{Fore.GREEN}Extraction complete: {extracted_count} file(s) processed{Style.RESET_ALL}")
    return extracted_count


def main():
    """Main execution function."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 70}")
    print("  ZIP FILE EXTRACTION UTILITY".center(70))
    print(f"{'=' * 70}{Style.RESET_ALL}\n")

    # Get available customers
    customers = get_customer_folders()

    if not customers:
        print(f"{Fore.RED}✗ No customer folders found!{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Please create a customer folder in 'customers/' directory.{Style.RESET_ALL}")
        return

    # Display customer list
    print(f"{Fore.CYAN}Available customers:{Style.RESET_ALL}\n")
    for i, customer in enumerate(customers, 1):
        print(f"  {i}. {customer}")

    print()

    # Prompt for customer selection
    while True:
        try:
            choice = input(f"{Fore.GREEN}Select customer (number or Q to quit): {Style.RESET_ALL}").strip()

            if choice.upper() == 'Q':
                print(f"\n{Fore.YELLOW}Cancelled.{Style.RESET_ALL}")
                return

            idx = int(choice) - 1
            if 0 <= idx < len(customers):
                selected_customer = customers[idx]
                break
            else:
                print(f"{Fore.RED}Invalid selection. Please try again.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Please enter a valid number or Q to quit.{Style.RESET_ALL}")

    # Extract ZIPs from customer's input/raw_data folder
    customer_path = Path("customers") / selected_customer
    raw_data_path = customer_path / "input" / "raw_data"

    print(f"\n{Fore.CYAN}Extracting ZIP files for customer: {selected_customer}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}Folder: {raw_data_path}{Style.RESET_ALL}\n")

    if not raw_data_path.exists():
        print(f"{Fore.RED}✗ Input folder does not exist: {raw_data_path}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Creating folder...{Style.RESET_ALL}")
        raw_data_path.mkdir(parents=True, exist_ok=True)
        print(f"{Fore.GREEN}✓ Folder created{Style.RESET_ALL}")
        return

    extract_zips_from_folder(raw_data_path)


if __name__ == "__main__":
    main()
