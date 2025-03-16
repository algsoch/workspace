"""
Staff model for Vicky Hair Salon Management System.
"""
import os
import pandas as pd
from typing import Dict, List, Optional, Union


class Staff:
    """
    Represents a staff member at the salon.
    """
    def __init__(self, id: int, name: str, role: str, commission_rate: float):
        """
        Initialize a staff member.
        
        Args:
            id: Unique identifier for the staff member
            name: Name of the staff member
            role: Role of the staff member (e.g., Owner, Stylist, Assistant)
            commission_rate: Commission rate for the staff member (0.0-1.0)
        """
        self.id = id
        self.name = name
        self.role = role
        self.commission_rate = commission_rate
    
    def to_dict(self) -> Dict:
        """
        Convert staff member to dictionary.
        
        Returns:
            Dictionary representation of the staff member
        """
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "commission_rate": self.commission_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Staff':
        """
        Create a staff member from dictionary.
        
        Args:
            data: Dictionary containing staff member data
            
        Returns:
            Staff instance
        """
        return cls(
            id=data["id"],
            name=data["name"],
            role=data["role"],
            commission_rate=data["commission_rate"]
        )
    
    @classmethod
    def load_all(cls, file_path: str = 'data/staff/staff.csv') -> List['Staff']:
        """
        Load all staff members from CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of Staff instances
        """
        if not os.path.exists(file_path):
            return []
        
        df = pd.read_csv(file_path)
        return [cls.from_dict(row) for _, row in df.iterrows()]
    
    @classmethod
    def save_all(cls, staff_list: List['Staff'], file_path: str = 'data/staff/staff.csv') -> None:
        """
        Save all staff members to CSV file.
        
        Args:
            staff_list: List of Staff instances
            file_path: Path to the CSV file
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df = pd.DataFrame([staff.to_dict() for staff in staff_list])
        df.to_csv(file_path, index=False)
    
    @classmethod
    def get_by_id(cls, staff_id: int, file_path: str = 'data/staff/staff.csv') -> Optional['Staff']:
        """
        Get a staff member by ID.
        
        Args:
            staff_id: ID of the staff member
            file_path: Path to the CSV file
            
        Returns:
            Staff instance if found, None otherwise
        """
        staff_list = cls.load_all(file_path)
        for staff in staff_list:
            if staff.id == staff_id:
                return staff
        return None