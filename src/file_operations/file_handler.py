"""
File operations module for handling CSV, Excel, and other file I/O.
Provides robust file reading, writing, and duplicate management.
"""

import pandas as pd
from pathlib import Path
from glob import glob
from typing import List, Set, Optional, Tuple
import zipfile

from src.utils.logger import get_logger
from src.utils.config import ProcessingConfig


logger = get_logger(__name__)


class FileReader:
    """Handles reading data files (CSV, Excel, etc.)."""

    def __init__(self, processing_config: ProcessingConfig):
        """
        Initialize the file reader.

        Args:
            processing_config: Processing configuration
        """
        self.processing_config = processing_config
        logger.info("FileReader initialized")

    def read_csv_files_from_folder(self, folder_path: Path) -> List[pd.DataFrame]:
        """
        Read all CSV files from a folder.

        Args:
            folder_path: Path to folder containing CSV files

        Returns:
            List of DataFrames read from CSV files
        """
        if not folder_path.exists():
            logger.warning(f"Folder does not exist: {folder_path}")
            return []

        if not folder_path.is_dir():
            logger.error(f"Path is not a directory: {folder_path}")
            return []

        # Find all CSV files
        csv_pattern = str(folder_path / "*.csv")
        csv_files = glob(csv_pattern)

        if not csv_files:
            logger.warning(f"No CSV files found in: {folder_path}")
            return []

        logger.info(f"Found {len(csv_files)} CSV file(s) in {folder_path}")

        dataframes = []
        for csv_file in csv_files:
            df = self.read_csv_file(Path(csv_file))
            if df is not None:
                dataframes.append(df)

        logger.info(f"Successfully read {len(dataframes)} CSV file(s)")

        return dataframes

    def read_csv_file(self, file_path: Path) -> Optional[pd.DataFrame]:
        """
        Read a single CSV file.

        Args:
            file_path: Path to CSV file

        Returns:
            DataFrame or None if error occurred
        """
        try:
            logger.debug(f"Reading CSV file: {file_path.name}")
            df = pd.read_csv(
                file_path,
                low_memory=self.processing_config.low_memory
            )
            logger.debug(f"Read {len(df):,} rows from {file_path.name}")
            return df

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return None

        except pd.errors.EmptyDataError:
            logger.warning(f"Empty CSV file: {file_path}")
            return None

        except Exception as e:
            logger.error(f"Error reading {file_path.name}: {e}", exc_info=True)
            return None

    def read_excel_file(self, file_path: Path, sheet_name: str = 0) -> Optional[pd.DataFrame]:
        """
        Read an Excel file.

        Args:
            file_path: Path to Excel file
            sheet_name: Sheet name or index to read

        Returns:
            DataFrame or None if error occurred
        """
        try:
            logger.debug(f"Reading Excel file: {file_path.name}")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            logger.debug(f"Read {len(df):,} rows from {file_path.name}")
            return df

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return None

        except Exception as e:
            logger.error(f"Error reading {file_path.name}: {e}", exc_info=True)
            return None


class DuplicateManager:
    """Manages duplicate address tracking and removal."""

    def __init__(self):
        """Initialize the duplicate manager."""
        logger.info("DuplicateManager initialized")

    def load_previous_addresses(self, dupes_folder: Path) -> Set[str]:
        """
        Load addresses from previous files in the dupes folder.

        Args:
            dupes_folder: Path to folder containing previous data files

        Returns:
            Set of lowercase addresses
        """
        if not dupes_folder.exists():
            logger.warning(f"Dupes folder does not exist: {dupes_folder}")
            return set()

        if not dupes_folder.is_dir():
            logger.error(f"Dupes path is not a directory: {dupes_folder}")
            return set()

        # Find CSV and Excel files
        csv_files = glob(str(dupes_folder / "*.csv"))
        xlsx_files = glob(str(dupes_folder / "*.xlsx"))
        all_files = csv_files + xlsx_files

        if not all_files:
            logger.warning(f"No CSV or XLSX files found in: {dupes_folder}")
            return set()

        logger.info(f"Found {len(all_files)} file(s) in dupes folder")

        addresses = set()

        for file_path in all_files:
            file_path = Path(file_path)
            file_addresses = self._extract_addresses_from_file(file_path)
            addresses.update(file_addresses)

        logger.info(f"Loaded {len(addresses):,} unique addresses from previous files")

        return addresses

    def _extract_addresses_from_file(self, file_path: Path) -> Set[str]:
        """
        Extract addresses from a single file.

        Args:
            file_path: Path to file (CSV or Excel)

        Returns:
            Set of lowercase addresses
        """
        try:
            logger.debug(f"Extracting addresses from: {file_path.name}")

            # Read file based on extension
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path, low_memory=False)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                logger.warning(f"Unsupported file type: {file_path.suffix}")
                return set()

            # Check for PROPERTY ADDRESS column
            if 'PROPERTY ADDRESS' not in df.columns:
                logger.warning(
                    f"File {file_path.name} does not contain 'PROPERTY ADDRESS' column"
                )
                return set()

            # Extract and clean addresses
            addresses = (
                df['PROPERTY ADDRESS']
                .dropna()
                .astype(str)
                .str.strip()
                .str.lower()
            )

            unique_addresses = set(addresses)
            logger.debug(f"Extracted {len(unique_addresses):,} addresses from {file_path.name}")

            return unique_addresses

        except Exception as e:
            logger.error(f"Error extracting addresses from {file_path.name}: {e}", exc_info=True)
            return set()


