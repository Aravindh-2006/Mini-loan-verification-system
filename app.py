from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
from werkzeug.utils import secure_filename
import re
import hashlib
from datetime import datetime, timedelta
from dotenv import load_dotenv
import io
import time
import time
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import socket
from email_handler import send_loan_status_email
import traceback


# Load environment variables
load_dotenv()


# ──────────────────────────────────────────────────────────────────────────────
# DB BACKEND SELECTION
# Try Supabase first. If DNS fails (project paused / no internet) fall back to
# a local SQLite database so the app stays fully operational.
# ──────────────────────────────────────────────────────────────────────────────

def _supabase_reachable():
    """Quick DNS check (< 2 s) to detect if Supabase project is reachable."""
    import os
    url = os.getenv('SUPABASE_URL', '')
    if not url:
        return False
    try:
        host = url.replace('https://', '').replace('http://', '').split('/')[0]
        socket.setdefaulttimeout(2)
        socket.gethostbyname(host)
        return True
    except Exception:
        return False


_USE_LOCAL_DB = False   # will be set once at startup


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Admin Credentials
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'kit27.ad05@gmail.com')

# Configuration
ALLOWED_EXTENSIONS = None  # Allow all file types; filenames are sanitized before upload

@app.context_processor
def inject_admin_email():
    return dict(admin_email=ADMIN_EMAIL, offline_mode=_USE_LOCAL_DB)


"""Global DB manager (lazy initialization — Supabase or LocalDB)"""
db_manager = None


def get_db_manager():
    """Return a DB manager instance (Supabase or local SQLite fallback)."""
    global db_manager, _USE_LOCAL_DB
    if db_manager is not None:
        return db_manager

    # ── Try Supabase first ──────────────────────────────────────────────────
    if _supabase_reachable():
        try:
            from supabase_manager import SupabaseManager
            db_manager = SupabaseManager()
            print("✅ Supabase Manager initialized successfully")
            _USE_LOCAL_DB = False
            return db_manager
        except Exception as e:
            print(f"⚠️  Supabase init failed ({e}). Falling back to local SQLite.")
    else:
        print("⚠️  Supabase host unreachable (project might be paused or offline).")
        print("⚠️  Continuing with Local SQLite Database as fallback to keep app fully operational.")

    # ── Fallback: local SQLite ───────────────────────────────────────────────
    try:
        from local_db import LocalDBManager
        db_manager = LocalDBManager()
        _USE_LOCAL_DB = True
        print("✅ Local SQLite DB Manager initialized as fallback")
        return db_manager
    except Exception as e2:
        print(f"❌ Local DB init also failed: {e2}")
        return None

def allowed_file(filename):
    # Accept all file types; presence of a filename is checked by caller
    return True
    
def sanitize_filename(name):
    """Preserve original filename while preventing traversal and invalid path chars.
    - Keeps spaces and unicode
    - Strips path separators and null bytes
    """
    # Strip any directory components
    name = os.path.basename(name or "")
    # Remove null bytes
    name = name.replace('\x00', '')
    # Replace path separators with underscores
    name = re.sub(r"[\\/]+", "_", name)
    # Fallback if empty after sanitization
    return name or "upload"

def init_db():
    """Initialize the database - create demo user or update its password if needed"""
    manager = get_db_manager()
    if manager is None:
        print("⚠️  Database manager not initialized")
        return
    
    # Create or update demo user
    try:
        user, error = manager.get_user_by_email(ADMIN_EMAIL)
        if error:
            print(f"❌ Error in init_db while checking user: {error}")
            return

        if not user:
            manager.create_user(ADMIN_EMAIL, 'kit@123')
            print("✅ Demo user created")
        else:
            # Ensure the password is correct for the demo user
            is_verified, v_error = manager.verify_user(ADMIN_EMAIL, 'kit@123')
            if v_error:
                print(f"❌ Error in init_db while verifying user: {v_error}")
                return

            if not is_verified:
                 manager.client.table('users').update({'password': manager.hash_password('kit@123')}).eq('email', ADMIN_EMAIL).execute()
                 print("✅ Demo user password updated to match kit@123")
            else:
                 print("✅ Demo user already exists with correct password")
    except Exception as e:
        print(f"⚠️  Error in init_db: {str(e)}")

