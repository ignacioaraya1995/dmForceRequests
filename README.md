# Real Estate Property Data Consolidation Tool

A professional, modular Python tool for consolidating and analyzing real estate property data with distress indicators. This tool processes CSV files, applies sophisticated filtering logic, removes duplicates, and generates formatted Excel reports.

## Features

- **Multi-source Data Consolidation**: Combine property data from multiple CSV files
- **Distress Scoring**: Calculate and rank properties by 25+ distress indicators
- **Intelligent Deduplication**: Remove duplicates based on mailing and property addresses
- **Interactive Filtering**: Filter by owner type, property type, and total value
- **FIPS County Mapping**: Automatically map FIPS codes to county names
- **Previous Data Suppression**: Compare against historical data to avoid duplicates
- **Professional Excel Output**: Generate formatted reports with color-coded headers
- **Comprehensive Logging**: Track all operations with detailed file and console logs
- **Multi-language Support**: English and Spanish interfaces

## Project Structure

```
dmForceRequests/
├── main.py                          # English version entry point
├── loantype.py                      # Spanish version entry point
├── zip.py                           # ZIP extraction utility
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── .env.example                     # Configuration template
│
├── src/                             # Source code modules
│   ├── data_processing/             # Data transformation logic
│   │   ├── __init__.py
│   │   └── processor.py             # DataProcessor, DataValidator
│   │
│   ├── file_operations/             # File I/O operations
│   │   ├── __init__.py
│   │   ├── file_handler.py          # FileReader, DuplicateManager, ZipExtractor
│   │   └── excel_formatter.py       # ExcelFormatter, ReportGenerator
│   │
│   ├── ui/                          # User interface
│   │   ├── __init__.py
│   │   └── console_interface.py     # ConsoleInterface, DataFilter, ProgressTracker
│   │
│   └── utils/                       # Utilities
│       ├── __init__.py
│       ├── logger.py                # Logging configuration
│       └── config.py                # Application configuration
│
├── Files/                           # Input CSV files (place your data here)
├── Dupes/                           # Previous suppression files
├── Output File/                     # Generated Excel reports
├── logs/                            # Application logs
└── FIPs.xlsx                        # FIPS to County mapping reference
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd dmForceRequests
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify directory structure:
```bash
mkdir -p Files Dupes "Output File" logs
```

## Usage

### English Version

```bash
python main.py
```

### Spanish Version

```bash
python loantype.py
```

### Basic Workflow

1. **Place CSV files** in the `Files/` directory
2. **Run the script** (main.py or loantype.py)
3. **Enter client name** when prompted
4. **Follow interactive prompts** for filtering options
5. **Find output** in `Output File/` directory

### Interactive Options

The tool will prompt you for:

- **Owner Type Filter**: Filter by specific owner types (e.g., Individual, Corporate)
- **Property Type Filter**: Filter by property types (e.g., Single Family, Condo)
- **Total Value Range**: Set minimum and maximum property values
- **Duplicate Removal**: Remove properties from previous campaigns (optional)

### Example Session

```
============================================================
     Real Estate Data Consolidation Tool
============================================================

[INFO] Starting data consolidation and cleaning process...
Please enter the client's name: John Doe
[SUCCESS] Client selected: John Doe

--- Reading CSV Files ---
[INFO] Processing folder: Files
[SUCCESS] Read 1 CSV file(s) from Files
[PROGRESS] Step 4/10 (40.0%): CSV files read

--- Processing Data ---
[INFO] Consolidated 100,000 total rows
[INFO] Selected 48 relevant columns
[INFO] Removed rows with incomplete addresses: 95,000 rows remaining
[INFO] Calculated distress scores
[INFO] Removed duplicates: 90,000 rows remaining
[INFO] Filtered top 70%: 63,000 rows remaining

--- Interactive Filtering ---
Do you want to filter by OWNER TYPE? (yes/no): yes
Available values for 'OWNER TYPE': Corporate, Individual, Trust
Enter desired 'OWNER TYPE' values (comma-separated): Individual
[INFO] Filter applied. Removed 10,000 rows. 53,000 rows remaining.

--- Saving Results ---
[SUCCESS] Saved Excel file: John Doe Consolidated 11-19-2025.xlsx

============================================================
               FINAL PROCESS SUMMARY
============================================================
TOTAL FINAL RECORDS: 53,000
--------------------------------------------------
COUNTIES PRESENT: Los Angeles, Orange, San Diego
--------------------------------------------------
PROPERTY TYPES: Condo, Single Family, Townhouse
--------------------------------------------------
OWNER TYPES: Individual
--------------------------------------------------
TOTAL VALUE RANGE: $150,000.00 - $2,500,000.00
==================================================

