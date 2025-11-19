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

    def __init__(self, input_folder='Files', output_folder='output'):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True)

        # Define all range buckets
        self.define_ranges()

    def define_ranges(self):
        """Define all range buckets for numeric columns."""

        # Total Value Ranges (in dollars)
        self.total_value_ranges = [
            ('Unknowns', 'Unknowns', None, None),
            ('$0', '$0', 0, 0),
            ('$1-$25', '$1-$25', 1, 25),
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
        self.build_date_ranges = [
            ('Unknown', 'Unknown', None, None),
            ('0-1 years', '0-1 years', 0, 1),
            ('2-4 years', '2-4 years', 2, 4),
            ('5-7 years', '5-7 years', 5, 7),
            ('8-9 years', '8-9 years', 8, 9),
            ('10-14 years', '10-14 years', 10, 14),
            ('15-19 years', '15-19 years', 15, 19),
            ('20-24 years', '20-24 years', 20, 24),
            ('25-29 years', '25-29 years', 25, 29),
            ('30-39 years', '30-39 years', 30, 39),
            ('40-49 years', '40-49 years', 40, 49),
            ('50-74 years', '50-74 years', 50, 74),
            ('75-99 years', '75-99 years', 75, 99),
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
        self.sale_date_ranges = [
            ('Unknown', 'Unknown', None, None),
            ('0-1 years', '0-1 years', 0, 1),
            ('2-4 years', '2-4 years', 2, 4),
            ('5-7 years', '5-7 years', 5, 7),
            ('8-9 years', '8-9 years', 8, 9),
            ('10-14 years', '10-14 years', 10, 14),
            ('15-19 years', '15-19 years', 15, 19),
            ('20-24 years', '20-24 years', 20, 24),
            ('25-29 years', '25-29 years', 25, 29),
            ('30-39 years', '30-39 years', 30, 39),
            ('40-49 years', '40-49 years', 40, 49),
            ('50-74 years', '50-74 years', 50, 74),
            ('75-99 years', '75-99 years', 75, 99),
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
                if '-' in date_value:
                    date_obj = pd.to_datetime(date_value)
                else:
                    # Assume it's a year
                    date_obj = pd.to_datetime(date_value + '-01-01')
            else:
                date_obj = pd.to_datetime(date_value)

            # Calculate years ago
            current_date = datetime.now()
            years_ago = (current_date - date_obj).days / 365.25
            return years_ago

        except:
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
            if min_val <= years_ago < max_val:
                return range_display
            if min_val <= years_ago and max_val == float('inf'):
                return range_display

        # If no range found, return the last range
        return ranges[-1][1]

    def process_csv_files(self):
        """Process all CSV files and generate the dynamic table."""
        print("=" * 80)
        print("DYNAMIC TABLE GENERATOR")
        print("=" * 80)
        print(f"\nInput Folder: {self.input_folder}")
        print(f"Output Folder: {self.output_folder}\n")

        # Find all CSV files
        csv_files = list(self.input_folder.glob('*.csv'))
        print(f"Found {len(csv_files)} CSV file(s) to process:\n")
        for csv_file in csv_files:
            print(f"  - {csv_file.name}")
        print()

        if not csv_files:
            print("ERROR: No CSV files found in the input folder!")
            return

        # Initialize data aggregator
        aggregated_data = defaultdict(int)
        total_rows_processed = 0

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

                    # Categorize dates
                    build_date_range = self.categorize_date(
                        row.get('buildDate'),
                        self.build_date_ranges
                    )

                    sale_date_range = self.categorize_date(
                        row.get('saleDate'),
                        self.sale_date_ranges
                    )

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
        print(f"Unique combinations: {len(aggregated_data):,}\n")

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

        # Generate output filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'dynamic_table_{timestamp}.csv'
        output_path = self.output_folder / output_filename

        # Save to CSV
        output_df.to_csv(output_path, index=False)
        print(f"✓ Output saved to: {output_path}")

        # Also save to Excel for better formatting
        excel_filename = f'dynamic_table_{timestamp}.xlsx'
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
    """Main execution function."""
    try:
        generator = DynamicTableGenerator(input_folder='Files', output_folder='output')
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