def is_valid_gmail(email):
    """Check if the email is a valid Gmail address"""
    pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    return re.match(pattern, email) is not None

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash"""
    return hash_password(password) == hashed

@app.route('/')
def index():
    """Redirect to login page"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with both local and Google auth"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email and password are required!', 'error')
            return render_template('login.html', google_client_id=os.getenv('GOOGLE_CLIENT_ID'))
            
        manager = get_db_manager()
        if not manager:
            flash('System error. Please try again later.', 'error')
            return render_template('login.html', google_client_id=os.getenv('GOOGLE_CLIENT_ID'))
            
        is_verified, error = manager.verify_user(email, password)
        if is_verified:
            session['email'] = email
            session.permanent = True
            flash('Successfully logged in!', 'success')
            
            if email == ADMIN_EMAIL:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
        else:
            if error:
                flash(f'Login error: {error}', 'error')
            else:
                flash('Incorrect email or password. Please try again.', 'error')
            return render_template('login.html', google_client_id=os.getenv('GOOGLE_CLIENT_ID'), email=email)
            
    # GET request
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    return render_template('login.html', google_client_id=client_id)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page with Gmail-only registration"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Input validation
        if not email or not password or not confirm_password:
            flash('All fields are required!', 'error')
            return render_template('signup.html')
            
        # Validate Gmail format
        if not is_valid_gmail(email):
            flash('Please use a valid Google Gmail ID', 'error')
            return render_template('signup.html')
            
        # Password requirements
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return render_template('signup.html')
            
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('signup.html')
        
        manager = get_db_manager()
        if not manager:
            flash('System error. Please try again later.', 'error')
            return render_template('signup.html')
        
        try:
            # Check if user already exists
            user, error = manager.get_user_by_email(email)
            if error:
                flash(error, 'error')
                return render_template('signup.html')
                
            if user:
                flash('This Gmail is already registered. Please login instead.', 'error')
                return redirect(url_for('login'))
                
            # Create new user
            if manager.create_user(email, password):
                flash('Account created successfully! Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Error creating account. Please try again.', 'error')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
    
    return render_template('signup.html')

@app.route('/google_login', methods=['POST'])
def google_login():
    """Handle Google Sign-In callback"""
    token = request.form.get('credential')
    if not token:
        flash('Authentication failed. No token received.', 'error')
        return redirect(url_for('login'))
        
    try:
        # Verify the token
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        if not client_id or client_id == 'YOUR_GOOGLE_CLIENT_ID_HERE':
            flash('Google Sign-In is not configured by the administrator.', 'error')
            return redirect(url_for('login'))
            
        print(f"DEBUG: Verifying Google token for Client ID: {client_id}")
        if token:
            print(f"DEBUG: Token starts with: {token[:20]}...")
        
        # Verify token using default clock skew
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            client_id
        )
        
        # ID token is valid. Get the user's Google Account ID from the decoded token.
        email = idinfo['email']
        name = idinfo.get('name', 'User')
        
        # Check if user exists in our DB, if not create them
        manager = get_db_manager()
        if manager:
            user, _ = manager.get_user_by_email(email)
            if not user:
                # Create user with a dummy password since they use Google SSO
                # We do this so they can exist in the DB for relational mapping
                manager.create_user(email, 'google_sso_dummy_pwd_123!')
                
        session['email'] = email
        session['name'] = name
        session.permanent = True
        
        flash('Successfully logged in with Google!', 'success')
        
        # Admin redirect
        if email == ADMIN_EMAIL:
            return redirect(url_for('admin_dashboard'))
            
        return redirect(url_for('user_dashboard'))
        
    except ValueError as e:
        # Invalid token
        error_msg = str(e)
        print(f"❌ Google Token validation error: {error_msg}")
        
        # Check for common issues like clock drift
        if "Token used too early" in error_msg:
            flash('Login failed: Your system clock might be incorrect. Please sync your computer time.', 'error')
        elif "Token expired" in error_msg:
            flash('Login session expired. Please try signing in again.', 'error')
        else:
            flash(f'Invalid Google sign-in token: {error_msg}', 'error')
            
        return redirect(url_for('login'))
    except Exception as e:
        print(f"❌ Unexpected error during Google login: {str(e)}")
        traceback.print_exc()
        flash('An unexpected error occurred during Google login.', 'error')

        return redirect(url_for('login'))

@app.route('/loan_selection')
def loan_selection():
    """Loan type selection page"""
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('loan_selection.html')

