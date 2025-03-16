import unittest
import os
import shutil
import pandas as pd
from datetime import datetime

from src.models.staff import Staff
from src.models.entry import DailyEntry, BulkEntry
from src.utils.csv_handler import CSVHandler
from src.utils.calculations import calculate_payouts, generate_daily_report

class TestSalonManagementSystem(unittest.TestCase):

    def setUp(self):
        """Set up test environment before each test."""
        # Create test data directory
        self.test_data_dir = 'test_data'
        os.makedirs(os.path.join(self.test_data_dir, 'staff'), exist_ok=True)
        os.makedirs(os.path.join(self.test_data_dir, 'entries'), exist_ok=True)
        os.makedirs(os.path.join(self.test_data_dir, 'reports'), exist_ok=True)

        # Create test staff data
        self.staff_data = [
            Staff(id=1, name="Test Owner", role="Owner", commission_rate=1.0),
            Staff(id=2, name="Test Stylist", role="Stylist", commission_rate=0.5)
        ]
        Staff.save_all(self.staff_data, os.path.join(self.test_data_dir, 'staff', 'staff.csv'))

        # Create test daily entries
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.daily_entries = [
            DailyEntry(date=self.today, staff_id=1, customer_name="Test Customer 1",
                      service="Haircut", amount=100.0, entry_id=1),
            DailyEntry(date=self.today, staff_id=2, customer_name="Test Customer 2",
                      service="Color", amount=150.0, entry_id=2)
        ]
        DailyEntry.save_all(self.daily_entries, os.path.join(self.test_data_dir, 'entries', 'daily_entries.csv'))

        # Create test bulk entries
        self.bulk_entries = [
            BulkEntry(date=self.today, staff_id=1, amounts=[50.0, 75.0, 100.0], entry_id=1),
            BulkEntry(date=self.today, staff_id=2, amounts=[60.0, 80.0], entry_id=2)
        ]
        BulkEntry.save_all(self.bulk_entries, os.path.join(self.test_data_dir, 'entries', 'bulk_entries.csv'))

    def tearDown(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)

    def test_staff_model(self):
        """Test Staff model functionality."""
        # Test loading staff
        loaded_staff = Staff.load_all(os.path.join(self.test_data_dir, 'staff', 'staff.csv'))
        self.assertEqual(len(loaded_staff), 2)
        self.assertEqual(loaded_staff[0].name, "Test Owner")
        self.assertEqual(loaded_staff[1].role, "Stylist")

        # Test getting staff by ID
        staff = Staff.get_by_id(1, os.path.join(self.test_data_dir, 'staff', 'staff.csv'))
        self.assertIsNotNone(staff)
        self.assertEqual(staff.name, "Test Owner")

        # Test staff not found
        staff = Staff.get_by_id(999, os.path.join(self.test_data_dir, 'staff', 'staff.csv'))
        self.assertIsNone(staff)

    def test_daily_entry_model(self):
        """Test DailyEntry model functionality."""
        # Test loading daily entries
        loaded_entries = DailyEntry.load_all(os.path.join(self.test_data_dir, 'entries', 'daily_entries.csv'))
        self.assertEqual(len(loaded_entries), 2)
        self.assertEqual(loaded_entries[0].customer_name, "Test Customer 1")
        self.assertEqual(loaded_entries[1].amount, 150.0)

        # Test adding a new entry
        new_entry = DailyEntry(
            date=self.today,
            staff_id=1,
            customer_name="Test Customer 3",
            service="Treatment",
            amount=200.0
        )
        DailyEntry.add_entry(new_entry, os.path.join(self.test_data_dir, 'entries', 'daily_entries.csv'))

        # Verify the entry was added
        loaded_entries = DailyEntry.load_all(os.path.join(self.test_data_dir, 'entries', 'daily_entries.csv'))
        self.assertEqual(len(loaded_entries), 3)
        self.assertEqual(loaded_entries[2].customer_name, "Test Customer 3")

    def test_bulk_entry_model(self):
        """Test BulkEntry model functionality."""
        # Test loading bulk entries
        loaded_entries = BulkEntry.load_all(os.path.join(self.test_data_dir, 'entries', 'bulk_entries.csv'))
        self.assertEqual(len(loaded_entries), 2)
        self.assertEqual(loaded_entries[0].count, 3)
        self.assertEqual(loaded_entries[1].total, 140.0)

        # Test adding a new entry
        new_entry = BulkEntry(
            date=self.today,
            staff_id=2,
            amounts=[70.0, 90.0, 110.0]
        )
        BulkEntry.add_entry(new_entry, os.path.join(self.test_data_dir, 'entries', 'bulk_entries.csv'))

        # Verify the entry was added
        loaded_entries = BulkEntry.load_all(os.path.join(self.test_data_dir, 'entries', 'bulk_entries.csv'))
        self.assertEqual(len(loaded_entries), 3)
        self.assertEqual(loaded_entries[2].count, 3)
        self.assertEqual(loaded_entries[2].total, 270.0)

    def test_csv_handler(self):
        """Test CSVHandler functionality."""
        csv_handler = CSVHandler(self.test_data_dir)

        # Test reading staff data
        staff_df = csv_handler.get_staff_data()
        self.assertEqual(len(staff_df), 2)

        # Test reading daily entries
        daily_df = csv_handler.get_daily_entries()
        self.assertEqual(len(daily_df), 2)

        # Test reading bulk entries
        bulk_df = csv_handler.get_bulk_entries()
        self.assertEqual(len(bulk_df), 2)

        # Test saving a report
        report_df = pd.DataFrame({
            'name': ['Test Owner', 'Test Stylist'],
            'total': [100, 150]
        })
        report_path = csv_handler.save_report(report_df, 'test_report')
        self.assertTrue(os.path.exists(report_path))

    def test_calculations(self):
        """Test calculation utilities."""
        # Test payout calculations
        payouts = calculate_payouts()
        self.assertGreaterEqual(len(payouts), 2)

        # Test daily report generation
        daily_report = generate_daily_report(self.today)
        self.assertGreaterEqual(len(daily_report), 4)  # 2 daily entries + 2 bulk entries with multiple customers

if __name__ == '__main__':
    unittest.main()