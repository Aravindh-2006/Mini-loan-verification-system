# Mini Loan Verification System

A full-stack web application built with Python Flask, HTML, CSS, and SQLite database for loan verification and management.

## Features

### 🔐 User Authentication
- **Login Page**: Secure user authentication
- **Signup Page**: New user registration
- **Demo Credentials**: 
  - Email: `kit27.ad05@gmail.com`
  - Password: `kit@123`

### 🏦 Loan Types
1. **Agriculture Loan** (Up to ₹10 Lakhs)
2. **Home Loan** (Up to ₹50 Lakhs)
3. **Education Loan** (Up to ₹5 Lakhs)
4. **Business Loan** (Up to ₹20 Lakhs)

### 📋 Loan Validation Rules

#### Agriculture Loan
- **Minimum Income**: ₹15,000/month
- **Maximum Existing Loans**: 5
- **Required Documents**: Land ownership document
- **High Amount (>₹10L)**: Crop plan/subsidy proof required

#### Home Loan
- **Minimum Income**: ₹30,000/month
- **Maximum Existing Loans**: 8
- **Required Documents**: Property document
- **High Amount (>₹50L)**: IT returns required

#### Education Loan
- **Minimum Income**: ₹20,000/month
- **Maximum Existing Loans**: 10
- **Required Documents**: Admission letter
- **High Amount (>₹5L)**: Guarantor proof required

#### Business Loan
- **Minimum Income**: ₹50,000/month
- **Maximum Existing Loans**: 12
- **Required Documents**: Business registration proof
- **High Amount (>₹20L)**: GST/IT returns required

### 📊 Data Management
- **SQLite Database**: Stores users and loan applications
- **File Uploads**: Document storage in `/uploads` folder
- **Admin View**: Complete loan data display for demo user
- **Real-time Validation**: Client and server-side validation

## Installation & Setup

1. **Clone/Download** the project files
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Application**:
   ```bash
   python app.py
   ```
4. **Access the Application**:
   - Open browser and go to `http://localhost:5000`
   - Use demo credentials to login and view all data

## Project Structure

```
indian/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── loan_verification.db  # SQLite database (auto-created)
├── templates/            # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── signup.html
│   ├── loan_selection.html
│   ├── loan_form.html
│   └── loan_data.html
├── static/              # CSS, JS, images
└── uploads/             # Uploaded documents
```

## Database Schema

### Users Table
- `id` (INTEGER PRIMARY KEY)
- `email` (TEXT UNIQUE)
- `password` (TEXT - SHA256 hashed)

### Loans Table
- `id` (INTEGER PRIMARY KEY)
- `email` (TEXT)
- `loan_type` (TEXT)
- `amount` (INTEGER)
- `income` (INTEGER)
- `liabilities` (INTEGER)
- `status` (TEXT - 'approved'/'rejected')
- `reason` (TEXT)
- `documents` (TEXT - comma-separated filenames)
- `created_at` (TIMESTAMP)

## Usage Flow

1. **Login/Signup** → Access the system
2. **Select Loan Type** → Choose from 4 loan categories
3. **Fill Application** → Enter details and upload documents
4. **Validation** → System checks all rules automatically
5. **Result** → Success/Rejection with reason
6. **Admin View** → Demo user can view all applications

## Technologies Used

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Database**: SQLite
- **Icons**: Font Awesome
- **File Handling**: Werkzeug

## Validation Features

- ✅ **Income Verification**: Minimum income checks
- ✅ **Loan Limit Validation**: Maximum loan amount limits
- ✅ **Existing Loan Checks**: Liability count validation
- ✅ **Document Requirements**: Type-specific document validation
- ✅ **File Upload Security**: Secure filename handling
- ✅ **Real-time Feedback**: Immediate validation results

## Demo Access

Login with the demo credentials to access the admin panel and view all loan applications with detailed statistics and analytics.


