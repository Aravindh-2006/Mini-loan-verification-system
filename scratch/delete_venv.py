import os
import shutil
import sys
import time

venv_dir = r"C:\Users\Acer\OneDrive\Documents\New folder\MINI LOAN\venv"

if not os.path.exists(venv_dir):
    print("venv directory does not exist. Nothing to delete.")
    sys.exit(0)

print(f"Attempting to delete virtual environment at: {venv_dir}")

def remove_readonly(func, path, excinfo):
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)

# Try up to 3 times with a brief delay in case files are locked momentarily
for attempt in range(1, 4):
    try:
        shutil.rmtree(venv_dir, onerror=remove_readonly)
        print("✅ Successfully deleted venv directory!")
        break
    except Exception as e:
        print(f"Attempt {attempt} failed to delete venv: {e}")
        if attempt < 3:
            print("Retrying in 2 seconds...")
            time.sleep(2)
        else:
            print("❌ Failed to delete venv after 3 attempts.")
            sys.exit(1)
