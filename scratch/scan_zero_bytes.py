import os

site_packages = r"C:\Users\Acer\OneDrive\Documents\New folder\MINI LOAN\venv\Lib\site-packages"
zero_byte_files = []
total_files = 0

for root, dirs, files in os.walk(site_packages):
    for f in files:
        full_path = os.path.join(root, f)
        total_files += 1
        try:
            if os.path.isfile(full_path) and os.path.getsize(full_path) == 0:
                zero_byte_files.append(full_path)
        except Exception as e:
            pass

print("Total files in site-packages:", total_files)
print("Total zero-byte files:", len(zero_byte_files))
if zero_byte_files:
    print("Some zero-byte files (first 20):")
    for f in zero_byte_files[:20]:
        print(" -", os.path.relpath(f, site_packages))
