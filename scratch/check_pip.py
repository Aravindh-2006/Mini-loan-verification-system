import subprocess
import sys

print("Python executable:", sys.executable)
print("Python path:", sys.path)

try:
    res = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
    print("Return code:", res.returncode)
    print("Stdout:")
    print(res.stdout)
    print("Stderr:")
    print(res.stderr)
except Exception as e:
    print("Exception:", e)
