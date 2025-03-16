"""
CSV handler utility for Vicky Hair Salon Management System.
"""
import os
import pandas as pd
import csv
from typing import Dict, List, Optional, Union, Any


class CSVHandler:
    """
    Handles CSV file operations for the salon management system.
    """
    def __init__(self, data_dir: str = 'data'):
        """
        Initialize the CSV handler.
        
        Args:
            data_dir: Directory where CSV files are stored
        """
        self.data_dir = data_dir
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """
        Ensure that all required directories exist.
        """
        os.makedirs(os.path.join(self.data_dir, 'staff'), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'entries'), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'reports'), exist_ok=True)
    
    def read_csv(self, file_path: str) -> pd.DataFrame:
        """
        Read a CSV file into a pandas DataFrame.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            DataFrame containing the CSV data
        """
        if not os.path.exists(file_path):
            return pd.DataFrame()
        
        return pd.read_csv(file_path)
    
    def write_csv(self, df: pd.DataFrame, file_path: str) -> None:
        """
        Write a pandas DataFrame to a CSV file.
        
        Args:
            df: DataFrame to write
            file_path: Path to the CSV file
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_csv(file_path, index=False)
    
    def append_to_csv(self, data: Dict[str, Any], file_path: str) -> None:
        """
        Append a row to a CSV file.
        
        Args:
            data: Dictionary containing the row data
            file_path: Path to the CSV file
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        file_exists = os.path.exists(file_path)
        
        with open(file_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(data.keys()))
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(data)
    
    def get_staff_data(self) -> pd.DataFrame:
        """
        Get staff data from the staff CSV file.
        
        Returns:
            DataFrame containing staff data
        """
        return self.read_csv(os.path.join(self.data_dir, 'staff', 'staff.csv'))
    
    def get_daily_entries(self) -> pd.DataFrame:
        """
        Get daily entries from the daily entries CSV file.
        
        Returns:
            DataFrame containing daily entries
        """
        return self.read_csv(os.path.join(self.data_dir, 'entries', 'daily_entries.csv'))
    
    def get_bulk_entries(self) -> pd.DataFrame:
        """
        Get bulk entries from the bulk entries CSV file.
        
        Returns:
            DataFrame containing bulk entries
        """
        return self.read_csv(os.path.join(self.data_dir, 'entries', 'bulk_entries.csv'))
    
    def save_report(self, df: pd.DataFrame, report_name: str) -> str:
        """
        Save a report to a CSV file.
        
        Args:
            df: DataFrame containing the report data
            report_name: Name of the report
            
        Returns:
            Path to the saved report
        """
        file_path = os.path.join(self.data_dir, 'reports', f"{report_name}.csv")
        self.write_csv(df, file_path)
        return file_path