@app.route('/loan_form/<loan_type>')
def loan_form(loan_type):
    """Loan form page"""
    if 'email' not in session:
        return redirect(url_for('login'))
    
    if loan_type not in ['agriculture', 'home', 'education', 'business']:
        flash('Invalid loan type!', 'error')
        return redirect(url_for('loan_selection'))
    
    return render_template('loan_form.html', loan_type=loan_type)

@app.route('/submit_loan', methods=['POST'])
def submit_loan():
    """Process loan application"""
    if 'email' not in session:
        return redirect(url_for('login'))
    
    email = session['email']
    loan_type = request.form['loan_type']
    amount = int(request.form['amount'])
    income = int(request.form['income'])
    liabilities = int(request.form['liabilities'])
    
    # Get uploaded files and upload to Supabase Storage
    uploaded_files = []  # list of uploaded storage paths
    uploaded_by_field = {}  # map form field -> storage path
    file_errors = []
    
    print(f"DEBUG: Processing files from request...")  # Debug log
    print(f"DEBUG: Files in request: {list(request.files.keys())}")  # Debug log
    
    for file_key in request.files:
        file = request.files[file_key]
        print(f"DEBUG: Processing file_key: {file_key}, filename: {file.filename}")  # Debug log
        
        if file and file.filename and file.filename.strip():
            try:
                filename = sanitize_filename(file.filename)
                # Add timestamp to avoid filename conflicts
                timestamp = str(int(time.time()))
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{timestamp}{ext}"
                
                # Read file data
                file_data = file.read()
                print(f"DEBUG: File size: {len(file_data)} bytes")  # Debug log
                
                # Upload to Supabase Storage
                manager = get_db_manager()
                if manager:
                    file_path = manager.upload_file(file_data, filename, folder=email)
                    if file_path:
                        uploaded_files.append(file_path)
                        uploaded_by_field[file_key] = file_path
                        print(f"✅ Successfully uploaded file: {file_path}")  # Debug log
                    else:
                        reason = getattr(manager, 'last_error', None) or 'unknown error'
                        file_errors.append(f"Failed to upload {filename}: {reason}")
                        print(f"❌ Upload failed for {filename}: {reason}")  # Debug log
                else:
                    file_errors.append("Database manager not available")
                    print("❌ Database manager not available")  # Debug log
            except Exception as e:
                file_errors.append(f"Failed to upload {file.filename}: {str(e)}")
                print(f"❌ Error uploading file {file.filename}: {str(e)}")  # Debug log
        else:
            print(f"DEBUG: Skipping empty file for key: {file_key}")  # Debug log
    
    # If there were file upload errors, show them
    if file_errors:
        flash(f'File upload errors: {"; ".join(file_errors)}', 'error')
    
    # Validation rules - use improved validation that prioritizes form fields
    # We will still run validation to get a suggested reason, but always set initial status to 'pending'
    _, reason = validate_loan_with_field_priority(loan_type, amount, income, liabilities, uploaded_files, uploaded_by_field)
    status = 'pending'
    
    # Store in Supabase database
    manager = get_db_manager()
    if manager:
        manager.create_loan_application(
            email, loan_type, amount, income, liabilities, 
            status, reason, ','.join(uploaded_files)
        )
    else:
        flash('Database not available. Please try again later.', 'error')
        return redirect(url_for('loan_selection'))
    
    # If AJAX request, return JSON instead of redirect
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': status,
            'reason': reason,
            'documents': uploaded_files,
            'loan_type': loan_type
        })
    
    flash('✅ Your loan application has been submitted successfully and is now PENDING review.', 'success')
    return redirect(url_for('user_dashboard'))

