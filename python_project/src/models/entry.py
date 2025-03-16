"""
Entry models for Vicky Hair Salon Management System.
"""
import os
import pandas as pd
from typing import Dict, List, Optional, Union
from datetime import datetime


class DailyEntry:
    """
    Represents a daily entry for a customer visit.
    """
    def __init__(self, date: str, staff_id: int, service: str, amount: float,
                 customer_name: Optional[str] = "Walk-in Customer", entry_id: Optional[int] = None):
        """
        Initialize a daily entry.

        Args:
            date: Date of the entry (YYYY-MM-DD)
            staff_id: ID of the staff member who served the customer
            service: Service provided
            amount: Amount paid by the customer
            customer_name: Name of the customer (optional, defaults to "Walk-in Customer")
            entry_id: Unique identifier for the entry (auto-generated if None)
        """
        self.date = date
        self.staff_id = staff_id
        self.customer_name = customer_name if customer_name else "Walk-in Customer"
        self.service = service
        self.amount = amount
        self.entry_id = entry_id
    
    def to_dict(self) -> Dict:
        """
        Convert daily entry to dictionary.
        
        Returns:
            Dictionary representation of the daily entry
        """
        return {
            "date": self.date,
            "staff_id": self.staff_id,
            "customer_name": self.customer_name,
            "service": self.service,
            "amount": self.amount,
            "entry_id": self.entry_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DailyEntry':
        """
        Create a daily entry from dictionary.

        Args:
            data: Dictionary containing daily entry data

        Returns:
            DailyEntry instance
        """
        return cls(
            date=data["date"],
            staff_id=data["staff_id"],
            service=data["service"],
            amount=data["amount"],
            customer_name=data.get("customer_name", "Walk-in Customer"),
            entry_id=data.get("entry_id")
        )
    
    @classmethod
    def load_all(cls, file_path: str = 'data/entries/daily_entries.csv') -> List['DailyEntry']:
        """
        Load all daily entries from CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of DailyEntry instances
        """
        if not os.path.exists(file_path):
            return []
        
        df = pd.read_csv(file_path)
        return [cls.from_dict(row) for _, row in df.iterrows()]
    
    @classmethod
    def save_all(cls, entries: List['DailyEntry'], file_path: str = 'data/entries/daily_entries.csv') -> None:
        """
        Save all daily entries to CSV file.
        
        Args:
            entries: List of DailyEntry instances
            file_path: Path to the CSV file
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Generate entry_ids if not present
        for i, entry in enumerate(entries):
            if entry.entry_id is None:
                entry.entry_id = i + 1
        
        df = pd.DataFrame([entry.to_dict() for entry in entries])
        df.to_csv(file_path, index=False)
    
    @classmethod
    def add_entry(cls, entry: 'DailyEntry', file_path: str = 'data/entries/daily_entries.csv') -> None:
        """
        Add a new daily entry to the CSV file.
        
        Args:
            entry: DailyEntry instance
            file_path: Path to the CSV file
        """
        entries = cls.load_all(file_path)
        
        # Generate entry_id if not present
        if entry.entry_id is None:
            entry.entry_id = len(entries) + 1
        
        entries.append(entry)
        cls.save_all(entries, file_path)


class BulkEntry:
    """
    Represents a bulk entry for multiple customer visits.
    """
    def __init__(self, date: str, staff_id: int, amounts: List[float], 
                 entry_id: Optional[int] = None):
        """
        Initialize a bulk entry.
        
        Args:
            date: Date of the entry (YYYY-MM-DD)
            staff_id: ID of the staff member who served the customers
            amounts: List of amounts paid by each customer
            entry_id: Unique identifier for the entry (auto-generated if None)
        """
        self.date = date
        self.staff_id = staff_id
        self.amounts = amounts
        self.count = len(amounts)
        self.total = sum(amounts)
        self.entry_id = entry_id
    
    def to_dict(self) -> Dict:
        """
        Convert bulk entry to dictionary.
        
        Returns:
            Dictionary representation of the bulk entry
        """
        return {
            "date": self.date,
            "staff_id": self.staff_id,
            "amounts": ",".join(map(str, self.amounts)),
            "count": self.count,
            "total": self.total,
            "entry_id": self.entry_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BulkEntry':
        """
        Create a bulk entry from dictionary.
        
        Args:
            data: Dictionary containing bulk entry data
            
        Returns:
            BulkEntry instance
        """
        amounts = [float(amount) for amount in data["amounts"].split(",")]
        return cls(
            date=data["date"],
            staff_id=data["staff_id"],
            amounts=amounts,
            entry_id=data.get("entry_id")
        )
    
    @classmethod
    def load_all(cls, file_path: str = 'data/entries/bulk_entries.csv') -> List['BulkEntry']:
        """
        Load all bulk entries from CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of BulkEntry instances
        """
        if not os.path.exists(file_path):
            return []
        
        df = pd.read_csv(file_path)
        return [cls.from_dict(row) for _, row in df.iterrows()]
    
    @classmethod
    def save_all(cls, entries: List['BulkEntry'], file_path: str = 'data/entries/bulk_entries.csv') -> None:
        """
        Save all bulk entries to CSV file.
        
        Args:
            entries: List of BulkEntry instances
            file_path: Path to the CSV file
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Generate entry_ids if not present
        for i, entry in enumerate(entries):
            if entry.entry_id is None:
                entry.entry_id = i + 1
        
        df = pd.DataFrame([entry.to_dict() for entry in entries])
        df.to_csv(file_path, index=False)
    
    @classmethod
    def add_entry(cls, entry: 'BulkEntry', file_path: str = 'data/entries/bulk_entries.csv') -> None:
        """
        Add a new bulk entry to the CSV file.
        
        Args:
            entry: BulkEntry instance
            file_path: Path to the CSV file
        """
        entries = cls.load_all(file_path)
        
        # Generate entry_id if not present
        if entry.entry_id is None:
            entry.entry_id = len(entries) + 1
        
        entries.append(entry)
        cls.save_all(entries, file_path)