# Data Directory Structure

This directory contains customer-specific data folders. Each customer has their own isolated workspace.

## Directory Structure

```
data/
└── {customer_name}/
    ├── input/
    │   ├── {FIPS}.csv          # FIPS code-named CSV data files (e.g., 49011.csv)
    │   ├── {FIPS}.csv          # Additional FIPS files as needed
    │   └── suppression.csv     # Optional suppression file for filtering
    └── output/                 # Generated Excel reports appear here
```

## Example

```
data/
└── Joe Homebuyer/
    ├── input/
    │   ├── 49011.csv
    │   ├── 49035.csv
    │   └── suppression.csv
    └── output/
        └── Joe_Homebuyer_Consolidated_20251119.xlsx
```

## Usage

1. **Create a new customer folder**:
   - Run `python main.py` and select option "0. Create new customer"
   - Or manually create: `data/{customer_name}/input/` and `data/{customer_name}/output/`

2. **Add input files**:
   - Place CSV data files in `data/{customer_name}/input/`
   - Files are typically named by FIPS code (e.g., `49011.csv`)
   - Optionally add `suppression.csv` for filtering

3. **Run processing**:
   - Run `python main.py`
   - Select operation (Dynamic Table or Main Pipeline)
   - Select your customer from the list

4. **Find output**:
   - Generated files appear in `data/{customer_name}/output/`

## Notes

- CSV and Excel files in this directory are ignored by git (see `.gitignore`)
- The directory structure is tracked, but actual data files are not committed
- Each customer's data is completely isolated from other customers
- The old `customers/` directory structure has been replaced with `data/`
