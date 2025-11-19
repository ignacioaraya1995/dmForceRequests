"""
Configuration module for the Real Estate Data Processing Tool.
Centralizes all configuration settings, column definitions, and default values.
"""

import os
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, field


@dataclass
class ColumnConfig:
    """Configuration for data columns and their processing."""

    # Distress indicator columns
    distress_columns: List[str] = field(default_factory=lambda: [
        "30-60-Days_Distress", "Absentee", "Bankruptcy_Distress", "Debt-Collection_Distress",
        "Divorce_Distress", "Downsizing_Distress", "Estate_Distress", "Eviction_Distress",
        "Failed_Listing_Distress", "highEquity", "Inter_Family_Distress", "Judgment_Distress",
        "Lien_City_County_Distress", "Lien_HOA_Distress", "Lien_Mechanical_Distress",
        "Lien_Other_Distress", "Lien_Utility_Distress", "Low_income_Distress",
        "PoorCondition_Distress", "Preforeclosure_Distress", "Probate_Distress",
        "Prop_Vacant_Flag", "Senior_Distress", "Tax_Delinquent_Distress", "Violation_Distress"
    ])

    # Unique identifier columns for deduplication
    unique1_columns: List[str] = field(default_factory=lambda: [
        "MailingFullStreetAddress", "MailingZIP5"
    ])

    unique2_columns: List[str] = field(default_factory=lambda: [
        "SitusFullStreetAddress", "SitusZIP5"
    ])

    # FIPS code column
    fips_column: List[str] = field(default_factory=lambda: ["FIPS"])

    # Key property variables
    key_variables: List[str] = field(default_factory=lambda: [
        "LotSizeSqFt", "LTV", "MailingCity", "MailingState", "MailingStreet", "Owner_Type",
        "Owner1FirstName", "Owner1LastName", "OwnerNAME1FULL", "PropertyID", "saleDate",
        "SumLivingAreaSqFt", "totalValue", "Use_Type", "YearBuilt", "SitusCity",
        "SitusState", "Bedrooms", "IsListedFlag"
    ])

    # Column rename mapping for standardization
    rename_mapping: Dict[str, str] = field(default_factory=lambda: {
        "SitusFullStreetAddress": "PROPERTY ADDRESS",
        "SitusCity": "PROPERTY CITY",
        "SitusState": "PROPERTY STATE",
        "SitusZIP5": "PROPERTY ZIP",
        "MailingFullStreetAddress": "MAILING ADDRESS",
        "MailingCity": "MAILING CITY",
        "MailingState": "MAILING STATE",
        "MailingZIP5": "MAILING ZIP",
        "OwnerNAME1FULL": "OWNER FULL NAME",
        "Owner1FirstName": "OWNER FIRST NAME",
        "Owner1LastName": "OWNER LAST NAME",
        "Owner_Type": "OWNER TYPE",
        "Use_Type": "PROPERTY TYPE",
        "IsListedFlag": "LISTED FLAG"
    })

    # Display order for final output
    display_order: List[str] = field(default_factory=lambda: [
        "FIPS", "PropertyID", "SitusFullStreetAddress", "SitusCity", "SitusState", "SitusZIP5",
        "MailingFullStreetAddress", "MailingCity", "MailingState", "MailingZIP5", "OwnerNAME1FULL",
        "Owner1FirstName", "Owner1LastName", "Owner_Type", "LotSizeSqFt", "LTV", "saleDate",
        "SumLivingAreaSqFt", "totalValue", "Use_Type", "YearBuilt", "Bedrooms",
        "IsListedFlag", "DistressCounter"
    ])

    # Columns that require address validation (no nulls allowed)
    address_validation_columns: List[str] = field(default_factory=lambda: [
        "MailingFullStreetAddress", "MailingZIP5",
        "SitusFullStreetAddress", "SitusZIP5"
    ])

    # Text columns that should be title-cased
    title_case_columns: List[str] = field(default_factory=lambda: [
        'OWNER TYPE', 'PROPERTY TYPE', 'COUNTY'
    ])

    def get_all_columns(self) -> List[str]:
        """Get all columns that should be kept during processing."""
        return (self.distress_columns +
                self.unique1_columns +
                self.unique2_columns +
                self.fips_column +
                self.key_variables)


@dataclass
class ProcessingConfig:
    """Configuration for data processing parameters."""

    # Percentage of top records to retain based on distress score
    percentage_to_retain: float = 0.7

    # LTV (Loan-to-Value) threshold for filtering
    ltv_max_threshold: int = 999

    # Default encoding for CSV files
    csv_encoding: str = 'utf-8'

    # Pandas read options
    low_memory: bool = False

    def validate(self) -> None:
        """Validate configuration parameters."""
        if not 0 < self.percentage_to_retain <= 1:
            raise ValueError("percentage_to_retain must be between 0 and 1")

        if self.ltv_max_threshold <= 0:
            raise ValueError("ltv_max_threshold must be positive")


