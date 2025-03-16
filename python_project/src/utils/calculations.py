"""
Calculation utilities for Vicky Hair Salon Management System.
"""
import os
import pandas as pd
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta

from src.models.staff import Staff
from src.models.entry import DailyEntry, BulkEntry


def calculate_payouts(start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
    """
    Calculate payouts for all staff members for a given date range.
    
    Args:
        start_date: Start date for the calculation (YYYY-MM-DD)
        end_date: End date for the calculation (YYYY-MM-DD)
        
    Returns:
        DataFrame containing payout information for each staff member
    """
    # Load staff data
    staff_list = Staff.load_all()
    if not staff_list:
        return pd.DataFrame()
    
    # Load daily entries
    daily_entries = DailyEntry.load_all()
    
    # Load bulk entries
    bulk_entries = BulkEntry.load_all()
    
    # Filter entries by date range if provided
    if start_date:
        daily_entries = [entry for entry in daily_entries if entry.date >= start_date]
        bulk_entries = [entry for entry in bulk_entries if entry.date >= start_date]
    
    if end_date:
        daily_entries = [entry for entry in daily_entries if entry.date <= end_date]
        bulk_entries = [entry for entry in bulk_entries if entry.date <= end_date]
    
    # Calculate payouts for each staff member
    payouts = []
    
    for staff in staff_list:
        # Calculate daily entries payout
        daily_total = sum(entry.amount for entry in daily_entries if entry.staff_id == staff.id)
        daily_payout = daily_total * staff.commission_rate
        
        # Calculate bulk entries payout
        bulk_total = sum(entry.total for entry in bulk_entries if entry.staff_id == staff.id)
        bulk_payout = bulk_total * staff.commission_rate
        
        # Total payout
        total_revenue = daily_total + bulk_total
        total_payout = daily_payout + bulk_payout
        
        payouts.append({
            "staff_id": staff.id,
            "name": staff.name,
            "role": staff.role,
            "commission_rate": staff.commission_rate,
            "daily_revenue": daily_total,
            "daily_payout": daily_payout,
            "bulk_revenue": bulk_total,
            "bulk_payout": bulk_payout,
            "total_revenue": total_revenue,
            "total_payout": total_payout
        })
    
    return pd.DataFrame(payouts)


def generate_daily_report(date: Optional[str] = None) -> pd.DataFrame:
    """
    Generate a daily report for a specific date.
    
    Args:
        date: Date for the report (YYYY-MM-DD), defaults to today
        
    Returns:
        DataFrame containing the daily report
    """
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # Load daily entries for the date
    daily_entries = DailyEntry.load_all()
    daily_entries = [entry for entry in daily_entries if entry.date == date]
    
    # Load bulk entries for the date
    bulk_entries = BulkEntry.load_all()
    bulk_entries = [entry for entry in bulk_entries if entry.date == date]
    
    # Load staff data
    staff_dict = {staff.id: staff for staff in Staff.load_all()}
    
    # Prepare report data
    report_data = []
    
    # Process daily entries
    for entry in daily_entries:
        staff = staff_dict.get(entry.staff_id)
        if staff:
            report_data.append({
                "date": entry.date,
                "staff_id": entry.staff_id,
                "staff_name": staff.name,
                "entry_type": "Daily",
                "customer_name": entry.customer_name,
                "service": entry.service,
                "amount": entry.amount,
                "payout": entry.amount * staff.commission_rate
            })
    
    # Process bulk entries
    for entry in bulk_entries:
        staff = staff_dict.get(entry.staff_id)
        if staff:
            for i, amount in enumerate(entry.amounts):
                report_data.append({
                    "date": entry.date,
                    "staff_id": entry.staff_id,
                    "staff_name": staff.name,
                    "entry_type": "Bulk",
                    "customer_name": f"Customer_{i+1}",
                    "service": "Bulk Service",
                    "amount": amount,
                    "payout": amount * staff.commission_rate
                })
    
    return pd.DataFrame(report_data)


def generate_monthly_report(year: int, month: int) -> pd.DataFrame:
    """
    Generate a monthly report for a specific year and month.
    
    Args:
        year: Year for the report
        month: Month for the report (1-12)
        
    Returns:
        DataFrame containing the monthly report
    """
    # Generate start and end dates for the month
    start_date = f"{year}-{month:02d}-01"
    
    # Calculate the last day of the month
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    end_date = (datetime(next_year, next_month, 1) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Calculate payouts for the month
    payouts = calculate_payouts(start_date, end_date)
    
    # Add month information
    if not payouts.empty:
        payouts['year'] = year
        payouts['month'] = month
    
    return payouts


def generate_staff_performance_report() -> pd.DataFrame:
    """
    Generate a staff performance report.
    
    Returns:
        DataFrame containing the staff performance report
    """
    # Load staff data
    staff_list = Staff.load_all()
    
    # Load daily entries
    daily_entries = DailyEntry.load_all()
    
    # Load bulk entries
    bulk_entries = BulkEntry.load_all()
    
    # Calculate performance metrics for each staff member
    performance = []
    
    for staff in staff_list:
        # Daily entries metrics
        staff_daily_entries = [entry for entry in daily_entries if entry.staff_id == staff.id]
        daily_customers = len(staff_daily_entries)
        daily_revenue = sum(entry.amount for entry in staff_daily_entries)
        daily_avg_per_customer = daily_revenue / daily_customers if daily_customers > 0 else 0
        
        # Bulk entries metrics
        staff_bulk_entries = [entry for entry in bulk_entries if entry.staff_id == staff.id]
        bulk_customers = sum(entry.count for entry in staff_bulk_entries)
        bulk_revenue = sum(entry.total for entry in staff_bulk_entries)
        bulk_avg_per_customer = bulk_revenue / bulk_customers if bulk_customers > 0 else 0
        
        # Total metrics
        total_customers = daily_customers + bulk_customers
        total_revenue = daily_revenue + bulk_revenue
        total_avg_per_customer = total_revenue / total_customers if total_customers > 0 else 0
        
        performance.append({
            "staff_id": staff.id,
            "name": staff.name,
            "role": staff.role,
            "daily_customers": daily_customers,
            "daily_revenue": daily_revenue,
            "daily_avg_per_customer": daily_avg_per_customer,
            "bulk_customers": bulk_customers,
            "bulk_revenue": bulk_revenue,
            "bulk_avg_per_customer": bulk_avg_per_customer,
            "total_customers": total_customers,
            "total_revenue": total_revenue,
            "total_avg_per_customer": total_avg_per_customer
        })
    
    return pd.DataFrame(performance)