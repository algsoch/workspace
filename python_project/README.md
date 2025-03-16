# Vicky Hair Salon Management System

## Overview
The Vicky Hair Salon Management System is a digital record-keeping solution designed to modernize salon management by addressing the lack of digital records among salon owners and staff. The system uses CSV files for data storage, making it simple to deploy and maintain without requiring a complex database setup.

## Key Features
- **Staff Management**: Track salon staff, their roles, and commission rates
- **Daily Entry System**: Record individual customer transactions with details like customer name, service, and amount
- **Bulk Entry System**: Process multiple customer transactions at once, automatically calculating totals
- **Automated Reporting**: Generate daily, monthly, and performance reports
- **Payout Calculations**: Automatically calculate staff payouts based on commission rates
- **Web Interface**: User-friendly web interface for managing all aspects of the salon
- **API Endpoints**: RESTful API for integration with other systems

## Installation
To install the necessary dependencies, run the following command:

```
pip install -r requirements.txt
```

## Usage

### Running the Web Application
To run the web application, execute the following command:

```
python app.py
```

This will start a Flask web server that you can access at http://localhost:5000.

### Demo Mode
To run the application in demo mode (generating sample data), execute:

```
python src/main.py
```

This will:
1. Create sample staff data
2. Generate sample daily entries
3. Generate sample bulk entries
4. Generate various reports

## Data Structure
The system uses CSV files for data storage, organized as follows:

- **Staff Data**: `data/staff/staff.csv`
  - Contains staff information (ID, name, role, commission rate)

- **Daily Entries**: `data/entries/daily_entries.csv`
  - Records individual customer transactions
  - Includes date, staff ID, customer name, service, and amount

- **Bulk Entries**: `data/entries/bulk_entries.csv`
  - Records multiple customer transactions in a single entry
  - Includes date, staff ID, comma-separated amounts, customer count, and total

- **Reports**: `data/reports/`
  - Contains generated reports (daily, monthly, staff performance, payouts)

- **Users**: `data/users/users.csv`
  - Contains user authentication information
  - Includes username, password hash, and role

## Directory Structure
```
python_project/
├── app.py              # Flask web application
├── vercel.json         # Vercel deployment configuration
├── templates/          # HTML templates for the web interface
├── data/               # Data storage directory (created at runtime)
│   ├── staff/          # Staff data
│   ├── entries/        # Daily and bulk entries
│   ├── reports/        # Generated reports
│   └── users/          # User authentication data
├── src/                # Source code for the application
│   ├── __init__.py     # Marks the src directory as a Python package
│   ├── main.py         # Entry point for demo mode
│   ├── models/         # Contains model definitions
│   │   ├── __init__.py # Marks the models directory as a Python package
│   │   ├── staff.py    # Staff model
│   │   └── entry.py    # Daily and bulk entry models
│   └── utils/          # Contains utility functions
│       ├── __init__.py # Marks the utils directory as a Python package
│       ├── csv_handler.py # CSV file operations
│       └── calculations.py # Payout and report calculations
├── tests/              # Contains unit tests
│   ├── __init__.py     # Marks the tests directory as a Python package
│   └── test_main.py    # Unit tests for main application logic
├── requirements.txt    # Lists project dependencies
└── setup.py            # Configuration file for packaging the project
```

## Deployment on Vercel

### Prerequisites
- A Vercel account (https://vercel.com)
- Git repository with your project

### Deployment Steps

1. **Prepare your project for deployment**
   - Ensure all dependencies are listed in `requirements.txt`
   - Make sure `vercel.json` is properly configured

2. **Deploy to Vercel**
   - Install Vercel CLI: `npm i -g vercel`
   - Login to Vercel: `vercel login`
   - Deploy the project: `vercel`
   - Follow the prompts to complete the deployment

3. **Configure Environment Variables**
   - Set `SECRET_KEY` for Flask session security
   - Set any other environment variables needed for your deployment

4. **Storage Considerations**
   Since Vercel's serverless functions have ephemeral file systems, you have several options for data persistence:

   a. **Use Vercel's integration with AWS S3**
      - Create an S3 bucket for your CSV files
      - Update the application to read/write to S3 instead of local files
      - Set AWS credentials as environment variables

   b. **Use a database service**
      - Consider using a service like MongoDB Atlas or Supabase
      - Modify the application to use the database instead of CSV files

   c. **Use Vercel's KV storage (Preview)**
      - Vercel offers a Key-Value storage solution that can be used for data persistence
      - Update the application to use Vercel KV for data storage

### Example S3 Integration

To use S3 for storage, you would need to:

1. Install boto3: `pip install boto3`
2. Add boto3 to requirements.txt
3. Modify the CSVHandler class to use S3 for file operations
4. Set AWS credentials as environment variables in Vercel

## API Documentation

The application provides the following API endpoints:

### Staff Endpoints
- `GET /api/staff` - Get all staff members
- `GET /api/staff/<staff_id>` - Get a specific staff member

### Daily Entry Endpoints
- `GET /api/daily-entries` - Get all daily entries
- `POST /api/daily-entries` - Add a new daily entry

### Bulk Entry Endpoints
- `GET /api/bulk-entries` - Get all bulk entries
- `POST /api/bulk-entries` - Add a new bulk entry

### Report Endpoints
- `GET /api/reports/daily/<date>` - Get daily report for a specific date
- `GET /api/reports/monthly/<year>/<month>` - Get monthly report for a specific year and month
- `GET /api/reports/performance` - Get staff performance report
- `GET /api/reports/payouts` - Get payout report

## Authentication

The web application uses session-based authentication. A default admin user is created with:
- Username: `admin`
- Password: `admin123`

It is recommended to change this password after first login or set up a new admin user.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.