@dataclass
class PathConfig:
    """Configuration for file paths and directories."""

    # Base directory (project root)
    base_dir: Path = field(default_factory=lambda: Path.cwd())

    # Client name for folder organization
    client_name: str = ""

    # Data folder structure
    data_folder: str = "customers"
    input_folder_name: str = "input"
    raw_data_folder_name: str = "raw_data"  # Subfolder under input
    suppress_folder_name: str = "suppressed"  # Subfolder under input
    output_folder_name: str = "output"

    # Reference data
    fips_filename: str = "FIPs.xlsx"

    # Log folder
    log_folder: str = "logs"

    def __post_init__(self):
        """Convert string paths to Path objects."""
        self.base_dir = Path(self.base_dir)

    def set_client_name(self, client_name: str) -> None:
        """
        Set the client name for folder paths.

        Args:
            client_name: Name of the client
        """
        self.client_name = client_name

    @property
    def input_path(self) -> Path:
        """Get full input folder path (raw_data subfolder)."""
        if not self.client_name:
            raise ValueError("Client name must be set before accessing input path")
        return self.base_dir / self.data_folder / self.client_name / self.input_folder_name / self.raw_data_folder_name

    @property
    def suppress_path(self) -> Path:
        """Get full suppress folder path (suppressed subfolder under input)."""
        if not self.client_name:
            raise ValueError("Client name must be set before accessing suppress path")
        return self.base_dir / self.data_folder / self.client_name / self.input_folder_name / self.suppress_folder_name

    @property
    def output_path(self) -> Path:
        """Get full output folder path."""
        if not self.client_name:
            raise ValueError("Client name must be set before accessing output path")
        return self.base_dir / self.data_folder / self.client_name / self.output_folder_name

    @property
    def fips_file_path(self) -> Path:
        """Get full FIPS file path."""
        return self.base_dir / self.fips_filename

    @property
    def log_path(self) -> Path:
        """Get full log folder path."""
        return self.base_dir / self.log_folder

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.input_path.mkdir(parents=True, exist_ok=True)
        self.suppress_path.mkdir(parents=True, exist_ok=True)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.log_path.mkdir(parents=True, exist_ok=True)


@dataclass
class ExcelFormatConfig:
    """Configuration for Excel output formatting."""

    # Sheet name
    sheet_name: str = "Consolidated"

    # Header format for main columns
    main_header_format: Dict[str, any] = field(default_factory=lambda: {
        'bold': True,
        'font_color': '#FFFFFF',
        'bg_color': '#000000',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })

    # Header format for distress columns
    distress_header_format: Dict[str, any] = field(default_factory=lambda: {
        'bold': True,
        'font_color': '#000000',
        'bg_color': '#FFC000',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })

    # Maximum column width
    max_column_width: int = 50

    # Column width padding
    column_width_padding: int = 2


@dataclass
class LanguageConfig:
    """Configuration for multi-language support."""

    language: str = "en"  # 'en' for English, 'es' for Spanish

    # Language-specific messages
    messages: Dict[str, Dict[str, str]] = field(default_factory=lambda: {
        'en': {
            'start': "Starting the data consolidation and cleaning script...",
            'client_prompt': "Please enter the client's name: ",
            'client_empty': "The client's name cannot be empty.",
            'client_selected': "Client selected: {}",
            'folders_found': "Found {} folders to process: {}",
            'processing_complete': "Process completed successfully!",
        },
        'es': {
            'start': "Iniciando el script de consolidación y limpieza de datos...",
            'client_prompt': "Por favor ingrese el nombre del cliente: ",
            'client_empty': "El nombre del cliente no puede estar vacío.",
            'client_selected': "Cliente seleccionado: {}",
            'folders_found': "Se encontraron {} carpetas para procesar: {}",
            'processing_complete': "¡Proceso completado con éxito!",
        }
    })

    def get_message(self, key: str) -> str:
        """Get message in the configured language."""
        return self.messages.get(self.language, self.messages['en']).get(key, key)


class AppConfig:
    """Main application configuration aggregator."""

    def __init__(
        self,
        base_dir: str = None,
        language: str = "en",
        log_level: str = "INFO"
    ):
        """
        Initialize application configuration.

        Args:
            base_dir: Base directory for the application (defaults to current directory)
            language: Language code ('en' or 'es')
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.columns = ColumnConfig()
        self.processing = ProcessingConfig()
        self.paths = PathConfig(base_dir=Path(base_dir) if base_dir else Path.cwd())
        self.excel = ExcelFormatConfig()
        self.language = LanguageConfig(language=language)
        self.log_level = log_level

        # Validate configuration
        self.processing.validate()

    def ensure_setup(self) -> None:
        """Ensure all necessary directories exist."""
        self.paths.ensure_directories()


# Convenience function to get default configuration
def get_default_config(language: str = "en", log_level: str = "INFO") -> AppConfig:
    """
    Get default application configuration.

    Args:
        language: Language code ('en' or 'es')
        log_level: Logging level

    Returns:
        AppConfig instance with default settings
    """
    return AppConfig(language=language, log_level=log_level)
