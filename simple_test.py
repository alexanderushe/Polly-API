#!/usr/bin/env python3
"""
Simple test script for the Polly API client.
"""

import time
import subprocess
import sys
from user_client import PollyAPIClient

def test_basic_functionality():
    """Test basic API client functionality."""
    print("🧪 Testing Polly API Client")
    print("=" * 40)

    # Initialize client
    client = PollyAPIClient("http://127.0.0.1:8000")

    # Test 1: Register a user
    print("\n1. Testing user registration...")
    result = client.register_user("testuser", "testpass123")

    if result["success"]:
        print("✅ Registration successful!")
        print(f"   User ID: {result['data'].get('id')}")
        print(f"   Username: {result['data'].get('username')}")
    else:
        print("❌ Registration failed!")
        print(f"   Error: {result.get('message')}")
        if result.get('status_code') == 400:
            print("   (This might be expected if user already exists)")

    # Test 2: Login
    print("\n2. Testing user login...")
    login_result = client.login("testuser", "testpass123")

    if login_result["success"]:
        print("✅ Login successful!")
        print(f"   Token received: {bool(client.token)}")
    else:
        print("❌ Login failed!")
        print(f"   Error: {login_result.get('message')}")
        return False

    # Test 3: Fetch polls
    print("\n3. Testing poll fetching...")
    polls_result = client.fetch_polls(skip=0, limit=5)

    if polls_result["success"]:
        polls = polls_result.get("polls", [])
        print("✅ Polls fetched successfully!")
        print(f"   Number of polls: {len(polls)}")
        if polls:
            print(f"   First poll: {polls[0].get('question', 'No question')[:30]}...")
    else:
        print("❌ Poll fetching failed!")
        print(f"   Error: {polls_result.get('message')}")

    # Test 4: Create a poll
    print("\n4. Testing poll creation...")
    if client.token:
        create_result = client.create_poll(
            question="What's your favorite color?",
            options=["Red", "Blue", "Green", "Yellow"]
        )

        if create_result["success"]:
            poll_data = create_result["data"]
            print("✅ Poll created successfully!")
            print(f"   Poll ID: {poll_data.get('id')}")
            print(f"   Question: {poll_data.get('question')}")
            return poll_data.get('id')
        else:
            print("❌ Poll creation failed!")
            print(f"   Error: {create_result.get('message')}")
    else:
        print("❌ Cannot create poll - no authentication token")

    return None

def main():
    """Main test function."""
    try:
        # Start server
        print("🚀 Starting server...")
        server_process = subprocess.Popen([
            "python3", "-m", "uvicorn", "main:app",
            "--host", "127.0.0.1", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait for server to start
        time.sleep(3)

        # Run tests
        poll_id = test_basic_functionality()

        # Test voting if we have a poll
        if poll_id:
            print("\n5. Testing voting...")
            client = PollyAPIClient("http://127.0.0.1:8000")

            # Login again for voting
            login_result = client.login("testuser", "testpass123")
            if login_result["success"]:
                # Get poll details to find an option
                poll_result = client.get_poll(poll_id)
                if poll_result["success"] and poll_result["data"].get("options"):
                    option_id = poll_result["data"]["options"][0]["id"]
                    vote_result = client.vote_on_poll(poll_id, option_id)

                    if vote_result["success"]:
                        print("✅ Voting successful!")
                    else:
                        print("❌ Voting failed!")
                        print(f"   Error: {vote_result.get('message')}")

        print("\n🏁 Tests completed!")

    except Exception as e:
        print(f"💥 Error: {e}")
    finally:
        # Clean up server
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
            print("✅ Server stopped")
        except:
            pass

if __name__ == "__main__":
    main()
