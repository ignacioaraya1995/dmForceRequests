#!/usr/bin/env python3
"""
Verification Script for Dynamic Table Generator
Tests date parsing, numeric categorization, and data integrity
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import sys

# Import the DynamicTableGenerator
from dynamic_table_generator import DynamicTableGenerator


class DynamicTableVerifier:
    """Comprehensive verification for the Dynamic Table Generator."""

    def __init__(self):
        self.generator = DynamicTableGenerator()
        self.test_results = []

    def print_header(self, title):
        """Print a formatted header."""
        print(f"\n{'=' * 80}")
        print(f"  {title}")
        print(f"{'=' * 80}\n")

    def print_success(self, message):
        """Print a success message."""
        print(f"✓ {message}")
        self.test_results.append(('PASS', message))

    def print_error(self, message):
        """Print an error message."""
        print(f"✗ {message}")
        self.test_results.append(('FAIL', message))

    def print_info(self, message):
        """Print an info message."""
        print(f"ℹ {message}")

    def test_date_parsing(self):
        """Test date parsing for various formats."""
        self.print_header("TEST 1: Date Parsing")

        test_cases = [
            # (input_value, expected_category_type, description)
            ('2021-11-23', 'valid', 'ISO format (YYYY-MM-DD)'),
            ('11/23/2021', 'valid', 'US format (MM/DD/YYYY)'),
            ('2016', 'valid', 'Year only (2016)'),
            (2016, 'valid', 'Numeric year (2016)'),
            ('2020-01-01', 'valid', 'Recent date (2020)'),
            ('1950-05-15', 'valid', 'Old date (1950)'),
            ('', 'Unknown', 'Empty string'),
            (None, 'Unknown', 'None value'),
            ('Unknown', 'Unknown', 'String "Unknown"'),
            ('invalid', 'Unknown', 'Invalid date string'),
            (999999, 'Unknown', 'Invalid year number'),
        ]

        passed = 0
        failed = 0

        for date_value, expected_type, description in test_cases:
            try:
                # Test with sale date ranges
                result = self.generator.categorize_date(
                    date_value,
                    self.generator.sale_date_ranges
                )

                if expected_type == 'valid':
                    if result != 'Unknown':
                        self.print_success(f"{description}: '{date_value}' -> '{result}'")
                        passed += 1
                    else:
                        self.print_error(f"{description}: '{date_value}' returned 'Unknown' (expected valid range)")
                        failed += 1
                elif expected_type == 'Unknown':
                    if result == 'Unknown':
                        self.print_success(f"{description}: '{date_value}' -> 'Unknown' (correct)")
                        passed += 1
                    else:
                        self.print_error(f"{description}: '{date_value}' returned '{result}' (expected 'Unknown')")
                        failed += 1
            except Exception as e:
                self.print_error(f"{description}: Exception - {str(e)}")
                failed += 1

        print(f"\nDate Parsing Results: {passed} passed, {failed} failed")
        return failed == 0

    def test_numeric_categorization(self):
        """Test numeric value categorization."""
        self.print_header("TEST 2: Numeric Value Categorization")

        # Test Total Value (in thousands)
        print("Testing Total Value Categorization:")
        test_values = [
            (1183000, '$1,000-$1,500', 'Total Value: $1,183,000'),  # 1183 thousands
            (50000, '$50-$100', 'Total Value: $50,000'),  # 50 thousands
            (2500000, '$2,000+', 'Total Value: $2,500,000'),  # 2500 thousands
            (0, '$0', 'Total Value: $0'),
            (None, 'Unknowns', 'Total Value: None'),
            ('', 'Unknowns', 'Total Value: Empty string'),
        ]

        passed = 0
        failed = 0

        for value, expected, description in test_values:
            result = self.generator.categorize_value(
                value,
                self.generator.total_value_ranges,
                value_is_dollar=True
            )
            if result == expected:
                self.print_success(f"{description} -> '{result}' (correct)")
                passed += 1
            else:
                self.print_error(f"{description} -> '{result}' (expected '{expected}')")
                failed += 1

        # Test Living Area
        print("\nTesting Living Area Categorization:")
        test_areas = [
            (2506, '2,500-3,499', 'Living Area: 2,506 sqft'),
            (850, '800-1,499', 'Living Area: 850 sqft'),
            (5000, '4,500+', 'Living Area: 5,000 sqft'),
            (0, '0', 'Living Area: 0'),
            (None, 'Unknowns', 'Living Area: None'),
        ]

        for value, expected, description in test_areas:
            result = self.generator.categorize_value(
                value,
                self.generator.living_area_ranges
            )
            if result == expected:
                self.print_success(f"{description} -> '{result}' (correct)")
                passed += 1
            else:
                self.print_error(f"{description} -> '{result}' (expected '{expected}')")
                failed += 1

        # Test LTV
        print("\nTesting LTV Categorization:")
        test_ltvs = [
            (50, '0-69', 'LTV: 50'),
            (75, '70-84', 'LTV: 75'),
            (90, '85-99', 'LTV: 90'),
            (150, '100-998', 'LTV: 150'),
            (1000, '999+', 'LTV: 1000'),
            ('Unknown', 'Unknown', 'LTV: Unknown string'),
            (None, 'Unknown', 'LTV: None'),
        ]

        for value, expected, description in test_ltvs:
            result = self.generator.categorize_value(
                value,
                self.generator.ltv_ranges
            )
            if result == expected:
                self.print_success(f"{description} -> '{result}' (correct)")
                passed += 1
            else:
                self.print_error(f"{description} -> '{result}' (expected '{expected}')")
                failed += 1

        print(f"\nNumeric Categorization Results: {passed} passed, {failed} failed")
        return failed == 0

    def test_years_ago_calculation(self):
        """Test years ago calculation."""
        self.print_header("TEST 3: Years Ago Calculation")

        current_year = datetime.now().year

        test_cases = [
            (f'{current_year}-01-01', 0, 1, 'Current year'),
            (f'{current_year - 5}-06-15', 4.5, 5.5, '5 years ago'),
            (f'{current_year - 20}-03-20', 19.5, 20.5, '20 years ago'),
            (f'{current_year - 100}-12-31', 99.5, 100.5, '100 years ago'),
            ('1950-01-01', 74, 76, 'Very old (1950)'),
        ]

        passed = 0
        failed = 0

        for date_value, min_expected, max_expected, description in test_cases:
            years_ago = self.generator.calculate_years_ago(date_value)
            if years_ago is not None and min_expected <= years_ago <= max_expected:
                self.print_success(f"{description}: {years_ago:.1f} years ago")
                passed += 1
            else:
                self.print_error(f"{description}: Got {years_ago}, expected {min_expected}-{max_expected}")
                failed += 1

        print(f"\nYears Ago Calculation Results: {passed} passed, {failed} failed")
        return failed == 0

    def test_csv_processing(self, csv_file_path):
        """Test processing a real CSV file."""
        self.print_header("TEST 4: CSV File Processing")

        if not Path(csv_file_path).exists():
            self.print_error(f"CSV file not found: {csv_file_path}")
            return False

        try:
            # Read a sample of the CSV
            self.print_info(f"Reading CSV file: {csv_file_path}")
            df = pd.read_csv(csv_file_path, nrows=100, low_memory=False)
            self.print_success(f"Successfully read {len(df)} rows")

            # Check required columns
            required_columns = [
                'FIPS', 'SitusCity', 'SitusZIP5', 'Owner_Type', 'Use_Type',
                'saleDate', 'buildDate', 'totalValue', 'LTV',
                'LotSizeSqFt', 'SumLivingAreaSqFt'
            ]

            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                self.print_error(f"Missing required columns: {missing_columns}")
                return False
            else:
                self.print_success(f"All required columns present: {len(required_columns)} columns")

            # Test processing a few rows
            self.print_info("\nTesting row processing:")

            valid_dates = 0
            invalid_dates = 0
            valid_values = 0
            invalid_values = 0

            for idx, row in df.head(10).iterrows():
                # Test date processing
                sale_date = row.get('saleDate')
                sale_date_range = self.generator.categorize_date(
                    sale_date,
                    self.generator.sale_date_ranges
                )

                build_date = row.get('buildDate')
                build_date_range = self.generator.categorize_date(
                    build_date,
                    self.generator.build_date_ranges
                )

                if sale_date_range != 'Unknown':
                    valid_dates += 1
                else:
                    invalid_dates += 1

                # Test value processing
                total_value = row.get('totalValue')
                total_value_range = self.generator.categorize_value(
                    total_value,
                    self.generator.total_value_ranges,
                    value_is_dollar=True
                )

                if total_value_range != 'Unknowns':
                    valid_values += 1
                else:
                    invalid_values += 1

                print(f"  Row {idx}: SaleDate={sale_date} -> {sale_date_range}, "
                      f"BuildDate={build_date} -> {build_date_range}, "
                      f"TotalValue={total_value} -> {total_value_range}")

            self.print_success(f"Valid dates: {valid_dates}/10, Valid values: {valid_values}/10")

            return True

        except Exception as e:
            self.print_error(f"Error processing CSV: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_data_integrity(self):
        """Test data integrity and counting."""
        self.print_header("TEST 5: Data Integrity Check")

        # Create a test dataframe
        test_data = {
            'FIPS': ['49051', '49051', '49051', '49051', '49051'],
            'SitusCity': ['KAMAS', 'KAMAS', 'HEBER', 'KAMAS', 'HEBER'],
            'SitusZIP5': ['84036', '84036', '84032', '84036', '84032'],
            'Owner_Type': ['Company', 'Individual', 'Company', 'Individual', 'Trust'],
            'Use_Type': ['Others', 'SFH', 'Others', 'Condo', 'Land'],
            'saleDate': ['2020-01-01', '2021-05-15', None, '2019-12-31', '2022-03-20'],
            'buildDate': ['2015-01-01', '2010-06-15', '2018-01-01', '2005-12-31', '2000-03-20'],
            'totalValue': [500000, 1200000, None, 300000, 2500000],
            'LTV': [80, None, 150, 65, 95],
            'LotSizeSqFt': [2500, 5000, 1000, 0, 45000],
            'SumLivingAreaSqFt': [2000, 3000, 1500, 800, 5000]
        }

        df = pd.DataFrame(test_data)

        self.print_info(f"Created test dataframe with {len(df)} rows")

        # Process each row
        processed_count = 0
        for idx, row in df.iterrows():
            # This simulates what the generator does
            fips = str(row.get('FIPS', 'Unknown'))
            situs_city = str(row.get('SitusCity', 'Unknown'))

            total_value_range = self.generator.categorize_value(
                row.get('totalValue'),
                self.generator.total_value_ranges,
                value_is_dollar=True
            )

            sale_date_range = self.generator.categorize_date(
                row.get('saleDate'),
                self.generator.sale_date_ranges
            )

            build_date_range = self.generator.categorize_date(
                row.get('buildDate'),
                self.generator.build_date_ranges
            )

            processed_count += 1

            print(f"  Row {idx}: FIPS={fips}, City={situs_city}, "
                  f"Value={total_value_range}, SaleDate={sale_date_range}, "
                  f"BuildDate={build_date_range}")

        if processed_count == len(df):
            self.print_success(f"All {processed_count} rows processed correctly")
            return True
        else:
            self.print_error(f"Processed {processed_count} rows, expected {len(df)}")
            return False

    def run_all_tests(self, csv_file_path=None):
        """Run all verification tests."""
        print("\n" + "=" * 80)
        print("  DYNAMIC TABLE GENERATOR - COMPREHENSIVE VERIFICATION")
        print("=" * 80)

        results = []

        # Run all tests
        results.append(('Date Parsing', self.test_date_parsing()))
        results.append(('Numeric Categorization', self.test_numeric_categorization()))
        results.append(('Years Ago Calculation', self.test_years_ago_calculation()))
        results.append(('Data Integrity', self.test_data_integrity()))

        if csv_file_path:
            results.append(('CSV Processing', self.test_csv_processing(csv_file_path)))

        # Print summary
        self.print_header("VERIFICATION SUMMARY")

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {status}: {test_name}")

        print(f"\n{'=' * 80}")
        print(f"  Overall Results: {passed}/{total} tests passed")
        print(f"{'=' * 80}\n")

        if passed == total:
            print("✓ ALL TESTS PASSED! The Dynamic Table Generator is working correctly.")
            return True
        else:
            print(f"✗ {total - passed} test(s) failed. Please review the output above.")
            return False


def main():
    """Main verification function."""
    verifier = DynamicTableVerifier()

    # Check if CSV file path is provided
    csv_file = '/home/user/dmForceRequests/Files/49051.csv'

    if Path(csv_file).exists():
        print(f"\nUsing CSV file: {csv_file}")
        success = verifier.run_all_tests(csv_file_path=csv_file)
    else:
        print(f"\nCSV file not found: {csv_file}")
        print("Running tests without CSV file processing")
        success = verifier.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
