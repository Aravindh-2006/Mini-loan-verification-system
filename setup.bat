@echo off
echo ================================================================================
echo SUPABASE LOAN VERIFICATION SYSTEM - AUTOMATED SETUP
echo ================================================================================
echo.

echo [1/4] Checking environment file...
if exist ".env" (
    echo ✅ .env file already exists
) else (
    if exist ".env.production" (
        echo Creating .env file from .env.production...
        ren ".env.production" ".env"
        echo ✅ .env file created
    ) else (
        echo ❌ ERROR: .env.production file not found!
        echo Please make sure .env.production exists
        pause
        exit /b 1
    )
)
echo.

echo [2/4] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed
echo.

echo [3/4] Testing Supabase connection...
python supabase_manager.py
if %errorlevel% neq 0 (
    echo ⚠️  WARNING: Supabase connection test failed
    echo Please check your .env file and Supabase setup
    echo.
    echo Make sure you have:
    echo 1. Run the SQL file in Supabase SQL Editor
    echo 2. Created the storage bucket 'loan-documents'
    echo 3. Correct credentials in .env file
    echo.
    pause
)
echo.

echo [4/4] Setup complete!
echo.
echo ================================================================================
echo NEXT STEPS:
echo ================================================================================
echo.
echo 1. Go to Supabase SQL Editor:
echo    https://bqvudmjhsvaiudwwlxgn.supabase.co
echo.
echo 2. Copy and paste content from: supabase_setup.sql
echo.
echo 3. Create storage bucket: 'loan-documents'
echo.
echo 4. Run the application:
echo    python app.py
echo.
echo 5. Open browser: http://127.0.0.1:5000
echo.
echo 6. Login with: kit27.ad05@gmail.com / kit@123
echo.
echo ================================================================================
echo.
pause