[SUCCESS] Process completed successfully!
```

## Configuration

### Column Configuration

Modify `src/utils/config.py` to customize:

- **Distress indicators**: Add or remove distress columns
- **Column display order**: Change the output column sequence
- **Column naming**: Adjust standardized column names
- **Processing parameters**: Adjust retention percentage, LTV thresholds

### Logging Configuration

Adjust logging behavior in `src/utils/logger.py`:

- **Log level**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Output destinations**: Console, file, or both
- **Log format**: Customize timestamp and message format

### Processing Parameters

Key parameters in `src/utils/config.py`:

```python
percentage_to_retain = 0.7        # Keep top 70% by distress score
ltv_max_threshold = 999           # Maximum LTV value allowed
```

## Modules Overview

### Data Processing (`src/data_processing/processor.py`)

- **DataProcessor**: Core data transformation operations
  - Consolidation, cleaning, filtering
  - Distress score calculation
  - Column management and reordering

- **DataValidator**: Data quality validation
  - DataFrame validation
  - Required column checks
  - Data summary statistics

### File Operations

#### File Handler (`src/file_operations/file_handler.py`)

- **FileReader**: CSV and Excel file reading
- **DuplicateManager**: Historical duplicate tracking
- **ZipExtractor**: Automatic ZIP file extraction
- **FolderScanner**: Directory management

#### Excel Formatter (`src/file_operations/excel_formatter.py`)

- **ExcelFormatter**: Professional Excel output
  - Color-coded headers (black for main, yellow for distress)
  - Auto-sized columns
  - Professional formatting

- **ReportGenerator**: Summary report generation
  - Console reports
  - Processing statistics

### User Interface (`src/ui/console_interface.py`)

- **ConsoleInterface**: User interaction management
  - Input prompts and validation
  - Status messages and progress

- **DataFilter**: Interactive filtering
  - Text-based filters
  - Numeric range filters

- **ProgressTracker**: Processing progress display

### Utilities

#### Logger (`src/utils/logger.py`)

- Centralized logging configuration
- File and console output
- Daily log rotation

#### Config (`src/utils/config.py`)

- `ColumnConfig`: Column definitions and mappings
- `ProcessingConfig`: Processing parameters
- `PathConfig`: Directory paths
- `ExcelFormatConfig`: Excel formatting settings
- `LanguageConfig`: Multi-language support

## Distress Indicators

The tool tracks 25 distress indicators:

| Indicator | Description |
|-----------|-------------|
| 30-60-Days_Distress | Short-term payment delays |
| Absentee | Non-resident owners |
| Bankruptcy_Distress | Bankruptcy filings |
| Debt-Collection_Distress | Active collections |
| Divorce_Distress | Divorce proceedings |
| Eviction_Distress | Eviction records |
| Failed_Listing_Distress | Previously failed listings |
| highEquity | High equity properties |
| Judgment_Distress | Legal judgments |
| Lien_* | Various lien types (5 categories) |
| Low_income_Distress | Low-income indicators |
| PoorCondition_Distress | Poor property condition |
| Preforeclosure_Distress | Preforeclosure status |
| Probate_Distress | Probate proceedings |
| Prop_Vacant_Flag | Vacant properties |
| Senior_Distress | Senior owner indicators |
| Tax_Delinquent_Distress | Tax delinquency |
| Violation_Distress | Code violations |

## Output Format

The tool generates Excel files with:

### Main Columns (Black header)
- FIPS, Property ID
- Property and mailing addresses
- Owner information
- Property characteristics (size, bedrooms, year built)
- Financial data (LTV, total value, sale date)

### Distress Columns (Yellow header)
- All 25 distress indicator columns
- DistressCounter (total active indicators)

## Logging

Logs are automatically created in the `logs/` directory:

```
logs/
└── realestate_processor_20251119.log
```

Log entries include:
- Timestamp
- Log level
- Module and function name
- Detailed message

## Best Practices

1. **Data Preparation**
   - Ensure CSV files have consistent column names
   - Place all input files in the `Files/` directory
   - Keep FIPS.xlsx updated with latest county mappings

2. **Duplicate Management**
   - Save previous output files to `Dupes/` folder
   - Use duplicate removal feature to avoid re-contacting properties

3. **Performance**
   - For large datasets (>1M rows), processing may take several minutes
   - Monitor log files for detailed progress

4. **Customization**
   - Modify `src/utils/config.py` for business logic changes
   - Adjust filtering criteria as needed
   - Update distress indicators based on data source

## Troubleshooting

### Common Issues

**Issue**: No CSV files found
- **Solution**: Verify files are in `Files/` directory and have `.csv` extension

**Issue**: Missing columns error
- **Solution**: Check that CSV files contain expected column names

**Issue**: FIPS county mapping fails
- **Solution**: Verify `FIPs.xlsx` exists and contains 'FIPS Code' and 'County' columns

**Issue**: Import errors
- **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

**Issue**: Permission denied on logs
- **Solution**: Ensure `logs/` directory has write permissions

## Contributing

When contributing to this project:

1. Follow PEP 8 style guidelines
2. Add docstrings to all functions and classes
3. Update tests for new functionality
4. Document configuration changes in README
5. Add log statements for important operations

## License

This project is proprietary software for real estate data processing.

## Support

For issues or questions:
- Check log files in `logs/` directory
- Review error messages in console output
- Verify data format matches expected structure

## Version History

### Version 2.0.0 (Current - Refactored)
- Complete modular refactoring
- Professional logging system
- Improved error handling
- Enhanced console interface
- Better code organization

### Version 1.0.0 (Legacy)
- Original monolithic implementation
- Basic functionality
- See `main_original.py` and `loantype_original.py` for reference