def validate_loan(loan_type, amount, income, liabilities, uploaded_files, uploaded_by_field):
    """Validate loan application based on type and rules"""
    
    print(f"Validating loan: type={loan_type}, amount={amount}, income={income}, liabilities={liabilities}")
    print(f"Uploaded files: {uploaded_files}")
    try:
        print(f"Uploaded fields: {list(uploaded_by_field.keys())}")
    except Exception:
        pass
    
    # Common validations
    if liabilities > 12:  # Business loan has highest limit
        return 'rejected', 'Too many existing loans'
    
    # Check if any files were uploaded at all
    if not uploaded_files:
        return 'rejected', 'No documents uploaded'
    
    # Loan type specific validations
    if loan_type == 'agriculture':
        if income < 15000:
            return 'rejected', 'Low income'
        if liabilities > 5:
            return 'rejected', 'Too many existing loans'
        
        # Field-based required doc (land_ownership) with keyword fallback
        has_land_doc = ('land_ownership' in uploaded_by_field) or any(
            keyword in f.lower() for f in uploaded_files 
            for keyword in ['land', 'patta', 'chitta', 'adangal', 'ownership', 'property']
        )
        
        if not has_land_doc:
            return 'rejected', 'Missing land ownership document (Patta/Chitta/Adangal)'
        
        # High amount validation
        if amount > 1000000:  # 10 lakhs
            has_extra_doc = ('crop_plan' in uploaded_by_field) or any(
                keyword in f.lower() for f in uploaded_files 
                for keyword in ['crop', 'subsidy', 'cultivation', 'plan']
            )
            if not has_extra_doc:
                return 'rejected', 'Missing required document for high amount (Crop Plan/Subsidy Proof)'
    
    elif loan_type == 'home':
        if income < 30000:
            return 'rejected', 'Low income'
        if liabilities > 8:
            return 'rejected', 'Too many existing loans'
        
        # Field-based required doc (property_doc) with keyword fallback
        has_property_doc = ('property_doc' in uploaded_by_field) or any(
            keyword in f.lower() for f in uploaded_files 
            for keyword in ['property', 'house', 'home', 'deed', 'title', 'ownership']
        )
        
        if not has_property_doc:
            return 'rejected', 'Missing property document'
        
        # High amount validation
        if amount > 5000000:  # 50 lakhs
            has_it_doc = ('it_returns' in uploaded_by_field) or any(
                keyword in f.lower() for f in uploaded_files 
                for keyword in ['it', 'return', 'income', 'tax']
            )
            if not has_it_doc:
                return 'rejected', 'Missing IT returns for high amount'
    
    elif loan_type == 'education':
        if income < 20000:
            return 'rejected', 'Low income'
        if liabilities > 10:
            return 'rejected', 'Too many existing loans'
        
        # Field-based required doc (admission_letter) with keyword fallback
        has_admission_doc = ('admission_letter' in uploaded_by_field) or any(
            keyword in f.lower() for f in uploaded_files 
            for keyword in ['admission', 'college', 'university', 'institute', 'course']
        )
        
        if not has_admission_doc:
            return 'rejected', 'Missing admission letter'
        
        # High amount validation
        if amount > 500000:  # 5 lakhs
            has_guarantor_doc = ('guarantor_proof' in uploaded_by_field) or any(
                keyword in f.lower() for f in uploaded_files 
                for keyword in ['guarantor', 'guarantee', 'sponsor']
            )
            if not has_guarantor_doc:
                return 'rejected', 'Missing guarantor proof for high amount'
    
    elif loan_type == 'business':
        if income < 50000:
            return 'rejected', 'Low income'
        if liabilities > 12:
            return 'rejected', 'Too many existing loans'
        
        # Field-based required doc (business_reg) with keyword fallback
        has_business_doc = ('business_reg' in uploaded_by_field) or any(
            keyword in f.lower() for f in uploaded_files 
            for keyword in ['business', 'registration', 'udyam', 'msme', 'gst', 'company', 'firm']
        )
        
        if not has_business_doc:
            return 'rejected', 'Missing business registration proof (Udyam/MSME/GST)'
        
        # High amount validation
        if amount > 2000000:  # 20 lakhs
            has_financial_doc = ('gst_returns' in uploaded_by_field or 'it_returns' in uploaded_by_field) or any(
                keyword in f.lower() for f in uploaded_files 
                for keyword in ['gst', 'it', 'return', 'financial', 'balance', 'profit']
            )
            if not has_financial_doc:
                return 'rejected', 'Missing GST/IT returns for high amount'
    
    return 'pending', 'Pending Admin Verification (Pre-check passed)'

