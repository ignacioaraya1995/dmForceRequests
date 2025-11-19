# Dynamic Table Generator

## Overview

This script generates a comprehensive dynamic table from CSV files containing property data. It processes multiple CSV files and creates aggregated counts based on various dimensions and value ranges.

## Features

- ✅ Processes multiple CSV files from a single input folder
- ✅ Real-time progress tracking with progress bars
- ✅ Handles missing, empty, and "Unknown" values gracefully
- ✅ Generates both CSV and Excel output files
- ✅ Includes detailed summary statistics
- ✅ Automatic timestamp-based file naming
- ✅ Comprehensive error handling

## Output Columns

The generated dynamic table includes the following columns:

### Dimension Columns
- **FIPS**: County FIPS code
- **SitusCity**: Property city
- **SitusZIP5**: 5-digit ZIP code
- **Owner_Type**: Type of owner (Individual, Company, Trust, etc.)
- **Use_Type**: Property use type (SFH, Condo, Land, Others)

### Range Columns
- **SaleDate_Range**: Sale date categorized by years ago
- **BuildDate_Range**: Build date categorized by years ago
- **TotalValue_Range**: Property total value in dollar ranges
- **LTV_Range**: Loan-to-Value ratio ranges
- **LotSizeSqFt_Range**: Lot size in square feet ranges
- **SumLivingAreaSqFt_Range**: Living area in square feet ranges

### Metrics
- **Number_of_Records**: Count of records for each unique combination

## Value Ranges

### Total Value Ranges (in $1,000s)
- Unknowns
- $0
- $1-$25
- $25-$50
- $50-$100
- $100-$150
- $150-$200
- $200-$250
- $250-$300
- $300-$350
- $350-$400
- $400-$450
- $450-$500
- $500-$650
- $650-$750
- $750-$1,000
- $1,000-$1,500
- $1,500-$2,000
- $2,000+

### Living Area Ranges (SqFt)
- Unknowns
- 0
- 1-199
- 200-799
- 800-1,499
- 1,500-2,499
- 2,500-3,499
- 3,500-4,499
- 4,500+

### Lot Size Ranges (SqFt)
- Unknowns
- 0
- 1-100
- 101-999
- 1,000-3,599
- 3,600-14,999
- 15,000-29,999
- 30,000-44,999
- 45,000+

### Build Date & Sale Date Ranges (Years Ago)
- Unknown
- 0-1 years
- 2-4 years
- 5-7 years
- 8-9 years
- 10-14 years
- 15-19 years
- 20-24 years
- 25-29 years
- 30-39 years
- 40-49 years
- 50-74 years
- 75-99 years
- 100+ years

### LTV Ranges
- Unknown
- 0-69
- 70-84
- 85-99
- 100-998
- 999+

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements_dynamic_table.txt
```

Or install manually:

```bash
pip install pandas numpy tqdm openpyxl
```

## Usage

### Basic Usage

1. Place your CSV files in the `Files` folder
2. Run the script:

```bash
python dynamic_table_generator.py
```

3. Find your output in the `output` folder with timestamp

### Input Requirements

- CSV files should contain the following columns:
  - FIPS
  - SitusCity
  - SitusZIP5
  - Owner_Type
  - Use_Type
  - saleDate (date format)
  - buildDate (date format)
  - totalValue (numeric, can be Unknown/empty)
  - LTV (numeric, can be Unknown/empty)
  - LotSizeSqFt (numeric, can be Unknown/empty)
  - SumLivingAreaSqFt (numeric, can be Unknown/empty)

### Customizing Input/Output Folders

You can modify the folders in the script:

```python
generator = DynamicTableGenerator(
    input_folder='YourInputFolder',
    output_folder='YourOutputFolder'
)
```

## Output Files

The script generates two files:

1. **CSV File**: `dynamic_table_YYYYMMDD_HHMMSS.csv`
   - Plain text format
   - Easy to import into other systems
   - Sorted by Number_of_Records (descending)

2. **Excel File**: `dynamic_table_YYYYMMDD_HHMMSS.xlsx`
   - Formatted spreadsheet
   - Ready for analysis
   - Same data as CSV

## Example Output

```
FIPS   SitusCity   SitusZIP5   Owner_Type   Use_Type   SaleDate_Range   BuildDate_Range   TotalValue_Range   LTV_Range   LotSizeSqFt_Range   SumLivingAreaSqFt_Range   Number_of_Records
49051  HEBER CITY  84032.0     Company      Others     Unknown          Unknown           $2,000+            Unknown     45,000+             4,500+                     340
49051  KAMAS       84036.0     Company      Others     Unknown          Unknown           $2,000+            Unknown     45,000+             4,500+                     202
```

## Progress Tracking

The script provides real-time progress information:

```
================================================================================
Processing: 49051.csv
================================================================================
Loading CSV file...
✓ Loaded 29,702 rows

Processing rows...
Processing: 100%|██████████| 29702/29702 [00:13<00:00, 2230.35rows/s]
✓ Processed 29,702 rows from 49051.csv

================================================================================
PROCESSING COMPLETE
================================================================================
Total rows processed: 29,702
Unique combinations: 17,219
```

## Performance

- **Processing Speed**: ~2,000-5,000 rows per second
- **Memory Efficient**: Uses streaming processing
- **Large File Support**: Can handle files with millions of rows

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   pip install pandas numpy tqdm openpyxl
   ```

2. **CSV File Not Found**
   - Ensure CSV files are in the `Files` folder
   - Check file extensions (.csv)

3. **Excel File Not Created**
   - Install openpyxl: `pip install openpyxl`
   - CSV file will still be created

4. **Memory Issues with Large Files**
   - Process files one at a time
   - Close other applications

## Data Quality Notes

- **Unknown Values**: Empty, null, "Unknown", or unparseable values are categorized as "Unknown" or "Unknowns"
- **Total Value**: Values are in dollars and divided by 1,000 for range categorization
- **Date Calculations**: Dates are calculated as years ago from the current date
- **Zero Values**: Zero values are kept in a separate "0" category

## Support

For issues or questions, please check:
1. CSV column names match the required format
2. All dependencies are installed
3. Input files are valid CSV format

## Version History

- **v1.0** (2025-11-19): Initial release
  - Complete range implementation
  - Progress tracking
  - CSV and Excel output
  - Comprehensive error handling
