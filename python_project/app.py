import os
import sys
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import pandas as pd
import json

# Add the project directory to path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.entry import DailyEntry, BulkEntry
from src.models.staff import Staff
from src.utils.csv_handler import CSVHandler
from src.utils.calculations import calculate_payouts, generate_daily_report, generate_monthly_report, generate_staff_performance_report

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.secret_key = os.environ.get('SECRET_KEY', 'vicky_salon_secret_key')

# Initialize CSV handler
csv_handler = CSVHandler()

# Ensure data directories exist
os.makedirs('data/staff', exist_ok=True)
os.makedirs('data/entries', exist_ok=True)
os.makedirs('data/reports', exist_ok=True)
os.makedirs('data/users', exist_ok=True)

# Simple user management with CSV
def get_users():
    users_file = 'data/users/users.csv'
    if not os.path.exists(users_file):
        return pd.DataFrame(columns=['username', 'password_hash', 'role'])
    return pd.read_csv(users_file)

def save_user(username, password, role='staff'):
    users = get_users()
    if username in users['username'].values:
        return False
    
    password_hash = generate_password_hash(password)
    new_user = pd.DataFrame([{
        'username': username,
        'password_hash': password_hash,
        'role': role
    }])
    
    if users.empty:
        users = new_user
    else:
        users = pd.concat([users, new_user], ignore_index=True)
    
    users.to_csv('data/users/users.csv', index=False)
    return True

# Create admin user if it doesn't exist
def ensure_admin_exists():
    users = get_users()
    if users.empty or 'admin' not in users['username'].values:
        save_user('admin', 'admin123', 'admin')
        print("Admin user created with username 'admin' and password 'admin123'")

# Call this function when the app starts
ensure_admin_exists()

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = get_users()
        user = users[users['username'] == username]
        
        if not user.empty and check_password_hash(user.iloc[0]['password_hash'], password):
            session['username'] = username
            session['role'] = user.iloc[0]['role']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

# Authentication middleware
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session.get('role') != 'admin':
            flash('Admin access required')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Main routes
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get summary data for dashboard
    staff_count = len(Staff.load_all())

    daily_entries = DailyEntry.load_all()
    bulk_entries = BulkEntry.load_all()

    # Get today's entries
    today = datetime.now().strftime('%Y-%m-%d')
    today_daily = [entry for entry in daily_entries if entry.date == today]
    today_bulk = [entry for entry in bulk_entries if entry.date == today]

    # Calculate totals
    total_daily_revenue = sum(entry.amount for entry in daily_entries)
    total_bulk_revenue = sum(entry.total for entry in bulk_entries)
    total_revenue = total_daily_revenue + total_bulk_revenue

    today_daily_revenue = sum(entry.amount for entry in today_daily)
    today_bulk_revenue = sum(entry.total for entry in today_bulk)
    today_revenue = today_daily_revenue + today_bulk_revenue

    # Get recent entries (last 5)
    recent_daily = sorted(daily_entries, key=lambda x: x.date, reverse=True)[:5]

    # Get current date for display
    current_date = datetime.now().strftime('%d %b')

    return render_template('dashboard.html',
                          staff_count=staff_count,
                          total_revenue=total_revenue,
                          today_revenue=today_revenue,
                          recent_entries=recent_daily,
                          current_date=current_date)

# Staff routes
@app.route('/staff')
@login_required
def staff_list():
    staff = Staff.load_all()
    return render_template('staff_list.html', staff=staff)

@app.route('/staff/add', methods=['GET', 'POST'])
@login_required
def add_staff():
    if request.method == 'POST':
        # Get existing staff to determine next ID
        existing_staff = Staff.load_all()
        next_id = 1
        if existing_staff:
            next_id = max(staff.id for staff in existing_staff) + 1

        # Get form data
        name = request.form.get('name')
        role = request.form.get('role')

        # Convert commission rate from percentage to decimal
        commission_percentage = float(request.form.get('commission_rate'))
        commission_rate = commission_percentage / 100.0

        new_staff = Staff(
            id=next_id,
            name=name,
            role=role,
            commission_rate=commission_rate
        )

        # Add to existing staff and save
        existing_staff.append(new_staff)
        Staff.save_all(existing_staff)

        flash(f'Staff member "{name}" added successfully with {commission_percentage}% commission rate')

        # Check if this was a quick add (from modal) or full add form
        if 'redirect' in request.form and request.form.get('redirect') == 'add_form':
            return redirect(url_for('add_staff'))
        else:
            return redirect(url_for('staff_list'))

    return render_template('add_staff.html')

