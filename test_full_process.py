#!/usr/bin/env python3
"""
Test the full dynamic table generation process with a sample customer.
"""

from pathlib import Path
from dynamic_table_generator import DynamicTableGenerator

# Test with example customer
customer_name = "example_customer"
customer_path = Path("customers") / customer_name
input_path = customer_path / "input" / "raw_data"
output_path = customer_path / "output"

print("=" * 80)
print("FULL PROCESS TEST")
print("=" * 80)
print(f"\nCustomer: {customer_name}")
print(f"Input: {input_path}")
print(f"Output: {output_path}\n")

# Check if input files exist
csv_files = list(input_path.glob("*.csv"))
print(f"Found {len(csv_files)} CSV file(s):")
for f in csv_files:
    size = f.stat().st_size / 1024
    print(f"  - {f.name} ({size:.1f} KB)")

if not csv_files:
    print("\n✗ No CSV files found! Please add files to test.")
    exit(1)

print("\n" + "=" * 80)
print("RUNNING DYNAMIC TABLE GENERATOR")
print("=" * 80)

try:
    generator = DynamicTableGenerator(
        input_folder=str(input_path),
        output_folder=str(output_path),
        customer_name=customer_name
    )

    result_df = generator.process_csv_files()

    print("\n" + "=" * 80)
    print("✓ SUCCESS! Dynamic table generated successfully")
    print("=" * 80)

    # List output files
    output_files = list(output_path.glob("*"))
    if output_files:
        print("\nGenerated files:")
        for f in sorted(output_files, key=lambda x: x.stat().st_mtime, reverse=True):
            if f.is_file():
                size = f.stat().st_size / 1024
                print(f"  - {f.name} ({size:.1f} KB)")

except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
