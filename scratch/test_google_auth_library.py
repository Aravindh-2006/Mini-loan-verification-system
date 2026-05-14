import os
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from datetime import timedelta
import traceback

def test():
    token = "dummy_token"
    client_id = "dummy_client_id"
    try:
        print("Testing id_token.verify_oauth2_token...")
        # This SHOULD raise a ValueError (invalid token), not a generic Exception
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            client_id,
            clock_skew=timedelta(seconds=600).total_seconds()
        )
        print("Success?")
    except ValueError as e:
        print(f"Caught expected ValueError: {e}")
    except Exception as e:
        print(f"Caught UNEXPECTED Exception: {type(e).__name__}: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test()