def validate_loan_with_field_priority(loan_type, amount, income, liabilities, uploaded_files, uploaded_by_field):
    """Improved validation that prioritizes form field mapping over filename keywords"""
    
    print(f"Validating loan (improved): type={loan_type}, amount={amount}, income={income}, liabilities={liabilities}")
    print(f"Uploaded files: {uploaded_files}")
    print(f"Uploaded fields: {list(uploaded_by_field.keys())}")
    
    # Common validations
    if liabilities > 12:
        return 'rejected', 'Too many existing loans'
    
    if not uploaded_files:
        return 'rejected', 'No documents uploaded'
    
    # Loan type specific validations with field priority
    if loan_type == 'agriculture':
        if income < 15000:
            return 'rejected', 'Low income'
        if liabilities > 5:
            return 'rejected', 'Too many existing loans'
        
        # Priority 1: Check if required field is uploaded
        if 'land_ownership' in uploaded_by_field:
            print("✅ Found land_ownership field - validation passed")
        else:
            # Priority 2: Check filename keywords
            has_land_doc = any(
                keyword in f.lower() for f in uploaded_files 
                for keyword in ['land', 'patta', 'chitta', 'adangal', 'ownership', 'property']
            )
            if not has_land_doc:
                return 'rejected', 'Missing land ownership document (Patta/Chitta/Adangal)'
        
        if amount > 1000000:
            if 'crop_plan' in uploaded_by_field:
                print("✅ Found crop_plan field - high amount validation passed")
            else:
                has_extra_doc = any(
                    keyword in f.lower() for f in uploaded_files 
                    for keyword in ['crop', 'subsidy', 'cultivation', 'plan']
                )
                if not has_extra_doc:
                    return 'rejected', 'Missing required document for high amount (Crop Plan/Subsidy Proof)'
    
    elif loan_type == 'home':
        if income < 30000:
            return 'rejected', 'Low income'
        if liabilities > 8:
            return 'rejected', 'Too many existing loans'
        
        # Priority 1: Check if required field is uploaded
        if 'property_doc' in uploaded_by_field:
            print("✅ Found property_doc field - validation passed")
        else:
            # Priority 2: Check filename keywords
            has_property_doc = any(
                keyword in f.lower() for f in uploaded_files 
                for keyword in ['property', 'house', 'home', 'deed', 'title', 'ownership']
            )
            if not has_property_doc:
                return 'rejected', 'Missing property document'
        
        if amount > 5000000:
            if 'it_returns' in uploaded_by_field:
                print("✅ Found it_returns field - high amount validation passed")
            else:
                has_it_doc = any(
                    keyword in f.lower() for f in uploaded_files 
                    for keyword in ['it', 'return', 'income', 'tax']
                )
                if not has_it_doc:
                    return 'rejected', 'Missing IT returns for high amount'
    
    elif loan_type == 'education':
        if income < 20000:
            return 'rejected', 'Low income'
        if liabilities > 10:
            return 'rejected', 'Too many existing loans'
        
        # Priority 1: Check if required field is uploaded
        if 'admission_letter' in uploaded_by_field:
            print("✅ Found admission_letter field - validation passed")
        else:
            # Priority 2: Check filename keywords
            has_admission_doc = any(
                keyword in f.lower() for f in uploaded_files 
                for keyword in ['admission', 'college', 'university', 'institute', 'course']
            )
            if not has_admission_doc:
                return 'rejected', 'Missing admission letter'
        
        if amount > 500000:
            if 'guarantor_proof' in uploaded_by_field:
                print("✅ Found guarantor_proof field - high amount validation passed")
            else:
                has_guarantor_doc = any(
                    keyword in f.lower() for f in uploaded_files 
                    for keyword in ['guarantor', 'guarantee', 'sponsor']
                )
                if not has_guarantor_doc:
                    return 'rejected', 'Missing guarantor proof for high amount'
    
    elif loan_type == 'business':
        if income < 50000:
            return 'rejected', 'Low income'
        if liabilities > 12:
            return 'rejected', 'Too many existing loans'
        
        # Priority 1: Check if required field is uploaded
        if 'business_reg' in uploaded_by_field:
            print("✅ Found business_reg field - validation passed")
        else:
            # Priority 2: Check filename keywords
            has_business_doc = any(
                keyword in f.lower() for f in uploaded_files 
                for keyword in ['business', 'registration', 'udyam', 'msme', 'gst', 'company', 'firm']
            )
            if not has_business_doc:
                return 'rejected', 'Missing business registration proof (Udyam/MSME/GST)'
        
        if amount > 2000000:
            if 'gst_returns' in uploaded_by_field or 'it_returns' in uploaded_by_field:
                print("✅ Found financial returns field - high amount validation passed")
            else:
                has_financial_doc = any(
                    keyword in f.lower() for f in uploaded_files 
                    for keyword in ['gst', 'it', 'return', 'financial', 'balance', 'profit']
                )
                if not has_financial_doc:
                    return 'rejected', 'Missing GST/IT returns for high amount'
    
    return 'pending', 'Pending Admin Verification (Pre-check passed)'

