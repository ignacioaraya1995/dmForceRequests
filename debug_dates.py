#!/usr/bin/env python3
"""Debug script for date parsing issues."""

import pandas as pd
from datetime import datetime
from dynamic_table_generator import DynamicTableGenerator

generator = DynamicTableGenerator()

# Test specific dates that are failing
test_dates = [
    '2016-01-01',
    '2016-10-19',
    '2016-10-28',
    '2016',
    2016,
    '2021-11-23',
    '2020-08-03',
]

print("=" * 80)
print("DATE DEBUGGING")
print("=" * 80)
print(f"\nCurrent date: {datetime.now().strftime('%Y-%m-%d')}\n")

for date_value in test_dates:
    print(f"\nTesting: {date_value} (type: {type(date_value).__name__})")

    # Step 1: Calculate years ago
    years_ago = generator.calculate_years_ago(date_value)
    print(f"  → Years ago: {years_ago}")

    # Step 2: Categorize
    category = generator.categorize_date(date_value, generator.sale_date_ranges)
    print(f"  → Category: {category}")

    # Step 3: Show which range it should match
    if years_ago is not None:
        print(f"  → Should match range containing {years_ago:.2f} years")
        for range_label, range_display, min_val, max_val in generator.sale_date_ranges:
            if min_val is not None:
                if min_val <= years_ago <= max_val:
                    print(f"     ✓ Matches: {range_display} ({min_val}-{max_val})")
                elif min_val <= years_ago and max_val == float('inf'):
                    print(f"     ✓ Matches: {range_display} ({min_val}+)")

print("\n" + "=" * 80)
print("RANGE DEFINITIONS")
print("=" * 80)
print("\nSale Date Ranges:")
for range_label, range_display, min_val, max_val in generator.sale_date_ranges:
    if max_val == float('inf'):
        print(f"  {range_display}: {min_val}+ years")
    else:
        print(f"  {range_display}: {min_val}-{max_val} years")
