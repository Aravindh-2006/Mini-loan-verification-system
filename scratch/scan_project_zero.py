import os

project_dir = r"C:\Users\Acer\OneDrive\Documents\New folder\MINI LOAN"
zero_byte_files = []
total_files = 0

for root, dirs, files in os.walk(project_dir):
    # Skip .git and venv directories
    if ".git" in root or "venv" in root or "scratch" in root:
        continue
    for f in files:
        full_path = os.path.join(root, f)
        total_files += 1
        try:
            if os.path.isfile(full_path) and os.path.getsize(full_path) == 0:
                zero_byte_files.append(full_path)
        except Exception as e:
            pass

print("Total files in project (excluding git, venv, scratch):", total_files)
print("Total zero-byte files:", len(zero_byte_files))
if zero_byte_files:
    print("Zero-byte files in project:")
    for f in zero_byte_files:
        print(" -", os.path.relpath(f, project_dir))
