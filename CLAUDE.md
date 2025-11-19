# CLAUDE.md - AI Assistant Guide for dmForceRequests

> **Last Updated**: 2025-11-19
> **Project**: Real Estate Property Data Consolidation Tool
> **Purpose**: Guide AI assistants in understanding and working with this codebase

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Design Patterns](#architecture--design-patterns)
3. [Directory Structure](#directory-structure)
4. [Key Components](#key-components)
5. [Development Workflows](#development-workflows)
6. [Code Conventions](#code-conventions)
7. [Testing & Debugging](#testing--debugging)
8. [Common Tasks](#common-tasks)
9. [Git Workflow](#git-workflow)
10. [Important Notes for AI Assistants](#important-notes-for-ai-assistants)

---

## Project Overview

### Purpose
This is a professional Python-based data processing tool designed for real estate professionals to:
- Consolidate property data from multiple CSV sources
- Calculate distress scores based on 25+ indicators
- Apply intelligent filtering and deduplication
- Generate formatted Excel reports

### Key Features
- **Multi-language Support**: English (`main.py`) and Spanish (`loantype.py`) versions
- **Customer Organization**: Customer-based folder structure for data isolation
- **Interactive Menu System**: User-friendly CLI interface (`main_menu.py`)
- **Dynamic Table Generation**: Pivot-style analysis with configurable ranges
- **Modular Architecture**: Clean separation of concerns across modules
- **Professional Logging**: Comprehensive file and console logging
- **FIPS County Mapping**: Automatic county name resolution

### Technology Stack
- **Language**: Python 3.8+
- **Core Libraries**: pandas, openpyxl, xlsxwriter
- **UI**: colorama for terminal colors
- **Configuration**: python-dotenv, dataclasses
- **Progress Tracking**: tqdm for progress bars

---

## Architecture & Design Patterns

### Design Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Configuration-Driven**: Centralized configuration in `src/utils/config.py`
3. **Dataclass-Based Config**: Type-safe configuration using Python dataclasses
4. **Dependency Injection**: Components receive configuration and dependencies
5. **Modular Design**: Easy to extend, test, and maintain

### Module Organization

```
src/
├── data_processing/    # Business logic for data transformation
├── file_operations/    # I/O operations (reading, writing, formatting)
├── ui/                 # User interface and interaction
└── utils/              # Cross-cutting concerns (config, logging)
```

### Key Design Patterns

1. **Factory Pattern**: Logger creation via `get_logger()`
2. **Configuration Object**: `AppConfig` aggregates all settings
3. **Strategy Pattern**: Different filtering strategies in `DataFilter`
4. **Builder Pattern**: Excel formatting with `ExcelFormatter`

---

## Directory Structure

### Root Structure

```
dmForceRequests/
├── main.py                          # English version entry point
├── loantype.py                      # Spanish version entry point
├── main_menu.py                     # Interactive menu system (NEW)
├── dynamic_table_generator.py       # Pivot table generation
├── zip.py                           # ZIP extraction utility
├── requirements.txt                 # Core dependencies
├── requirements_dynamic_table.txt   # Dynamic table dependencies
├── .env.example                     # Environment configuration template
├── .gitignore                       # Git ignore patterns
│
├── src/                             # Source code modules
│   ├── data_processing/
│   │   ├── __init__.py
│   │   └── processor.py             # DataProcessor, DataValidator
│   │
│   ├── file_operations/
│   │   ├── __init__.py
│   │   ├── file_handler.py          # FileReader, DuplicateManager, ZipExtractor
│   │   └── excel_formatter.py       # ExcelFormatter, ReportGenerator
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   └── console_interface.py     # ConsoleInterface, DataFilter, ProgressTracker
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                # Logging configuration
│       └── config.py                # Application configuration
│
├── customers/                       # Customer data folders (NEW)
│   ├── README.md                    # Customer structure docs
│   └── {customer_name}/
│       ├── input/
│       │   ├── raw_data/            # CSV input files
│       │   └── suppressed/          # Suppression files
│       └── output/                  # Generated reports
│
├── Files/                           # Legacy input folder
├── Dupes/                           # Legacy duplicate tracking
├── Output File/                     # Legacy output folder
├── logs/                            # Application logs (gitignored)
└── FIPs.xlsx                        # FIPS to County mapping
```

### Customer-Based Organization (Preferred)

The new structure uses customer-specific folders:

```
customers/
└── example_customer/
    ├── input/
    │   ├── raw_data/          # Place CSV files here
    │   └── suppressed/        # Place suppression files here
    └── output/                # Generated reports appear here
```

**Benefits**:
- Clean data isolation per customer
- Easy to manage multiple clients
- Prevents data mixing
- Better organization for production use

---

## Key Components

### 1. Configuration System (`src/utils/config.py`)

**Purpose**: Centralized configuration management using dataclasses

**Key Classes**:
- `ColumnConfig`: Column definitions, distress indicators, rename mappings
- `ProcessingConfig`: Processing parameters (retention %, LTV thresholds)
- `PathConfig`: File paths, directory management, client-specific paths
- `ExcelFormatConfig`: Excel styling (colors, fonts, borders)
- `LanguageConfig`: Multi-language message support
- `AppConfig`: Main configuration aggregator

**Usage**:
```python
from src.utils.config import get_default_config

config = get_default_config(language='en', log_level='INFO')
config.paths.set_client_name("example_customer")
config.ensure_setup()  # Creates necessary directories
```

**Important Constants**:
- `distress_columns`: 25 distress indicator column names
- `percentage_to_retain`: 0.7 (keep top 70% by distress score)
- `ltv_max_threshold`: 999 (filter out extreme LTV values)

### 2. Logging System (`src/utils/logger.py`)

**Purpose**: Professional logging with file and console output

**Features**:
- Daily log rotation (filename includes date)
- Separate console and file formatters
- Module-level logging with function names and line numbers
- Configurable log levels

**Usage**:
```python
from src.utils.logger import get_logger

logger = get_logger(__name__, log_level='INFO')
logger.info("Processing started")
logger.error("Error message")
```

**Log File Location**: `logs/realestate_processor_YYYYMMDD.log`

**Log Format**:
```
2025-11-19 10:30:45 | INFO     | module:function:123 | Message here
```

### 3. Data Processing (`src/data_processing/processor.py`)

**Purpose**: Core data transformation and business logic

**Classes**:

#### `DataProcessor`
- `consolidate_dataframes()`: Merge multiple DataFrames
- `select_relevant_columns()`: Filter to required columns
- `remove_incomplete_addresses()`: Remove rows with missing addresses
- `calculate_distress_score()`: Sum all distress indicators
- `remove_duplicates()`: Deduplicate by address combinations
- `filter_by_top_percentage()`: Keep top N% by distress score
- `reorder_columns()`: Apply display order
- `apply_title_case()`: Standardize text columns

#### `DataValidator`
- `validate_dataframe()`: Check DataFrame is not None/empty
- `validate_columns_exist()`: Verify required columns present
- `get_data_summary()`: Generate statistics summary

**Key Method Signatures**:
```python
def calculate_distress_score(df: pd.DataFrame, distress_cols: List[str]) -> pd.DataFrame:
    """
    Calculate total distress score by summing all distress indicator columns.
    Adds 'DistressCounter' column with the sum.
    """
```

### 4. File Operations

#### File Handler (`src/file_operations/file_handler.py`)

**Classes**:
- `FileReader`: Read CSV/Excel files with error handling
- `DuplicateManager`: Track and suppress previous campaign data
- `ZipExtractor`: Automatically extract ZIP archives
- `FolderScanner`: Scan directories for data files

**Key Methods**:
```python
def read_csv_files_from_folder(folder: Path) -> List[pd.DataFrame]:
    """Read all CSV files from a folder, return list of DataFrames"""

def extract_zip_files(folder: Path) -> int:
    """Extract all ZIP files in folder, return count extracted"""
```

#### Excel Formatter (`src/file_operations/excel_formatter.py`)

**Classes**:
- `ExcelFormatter`: Professional Excel output with formatting
- `ReportGenerator`: Summary reports and statistics

**Formatting**:
- Main columns: Black header, white text
- Distress columns: Yellow/orange header (#FFC000), black text
- Auto-sized columns (max 50 characters wide)
- Center-aligned headers with borders

### 5. User Interface (`src/ui/console_interface.py`)

**Purpose**: Interactive CLI for user interaction

**Classes**:

#### `ConsoleInterface`
- `print_header()`: Section headers with borders
- `print_success()`, `print_error()`, `print_warning()`, `print_info()`: Colored messages
- `get_client_name()`: Prompt for client name with validation
- `print_section()`: Visual section separators

#### `DataFilter`
- `filter_by_text_column()`: Interactive filtering by categorical columns
- `filter_by_numeric_range()`: Interactive filtering by numeric ranges
- `get_available_values()`: Show unique values in column

#### `ProgressTracker`
- `set_total_steps()`: Define total processing steps
- `step_completed()`: Mark step as done, show progress
- `get_progress_percentage()`: Calculate completion %

**Color Scheme**:
- Green: Success messages
- Red: Error messages
- Yellow: Warning messages
- Blue: Info messages
- Cyan: Headers and prompts

### 6. Main Entry Points

#### `main.py` (English Version)
**Workflow**:
1. Initialize configuration and logger
2. Get client name
3. Extract ZIP files if present
4. Read CSV files
5. Process data (consolidate, filter, deduplicate)
6. Apply FIPS county mapping
7. Interactive filtering
8. Suppress duplicates against previous campaigns
9. Generate Excel output
10. Display summary report

#### `main_menu.py` (Interactive Menu)
**Features**:
- Customer selection from available folders
- Create new customer with folder structure
- Run dynamic table generator
- Run main data processing pipeline
- View customer information

**Menu Options**:
1. Generate Dynamic Summary Table (Pivot Analysis)
2. Process Real Estate Data (Main Pipeline)
3. View Customer Information
Q. Quit

#### `dynamic_table_generator.py` (Pivot Analysis)
**Purpose**: Generate aggregated counts by dimensions and ranges

**Output Columns**:
- Dimensions: FIPS, SitusCity, SitusZIP5, Owner_Type, Use_Type
- Ranges: SaleDate, BuildDate, TotalValue, LTV, LotSize, LivingArea
- Metric: Number_of_Records

**Range Definitions**:
- TotalValue: $0, $1-25k, $25-50k, ..., $2M+
- LTV: Unknown, 0-69, 70-84, 85-99, 100-998, 999+
- Dates: Unknown, 0-1yr, 2-4yr, 5-7yr, ..., 100+yr
- LotSize: 0, 1-100, 101-999, 1k-3.6k, ..., 45k+ sqft
- LivingArea: 0, 1-199, 200-799, 800-1.5k, ..., 4.5k+ sqft

---

## Development Workflows

### Adding a New Feature

1. **Identify the appropriate module**:
   - Data transformation? → `src/data_processing/`
   - File I/O? → `src/file_operations/`
   - User interaction? → `src/ui/`
   - Configuration? → `src/utils/config.py`

2. **Follow existing patterns**:
   - Use dataclasses for configuration
   - Add logging to new functions
   - Use type hints
   - Add docstrings with Args/Returns

3. **Update configuration if needed**:
   - Add new settings to appropriate `@dataclass` in `config.py`
   - Provide sensible defaults

4. **Test the change**:
   - Run with sample data
   - Check logs for errors
   - Verify output format

### Adding a New Distress Indicator

1. **Update `src/utils/config.py`**:
   ```python
   distress_columns: List[str] = field(default_factory=lambda: [
       "30-60-Days_Distress",
       # ... existing columns ...
       "YourNew_Distress",  # Add here
   ])
   ```

2. **Ensure CSV files contain the column**

3. **Update Excel formatting** in `excel_formatter.py` if needed

4. **Re-run processing** - automatic distress score calculation

### Adding a New Filter

1. **Add filter logic** to `src/ui/console_interface.py`:
   ```python
   def filter_by_your_column(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
       """Your filter description."""
       # Implementation
       return filtered_df
   ```

2. **Call from main pipeline** in `main.py`:
   ```python
   df = data_filter.filter_by_your_column(df, "ColumnName")
   ```

3. **Add logging** for filter results

### Modifying Excel Output

1. **Update formatting** in `src/file_operations/excel_formatter.py`:
   ```python
   # Modify header formats in ExcelFormatConfig
   main_header_format: Dict[str, any] = field(default_factory=lambda: {
       'bold': True,
       'font_color': '#FFFFFF',
       'bg_color': '#000000',  # Change colors here
   })
   ```

2. **Adjust column order** in `src/utils/config.py`:
   ```python
   display_order: List[str] = field(default_factory=lambda: [
       "FIPS", "PropertyID", ...  # Reorder here
   ])
   ```

---

## Code Conventions

### Python Style

**Follow PEP 8** with these specifics:

1. **Imports**:
   ```python
   # Standard library
   import os
   from pathlib import Path

   # Third-party
   import pandas as pd

   # Local modules
   from src.utils.logger import get_logger
   from src.utils.config import get_default_config
   ```

2. **Type Hints**: Always use type hints
   ```python
   def process_data(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
       """Process data with threshold."""
       return df
   ```

3. **Docstrings**: Use Google-style docstrings
   ```python
   def calculate_score(values: List[int]) -> float:
       """
       Calculate average score from values.

       Args:
           values: List of integer values to average

       Returns:
           Float average, or 0.0 if empty

       Example:
           >>> calculate_score([1, 2, 3])
           2.0
       """
       return sum(values) / len(values) if values else 0.0
   ```

4. **Constants**: UPPER_CASE for module-level constants
   ```python
   MAX_COLUMN_WIDTH = 50
   DEFAULT_ENCODING = 'utf-8'
   ```

5. **Private Methods**: Use single underscore prefix
   ```python
   def _internal_helper(self, data):
       """Private helper method."""
       pass
   ```

### Logging Conventions

1. **Module-level logger**:
   ```python
   from src.utils.logger import get_logger
   logger = get_logger(__name__)
   ```

2. **Log levels**:
   - `DEBUG`: Detailed debugging information
   - `INFO`: Major processing steps, counts, summaries
   - `WARNING`: Unexpected but handled situations
   - `ERROR`: Errors that prevent operation
   - `CRITICAL`: Critical failures

3. **Log messages**:
   ```python
   logger.info(f"Processing {len(files)} files")
   logger.warning(f"Missing column: {col_name}")
   logger.error(f"Failed to read file: {filepath}", exc_info=True)
   ```

### Configuration Conventions

1. **Use dataclasses** for all configuration
2. **Provide defaults** in `field(default_factory=...)`
3. **Validate in `__post_init__`** if needed
4. **Group related settings** in separate dataclasses
5. **Aggregate in AppConfig** for convenience

### File Naming

- **Modules**: `lowercase_with_underscores.py`
- **Classes**: `PascalCase`
- **Functions**: `lowercase_with_underscores()`
- **Constants**: `UPPER_CASE_WITH_UNDERSCORES`

### Error Handling

1. **Be specific** with exceptions:
   ```python
   try:
       df = pd.read_csv(filepath)
   except FileNotFoundError:
       logger.error(f"File not found: {filepath}")
       return None
   except pd.errors.ParserError:
       logger.error(f"Failed to parse CSV: {filepath}")
       return None
   ```

2. **Log errors** before raising/returning
3. **Provide context** in error messages
4. **Don't suppress exceptions** without logging

---

## Testing & Debugging

### Manual Testing Workflow

1. **Prepare test data**:
   ```bash
   mkdir -p customers/test_customer/input/raw_data
   # Copy sample CSV files to raw_data/
   ```

2. **Run with test customer**:
   ```bash
   python main_menu.py
   # Select test_customer
   ```

3. **Check logs**:
   ```bash
   tail -f logs/realestate_processor_$(date +%Y%m%d).log
   ```

4. **Verify output**:
   - Check `customers/test_customer/output/` for Excel files
   - Open and inspect formatting, data accuracy

### Debugging Tips

1. **Enable DEBUG logging**:
   ```python
   config = get_default_config(log_level='DEBUG')
   ```

2. **Add temporary print statements**:
   ```python
   logger.debug(f"DataFrame shape: {df.shape}")
   logger.debug(f"Columns: {df.columns.tolist()}")
   logger.debug(f"First row: {df.iloc[0].to_dict()}")
   ```

3. **Use DataFrame info methods**:
   ```python
   logger.debug(f"Info:\n{df.info()}")
   logger.debug(f"Describe:\n{df.describe()}")
   logger.debug(f"Null counts:\n{df.isnull().sum()}")
   ```

4. **Check intermediate steps**:
   - Save intermediate DataFrames to CSV for inspection
   - Add assertions to validate assumptions

### Common Issues & Solutions

**Issue**: Missing columns error
- **Cause**: CSV file doesn't have expected column names
- **Solution**: Check CSV column names, update `ColumnConfig` if needed

**Issue**: No data after filtering
- **Cause**: Filters too restrictive or data quality issues
- **Solution**: Check filter logic, validate input data quality

**Issue**: FIPS mapping fails
- **Cause**: Missing FIPs.xlsx file or incorrect format
- **Solution**: Verify file exists, has 'FIPS Code' and 'County' columns

**Issue**: Excel file not created
- **Cause**: openpyxl not installed or write permissions
- **Solution**: `pip install openpyxl`, check folder permissions

---

## Common Tasks

### Task 1: Process Data for a New Customer

```bash
# Step 1: Run menu
python main_menu.py

# Step 2: Select operation (1 or 2)
# Step 3: Create new customer (option 0)
# Step 4: Add CSV files to customers/{name}/input/raw_data/
# Step 5: Run menu again and process
```

### Task 2: Add a New Column to Output

1. Edit `src/utils/config.py`:
   ```python
   key_variables: List[str] = field(default_factory=lambda: [
       "LotSizeSqFt", "LTV", ..., "YourNewColumn"
   ])

   display_order: List[str] = field(default_factory=lambda: [
       "FIPS", "PropertyID", ..., "YourNewColumn"
   ])
   ```

2. Ensure CSV files contain the column

3. Re-run processing

### Task 3: Change Retention Percentage

Edit `src/utils/config.py`:
```python
@dataclass
class ProcessingConfig:
    percentage_to_retain: float = 0.8  # Change from 0.7 to 0.8 (80%)
```

### Task 4: Generate Dynamic Table Only

```bash
python dynamic_table_generator.py
# Or use main_menu.py and select option 1
```

### Task 5: View Customer Data

```bash
python main_menu.py
# Select option 3
# Choose customer
```

---

## Git Workflow

### Branch Naming Convention

- **Feature branches**: `claude/{description}-{session-id}`
- **Bug fixes**: `fix/{description}`
- **Experiments**: `experiment/{description}`

**Important**: When pushing, branch name must start with `claude/` and end with matching session ID, otherwise push will fail with 403.

### Commit Message Format

```
<type>: <short description>

<optional longer description>

<optional footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `docs`: Documentation changes
- `style`: Formatting, no code change
- `test`: Adding tests
- `chore`: Maintenance tasks

**Example**:
```
feat: Add support for multiple FIPS counties in single batch

- Added county aggregation logic
- Updated Excel formatter to include county summary
- Added tests for multi-county scenarios

Closes #123
```

### Git Operations

**Push to branch**:
```bash
git push -u origin claude/feature-name-session-id
```

**Retry logic for network failures**:
- Retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s)
- Apply to both push and fetch/pull operations

### Before Committing

1. **Check git status**: `git status`
2. **Review changes**: `git diff`
3. **Check recent commits**: `git log --oneline -5`
4. **Follow commit message style** from recent commits

### Pull Request Guidelines

When creating PRs:
1. **Clear title**: Describe what the PR does
2. **Summary**: Bulleted list of changes
3. **Test plan**: How to verify the changes
4. **Screenshots**: For UI changes

---

## Important Notes for AI Assistants

### Critical Conventions

1. **Never commit secrets**: Check for `.env`, credentials, API keys
2. **Preserve data privacy**: Don't commit actual customer CSV/Excel files
3. **Follow gitignore**: Respect patterns in `.gitignore`
4. **Use type hints**: Always add type annotations
5. **Add logging**: Every major operation should log
6. **Update documentation**: Keep README.md and this file in sync

### When Making Changes

1. **Read existing code first**: Understand patterns before modifying
2. **Match existing style**: Follow the conventions in the file
3. **Test thoroughly**: Use test customer data
4. **Check logs**: Ensure no errors or warnings
5. **Update docstrings**: Keep documentation current

### Code Reading Guidelines

1. **Start with `main.py`**: Understand the main workflow
2. **Then read `config.py`**: See all configuration options
3. **Check `processor.py`**: Core business logic
4. **Review UI files**: Understand user interaction
5. **Read docstrings**: They explain purpose and usage

### When Implementing Features

1. **Ask about requirements**: Clarify unclear specifications
2. **Propose approach**: Explain how you'll implement
3. **Show examples**: Provide code snippets for review
4. **Consider edge cases**: Handle errors gracefully
5. **Think about scale**: Will it work with large files?

### Configuration Philosophy

- **Centralized**: All config in `src/utils/config.py`
- **Type-safe**: Use dataclasses with type hints
- **Defaulted**: Provide sensible defaults
- **Documented**: Explain what each setting does
- **Validated**: Check values in `__post_init__` or `validate()`

### Logging Philosophy

- **Informative**: Help users understand what's happening
- **Structured**: Consistent format across modules
- **Leveled**: Use appropriate log levels
- **Contextual**: Include relevant data (counts, filenames)
- **Error-rich**: Include stack traces for errors

### UI/UX Philosophy

- **Clear**: Use descriptive prompts and messages
- **Colorful**: Use colors to indicate status (green=good, red=error)
- **Progressive**: Show progress for long operations
- **Helpful**: Provide guidance when errors occur
- **Professional**: Maintain professional tone in all messages

---

## Quick Reference

### File Locations

| Item | Path |
|------|------|
| Main entry (English) | `main.py` |
| Main entry (Spanish) | `loantype.py` |
| Interactive menu | `main_menu.py` |
| Dynamic table gen | `dynamic_table_generator.py` |
| Config | `src/utils/config.py` |
| Logger | `src/utils/logger.py` |
| Data processor | `src/data_processing/processor.py` |
| File handler | `src/file_operations/file_handler.py` |
| Excel formatter | `src/file_operations/excel_formatter.py` |
| UI | `src/ui/console_interface.py` |
| Customer data | `customers/{name}/` |
| Logs | `logs/` |
| FIPS mapping | `FIPs.xlsx` |

### Key Configuration Values

| Setting | Location | Default | Purpose |
|---------|----------|---------|---------|
| Retention % | `ProcessingConfig.percentage_to_retain` | 0.7 | Keep top 70% by distress |
| LTV threshold | `ProcessingConfig.ltv_max_threshold` | 999 | Max LTV allowed |
| Log level | `AppConfig.log_level` | INFO | Logging verbosity |
| Max column width | `ExcelFormatConfig.max_column_width` | 50 | Excel column width cap |
| Distress columns | `ColumnConfig.distress_columns` | 25 items | Distress indicators |

### Common Commands

```bash
# Run interactive menu
python main_menu.py

# Run main pipeline (English)
python main.py

# Run main pipeline (Spanish)
python loantype.py

# Generate dynamic table
python dynamic_table_generator.py

# Extract ZIP files
python zip.py

# Install dependencies
pip install -r requirements.txt

# View logs
tail -f logs/realestate_processor_$(date +%Y%m%d).log
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2025-11-19 | Customer-based organization, interactive menu, modular refactoring |
| 1.0.0 | Earlier | Original monolithic implementation |

---

## Additional Resources

- **README.md**: General project documentation
- **QUICK_START_GUIDE.md**: Getting started guide
- **DYNAMIC_TABLE_README.md**: Dynamic table generator details
- **customers/README.md**: Customer folder structure
- **.env.example**: Environment configuration template

---

## Contact & Support

For issues or questions:
1. Check log files in `logs/` directory
2. Review error messages in console output
3. Verify data format matches expected structure
4. Consult this documentation

---

**End of CLAUDE.md**
