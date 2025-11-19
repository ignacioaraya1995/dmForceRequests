#!/usr/bin/env python3
"""
Real Estate Property Data Consolidation Tool
Main entry point - Interactive Menu System

This is the main entry point for the Data Processing System.
It provides an interactive menu for:
  1. Generate Dynamic Summary Table (Pivot Analysis)
  2. Process Real Estate Data (Main Pipeline)
  3. View Customer Information

The old main.py has been backed up as main_old.py
"""

from main_menu import MainMenu

if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
