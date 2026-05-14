import os
from dotenv import load_dotenv
import requests
import socket
import sys

# Ensure UTF-8 output if possible, but keep it simple
load_dotenv()

def check_connectivity():
    print("--- Environment Check ---")
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    print(f"GOOGLE_CLIENT_ID: {client_id}")
    
    if not client_id:
        print("[FAIL] GOOGLE_CLIENT_ID NOT found in .env")
    else:
        print("[OK] GOOGLE_CLIENT_ID found")

    print("\n--- Network Check ---")
    try:
        # Check Google Certs endpoint
        response = requests.get('https://www.googleapis.com/oauth2/v3/certs', timeout=5)
        if response.status_code == 200:
            print("[OK] Can reach Google OAuth certs endpoint")
        else:
            print(f"[FAIL] Failed to reach Google OAuth certs endpoint (Status: {response.status_code})")
    except Exception as e:
        print(f"[ERROR] Error reaching Google OAuth certs endpoint: {e}")

    try:
        # Check general internet
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("[OK] General internet access (8.8.8.8) is OK")
    except Exception as e:
        print(f"[FAIL] No general internet access: {e}")

if __name__ == "__main__":
    check_connectivity()