@app.route('/staff/edit/<int:staff_id>', methods=['GET', 'POST'])
@login_required
def edit_staff(staff_id):
    staff_member = Staff.get_by_id(staff_id)
    if not staff_member:
        flash('Staff member not found')
        return redirect(url_for('staff_list'))

    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        role = request.form.get('role')

        # Convert commission rate from percentage to decimal
        commission_percentage = float(request.form.get('commission_rate'))
        commission_rate = commission_percentage / 100.0

        # Update staff member
        staff_member.name = name
        staff_member.role = role
        staff_member.commission_rate = commission_rate

        # Update in the list and save
        staff_list = Staff.load_all()
        for i, staff in enumerate(staff_list):
            if staff.id == staff_id:
                staff_list[i] = staff_member
                break

        Staff.save_all(staff_list)

        flash(f'Staff member "{name}" updated successfully with {commission_percentage}% commission rate')
        return redirect(url_for('staff_list'))

    # Convert commission rate to percentage for display
    commission_percentage = staff_member.commission_rate * 100

    return render_template('edit_staff.html', staff=staff_member, commission_percentage=commission_percentage)

# Daily Entry routes
@app.route('/daily-entries')
@login_required
def daily_entries_list():
    entries = DailyEntry.load_all()
    staff_dict = {staff.id: staff for staff in Staff.load_all()}
    
    # Sort entries by date (newest first)
    entries.sort(key=lambda x: x.date, reverse=True)
    
    return render_template('daily_entries.html', entries=entries, staff_dict=staff_dict)

@app.route('/daily-entries/add', methods=['GET', 'POST'])
@login_required
def add_daily_entry():
    if request.method == 'POST':
        # Get form data
        date = request.form.get('date')
        staff_id = int(request.form.get('staff_id'))
        customer_name = request.form.get('customer_name', '')
        service = request.form.get('service')
        amount = float(request.form.get('amount'))

        # Get staff details for commission calculation
        staff_member = Staff.get_by_id(staff_id)
        commission_rate = staff_member.commission_rate if staff_member else 0
        payout = amount * commission_rate

        # Create new entry
        new_entry = DailyEntry(
            date=date,
            staff_id=staff_id,
            service=service,
            amount=amount,
            customer_name=customer_name
        )

        DailyEntry.add_entry(new_entry)

        # Create detailed success message
        staff_name = staff_member.name if staff_member else "Unknown Staff"
        flash(f'Entry added successfully! ₹{amount:.2f} received for {service}. Staff: {staff_name}, Payout: ₹{payout:.2f}')
        return redirect(url_for('daily_entries_list'))

    staff = Staff.load_all()
    today = datetime.now().strftime('%Y-%m-%d')

    return render_template('add_daily_entry.html', staff=staff, today=today)

# Bulk Entry routes
@app.route('/bulk-entries')
@login_required
def bulk_entries_list():
    entries = BulkEntry.load_all()
    staff_dict = {staff.id: staff for staff in Staff.load_all()}
    
    # Sort entries by date (newest first)
    entries.sort(key=lambda x: x.date, reverse=True)
    
    return render_template('bulk_entries.html', entries=entries, staff_dict=staff_dict)

@app.route('/bulk-entries/add', methods=['GET', 'POST'])
@login_required
def add_bulk_entry():
    if request.method == 'POST':
        # Parse the comma-separated amounts
        amounts_str = request.form.get('amounts')
        amounts = [float(amount.strip()) for amount in amounts_str.split(',') if amount.strip()]

        # Get staff details for commission calculation
        staff_id = int(request.form.get('staff_id'))
        staff_member = Staff.get_by_id(staff_id)
        commission_rate = staff_member.commission_rate if staff_member else 0

        new_entry = BulkEntry(
            date=request.form.get('date'),
            staff_id=staff_id,
            amounts=amounts
        )

        BulkEntry.add_entry(new_entry)

        # Calculate totals for success message
        total_amount = sum(amounts)
        total_payout = total_amount * commission_rate
        customer_count = len(amounts)
        staff_name = staff_member.name if staff_member else "Unknown Staff"

        # Create detailed success message
        flash(f'Bulk entry added successfully! {customer_count} customers, Total: ₹{total_amount:.2f}, Staff: {staff_name}, Payout: ₹{total_payout:.2f}')
        return redirect(url_for('bulk_entries_list'))

    staff = Staff.load_all()
    today = datetime.now().strftime('%Y-%m-%d')

    return render_template('add_bulk_entry.html', staff=staff, today=today)