class ZipExtractor:
    """Handles ZIP file extraction."""

    def __init__(self):
        """Initialize the ZIP extractor."""
        logger.info("ZipExtractor initialized")

    def extract_zip_files(self, folder_path: Path, remove_after_extract: bool = True) -> int:
        """
        Extract all ZIP files in a folder.

        Args:
            folder_path: Path to folder containing ZIP files
            remove_after_extract: Whether to remove ZIP files after extraction

        Returns:
            Number of ZIP files extracted
        """
        if not folder_path.exists():
            logger.warning(f"Folder does not exist: {folder_path}")
            return 0

        zip_pattern = str(folder_path / "*.zip")
        zip_files = glob(zip_pattern)

        if not zip_files:
            logger.info(f"No ZIP files found in: {folder_path}")
            return 0

        logger.info(f"Found {len(zip_files)} ZIP file(s) to extract")

        extracted_count = 0
        for zip_path in zip_files:
            zip_path = Path(zip_path)
            if self.extract_zip_file(zip_path, folder_path, remove_after_extract):
                extracted_count += 1

        logger.info(f"Successfully extracted {extracted_count} ZIP file(s)")

        return extracted_count

    def extract_zip_file(
        self,
        zip_path: Path,
        extract_to: Path,
        remove_after_extract: bool = True
    ) -> bool:
        """
        Extract a single ZIP file.

        Args:
            zip_path: Path to ZIP file
            extract_to: Directory to extract files to
            remove_after_extract: Whether to remove ZIP file after extraction

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Extracting: {zip_path.name}")

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)

            logger.info(f"Successfully extracted: {zip_path.name}")

            # Remove ZIP file if requested
            if remove_after_extract:
                zip_path.unlink()
                logger.debug(f"Removed ZIP file: {zip_path.name}")

            return True

        except zipfile.BadZipFile:
            logger.error(f"Invalid ZIP file: {zip_path.name}")
            return False

        except Exception as e:
            logger.error(f"Error extracting {zip_path.name}: {e}", exc_info=True)
            return False


class FolderScanner:
    """Scans and manages folder structures."""

    def __init__(self):
        """Initialize the folder scanner."""
        logger.debug("FolderScanner initialized")

    def get_folders_to_process(
        self,
        base_dir: Path,
        folder_names: List[str]
    ) -> List[Path]:
        """
        Get list of folders that exist and are ready to process.

        Args:
            base_dir: Base directory to search in
            folder_names: List of folder names to look for

        Returns:
            List of Path objects for existing folders
        """
        existing_folders = []

        for folder_name in folder_names:
            folder_path = base_dir / folder_name
            if folder_path.exists() and folder_path.is_dir():
                existing_folders.append(folder_path)
                logger.debug(f"Found folder: {folder_name}")
            else:
                logger.warning(f"Folder not found: {folder_name}")

        logger.info(f"Found {len(existing_folders)} folder(s) to process")

        return existing_folders

    def ensure_folder_exists(self, folder_path: Path) -> bool:
        """
        Ensure a folder exists, creating it if necessary.

        Args:
            folder_path: Path to folder

        Returns:
            True if folder exists or was created, False on error
        """
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured folder exists: {folder_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating folder {folder_path}: {e}", exc_info=True)
            return False

    def get_file_count(self, folder_path: Path, pattern: str = "*") -> int:
        """
        Get count of files matching pattern in folder.

        Args:
            folder_path: Path to folder
            pattern: Glob pattern (e.g., "*.csv")

        Returns:
            Number of matching files
        """
        if not folder_path.exists():
            return 0

        files = list(folder_path.glob(pattern))
        return len(files)
