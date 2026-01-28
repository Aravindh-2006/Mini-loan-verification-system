from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
from werkzeug.utils import secure_filename
import re
import hashlib
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase_manager import SupabaseManager
import io
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Configuration
ALLOWED_EXTENSIONS = None  # Allow all file types; filenames are sanitized before upload

"""Global Supabase manager (lazy initialization)"""
db_manager = None

def get_db_manager():
    """Return a SupabaseManager instance, initializing if needed.
    This prevents 'Database not available' if import-time init failed."""
    global db_manager
    if db_manager is not None:
        return db_manager
    try:
        db_manager_local = SupabaseManager()
        print("✅ Supabase Manager initialized successfully")
        db_manager = db_manager_local
        return db_manager
    except Exception as e:
        print(f"❌ Error initializing Supabase Manager: {str(e)}")
        print("⚠️  Please check your .env file and Supabase configuration")
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
    """Initialize the database - create demo user if needed"""
    manager = get_db_manager()
    if manager is None:
        print("⚠️  Database manager not initialized")
        return
    
    # Create demo user if not exists
    try:
        existing_user = manager.get_user_by_email('kit27.ad05@gmail.com')
        if not existing_user:
            manager.create_user('kit27.ad05@gmail.com', 'kit@123')
            print("✅ Demo user created")
        else:
            print("✅ Demo user already exists")
    except Exception as e:
        print(f"⚠️  Error creating demo user: {str(e)}")

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

def is_valid_gmail(email):
    """Validate if email is a valid Gmail address"""
    import re
    gmail_pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    return re.match(gmail_pattern, email) is not None

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with Gmail-only authentication"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Input validation
        if not email or not password:
            flash('Email and password are required!', 'error')
            return render_template('login.html')
            
        # Validate Gmail format
        if not is_valid_gmail(email):
            flash('Please use a valid Google Gmail ID', 'error')
            return render_template('login.html')
        
        # Verify credentials
        manager = get_db_manager()
        if not manager:
            flash('System error. Please try again later.', 'error')
            return render_template('login.html')
            
        # Check if user exists and password is correct
        user = manager.get_user_by_email(email)
        if not user:
            flash('No account found with this Gmail address', 'error')
            return render_template('login.html')
            
        if manager.verify_user(email, password):
            session['email'] = email
            session.permanent = True  # Enable session persistence
            flash('Login successful!', 'success')
            return redirect(url_for('loan_selection'))
        else:
            flash('Incorrect Google password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page with Gmail-only registration"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
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
        if len(password) < 8:
            flash('Password must be at least 8 characters long!', 'error')
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
            existing_user = manager.get_user_by_email(email)
            if existing_user:
                flash('This Gmail is already registered. Please login instead.', 'error')
                return redirect(url_for('login'))
                
            # Create new user with hashed password
            if manager.create_user(email, password):
                flash('Account created successfully! Please login with your Gmail.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Error creating account. Please try again.', 'error')
        except Exception as e:
            print(f"Error during signup: {str(e)}")
            flash('An error occurred while creating your account. Please try again.', 'error')
    
    return render_template('signup.html')

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
    status, reason = validate_loan_with_field_priority(loan_type, amount, income, liabilities, uploaded_files, uploaded_by_field)
    
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
    
    if status == 'approved':
        flash('✅ Successfully Saved', 'success')
    else:
        flash(f'❌ Rejected: {reason}', 'error')
    
    return redirect(url_for('loan_selection'))

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
    
    return 'approved', 'All conditions satisfied'

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
    
    return 'approved', 'All conditions satisfied'

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
    emi_date = str(data.get('emi_date') or '1')
    job_type = str(data.get('job_type') or 'Unknown')
    location = str(data.get('location') or 'your area')
    purpose = str(data.get('purpose') or 'personal needs')

    disposable = max(income - expenses, 0)
    burden = (loan_amount / 12) if loan_amount else 0
    ratio = (burden / disposable) if disposable else 1.0
    if ratio < 0.3:
        risk = 'Low'
    elif ratio < 0.6:
        risk = 'Medium'
    else:
        risk = 'High'

    festival_hint = 'Consider festival and seasonal expenses in ' + location + '. '
    emi_hint = f"Your EMI due around date {emi_date} may clash with monthly bills. "
    suggestion = 'Try keeping 2–3 months EMI buffer and reduce discretionary spends.'
    factors = []
    if expenses > income * 0.6:
        factors.append('high monthly expenses')
    if loan_amount > income * 20:
        factors.append('loan amount is large relative to income')
    if job_type.lower() in ['contract', 'temporary', 'seasonal']:
        factors.append('income stability')
    factors_text = ', '.join(factors) if factors else 'current income and expense pattern'

    story = (
        f"Hi {name}, based on your profile in {location} and a requested loan of ₹{loan_amount:,} for {purpose}, "
        f"your risk level looks {risk}. "
        f"Key factors are {factors_text}. "
        f"{festival_hint}"
        f"{emi_hint}"
        f"With income of ₹{income:,} and expenses of ₹{expenses:,}, your monthly buffer is about ₹{disposable:,}. "
        f"{suggestion}"
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

        # Construct the story
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

@app.route('/loan_data')
def loan_data():
    """Display loan data - all loans for demo user, only own loans for others"""
    if 'email' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    
    manager = get_db_manager()
    if not manager:
        flash('Database not available. Please try again later.', 'error')
        return redirect(url_for('loan_selection'))
    
    # Demo user can see all loans, others see only their own
    if session['email'] == 'kit27.ad05@gmail.com':
        loans = manager.get_all_loans()
    else:
        loans = manager.get_user_loans(session['email'])
    
    # Convert dict format to tuple format for template compatibility
    loans_list = []
    for loan in loans:
        loans_list.append((
            loan['id'],
            loan['email'],
            loan['loan_type'],
            loan['amount'],
            loan['income'],
            loan['liabilities'],
            loan['status'],
            loan['reason'],
            loan['documents'],
            loan['created_at']
        ))
    
    return render_template('loan_data.html', loans=loans_list, user_email=session['email'])

@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('email', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
