import sys
import os

try:
    import flask
    print("flask imported successfully from:", flask.__file__)
except Exception as e:
    print("Failed to import flask:", e)

flask_dir = r"C:\Users\Acer\OneDrive\Documents\New folder\MINI LOAN\venv\Lib\site-packages\flask"
if os.path.exists(flask_dir):
    print("flask directory exists. Files:")
    for f in os.listdir(flask_dir):
        full_path = os.path.join(flask_dir, f)
        if os.path.isfile(full_path):
            print(f" - {f}: {os.path.getsize(full_path)} bytes")
        elif os.path.isdir(full_path):
            print(f" - [DIR] {f}")
else:
    print("flask directory does not exist at:", flask_dir)