# Report routes
@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html')

@app.route('/reports/daily', methods=['GET', 'POST'])
@login_required
def daily_report():
    if request.method == 'POST':
        date = request.form.get('date')
    else:
        date = datetime.now().strftime('%Y-%m-%d')
    
    report = generate_daily_report(date)
    
    if report.empty:
        flash('No data found for the selected date')
    
    return render_template('daily_report.html', report=report, date=date)

# Helper function for month names
def month_name(month_number):
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
    return month_names[month_number - 1]

@app.route('/reports/monthly', methods=['GET', 'POST'])
@login_required
def monthly_report():
    if request.method == 'POST':
        year = int(request.form.get('year'))
        month = int(request.form.get('month'))
    else:
        today = datetime.now()
        year = today.year
        month = today.month

    report = generate_monthly_report(year, month)

    if report.empty:
        flash('No data found for the selected month')

    # Add current date to template context
    current_year = datetime.now().year

    return render_template('monthly_report.html',
                          report=report,
                          year=year,
                          month=month,
                          current_year=current_year,
                          month_name=month_name)

@app.route('/reports/performance')
@login_required
def performance_report():
    report = generate_staff_performance_report()
    
    if report.empty:
        flash('No data found for performance report')
    
    return render_template('performance_report.html', report=report)

@app.route('/reports/payouts')
@login_required
def payout_report():
    report = calculate_payouts()
    
    if report.empty:
        flash('No data found for payout report')
    
    return render_template('payout_report.html', report=report)

# API routes for potential frontend integration
@app.route('/api/staff', methods=['GET'])
def api_staff_list():
    staff = Staff.load_all()
    return jsonify([s.to_dict() for s in staff])

@app.route('/api/staff/<int:staff_id>', methods=['GET'])
def api_staff_detail(staff_id):
    staff = Staff.get_by_id(staff_id)
    if staff:
        return jsonify(staff.to_dict())
    return jsonify({"error": "Staff not found"}), 404

@app.route('/api/daily-entries', methods=['GET'])
def api_daily_entries():
    entries = DailyEntry.load_all()
    return jsonify([e.to_dict() for e in entries])

@app.route('/api/daily-entries', methods=['POST'])
def api_add_daily_entry():
    data = request.json
    try:
        entry = DailyEntry(
            date=data.get('date'),
            staff_id=data.get('staff_id'),
            customer_name=data.get('customer_name'),
            service=data.get('service'),
            amount=data.get('amount')
        )
        DailyEntry.add_entry(entry)
        return jsonify({"success": True, "entry": entry.to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/bulk-entries', methods=['GET'])
def api_bulk_entries():
    entries = BulkEntry.load_all()
    return jsonify([{
        "date": e.date,
        "staff_id": e.staff_id,
        "amounts": e.amounts,
        "count": e.count,
        "total": e.total,
        "entry_id": e.entry_id
    } for e in entries])

@app.route('/api/bulk-entries', methods=['POST'])
def api_add_bulk_entry():
    data = request.json
    try:
        entry = BulkEntry(
            date=data.get('date'),
            staff_id=data.get('staff_id'),
            amounts=data.get('amounts')
        )
        BulkEntry.add_entry(entry)
        return jsonify({
            "success": True, 
            "entry": {
                "date": entry.date,
                "staff_id": entry.staff_id,
                "amounts": entry.amounts,
                "count": entry.count,
                "total": entry.total,
                "entry_id": entry.entry_id
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/reports/daily/<date>', methods=['GET'])
def api_daily_report(date):
    report = generate_daily_report(date)
    return jsonify(report.to_dict(orient='records'))

@app.route('/api/reports/monthly/<int:year>/<int:month>', methods=['GET'])
def api_monthly_report(year, month):
    report = generate_monthly_report(year, month)
    return jsonify(report.to_dict(orient='records'))

@app.route('/api/reports/performance', methods=['GET'])
def api_performance_report():
    report = generate_staff_performance_report()
    return jsonify(report.to_dict(orient='records'))

@app.route('/api/reports/payouts', methods=['GET'])
def api_payout_report():
    report = calculate_payouts()
    return jsonify(report.to_dict(orient='records'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)