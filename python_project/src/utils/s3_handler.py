import os
import io
import boto3
import pandas as pd
from typing import Dict, Any, Optional

class S3Handler:
    """
    Handles S3 file operations for the salon management system.
    This class can be used as a replacement for CSVHandler when deploying to Vercel.
    """
    def __init__(self, bucket_name: Optional[str] = None):
        """
        Initialize the S3 handler.
        
        Args:
            bucket_name: Name of the S3 bucket to use
        """
        self.bucket_name = bucket_name or os.environ.get('S3_BUCKET_NAME')
        if not self.bucket_name:
            raise ValueError("S3 bucket name must be provided or set as S3_BUCKET_NAME environment variable")
        
        # Initialize S3 client
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        
        # Ensure required directories exist in S3
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """
        Ensure that all required directories exist in S3.
        In S3, directories are represented by objects with trailing slashes.
        """
        directories = [
            'staff/',
            'entries/',
            'reports/',
            'users/'
        ]
        
        for directory in directories:
            try:
                self.s3.put_object(
                    Bucket=self.bucket_name,
                    Key=directory,
                    Body=''
                )
            except Exception as e:
                print(f"Warning: Could not create directory {directory}: {e}")
    
    def read_csv(self, file_path: str) -> pd.DataFrame:
        """
        Read a CSV file from S3 into a pandas DataFrame.
        
        Args:
            file_path: Path to the CSV file in S3
            
        Returns:
            DataFrame containing the CSV data
        """
        try:
            # Remove leading slash if present
            if file_path.startswith('/'):
                file_path = file_path[1:]
                
            # Get the object from S3
            response = self.s3.get_object(Bucket=self.bucket_name, Key=file_path)
            
            # Read the CSV data
            return pd.read_csv(io.BytesIO(response['Body'].read()))
        except self.s3.exceptions.NoSuchKey:
            # Return empty DataFrame if file doesn't exist
            return pd.DataFrame()
        except Exception as e:
            print(f"Error reading {file_path} from S3: {e}")
            return pd.DataFrame()
    
    def write_csv(self, df: pd.DataFrame, file_path: str) -> None:
        """
        Write a pandas DataFrame to a CSV file in S3.
        
        Args:
            df: DataFrame to write
            file_path: Path to the CSV file in S3
        """
        try:
            # Remove leading slash if present
            if file_path.startswith('/'):
                file_path = file_path[1:]
            
            # Convert DataFrame to CSV
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            
            # Upload to S3
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=csv_buffer.getvalue()
            )
        except Exception as e:
            print(f"Error writing to {file_path} in S3: {e}")
    
    def append_to_csv(self, data: Dict[str, Any], file_path: str) -> None:
        """
        Append a row to a CSV file in S3.
        
        Args:
            data: Dictionary containing the row data
            file_path: Path to the CSV file in S3
        """
        # Read existing data
        df = self.read_csv(file_path)
        
        # Append new row
        new_row = pd.DataFrame([data])
        if df.empty:
            df = new_row
        else:
            df = pd.concat([df, new_row], ignore_index=True)
        
        # Write back to S3
        self.write_csv(df, file_path)
    
    def get_staff_data(self) -> pd.DataFrame:
        """
        Get staff data from the staff CSV file in S3.
        
        Returns:
            DataFrame containing staff data
        """
        return self.read_csv('data/staff/staff.csv')
    
    def get_daily_entries(self) -> pd.DataFrame:
        """
        Get daily entries from the daily entries CSV file in S3.
        
        Returns:
            DataFrame containing daily entries
        """
        return self.read_csv('data/entries/daily_entries.csv')
    
    def get_bulk_entries(self) -> pd.DataFrame:
        """
        Get bulk entries from the bulk entries CSV file in S3.
        
        Returns:
            DataFrame containing bulk entries
        """
        return self.read_csv('data/entries/bulk_entries.csv')
    
    def save_report(self, df: pd.DataFrame, report_name: str) -> str:
        """
        Save a report to a CSV file in S3.
        
        Args:
            df: DataFrame containing the report data
            report_name: Name of the report
            
        Returns:
            Path to the saved report
        """
        file_path = f"data/reports/{report_name}.csv"
        self.write_csv(df, file_path)
        return file_path