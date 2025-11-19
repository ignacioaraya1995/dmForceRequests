# Customer Data Organization

This directory contains customer-specific data folders.

## Folder Structure

Each customer should have the following structure:

```
customers/
├── customer_name/
│   ├── input/
│   │   ├── raw_data/          # CSV files with FIPS data
│   │   └── suppressed/        # Suppression files
│   └── output/                # Generated reports and tables
```

## Input Folder Requirements

### raw_data/
- Contains CSV files with property data
- Must include FIPS codes
- All CSV files in this folder will be processed together

### suppressed/
- Contains suppression files
- Files that should be excluded from the final results

## Output Folder

All generated files will be saved here:
- Dynamic summary tables (CSV and Excel)
- Processed reports
- Analysis results

## Creating a New Customer

To add a new customer:

1. Create a folder with the customer name: `customers/your_customer_name/`
2. Create the required subfolders: `input/raw_data/`, `input/suppressed/`, and `output/`
3. Place your CSV files in the `input/raw_data/` folder
4. Place any suppression files in the `input/suppressed/` folder
5. Run the main program and select the customer

The program will automatically detect all customer folders.
