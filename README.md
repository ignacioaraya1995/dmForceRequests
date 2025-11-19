# Data Analysis Tool - Client Data Processor

A Python-based tool for analyzing client data from standardized folder structures. The tool discovers available clients, validates their data structure, and processes their files for analysis.

## Features

- 🔍 Automatic client discovery from folder structure
- ✅ Data validation (ensures required folders and files exist)
- 📊 Support for CSV and Excel files (.csv, .xlsx, .xls)
- 🐳 Docker support for cross-platform compatibility
- 📁 Organized output structure per client

## Project Structure

```
dmForceRequests/
├── data/
│   ├── input/               # Input data organized by client
│   │   ├── ClientA/
│   │   │   ├── requestForm/     # Excel/CSV files
│   │   │   ├── suppressFile/    # Excel/CSV files
│   │   │   └── rawData/         # Excel/CSV files
│   │   └── ClientB/
│   │       ├── requestForm/
│   │       ├── suppressFile/
│   │       └── rawData/
│   └── output/              # Analysis results
│       ├── ClientA/
│       └── ClientB/
├── main.py                  # Main application
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
└── requirements.txt        # Python dependencies
```

## Requirements

### Option 1: Docker (Recommended for Windows)
- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))

### Option 2: Local Python
- Python 3.11 or higher
- pip (Python package manager)

## Setup Instructions

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   cd dmForceRequests
   ```

2. **Prepare your data**
   - Place client folders in `data/input/`
   - Each client folder must contain three subfolders:
     - `requestForm/`
     - `suppressFile/`
     - `rawData/`
   - Each subfolder should contain at least one CSV or Excel file

3. **Build the Docker image**
   ```bash
   docker-compose build
   ```

4. **Run the application**
   ```bash
   docker-compose run --rm data-analyzer
   ```

### Using Local Python

1. **Clone the repository**
   ```bash
   cd dmForceRequests
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare your data** (same as Docker setup above)

5. **Run the application**
   ```bash
   python main.py
   ```

## Usage

1. **Start the application** using either Docker or Python method above

2. **Select clients to analyze**
   - The tool will display all available clients found in `data/input/`
   - Choose one or more clients by entering their numbers (e.g., `1` or `1,3,5`)
   - Or type `all` to process all clients
   - Type `q` to quit

3. **View validation results**
   - The tool will validate each client's folder structure
   - It will list all files found in each required folder
   - Validation failures will be clearly marked

4. **Review output**
   - Processed results will be saved in `data/output/{ClientName}/`
   - Each client gets its own output directory

## Example Session

```
============================================================
DATA ANALYSIS TOOL - CLIENT DATA PROCESSOR
============================================================

============================================================
AVAILABLE CLIENTS
============================================================
1. Acme Corp
2. Beta Industries
3. Gamma Solutions

------------------------------------------------------------
Enter client number(s) to analyze:
  - Single: 1
  - Multiple: 1,3,5
  - All: 'all'
  - Quit: 'q'
------------------------------------------------------------

Your selection: 1

============================================================
PROCESSING 1 CLIENT(S)
============================================================

============================================================
Validating client: Acme Corp
============================================================
✅ Folder 'requestForm' - Found 1 file(s):
   📄 request_form_2024.xlsx
✅ Folder 'suppressFile' - Found 1 file(s):
   📄 suppressed_data.csv
✅ Folder 'rawData' - Found 2 file(s):
   📄 raw_data_jan.xlsx
   📄 raw_data_feb.xlsx

✅ Client 'Acme Corp' validated successfully!
📁 Output directory ready: data/output/Acme Corp
```

## Docker Commands Reference

```bash
# Build the image
docker-compose build

# Run the application interactively
docker-compose run --rm data-analyzer

# Rebuild after code changes
docker-compose build --no-cache

# View Docker logs
docker-compose logs
```

## Troubleshooting

### Windows Users

**Issue: Line ending problems**
- Git may convert line endings automatically
- Solution: Ensure `.gitattributes` is configured properly

**Issue: Docker not starting**
- Ensure Docker Desktop is running
- Check virtualization is enabled in BIOS

### Data Not Found

**Issue: "No clients found"**
- Verify client folders exist in `data/input/`
- Ensure folder names don't have special characters
- Check folder permissions

**Issue: "No valid files"**
- Verify files are CSV or Excel format (.csv, .xlsx, .xls)
- Check files aren't corrupted
- Ensure files have proper extensions

## Development

### Adding New Analysis Features

The main analysis logic is in the `process_client()` method in `main.py`. To add new analysis features:

1. Import required libraries at the top of `main.py`
2. Implement your analysis logic in `process_client()`
3. Save results to the client's output directory

### Project Dependencies

Key libraries included:
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `openpyxl` - Excel file support
- `matplotlib`, `seaborn` - Data visualization (for future use)

## License

[Add your license here]

## Support

For issues or questions, please contact [your contact information]