import google.generativeai as genai

@app.route('/api/generate_risk_story', methods=['POST'])
def api_generate_risk_story():
    data = request.get_json(silent=True) or request.form
    name = (data.get('name') or 'Customer').strip()
    try:
        income = int(str(data.get('income') or 0))
    except Exception:
        income = 0
    try:
        expenses = int(str(data.get('expenses') or 0))
    except Exception:
        expenses = 0
    try:
        loan_amount = int(str(data.get('loan_amount') or 0))
    except Exception:
        loan_amount = 0
    try:
        liabilities_val = int(str(data.get('liabilities') or 0))
    except Exception:
        liabilities_val = 0
    emi_date     = str(data.get('emi_date')   or '1')
    job_type     = str(data.get('job_type')   or 'Unknown')
    location     = str(data.get('location')   or 'your area')
    purpose      = str(data.get('purpose')    or 'personal needs')
    loan_type_val = str(data.get('loan_type') or 'personal')

    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            disposable_preview = max(income - expenses, 0)
            monthly_emi_approx = round(loan_amount / 60) if loan_amount else 0  # rough 5-year estimate
            prompt = (
                f"You are a bank loan advisor in India. Analyse the following customer profile and write a "
                f"clear, honest, 4-sentence personalised loan risk story. "
                f"Use plain English, no markdown, no bullet points.\n\n"
                f"Customer Profile:\n"
                f"- Name: {name}\n"
                f"- Location: {location}\n"
                f"- Loan Type: {loan_type_val} loan\n"
                f"- Loan Amount Requested: ₹{loan_amount:,}\n"
                f"- Purpose: {purpose}\n"
                f"- Monthly Income: ₹{income:,}\n"
                f"- Monthly Expenses: ₹{expenses:,}\n"
                f"- Monthly Disposable Income: ₹{disposable_preview:,}\n"
                f"- Approximate Monthly EMI (5-yr): ₹{monthly_emi_approx:,}\n"
                f"- Existing Active Loans: {liabilities_val}\n"
                f"- Job Type: {job_type}\n"
                f"- Preferred EMI Date: {emi_date}\n\n"
                f"Cover: (1) whether the income comfortably supports the EMI, "
                f"(2) risk level based on existing loans and job stability, "
                f"(3) one practical financial tip specific to their situation, "
                f"(4) a brief encouraging closing line. "
                f"Do not use markdown or symbols."
            )
            response = model.generate_content(prompt)
            if response.text:
                return jsonify({'story': response.text.strip()})
        except Exception as e:
            print(f"Generative AI failed: {e}")

    # Fallback to deterministic logic
    disposable = max(income - expenses, 0)
    burden = (loan_amount / 60) if loan_amount else 0   # rough 5-year EMI estimate
    ratio = (burden / disposable) if disposable else 1.0
    if ratio < 0.3:
        risk = 'Low'
    elif ratio < 0.6:
        risk = 'Medium'
    else:
        risk = 'High'

    factors = []
    if expenses > income * 0.6:
        factors.append('high monthly expenses relative to income')
    if loan_amount > income * 20:
        factors.append('loan amount is large relative to income')
    if job_type.lower() in ['contract', 'temporary', 'seasonal']:
        factors.append(f'income stability concerns due to {job_type.lower()} employment')
    if liabilities_val >= 3:
        factors.append(f'{liabilities_val} existing active loans increasing debt burden')
    factors_text = ', '.join(factors) if factors else 'a generally manageable financial profile'

    if risk == 'High':
        tip = f'We recommend reducing existing liabilities before taking on a new {loan_type_val} loan.'
    elif risk == 'Medium':
        tip = f'Try to build a 3-month EMI buffer in savings before the first payment is due.'
    else:
        tip = f'You appear well-positioned for this {loan_type_val} loan — maintain your current savings habit.'

    story = (
        f"Hi {name}, based on your {loan_type_val} loan request of ₹{loan_amount:,} for {purpose} in {location}, "
        f"your overall risk level is assessed as {risk}. "
        f"Key factors identified: {factors_text}. "
        f"With a monthly income of ₹{income:,} and expenses of ₹{expenses:,}, your disposable income is "
        f"approximately ₹{disposable:,} and your estimated monthly EMI would be around ₹{int(burden):,}. "
        f"{tip} "
        f"Your preferred EMI date is the {emi_date}th — plan your monthly budget around that date to avoid late payments."
    )
    return jsonify({'story': story})

