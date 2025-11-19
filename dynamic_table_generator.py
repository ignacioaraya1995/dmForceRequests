"""
Dynamic Table Generator for CSV Data Analysis
This script processes CSV files and generates a dynamic table with record counts
based on various dimensions and value ranges.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys
from collections import defaultdict
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')


class DynamicTableGenerator:
    """Generator for creating dynamic tables from CSV data with specified ranges."""

    def __init__(self, input_folder='Files', output_folder='output', customer_name=None, suppress_folder=None):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True)
        self.customer_name = customer_name
        self.suppress_folder = Path(suppress_folder) if suppress_folder else None

        # Suppression records will be loaded in process_csv_files
        self.suppression_records = set()

        # Define all range buckets
        self.define_ranges()

    def define_ranges(self):
        """Define all range buckets for numeric columns."""

        # Total Value Ranges (in dollars, values in thousands)
        # Note: Upper bounds are exclusive except for special cases
        self.total_value_ranges = [
            ('Unknowns', 'Unknowns', None, None),
            ('$0', '$0', 0, 0),  # Exact match
            ('$1-$25', '$1-$25', 0.001, 25),
            ('$25-$50', '$25-$50', 25, 50),
            ('$50-$100', '$50-$100', 50, 100),
            ('$100-$150', '$100-$150', 100, 150),
            ('$150-$200', '$150-$200', 150, 200),
            ('$200-$250', '$200-$250', 200, 250),
            ('$250-$300', '$250-$300', 250, 300),
            ('$300-$350', '$300-$350', 300, 350),
            ('$350-$400', '$350-$400', 350, 400),
            ('$400-$450', '$400-$450', 400, 450),
            ('$450-$500', '$450-$500', 450, 500),
            ('$500-$650', '$500-$650', 500, 650),
            ('$650-$750', '$650-$750', 650, 750),
            ('$750-$1,000', '$750-$1,000', 750, 1000),
            ('$1,000-$1,500', '$1,000-$1,500', 1000, 1500),
            ('$1,500-$2,000', '$1,500-$2,000', 1500, 2000),
            ('$2,000+', '$2,000+', 2000, float('inf'))
        ]

        # SumLivingAreaSqFt Ranges
        self.living_area_ranges = [
            ('Unknowns', 'Unknowns', None, None),
            ('0', '0', 0, 0),
            ('1-199', '1-199', 1, 199),
            ('200-799', '200-799', 200, 799),
            ('800-1,499', '800-1,499', 800, 1499),
            ('1,500-2,499', '1,500-2,499', 1500, 2499),
            ('2,500-3,499', '2,500-3,499', 2500, 3499),
            ('3,500-4,499', '3,500-4,499', 3500, 4499),
            ('4,500+', '4,500+', 4500, float('inf'))
        ]

        # Lot Size Ranges (in SqFt)
        self.lot_size_ranges = [
            ('Unknowns', 'Unknowns', None, None),
            ('0', '0', 0, 0),
            ('1-100', '1-100', 1, 100),
            ('101-999', '101-999', 101, 999),
            ('1,000-3,599', '1,000-3,599', 1000, 3599),
            ('3,600-14,999', '3,600-14,999', 3600, 14999),
            ('15,000-29,999', '15,000-29,999', 15000, 29999),
            ('30,000-44,999', '30,000-44,999', 30000, 44999),
            ('45,000+', '45,000+', 45000, float('inf'))
        ]

        # Build Date Ranges (years ago from current date)
        # Note: Upper bounds are exclusive (e.g., "0-1 years" means 0 <= years < 2)
        self.build_date_ranges = [
            ('Unknown', 'Unknown', None, None),
            ('0-1 years', '0-1 years', 0, 2),
            ('2-4 years', '2-4 years', 2, 5),
            ('5-7 years', '5-7 years', 5, 8),
            ('8-9 years', '8-9 years', 8, 10),
            ('10-14 years', '10-14 years', 10, 15),
            ('15-19 years', '15-19 years', 15, 20),
            ('20-24 years', '20-24 years', 20, 25),
            ('25-29 years', '25-29 years', 25, 30),
            ('30-39 years', '30-39 years', 30, 40),
            ('40-49 years', '40-49 years', 40, 50),
            ('50-74 years', '50-74 years', 50, 75),
            ('75-99 years', '75-99 years', 75, 100),
            ('100+ years', '100+ years', 100, float('inf'))
        ]

        # LTV Ranges (Loan-to-Value ratio)
        self.ltv_ranges = [
            ('Unknown', 'Unknown', None, None),
            ('0-69', '0-69', 0, 69),
            ('70-84', '70-84', 70, 84),
            ('85-99', '85-99', 85, 99),
            ('100-998', '100-998', 100, 998),
            ('999+', '999+', 999, float('inf'))
        ]

        # Sale Date Ranges (years ago from current date)
        # Note: Upper bounds are exclusive (e.g., "0-1 years" means 0 <= years < 2)
        self.sale_date_ranges = [
            ('Unknown', 'Unknown', None, None),
            ('0-1 years', '0-1 years', 0, 2),
            ('2-4 years', '2-4 years', 2, 5),
            ('5-7 years', '5-7 years', 5, 8),
            ('8-9 years', '8-9 years', 8, 10),
            ('10-14 years', '10-14 years', 10, 15),
            ('15-19 years', '15-19 years', 15, 20),
            ('20-24 years', '20-24 years', 20, 25),
            ('25-29 years', '25-29 years', 25, 30),
            ('30-39 years', '30-39 years', 30, 40),
            ('40-49 years', '40-49 years', 40, 50),
            ('50-74 years', '50-74 years', 50, 75),
            ('75-99 years', '75-99 years', 75, 100),
            ('100+ years', '100+ years', 100, float('inf'))
        ]

    def categorize_value(self, value, ranges, value_is_dollar=False):
        """Categorize a value into one of the defined ranges."""
        # Handle unknown/null/empty values
        if pd.isna(value) or value == '' or value == 'Unknown' or value == 'unknown':
            return ranges[0][1]  # Return 'Unknowns' or 'Unknown'

        try:
            # Convert to float
            if value_is_dollar:
                # Handle dollar values (in thousands typically)
                num_value = float(value) / 1000  # Convert to thousands
            else:
                num_value = float(value)

            # Find the appropriate range
            for range_label, range_display, min_val, max_val in ranges:
                if min_val is None:  # This is the Unknown category
                    continue
                # Special case: exact match for ranges where min_val == max_val (like $0)
                if min_val == max_val and num_value == min_val:
                    return range_display
                # Use < for upper bound (ranges are defined with exclusive upper bounds)
                if min_val <= num_value < max_val:
                    return range_display
                if min_val <= num_value and max_val == float('inf'):
                    return range_display

            # If no range found, return the last range (typically the "+" range)
            return ranges[-1][1]

        except (ValueError, TypeError):
            return ranges[0][1]  # Return 'Unknowns' or 'Unknown' if conversion fails

    def calculate_years_ago(self, date_value):
        """Calculate how many years ago from current date."""
        if pd.isna(date_value) or date_value == '' or date_value == 'Unknown':
            return None

        try:
            # Try to parse the date
            if isinstance(date_value, str):
                # Handle various date formats
                if '-' in date_value or '/' in date_value:
                    date_obj = pd.to_datetime(date_value, errors='coerce')
                    if pd.isna(date_obj):
                        return None
                else:
                    # Assume it's a year
                    try:
                        year = int(date_value)
                        if year < 1800 or year > 2100:
                            return None
                        date_obj = pd.to_datetime(f'{year}-01-01')
                    except ValueError:
                        return None
            elif isinstance(date_value, (int, float)):
                # Handle numeric year values
                year = int(date_value)
                if year < 1800 or year > 2100:
                    return None
                date_obj = pd.to_datetime(f'{year}-01-01')
            else:
                date_obj = pd.to_datetime(date_value, errors='coerce')
                if pd.isna(date_obj):
                    return None

            # Calculate years ago
            current_date = datetime.now()
            years_ago = (current_date - date_obj).days / 365.25
            return years_ago

        except Exception as e:
            # Log the error for debugging
            # print(f"Warning: Could not parse date '{date_value}': {e}")
            return None

    def categorize_date(self, date_value, ranges):
        """Categorize a date value into years-ago ranges."""
        years_ago = self.calculate_years_ago(date_value)

        if years_ago is None:
            return ranges[0][1]  # Return 'Unknown'

        # Find the appropriate range
        for range_label, range_display, min_val, max_val in ranges:
            if min_val is None:  # This is the Unknown category
                continue
            # Use < for upper bound (ranges are defined with exclusive upper bounds)
            if min_val <= years_ago < max_val:
                return range_display
            if min_val <= years_ago and max_val == float('inf'):
                return range_display

        # If no range found, return the last range
        return ranges[-1][1]

    def load_suppression_records(self):
        """Load suppression records from the suppress folder."""
        if not self.suppress_folder or not self.suppress_folder.exists():
            print("No suppression folder specified or folder does not exist - skipping suppression")
            return set()

        from glob import glob

        # Find CSV and Excel files
        csv_files = glob(str(self.suppress_folder / "*.csv"))
        xlsx_files = glob(str(self.suppress_folder / "*.xlsx"))
        all_files = csv_files + xlsx_files

        if not all_files:
            print(f"No suppression files found in: {self.suppress_folder}")
            return set()

        print(f"\n{'=' * 80}")
        print(f"LOADING SUPPRESSION RECORDS")
        print(f"{'=' * 80}")
        print(f"Found {len(all_files)} suppression file(s)")

        suppression_records = set()

        for file_path in all_files:
            file_path = Path(file_path)
            print(f"  - Loading: {file_path.name}")

            try:
                # Read file based on extension
                if file_path.suffix.lower() == '.csv':
                    df = pd.read_csv(file_path, low_memory=False)
                elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                    df = pd.read_excel(file_path)
                else:
                    print(f"    ⚠ Unsupported file type: {file_path.suffix}")
                    continue

                # Look for address and zip columns
                property_addr_cols = [
                    'PROPERTY ADDRESS', 'PropertyAddress', 'Property_Address',
                    'SitusFullStreetAddress', 'Situs_Full_Street_Address'
                ]
                mailing_addr_cols = [
                    'MAILING ADDRESS', 'MailingAddress', 'Mailing_Address',
                    'MailingFullStreetAddress', 'Mailing_Full_Street_Address'
                ]
                zip_cols = [
                    'PROPERTY ZIP', 'PropertyZIP', 'SitusZIP5', 'SitusZIP',
                    'MAILING ZIP', 'MailingZIP', 'MailingZIP5',
                    'ZIP', 'Zip', 'ZipCode'
                ]

                # Find which columns exist
                property_col = next((col for col in property_addr_cols if col in df.columns), None)
                mailing_col = next((col for col in mailing_addr_cols if col in df.columns), None)
                zip_col = next((col for col in zip_cols if col in df.columns), None)

                if not property_col and not mailing_col:
                    print(f"    ⚠ No address columns found in {file_path.name}")
                    continue

                # Extract records from property address - VECTORIZED
                if property_col:
                    prop_addr_clean = df[property_col].fillna('').astype(str).str.strip().str.lower()
                    prop_zip_clean = df[zip_col].fillna('').astype(str).str.strip() if zip_col else pd.Series([''] * len(df))

                    # Filter out empty addresses
                    valid_mask = prop_addr_clean != ''
                    valid_addrs = prop_addr_clean[valid_mask]
                    valid_zips = prop_zip_clean[valid_mask]

                    # Create tuples and add to set
                    prop_records = set(zip(valid_addrs, valid_zips))
                    suppression_records.update(prop_records)

                # Extract records from mailing address - VECTORIZED
                if mailing_col:
                    mail_addr_clean = df[mailing_col].fillna('').astype(str).str.strip().str.lower()
                    mail_zip_clean = df[zip_col].fillna('').astype(str).str.strip() if zip_col else pd.Series([''] * len(df))

                    # Filter out empty addresses
                    valid_mask = mail_addr_clean != ''
                    valid_addrs = mail_addr_clean[valid_mask]
                    valid_zips = mail_zip_clean[valid_mask]

                    # Create tuples and add to set
                    mail_records = set(zip(valid_addrs, valid_zips))
                    suppression_records.update(mail_records)

                print(f"    ✓ Loaded {len(suppression_records):,} total suppression records so far")

            except Exception as e:
                print(f"    ✗ Error reading {file_path.name}: {e}")
                continue

        print(f"\n✓ Total suppression records loaded: {len(suppression_records):,}")
        print(f"{'=' * 80}\n")

        return suppression_records

    def is_suppressed(self, row):
        """Check if a row should be suppressed based on loaded suppression records."""
        if not self.suppression_records:
            return False

        # Check property address
        situs_addr = row.get('SitusFullStreetAddress')
        situs_zip = row.get('SitusZIP5')
        if pd.notna(situs_addr) and pd.notna(situs_zip):
            clean_addr = str(situs_addr).strip().lower()
            clean_zip = str(situs_zip).strip()
            if (clean_addr, clean_zip) in self.suppression_records:
                return True

        # Check mailing address
        mailing_addr = row.get('MailingFullStreetAddress')
        mailing_zip = row.get('MailingZIP5')
        if pd.notna(mailing_addr) and pd.notna(mailing_zip):
            clean_addr = str(mailing_addr).strip().lower()
            clean_zip = str(mailing_zip).strip()
            if (clean_addr, clean_zip) in self.suppression_records:
                return True

        return False

    def filter_suppressed_vectorized(self, df):
        """
        Filter out suppressed rows using vectorized operations.
        Returns tuple of (filtered_df, suppressed_count).
        """
        if not self.suppression_records:
            return df, 0

        initial_rows = len(df)
        keep_mask = pd.Series([True] * len(df), index=df.index)

        # Check property address + zip combinations - VECTORIZED
        if 'SitusFullStreetAddress' in df.columns and 'SitusZIP5' in df.columns:
            prop_addr_clean = df['SitusFullStreetAddress'].fillna('').astype(str).str.strip().str.lower()
            prop_zip_clean = df['SitusZIP5'].fillna('').astype(str).str.strip()

            # Create tuples for comparison
            prop_tuples = list(zip(prop_addr_clean, prop_zip_clean))

            # Check membership in suppression set
            suppress_mask = [tuple_val in self.suppression_records for tuple_val in prop_tuples]

            # Update keep mask
            keep_mask = keep_mask & ~pd.Series(suppress_mask, index=df.index)

        # Check mailing address + zip combinations - VECTORIZED
        if 'MailingFullStreetAddress' in df.columns and 'MailingZIP5' in df.columns:
            mail_addr_clean = df['MailingFullStreetAddress'].fillna('').astype(str).str.strip().str.lower()
            mail_zip_clean = df['MailingZIP5'].fillna('').astype(str).str.strip()

            # Create tuples for comparison
            mail_tuples = list(zip(mail_addr_clean, mail_zip_clean))

            # Check membership in suppression set
            suppress_mask = [tuple_val in self.suppression_records for tuple_val in mail_tuples]

            # Update keep mask
            keep_mask = keep_mask & ~pd.Series(suppress_mask, index=df.index)

        df_filtered = df[keep_mask].copy()
        suppressed_count = initial_rows - len(df_filtered)

        return df_filtered, suppressed_count

    def process_csv_files(self):
        """Process all CSV files and generate the dynamic table."""
        print("=" * 80)
        print("DYNAMIC TABLE GENERATOR")
        print("=" * 80)
        print(f"\nInput Folder: {self.input_folder}")
        print(f"Output Folder: {self.output_folder}")
        if self.suppress_folder:
            print(f"Suppress Folder: {self.suppress_folder}")
        print()

        # Load suppression records BEFORE processing
        self.suppression_records = self.load_suppression_records()

        # Find all CSV files
        csv_files = list(self.input_folder.glob('*.csv'))
        print(f"Found {len(csv_files)} CSV file(s) to process:\n")
        for csv_file in csv_files:
            file_size_mb = csv_file.stat().st_size / (1024 * 1024)
            print(f"  - {csv_file.name} ({file_size_mb:.2f} MB)")
        print()

        if not csv_files:
            print("ERROR: No CSV files found in the input folder!")
            return

        # Initialize data aggregator
        aggregated_data = defaultdict(int)
        total_rows_processed = 0
        total_rows_suppressed = 0

        # Statistics tracking
        date_stats = {
            'buildDate_valid': 0,
            'buildDate_invalid': 0,
            'saleDate_valid': 0,
            'saleDate_invalid': 0
        }

        # Process each CSV file
        for csv_file in csv_files:
            print(f"\n{'=' * 80}")
            print(f"Processing: {csv_file.name}")
            print(f"{'=' * 80}")

            try:
                # Read CSV with progress
                print("Loading CSV file...")
                df = pd.read_csv(csv_file, low_memory=False)
                print(f"✓ Loaded {len(df):,} rows")

                # Apply suppression filter BEFORE processing rows - VECTORIZED
                if self.suppression_records:
                    print("Applying suppression filter (vectorized)...")
                    df, file_suppressed = self.filter_suppressed_vectorized(df)
                    total_rows_suppressed += file_suppressed
                    print(f"✓ Suppressed {file_suppressed:,} rows, {len(df):,} rows remaining")

                # Process each row with progress bar
                print("\nProcessing rows...")
                for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing", unit="rows"):

                    # Extract dimension values
                    fips = str(row.get('FIPS', 'Unknown'))
                    situs_city = str(row.get('SitusCity', 'Unknown'))
                    situs_zip = str(row.get('SitusZIP5', 'Unknown'))
                    owner_type = str(row.get('Owner_Type', 'Unknown'))
                    use_type = str(row.get('Use_Type', 'Unknown'))

                    # Categorize numeric values
                    total_value_range = self.categorize_value(
                        row.get('totalValue'),
                        self.total_value_ranges,
                        value_is_dollar=True
                    )

                    ltv_range = self.categorize_value(
                        row.get('LTV'),
                        self.ltv_ranges
                    )

                    lot_size_range = self.categorize_value(
                        row.get('LotSizeSqFt'),
                        self.lot_size_ranges
                    )

                    living_area_range = self.categorize_value(
                        row.get('SumLivingAreaSqFt'),
                        self.living_area_ranges
                    )

                    # Categorize dates and track statistics
                    build_date_value = row.get('buildDate')
                    build_date_range = self.categorize_date(
                        build_date_value,
                        self.build_date_ranges
                    )
                    if build_date_range != 'Unknown':
                        date_stats['buildDate_valid'] += 1
                    else:
                        date_stats['buildDate_invalid'] += 1

                    sale_date_value = row.get('saleDate')
                    sale_date_range = self.categorize_date(
                        sale_date_value,
                        self.sale_date_ranges
                    )
                    if sale_date_range != 'Unknown':
                        date_stats['saleDate_valid'] += 1
                    else:
                        date_stats['saleDate_invalid'] += 1

                    # Create a key for aggregation
                    key = (
                        fips,
                        situs_city,
                        situs_zip,
                        owner_type,
                        use_type,
                        sale_date_range,
                        build_date_range,
                        total_value_range,
                        ltv_range,
                        lot_size_range,
                        living_area_range
                    )

                    # Increment count
                    aggregated_data[key] += 1
                    total_rows_processed += 1

                print(f"✓ Processed {len(df):,} rows from {csv_file.name}")

            except Exception as e:
                print(f"✗ ERROR processing {csv_file.name}: {str(e)}")
                continue

        print(f"\n{'=' * 80}")
        print(f"PROCESSING COMPLETE")
        print(f"{'=' * 80}")
        print(f"Total rows processed: {total_rows_processed:,}")
        print(f"Total rows suppressed: {total_rows_suppressed:,}")
        print(f"Unique combinations: {len(aggregated_data):,}")

        # Print date statistics
        print(f"\n{'=' * 80}")
        print("DATE PROCESSING STATISTICS")
        print(f"{'=' * 80}")
        print(f"Build Dates:")
        print(f"  - Valid (parsed): {date_stats['buildDate_valid']:,} ({100 * date_stats['buildDate_valid'] / max(1, total_rows_processed):.1f}%)")
        print(f"  - Invalid/Unknown: {date_stats['buildDate_invalid']:,} ({100 * date_stats['buildDate_invalid'] / max(1, total_rows_processed):.1f}%)")
        print(f"Sale Dates:")
        print(f"  - Valid (parsed): {date_stats['saleDate_valid']:,} ({100 * date_stats['saleDate_valid'] / max(1, total_rows_processed):.1f}%)")
        print(f"  - Invalid/Unknown: {date_stats['saleDate_invalid']:,} ({100 * date_stats['saleDate_invalid'] / max(1, total_rows_processed):.1f}%)")
        print()

        # Convert to DataFrame
        print("Creating output table...")
        output_data = []
        for key, count in aggregated_data.items():
            output_data.append({
                'FIPS': key[0],
                'SitusCity': key[1],
                'SitusZIP5': key[2],
                'Owner_Type': key[3],
                'Use_Type': key[4],
                'SaleDate_Range': key[5],
                'BuildDate_Range': key[6],
                'TotalValue_Range': key[7],
                'LTV_Range': key[8],
                'LotSizeSqFt_Range': key[9],
                'SumLivingAreaSqFt_Range': key[10],
                'Number_of_Records': count
            })

        output_df = pd.DataFrame(output_data)

        # Sort by number of records (descending)
        output_df = output_df.sort_values('Number_of_Records', ascending=False)

        # Generate output filename with timestamp and customer name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if self.customer_name:
            output_filename = f'{self.customer_name}_dynamic_table_{timestamp}.csv'
            excel_filename = f'{self.customer_name}_dynamic_table_{timestamp}.xlsx'
        else:
            output_filename = f'dynamic_table_{timestamp}.csv'
            excel_filename = f'dynamic_table_{timestamp}.xlsx'

        output_path = self.output_folder / output_filename

        # Verify data integrity before saving
        print(f"\n{'=' * 80}")
        print("VERIFYING DATA INTEGRITY")
        print(f"{'=' * 80}")

        total_counted = output_df['Number_of_Records'].sum()
        print(f"Records in input: {total_rows_processed:,}")
        print(f"Records in output: {total_counted:,}")

        if total_counted == total_rows_processed:
            print(f"✓ Verification PASSED: All records accounted for")
        else:
            print(f"⚠ WARNING: Record count mismatch!")
            print(f"  Difference: {abs(total_counted - total_rows_processed):,}")

        # Save to CSV
        output_df.to_csv(output_path, index=False)
        print(f"\n✓ CSV output saved to: {output_path}")

        # Also save to Excel for better formatting
        excel_path = self.output_folder / excel_filename
        try:
            output_df.to_excel(excel_path, index=False, sheet_name='Dynamic Table')
            print(f"✓ Excel output saved to: {excel_path}")
        except Exception as e:
            print(f"⚠ Could not save Excel file: {str(e)}")

        # Print summary statistics
        print(f"\n{'=' * 80}")
        print("SUMMARY STATISTICS")
        print(f"{'=' * 80}")
        print(f"Total unique combinations: {len(output_df):,}")
        print(f"Total records counted: {output_df['Number_of_Records'].sum():,}")
        print(f"\nTop 10 combinations by record count:")
        print(output_df.head(10).to_string(index=False))

        return output_df


def main():
    """
    Main execution function (legacy - for backward compatibility).

    NOTE: It is recommended to use main_menu.py instead, which provides
    proper customer folder structure support and suppression handling.
    """
    print("\n" + "=" * 80)
    print("NOTICE: Direct execution of this script is deprecated.")
    print("Please use 'python main_menu.py' for proper customer folder support.")
    print("=" * 80 + "\n")

    try:
        # Legacy mode - uses old 'Files' folder structure
        generator = DynamicTableGenerator(
            input_folder='Files',
            output_folder='output',
            suppress_folder=None  # No suppression in legacy mode
        )
        result_df = generator.process_csv_files()

        print(f"\n{'=' * 80}")
        print("✓ PROCESS COMPLETED SUCCESSFULLY!")
        print(f"{'=' * 80}\n")

    except Exception as e:
        print(f"\n{'=' * 80}")
        print("✗ ERROR:")
        print(f"{'=' * 80}")
        print(f"{str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
