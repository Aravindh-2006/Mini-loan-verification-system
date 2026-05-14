# Loan Verification System (Supabase)

A full-stack web application built with **Python Flask** and **Supabase** for loan verification and management.

Now fully migrated from SQLite to Supabase for scalable database and cloud storage.

## 🚀 Features

### 🔐 User Authentication
- **Gmail-Only Authentication**: Restricts registration to Gmail addresses only
- **Secure Login**: SHA256 password hashing
- **Session Management**: Persistent user sessions
- **Demo Credentials**: 
  - **Email**: `kit27.ad05@gmail.com`
  - **Password**: `kit@123`

### 🏦 Loan Types & Validation
1. **Agriculture Loan** (Up to ₹10L)
   - Min Income: ₹15k | Max Loans: 5 | Docs: Land Ownership
   - >₹10L requires Crop Plan
2. **Home Loan** (Up to ₹50L)
   - Min Income: ₹30k | Max Loans: 8 | Docs: Property Document
   - >₹50L requires IT Returns
3. **Education Loan** (Up to ₹5L)
   - Min Income: ₹20k | Max Loans: 10 | Docs: Admission Letter
   - >₹5L requires Guarantor Proof
4. **Business Loan** (Up to ₹20L)
   - Min Income: ₹50k | Max Loans: 12 | Docs: Business Registration
   - >₹20L requires GST/IT Returns

### 💡 Key Capabilities
- **AI Risk Assessment**: Generates personalized risk profile stories
- **EMI Calculator**: Interactive loan repayment calculator with repayment stories
- **Smart Document Verification**: Checks for required document types via form fields and keywords
- **Supabase Backend**: 
  - **Database**: PostgreSQL for robust data management
  - **Storage**: Cloud bucket storage for secure document uploads

---

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Security**: SHA256 hashing, filename sanitization, environment variables

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.7+
- Supabase Account
- `pip`

### 2. Initial Setup
1. **Clone the repository**
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment**:
   - Create a `.env` file in the root directory
   - Add your Supabase credentials (see `.env.example`):
     ```env
     SUPABASE_URL=your_project_url
     SUPABASE_KEY=your_anon_key
     SECRET_KEY=your_secret_key
     SUPABASE_BUCKET_NAME=loan-documents
     ```

### 3. Supabase Setup
If setting up a fresh project:
1. **Create Project** at [supabase.com](https://supabase.com)
2. **Run SQL Setup**: Copy contents of `supabase_setup.sql` to Supabase SQL Editor and run it.
3. **Create Storage Bucket**:
   - Name: `loan-documents`
   - Privacy: **Private** (Public Unchecked)
   - Add storage policies (see `supabase_setup.sql` or docs for policy details)

### 4. Run Application
```bash
python app.py
```
Access at: `http://localhost:5000`

---

## 📂 Project Structure

```
indian/
├── app.py                 # Main Flask application
├── supabase_manager.py    # Database & Storage manager class
├── supabase_config.py     # Client configuration
├── supabase_setup.sql     # Database schema & policies
├── requirements.txt       # Python dependencies
├── templates/             # HTML Templates (Login, Loan Forms, Dashboard)
├── static/                # CSS, JS, Images
└── uploads/               # Temporary upload folder
```

---

## 📊 Database Schema

### Users Table
- `id` (BIGSERIAL)
- `email` (TEXT UNIQUE)
- `password` (TEXT)
- `created_at` (TIMESTAMP)

### Loans Table
- `id` (BIGSERIAL)
- `email` (TEXT - FK)
- `loan_type` (TEXT)
- `amount`, `income`, `liabilities` (INTEGER)
- `status` (TEXT)
- `reason`, `documents` (TEXT)

---

## 🔧 Troubleshooting

- **Supabase Credentials Not Found**: Check `.env` file exists and has correct `SUPABASE_URL` and `SUPABASE_KEY`.
- **Storage Bucket Error**: Ensure bucket is named `loan-documents` and policies are set to allow uploads.
- **Login Issues**: Use the demo credentials or sign up with a valid Gmail address.

---

## 📝 License
This project is open-source and available for educational purposes.