@app.route('/api/generate_repayment_story', methods=['POST'])
def api_generate_repayment_story():
    """
    Generates a narrative story about the loan repayment schedule, including
    EMI, total interest, and the final payment date.
    """
    data = request.get_json(silent=True) or request.form
    try:
        loan_amount = float(data.get('loan_amount', 0))
        annual_rate = float(data.get('interest_rate', 0))
        tenure_months = int(data.get('tenure_months', 0))

        if not all([loan_amount > 0, annual_rate > 0, tenure_months > 0]):
            return jsonify({'story': 'Please provide a valid loan amount, interest rate, and tenure.'})

        # EMI Calculation
        monthly_rate = annual_rate / 12 / 100
        
        if monthly_rate > 0:
            emi = (loan_amount * monthly_rate * (1 + monthly_rate)**tenure_months) / ((1 + monthly_rate)**tenure_months - 1)
        else:
            emi = loan_amount / tenure_months

        total_payment = emi * tenure_months
        total_interest = total_payment - loan_amount

        # Calculate last payment date
        # We use timedelta which is simpler than dateutil for this purpose
        # Approximate months as 30.44 days on average
        end_date = datetime.now() + timedelta(days=tenure_months * 30.44)
        last_payment_date = end_date.strftime('%B %Y') # e.g., "November 2029"

        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"Act as a friendly financial advisor. Write a 2-sentence summary for a customer taking a loan of ₹{loan_amount:,.2f} at {annual_rate}% interest for {tenure_months} months. Their monthly EMI is ₹{emi:,.2f}. The total interest is ₹{total_interest:,.2f} and the final payment is around {last_payment_date}. Make it encouraging and clear. Do not use markdown."
                response = model.generate_content(prompt)
                if response.text:
                    return jsonify({'story': response.text.strip()})
            except Exception as e:
                print(f"Generative AI failed: {e}")

        # Construct the story fallback
        story = (
            f"For a loan of ₹{loan_amount:,.2f} with a tenure of {tenure_months} months at {annual_rate}% interest, "
            f"your estimated monthly payment (EMI) will be approximately ₹{emi:,.2f}. "
            f"Over the entire loan period, you will pay a total of ₹{total_payment:,.2f}, "
            f"which includes ₹{total_interest:,.2f} in interest. "
            f"Your payments will continue for {tenure_months} months, with your final payment expected around {last_payment_date}. "
            "This helps you plan your finances for the long term."
        )
        
        return jsonify({'story': story})

    except (ValueError, TypeError):
        return jsonify({'story': 'Invalid input. Please ensure all values are correct numbers.'})
    except Exception as e:
        print(f"Error in repayment story generation: {e}")
        return jsonify({'story': 'An unexpected error occurred while generating the repayment details.'})


@app.route('/emi_calculator', methods=['GET', 'POST'])
def emi_calculator():
    """EMI Calculator page"""
    if 'email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            principal = float(request.form['principal'])
            annual_rate = float(request.form['rate'])
            tenure_years = int(request.form['tenure'])

            # Convert to monthly rate and tenure
            monthly_rate = annual_rate / 12 / 100
            tenure_months = tenure_years * 12

            # Calculate EMI
            if monthly_rate > 0:
                emi = (principal * monthly_rate * (1 + monthly_rate)**tenure_months) / ((1 + monthly_rate)**tenure_months - 1)
            else: # Handle zero interest rate
                emi = principal / tenure_months

            total_payment = emi * tenure_months
            total_interest = total_payment - principal

            return render_template(
                'emi_calculator.html', 
                emi=f'{emi:,.2f}', 
                principal=principal, 
                rate=annual_rate, 
                tenure=tenure_years,
                total_payment=f'{total_payment:,.2f}',
                total_interest=f'{total_interest:,.2f}'
            )
        except (ValueError, ZeroDivisionError) as e:
            flash(f'Invalid input. Please enter valid numbers. Error: {e}', 'error')

    return render_template('emi_calculator.html')

