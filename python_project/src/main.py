import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import random
import csv

# Add the project directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.entry import DailyEntry, BulkEntry
from src.models.staff import Staff
from src.utils.csv_handler import CSVHandler
from src.utils.calculations import calculate_payouts, generate_daily_report, generate_monthly_report, generate_staff_performance_report

def main():
    print("Welcome to Vicky Hair Salon Management System!")
    print("-" * 50)

    # Initialize handlers
    csv_handler = CSVHandler()

    # Demo functionality
    print("\n1. Creating sample staff data...")
    create_sample_staff()

    print("\n2. Creating sample daily entries...")
    create_sample_daily_entries()

    print("\n3. Creating sample bulk entries...")
    create_sample_bulk_entries()

    print("\n4. Generating reports...")
    generate_reports()

    print("\nAll operations completed successfully!")

def create_sample_staff():
    # Create staff directory if it doesn't exist
    os.makedirs('data/staff', exist_ok=True)

    # Sample staff data
    staff_data = [
        {"id": 1, "name": "Victoria", "role": "Owner", "commission_rate": 1.0},
        {"id": 2, "name": "John", "role": "Stylist", "commission_rate": 0.5},
        {"id": 3, "name": "Emma", "role": "Assistant", "commission_rate": 0.5},
        {"id": 4, "name": "Mike", "role": "Colorist", "commission_rate": 0.5}
    ]

    # Create Staff objects and save them
    staff_list = [Staff(**data) for data in staff_data]
    Staff.save_all(staff_list)

    print(f"Created {len(staff_data)} staff records")
    for staff in staff_list:
        print(f"ID: {staff.id}, Name: {staff.name}, Role: {staff.role}, Commission Rate: {staff.commission_rate}")

def create_sample_daily_entries():
    # Load staff
    staff_list = Staff.load_all()
    staff_ids = [staff.id for staff in staff_list]

    # Generate random daily entries for the past week
    daily_entries = []
    today = datetime.now()

    for i in range(7):
        entry_date = (today - timedelta(days=i)).strftime('%Y-%m-%d')

        # Random entries for each staff member
        for staff_id in staff_ids:
            num_customers = random.randint(3, 10)
            for _ in range(num_customers):
                daily_entries.append(DailyEntry(
                    date=entry_date,
                    staff_id=staff_id,
                    customer_name=f"Customer_{random.randint(1, 100)}",
                    service=random.choice(["Haircut", "Color", "Style", "Treatment"]),
                    amount=random.randint(20, 200)
                ))

    # Save daily entries
    DailyEntry.save_all(daily_entries)

    print(f"Created {len(daily_entries)} daily entries")
    print(f"Sample entry: {daily_entries[0].to_dict()}")

def create_sample_bulk_entries():
    # Generate a sample bulk entry file
    bulk_entries = []
    entry_date = datetime.now().strftime('%Y-%m-%d')

    # Staff member 2 bulk entry
    staff_id = 2
    customers = [30, 45, 60, 25, 100]  # Amounts for each customer
    bulk_entries.append(BulkEntry(
        date=entry_date,
        staff_id=staff_id,
        amounts=customers
    ))

    # Staff member 3 bulk entry
    staff_id = 3
    customers = [40, 55, 65, 30]  # Amounts for each customer
    bulk_entries.append(BulkEntry(
        date=entry_date,
        staff_id=staff_id,
        amounts=customers
    ))

    # Staff member 4 bulk entry
    staff_id = 4
    customers = [50, 75, 35, 40, 60, 90]  # Amounts for each customer
    bulk_entries.append(BulkEntry(
        date=entry_date,
        staff_id=staff_id,
        amounts=customers
    ))

    # Save bulk entries
    BulkEntry.save_all(bulk_entries)

    print(f"Created {len(bulk_entries)} bulk entries")
    for entry in bulk_entries:
        print(f"Staff ID: {entry.staff_id}, Date: {entry.date}, Customers: {entry.count}, Total: ${entry.total}")

def generate_reports():
    # Create reports directory if it doesn't exist
    os.makedirs('data/reports', exist_ok=True)

    # Generate daily report
    print("\n4.1. Generating daily report...")
    today = datetime.now().strftime('%Y-%m-%d')
    daily_report = generate_daily_report(today)
    daily_report_path = f"data/reports/daily_report_{today}.csv"
    daily_report.to_csv(daily_report_path, index=False)
    print(f"Daily report saved to {daily_report_path}")
    print(daily_report.head())

    # Generate monthly report
    print("\n4.2. Generating monthly report...")
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_report = generate_monthly_report(current_year, current_month)
    monthly_report_path = f"data/reports/monthly_report_{current_year}_{current_month:02d}.csv"
    monthly_report.to_csv(monthly_report_path, index=False)
    print(f"Monthly report saved to {monthly_report_path}")
    print(monthly_report.head())

    # Generate staff performance report
    print("\n4.3. Generating staff performance report...")
    performance_report = generate_staff_performance_report()
    performance_report_path = f"data/reports/staff_performance_report.csv"
    performance_report.to_csv(performance_report_path, index=False)
    print(f"Staff performance report saved to {performance_report_path}")
    print(performance_report)

    # Generate payout report
    print("\n4.4. Generating payout report...")
    payout_report = calculate_payouts()
    payout_report_path = f"data/reports/payout_report.csv"
    payout_report.to_csv(payout_report_path, index=False)
    print(f"Payout report saved to {payout_report_path}")
    print(payout_report)

if __name__ == "__main__":
    