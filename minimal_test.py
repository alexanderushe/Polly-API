#!/usr/bin/env python3
"""
Minimal test to check if the Polly API server is working.
"""

import requests
import json
import time
import subprocess
import sys

def test_server_connection():
    """Test basic server connection."""
    try:
        response = requests.get("http://127.0.0.1:8000/polls", timeout=5)
        print(f"Server response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response text: {response.text[:200]}...")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return False

def test_registration():
    """Test user registration endpoint."""
    url = "http://127.0.0.1:8000/register"
    data = {
        "username": "testuser_minimal",
        "password": "testpass123"
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    print(f"\nTesting registration at {url}")
    print(f"Data: {data}")

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Raw Response: {response.text}")

        if response.status_code in [200, 201]:
            try:
                json_data = response.json()
                print(f"JSON Response: {json_data}")
                return True, json_data
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                return False, None
        else:
            print(f"Registration failed with status {response.status_code}")
            return False, None

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return False, None

def test_login():
    """Test user login endpoint."""
    url = "http://127.0.0.1:8000/login"
    data = {
        "username": "testuser_minimal",
        "password": "testpass123"
    }
    headers = {
        "Accept": "application/json"
    }

    print(f"\nTesting login at {url}")
    print(f"Data: {data}")

    try:
        # Use form data as per OpenAPI spec
        response = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Raw Response: {response.text}")

        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"JSON Response: {json_data}")
                return True, json_data.get('access_token')
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                return False, None
        else:
            print(f"Login failed with status {response.status_code}")
            return False, None

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return False, None

def main():
    """Run minimal tests."""
    print("🧪 MINIMAL POLLY API TEST")
    print("=" * 40)

    # Start server
    print("Starting server...")
    try:
        server_process = subprocess.Popen([
            "python3", "-m", "uvicorn", "main:app",
            "--host", "127.0.0.1", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print("Waiting for server to start...")
        time.sleep(5)

        # Test basic connection
        print("\n1. Testing server connection...")
        if not test_server_connection():
            print("❌ Server connection failed")
            return

        # Test registration
        print("\n2. Testing user registration...")
        reg_success, user_data = test_registration()
        if reg_success:
            print("✅ Registration successful!")
        else:
            print("❌ Registration failed!")

        # Test login
        print("\n3. Testing user login...")
        login_success, token = test_login()
        if login_success:
            print("✅ Login successful!")
            print(f"Token: {token[:20]}..." if token else "No token")
        else:
            print("❌ Login failed!")

        print("\n🏁 Minimal tests completed!")

    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Stop server
        try:
            if 'server_process' in locals():
                server_process.terminate()
                server_process.wait(timeout=5)
                print("\n✅ Server stopped")
        except Exception as e:
            print(f"Error stopping server: {e}")

if __name__ == "__main__":
    main()