@app.route('/dashboard')
def user_dashboard():
    """Display user dashboard with loan application status"""
    if 'email' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    
    manager = get_db_manager()
    if not manager:
        flash('Database not available. Please try again later.', 'error')
        return redirect(url_for('loan_selection'))
    
    # Demo user (Admin) should access the admin dashboard instead
    if session['email'] == ADMIN_EMAIL:
        return redirect(url_for('admin_dashboard'))
    
    loans = manager.get_user_loans(session['email'])
    
    # Process loans to ensure clarity
    processed_loans = []
    for loan in loans:
        processed_loans.append({
            'id': loan['id'],
            'email': loan['email'],
            'loan_type': loan['loan_type'],
            'amount': loan['amount'],
            'income': loan['income'],
            'liabilities': loan['liabilities'],
            'status': loan['status'].lower(),
            'reason': loan['reason'],
            'documents': loan['documents'],
            'created_at': loan['created_at']
        })
    
    return render_template('user_dashboard.html', loans=processed_loans, user_email=session['email'])

@app.route('/loan_data')
def loan_data():
    """Legacy route redirecting to dashboard"""
    return redirect(url_for('user_dashboard'))

@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('email', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

# --- Admin Routes ---

def is_admin():
    return session.get('email') == ADMIN_EMAIL

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin Dashboard to view and manage loans"""
    if 'email' not in session:
        return redirect(url_for('login'))
    
    if not is_admin():
        flash('Unauthorized access!', 'error')
        return redirect(url_for('user_dashboard'))
    
    manager = get_db_manager()
    if not manager:
        flash('Database error', 'error')
        return redirect(url_for('loan_selection'))
    
    loans = manager.get_all_loans()
    
    # Process loans to include document lists
    processed_loans = []
    for loan in loans:
        doc_str = loan.get('documents', '')
        docs = doc_str.split(',') if doc_str else []
        processed_loans.append({
            **loan,
            'doc_list': docs
        })
        
    return render_template('admin_dashboard.html', loans=processed_loans)

@app.route('/admin/update_status', methods=['POST'])
def admin_update_status():
    """Update loan status and trigger email"""
    if 'email' not in session or not is_admin():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    loan_id = request.form.get('loan_id')
    status = request.form.get('status')
    remarks = request.form.get('remarks')
    
    if not all([loan_id, status]):
        return jsonify({'success': False, 'message': 'Missing fields'}), 400
        
    manager = get_db_manager()
    
    # 1. Fetch loan details to get applicant's email before updating
    loan = manager.get_loan_by_id(loan_id)
    if not loan:
        return jsonify({'success': False, 'message': 'Loan application not found'}), 404
        
    applicant_email = loan.get('email')
    
    # 2. Update status and remarks in database
    if manager.update_loan_status(loan_id, status, remarks):
        # 3. Automatically send email to user
        email_sent = send_loan_status_email(applicant_email, loan_id, status, remarks)
        
        return jsonify({
            'success': True, 
            'message': 'Status updated and email sent successfully' if email_sent else 'Status updated but email failed'
        })
    else:
        return jsonify({'success': False, 'message': 'Database update failed'})

@app.route('/admin/view_doc')
def admin_view_doc():
    """Redirect to signed URL for document"""
    if 'email' not in session or not is_admin():
        flash('Unauthorized', 'error')
        return redirect(url_for('login'))
        
    file_path = request.args.get('path')
    if not file_path:
        return "Missing file path", 400
        
    manager = get_db_manager()
    url = manager.get_file_url(file_path)
    if url:
        return redirect(url)
    else:
        return "Could not generate link (File might not exist)", 404


@app.route('/local_file/<path:file_path>')
def serve_local_file(file_path):
    """Serve a locally stored upload (used in offline/SQLite mode)."""
    from flask import send_from_directory
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    return send_from_directory(uploads_dir, file_path)


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  Mini Loan Verification System — Starting Up")
    print("="*60)
    init_db()
    mode = "LOCAL SQLite (Offline)" if _USE_LOCAL_DB else "Supabase (Cloud)"
    print(f"\n  🗄️  Database mode : {mode}")
    if _USE_LOCAL_DB:
        print("  ⚠️  Supabase is unreachable. Running in OFFLINE mode.")
        print("  ℹ️  To re-enable Supabase: log in to supabase.com and")
        print("     'Restore' your paused project, then restart this app.")
    print("="*60 + "\n")
    app.run(debug=True)

