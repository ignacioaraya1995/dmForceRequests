#!/usr/bin/env python3
"""
Data Analysis Tool - Client Data Processor
Main entry point for selecting and analyzing client data.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime


class ClientDataAnalyzer:
    """Handles client data discovery, validation, and analysis."""

    # Required folder structure for each client
    REQUIRED_FOLDERS = ["request form", "suppressed file", "raw data"]

    # Supported file extensions
    VALID_EXTENSIONS = ['.csv', '.xlsx', '.xls']

    def __init__(self, input_base_path: str = "data/input", output_base_path: str = "data/output"):
        """Initialize the analyzer with base paths."""
        self.input_base = Path(input_base_path)
        self.output_base = Path(output_base_path)

        # Ensure output directory exists
        self.output_base.mkdir(parents=True, exist_ok=True)

    def discover_clients(self) -> List[str]:
        """
        Discover available client folders in the input directory.

        Returns:
            List of client folder names
        """
        if not self.input_base.exists():
            print(f"❌ Input directory not found: {self.input_base}")
            return []

        clients = []
        for item in self.input_base.iterdir():
            if item.is_dir():
                clients.append(item.name)

        return sorted(clients)

    def validate_client_structure(self, client_name: str) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate that a client folder has the required structure and files.

        Args:
            client_name: Name of the client folder

        Returns:
            Tuple of (is_valid, files_dict) where files_dict maps folder names to file lists
        """
        client_path = self.input_base / client_name
        files_found = {}
        is_valid = True

        print(f"\n{'='*60}")
        print(f"Validating client: {client_name}")
        print(f"{'='*60}")

        for folder in self.REQUIRED_FOLDERS:
            folder_path = client_path / folder

            if not folder_path.exists():
                print(f"❌ Missing folder: {folder}")
                is_valid = False
                files_found[folder] = []
                continue

            # Find all valid files in the folder
            valid_files = [
                f.name for f in folder_path.iterdir()
                if f.is_file() and f.suffix.lower() in self.VALID_EXTENSIONS
            ]

            files_found[folder] = valid_files

            if not valid_files:
                print(f"❌ No valid files in '{folder}' (expected CSV or Excel files)")
                is_valid = False
            else:
                print(f"✅ Folder '{folder}' - Found {len(valid_files)} file(s):")
                for file in valid_files:
                    print(f"   📄 {file}")

        return is_valid, files_found

    def display_clients(self, clients: List[str]) -> None:
        """Display available clients in a formatted menu."""
        print("\n" + "="*60)
        print("AVAILABLE CLIENTS")
        print("="*60)

        if not clients:
            print("❌ No client folders found in data/input/")
            return

        for idx, client in enumerate(clients, 1):
            print(f"{idx}. {client}")

    def get_client_selection(self, clients: List[str]) -> List[str]:
        """
        Prompt user to select clients for analysis.

        Args:
            clients: List of available client names

        Returns:
            List of selected client names
        """
        if not clients:
            return []

        print("\n" + "-"*60)
        print("Enter client number(s) to analyze:")
        print("  - Single: 1")
        print("  - Multiple: 1,3,5")
        print("  - All: 'all'")
        print("  - Quit: 'q'")
        print("-"*60)

        while True:
            try:
                selection = input("\nYour selection: ").strip().lower()

                if selection == 'q':
                    print("👋 Exiting...")
                    return []

                if selection == 'all':
                    return clients

                # Parse comma-separated numbers
                indices = [int(x.strip()) for x in selection.split(',')]

                # Validate indices
                selected_clients = []
                for idx in indices:
                    if 1 <= idx <= len(clients):
                        selected_clients.append(clients[idx - 1])
                    else:
                        print(f"❌ Invalid selection: {idx} (must be between 1 and {len(clients)})")
                        break
                else:
                    # All indices valid
                    return selected_clients

            except ValueError:
                print("❌ Invalid input. Please enter numbers separated by commas, 'all', or 'q'")
            except KeyboardInterrupt:
                print("\n👋 Exiting...")
                return []

    def process_client(self, client_name: str) -> bool:
        """
        Process a single client's data.

        Args:
            client_name: Name of the client to process

        Returns:
            True if processing was successful, False otherwise
        """
        # Validate structure and get files
        is_valid, files_found = self.validate_client_structure(client_name)

        if not is_valid:
            print(f"\n❌ Client '{client_name}' validation failed. Skipping...\n")
            return False

        print(f"\n✅ Client '{client_name}' validated successfully!")

        # Create output directory for this client
        output_dir = self.output_base / client_name
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"📁 Output directory ready: {output_dir}")

        # TODO: Add actual data analysis logic here
        # For now, just showing the discovered files
        print(f"\n📊 Ready to analyze data for '{client_name}'")
        print("   (Analysis logic to be implemented)")

        return True

    def run(self) -> None:
        """Main execution flow."""
        print("\n" + "="*60)
        print("DATA ANALYSIS TOOL - CLIENT DATA PROCESSOR")
        print("="*60)

        # Discover available clients
        clients = self.discover_clients()

        if not clients:
            print("\n❌ No clients found. Please add client folders to data/input/")
            print(f"   Each client folder should contain:")
            for folder in self.REQUIRED_FOLDERS:
                print(f"   - {folder}/")
            return

        # Display available clients
        self.display_clients(clients)

        # Get user selection
        selected_clients = self.get_client_selection(clients)

        if not selected_clients:
            return

        # Process each selected client
        print(f"\n{'='*60}")
        print(f"PROCESSING {len(selected_clients)} CLIENT(S)")
        print(f"{'='*60}")

        success_count = 0
        for client in selected_clients:
            if self.process_client(client):
                success_count += 1

        # Summary
        print(f"\n{'='*60}")
        print(f"PROCESSING COMPLETE")
        print(f"{'='*60}")
        print(f"✅ Successful: {success_count}/{len(selected_clients)}")
        print(f"❌ Failed: {len(selected_clients) - success_count}/{len(selected_clients)}")


def main():
    """Entry point for the application."""
    try:
        analyzer = ClientDataAnalyzer()
        analyzer.run()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
