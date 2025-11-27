"""Supabase database and storage manager for loan verification system"""
import hashlib
import mimetypes
from datetime import datetime
import io
import re
from supabase_config import (
    get_supabase_client,
    get_supabase_admin_client,
    SUPABASE_BUCKET_NAME,
)

class SupabaseManager:
    """Manage loan verification operations with Supabase"""
    
    def __init__(self):
        # Regular client for database reads/writes under RLS
        self.client = get_supabase_client()
        # Admin client for privileged storage operations (bucket/file upload)
        self.admin_client = get_supabase_admin_client()
        self.bucket_name = SUPABASE_BUCKET_NAME
        self.last_error = None
        self.init_storage()
    
    def init_storage(self):
        """Initialize storage bucket if it doesn't exist"""
        try:
            # Check if bucket exists
            buckets = self.admin_client.storage.list_buckets()
            bucket_exists = any(b.name == self.bucket_name for b in buckets)
            
            if not bucket_exists:
                # Create bucket with admin client (private by default)
                self.admin_client.storage.create_bucket(self.bucket_name, public=False)
                print(f"✅ Created storage bucket '{self.bucket_name}'")
            else:
                print(f"✅ Storage bucket '{self.bucket_name}' already exists")
        except Exception as e:
            self.last_error = str(e)
            print(f"⚠️  Storage bucket check/create: {str(e)}")
    
    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, email, password):
        """Create a new user"""
        try:
            hashed_password = self.hash_password(password)
            data = {
                'email': email,
                'password': hashed_password
            }
            result = self.client.table('users').insert(data).execute()
            print(f"✅ User created: {email}")
            return True
        except Exception as e:
            print(f"❌ Error creating user: {str(e)}")
            return False
    
    def verify_user(self, email, password):
        """Verify user credentials"""
        try:
            hashed_password = self.hash_password(password)
            result = self.client.table('users').select('*').eq('email', email).eq('password', hashed_password).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"❌ Error verifying user: {str(e)}")
            return False
    
    def get_user_by_email(self, email):
        """Get user by email"""
        try:
            result = self.client.table('users').select('*').eq('email', email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"❌ Error getting user: {str(e)}")
            return None
    
    def upload_file(self, file_data, filename, folder=''):
        """Upload file to Supabase Storage"""
        try:
            safe_folder = folder or ''
            if safe_folder:
                # Replace any characters not allowed in storage keys
                safe_folder = re.sub(r"[^a-zA-Z0-9/_-]", "_", safe_folder).strip('/')
            file_path = f"{safe_folder}/{filename}" if safe_folder else filename
            # Detect content type
            content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
            print(f"[Storage] Uploading path='{file_path}', content_type='{content_type}'")
            
            # Pass raw bytes to supabase-py storage upload (expects bytes/str/path)
            # Use proper option keys and string values where required
            self.admin_client.storage.from_(self.bucket_name).upload(
                file_path,
                file_data,
                {"contentType": content_type, "upsert": "true"}
            )
            print(f"✅ File uploaded: {file_path}")
            self.last_error = None
            return file_path
        except Exception as e:
            self.last_error = str(e)
            print(f"❌ Error uploading file: {str(e)}")
            return None
    
    def get_file_url(self, file_path):
        """Get public URL for a file"""
        try:
            # For private buckets, create a signed URL (valid for 1 hour)
            result = self.client.storage.from_(self.bucket_name).create_signed_url(
                file_path,
                expires_in=3600  # 1 hour
            )
            return result.get('signedURL')
        except Exception as e:
            print(f"❌ Error getting file URL: {str(e)}")
            return None
    
    def delete_file(self, file_path):
        """Delete file from storage"""
        try:
            self.client.storage.from_(self.bucket_name).remove([file_path])
            print(f"✅ File deleted: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Error deleting file: {str(e)}")
            return False
    
    def create_loan_application(self, email, loan_type, amount, income, liabilities, status, reason, documents):
        """Create a new loan application"""
        try:
            data = {
                'email': email,
                'loan_type': loan_type,
                'amount': amount,
                'income': income,
                'liabilities': liabilities,
                'status': status,
                'reason': reason,
                'documents': documents
            }
            result = self.client.table('loans').insert(data).execute()
            loan_id = result.data[0]['id'] if result.data else None
            print(f"✅ Loan application created with ID: {loan_id}")
            return loan_id
        except Exception as e:
            print(f"❌ Error creating loan application: {str(e)}")
            return None
    
    def get_user_loans(self, email):
        """Get all loans for a specific user"""
        try:
            result = self.client.table('loans').select('*').eq('email', email).order('created_at', desc=True).execute()
            return result.data
        except Exception as e:
            print(f"❌ Error getting user loans: {str(e)}")
            return []
    
    def get_all_loans(self):
        """Get all loan applications"""
        try:
            result = self.client.table('loans').select('*').order('created_at', desc=True).execute()
            return result.data
        except Exception as e:
            print(f"❌ Error getting all loans: {str(e)}")
            return []
    
    def get_loan_by_id(self, loan_id):
        """Get loan by ID"""
        try:
            result = self.client.table('loans').select('*').eq('id', loan_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"❌ Error getting loan: {str(e)}")
            return None
    
    def display_database_stats(self):
        """Display database statistics"""
        print("\n" + "="*60)
        print("SUPABASE DATABASE STATISTICS")
        print("="*60)
        
        # Users
        try:
            users = self.client.table('users').select('id, email').execute()
            print(f"\n📊 Total Registered Users: {len(users.data)}")
            print("\nUser List:")
            for user in users.data:
                print(f"  • ID: {user['id']}, Email: {user['email']}")
        except Exception as e:
            print(f"❌ Error getting users: {str(e)}")
        
        # Loans
        try:
            loans = self.get_all_loans()
            print(f"\n📊 Total Loan Applications: {len(loans)}")
            
            # Loan status breakdown
            approved = sum(1 for loan in loans if loan['status'] == 'approved')
            rejected = sum(1 for loan in loans if loan['status'] == 'rejected')
            print(f"  ✅ Approved: {approved}")
            print(f"  ❌ Rejected: {rejected}")
            
            # Loan type breakdown
            loan_types = {}
            for loan in loans:
                loan_type = loan['loan_type']
                loan_types[loan_type] = loan_types.get(loan_type, 0) + 1
            
            print("\n📈 Loan Applications by Type:")
            for loan_type, count in loan_types.items():
                print(f"  • {loan_type.capitalize()}: {count}")
        except Exception as e:
            print(f"❌ Error getting loans: {str(e)}")
        
        print("\n" + "="*60)

# Demo usage
if __name__ == '__main__':
    try:
        manager = SupabaseManager()
        manager.display_database_stats()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n⚠️  Make sure to:")
        print("1. Create a .env file with your Supabase credentials")
        print("2. Set up the database tables in Supabase (see SUPABASE_SETUP.md)")
