# Quick Start Guide - Customer Data Processing System

## Overview

This system provides an organized, customer-based workflow for processing real estate data and generating dynamic summary tables.

## New Features

1. **Customer-based organization** - Each customer has their own folder structure
2. **Interactive menu** - Choose operations from a user-friendly menu
3. **Customer selection** - Select from available customers or create new ones
4. **Improved date handling** - Better parsing and validation of date fields
5. **Data verification** - Automatic verification that all records are counted

## Folder Structure

```
dmForceRequests/
├── customers/                    # All customer data goes here
│   ├── customer_name_1/
│   │   ├── input/
│   │   │   ├── raw_data/        # CSV files with FIPS data
│   │   │   └── suppressed/      # Suppression files
│   │   └── output/              # Generated reports
│   ├── customer_name_2/
│   │   └── ...
│   └── README.md                # Customer folder documentation
├── main_menu.py                 # NEW: Main interactive menu
├── dynamic_table_generator.py   # UPDATED: Enhanced date handling
└── main.py                      # Original real estate pipeline
```

## How to Use

### Step 1: Run the Main Menu

```bash
python3 main_menu.py
```

### Step 2: Choose an Operation

You'll see a menu with options:

1. **Generate Dynamic Summary Table** - Create pivot analysis of customer data
2. **Process Real Estate Data** - Run the main data processing pipeline
3. **View Customer Information** - See customer folder contents
Q. **Quit** - Exit the program

### Step 3: Select or Create a Customer

- Choose from existing customers (numbered list)
- Or create a new customer (option 0)
- System automatically detects customer folders

### Step 4: Process Data

The system will:
- Find all CSV files in `input/raw_data/`
- Process and categorize data
- Verify all records are counted
- Save results to `output/` folder

## Creating a New Customer

### Option A: Using the Menu (Recommended)

1. Run `python3 main_menu.py`
2. Choose any operation
3. Select option `0` to create new customer
4. Enter customer name
5. Add CSV files to the created folder

### Option B: Manual Creation

```bash
mkdir -p customers/your_customer_name/input/raw_data
mkdir -p customers/your_customer_name/input/suppressed
mkdir -p customers/your_customer_name/output
```

Then add your CSV files to `customers/your_customer_name/input/raw_data/`

## Input File Requirements

### raw_data folder

Your CSV files should contain:
- **FIPS** - County FIPS codes
- **SitusCity** - Property city
- **SitusZIP5** - Property ZIP code
- **Owner_Type** - Type of property owner
- **Use_Type** - Property use type
- **totalValue** - Total property value
- **LTV** - Loan-to-Value ratio
- **LotSizeSqFt** - Lot size in square feet
- **SumLivingAreaSqFt** - Living area in square feet
- **buildDate** - Property build date (various formats supported)
- **saleDate** - Last sale date (various formats supported)

### suppressed folder

Place any suppression or exclusion files here (for future use).

## Output Files

The system generates files with timestamps and customer names:

- `{customer_name}_dynamic_table_{timestamp}.csv`
- `{customer_name}_dynamic_table_{timestamp}.xlsx`

## Date Handling

The system now properly handles:
- Standard formats: `2020-01-15`, `01/15/2020`
- Year only: `2020` or `2020`
- Numeric years: `2015` (as integer)
- Invalid/missing dates are marked as "Unknown"

## Data Verification

After processing, the system automatically:
- Counts all input records
- Verifies all records are in the output
- Reports date parsing statistics
- Shows percentage of valid vs. unknown dates

## Progress Tracking

The system shows:
- Number of CSV files found
- File sizes
- Processing progress with progress bars
- Date parsing statistics
- Verification results

## Example Session

```
================================================================================
                    DATA PROCESSING MAIN MENU
================================================================================

What would you like to do?

  1. Generate Dynamic Summary Table (Pivot Analysis)
  2. Process Real Estate Data (Main Pipeline)
  3. View Customer Information
  Q. Quit

Select operation (1-3 or Q): 1

================================================================================
                          SELECT CUSTOMER
================================================================================

Available customers:

  1. example_customer
     └─ 1 CSV file(s) in raw_data

  0. Create new customer
  Q. Quit

Select customer (number or Q to quit): 1

✓ Selected customer: example_customer

[Processing begins...]
```

## Troubleshooting

### No CSV files found

**Problem:** "No CSV files found in input/raw_data/"
**Solution:** Add CSV files to the customer's `input/raw_data/` folder

### No customers found

**Problem:** "No customer folders found!"
**Solution:** Create a customer using option 0 in the menu

### Date parsing issues

The system now handles multiple date formats automatically. Check the "DATE PROCESSING STATISTICS" section in the output to see how many dates were successfully parsed.

### Record count mismatch

If you see a warning about record count mismatch, check:
- CSV file encoding
- Data corruption
- Missing values in key fields

## Additional Tools

### View Customer Info

Use option 3 in the main menu to:
- See all input files and sizes
- View output files
- Check folder structure

### Legacy Tools

- `main.py` - Original real estate data processing
- `dynamic_table_generator.py` - Can still be run standalone
- `loantype.py` - Loan type analysis

## Next Steps

1. Create your first customer
2. Add CSV files to the input folder
3. Run the dynamic table generator
4. Review the output in the customer's output folder
5. Check the verification statistics

## Support

For issues or questions, check:
- `customers/README.md` - Customer folder structure
- `DYNAMIC_TABLE_README.md` - Dynamic table details
- `README.md` - Original project documentation
