#!/usr/bin/env python3
"""
Test script for the Polly API client to verify functionality.
"""

import time
import sys
import subprocess
import threading
from user_client import PollyAPIClient, format_poll_summary


def start_server():
    """Start the FastAPI server in a separate process."""
    try:
        print("Starting Polly API server...")
        process = subprocess.Popen([
            "python3", "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Give server time to start
        time.sleep(3)

        return process
    except Exception as e:
        print(f"Failed to start server: {e}")
        return None


def test_user_registration(client):
    """Test user registration functionality."""
    print("\n" + "="*50)
    print("TESTING USER REGISTRATION")
    print("="*50)

    # Test with valid data
    print("Test 1: Valid registration")
    result = client.register_user("testuser_123", "securepassword123")

    if result["success"]:
        user_data = result["data"]
        print("✅ Registration successful!")
        print(f"   User ID: {user_data.get('id')}")
        print(f"   Username: {user_data.get('username')}")
        print(f"   Status Code: {result.get('status_code')}")

        # Validate response structure
        if "validation_warning" in result:
            print(f"⚠️  Validation Warning: {result['validation_warning']}")

        return True
    else:
        print("❌ Registration failed!")
        print(f"   Error: {result.get('error')}")
        print(f"   Message: {result.get('message')}")
        print(f"   Status Code: {result.get('status_code')}")
        return False


def test_duplicate_registration(client):
    """Test duplicate user registration."""
    print("\nTest 2: Duplicate registration (should fail)")
    result = client.register_user("testuser_123", "differentpassword")

    if not result["success"] and result.get("status_code") == 400:
        print("✅ Duplicate registration properly rejected!")
        print(f"   Error: {result.get('error')}")
        print(f"   Message: {result.get('message')}")
        return True
    else:
        print("❌ Duplicate registration not properly handled!")
        print(f"   Result: {result}")
        return False


def test_user_login(client):
    """Test user login functionality."""
    print("\n" + "="*50)
    print("TESTING USER LOGIN")
    print("="*50)

    # Test valid login
    print("Test 1: Valid login")
    result = client.login("testuser_123", "securepassword123")

    if result["success"]:
        token_data = result["data"]
        print("✅ Login successful!")
        print(f"   Token Type: {token_data.get('token_type')}")
        print(f"   Has Access Token: {'access_token' in token_data}")
        print(f"   Status Code: {result.get('status_code')}")
        print(f"   Client has token: {client.token is not None}")
        return True
    else:
        print("❌ Login failed!")
        print(f"   Error: {result.get('error')}")
        print(f"   Message: {result.get('message')}")
        return False


def test_invalid_login(client):
    """Test login with invalid credentials."""
    print("\nTest 2: Invalid login (should fail)")
    result = client.login("testuser_123", "wrongpassword")

    if not result["success"] and result.get("status_code") == 400:
        print("✅ Invalid login properly rejected!")
        print(f"   Error: {result.get('error')}")
        print(f"   Message: {result.get('message')}")
        return True
    else:
        print("❌ Invalid login not properly handled!")
        print(f"   Result: {result}")
        return False


def test_fetch_polls(client):
    """Test fetching polls."""
    print("\n" + "="*50)
    print("TESTING POLL FETCHING")
    print("="*50)

    print("Test 1: Fetch polls with default pagination")
    result = client.fetch_polls()

    if result["success"]:
        polls = result.get("polls", [])
        print("✅ Polls fetched successfully!")
        print(f"   Number of polls: {len(polls)}")
        print(f"   Skip: {result.get('skip')}")
        print(f"   Limit: {result.get('limit')}")
        print(f"   Status Code: {result.get('status_code')}")

        if polls:
            print(f"   First poll ID: {polls[0].get('id')}")
            print(f"   First poll question: {polls[0].get('question', 'No question')[:50]}...")

        # Check for validation warnings
        if "validation_warning" in result:
            print(f"⚠️  Validation Warning: {result['validation_warning']}")

        return True, polls
    else:
        print("❌ Failed to fetch polls!")
        print(f"   Error: {result.get('error')}")
        print(f"   Message: {result.get('message')}")
        return False, []


def test_pagination(client):
    """Test pagination functionality."""
    print("\nTest 2: Pagination test")
    result = client.fetch_polls(skip=0, limit=2)

    if result["success"]:
        polls = result.get("polls", [])
        print("✅ Pagination works!")
        print(f"   Requested limit: 2, Got: {len(polls)}")
        return True
    else:
        print("❌ Pagination failed!")
        print(f"   Error: {result.get('message')}")
        return False


def test_create_poll(client):
    """Test poll creation (requires authentication)."""
    print("\n" + "="*50)
    print("TESTING POLL CREATION")
    print("="*50)

    if not client.token:
        print("❌ No authentication token available for poll creation!")
        return False

    print("Test 1: Create a valid poll")
    result = client.create_poll(
        question="What's the best testing framework for Python?",
        options=["pytest", "unittest", "nose2", "Robot Framework"]
    )

    if result["success"]:
        poll_data = result["data"]
        print("✅ Poll created successfully!")
        print(f"   Poll ID: {poll_data.get('id')}")
        print(f"   Question: {poll_data.get('question')}")
        print(f"   Number of options: {len(poll_data.get('options', []))}")
        print(f"   Status Code: {result.get('status_code')}")

        if "validation_warning" in result:
            print(f"⚠️  Validation Warning: {result['validation_warning']}")

        return True, poll_data.get('id')
    else:
        print("❌ Failed to create poll!")
        print(f"   Error: {result.get('error')}")
        print(f"   Message: {result.get('message')}")
        return False, None


def test_get_specific_poll(client, poll_id):
    """Test getting a specific poll."""
    print("\n" + "="*50)
    print("TESTING GET SPECIFIC POLL")
    print("="*50)

    print(f"Test 1: Get poll with ID {poll_id}")
    result = client.get_poll(poll_id)

    if result["success"]:
        poll_data = result["data"]
        print("✅ Poll retrieved successfully!")
        print(f"   Poll ID: {poll_data.get('id')}")
        print(f"   Question: {poll_data.get('question')}")
        print(f"   Created at: {poll_data.get('created_at')}")
        print(f"   Owner ID: {poll_data.get('owner_id')}")
        print(f"   Options count: {len(poll_data.get('options', []))}")

        # Show formatted summary
        print("\n📋 Poll Summary:")
        print(format_poll_summary(poll_data))

        return True, poll_data.get('options', [])
    else:
        print("❌ Failed to get poll!")
        print(f"   Error: {result.get('error')}")
        print(f"   Message: {result.get('message')}")
        return False, []


def test_vote_on_poll(client, poll_id, options):
    """Test voting on a poll."""
    print("\n" + "="*50)
    print("TESTING POLL VOTING")
    print("="*50)

    if not client.token:
        print("❌ No authentication token available for voting!")
        return False

    if not options:
        print("❌ No options available to vote on!")
        return False

    # Vote on the first option
    option_id = options[0].get('id')
    option_text = options[0].get('text')

    print(f"Test 1: Vote on option '{option_text}' (ID: {option_id})")
    result = client.vote_on_poll(poll_id, option_id)

    if result["success"]:
        print("✅ Vote recorded successfully!")
        print(f"   Status Code: {result.get('status_code')}")
        return True
    else:
        print("❌ Failed to vote!")
        print(f"   Error: {result.get('error')}")
        print(f"   Message: {result.get('message')}")
        return False


def test_poll_results(client, poll_id):
    """Test getting poll results."""
    print("\n" + "="*50)
    print("TESTING POLL RESULTS")
    print("="*50)

    print(f"Test 1: Get results for poll {poll_id}")
    result = client.get_poll_results(poll_id)

    if result["success"]:
        results_data = result["data"]
        print("✅ Poll results retrieved successfully!")
        print(f"   Poll ID: {results_data.get('poll_id')}")
        print(f"   Question: {results_data.get('question')}")

        results = results_data.get("results", [])
        print(f"   Number of options: {len(results)}")

        print("\n📊 Vote Results:")
        total_votes = sum(r.get('vote_count', 0) for r in results)
        for result_item in results:
            text = result_item.get('text', 'Unknown')
            votes = result_item.get('vote_count', 0)
            percentage = (votes / total_votes * 100) if total_votes > 0 else 0
            print(f"   • {text}: {votes} votes ({percentage:.1f}%)")

        return True
    else:
        print("❌ Failed to get poll results!")
        print(f"   Error: {result.get('error')}")
        print(f"   Message: {result.get('message')}")
        return False


def test_error_cases(client):
    """Test various error scenarios."""
    print("\n" + "="*50)
    print("TESTING ERROR CASES")
    print("="*50)

    # Test empty username/password
    print("Test 1: Empty credentials")
    result = client.register_user("", "")
    if not result["success"]:
        print("✅ Empty credentials properly rejected!")
    else:
        print("❌ Empty credentials not properly handled!")

    # Test invalid poll ID
    print("\nTest 2: Invalid poll ID")
    result = client.get_poll(-1)
    if not result["success"]:
        print("✅ Invalid poll ID properly rejected!")
    else:
        print("❌ Invalid poll ID not properly handled!")

    # Test voting without authentication
    print("\nTest 3: Voting without authentication")
    client_no_auth = PollyAPIClient()  # New client without token
    result = client_no_auth.vote_on_poll(1, 1)
    if not result["success"] and result.get("error") == "authentication_required":
        print("✅ Unauthenticated voting properly rejected!")
    else:
        print("❌ Unauthenticated voting not properly handled!")


def run_comprehensive_tests():
    """Run all tests."""
    print("🚀 Starting Polly API Client Tests")
    print("="*60)

    # Start server
    server_process = start_server()
    if not server_process:
        print("❌ Failed to start server. Exiting.")
        return

    try:
        # Wait a bit more for server to be ready
        print("⏳ Waiting for server to be ready...")
        time.sleep(2)

        # Initialize client
        client = PollyAPIClient("http://127.0.0.1:8000")

        # Run tests
        tests_passed = 0
        total_tests = 0

        # User registration tests
        total_tests += 1
        if test_user_registration(client):
            tests_passed += 1

        total_tests += 1
        if test_duplicate_registration(client):
            tests_passed += 1

        # Login tests
        total_tests += 1
        if test_user_login(client):
            tests_passed += 1

        total_tests += 1
        if test_invalid_login(client):
            tests_passed += 1

        # Poll fetching tests
        total_tests += 1
        fetch_success, existing_polls = test_fetch_polls(client)
        if fetch_success:
            tests_passed += 1

        total_tests += 1
        if test_pagination(client):
            tests_passed += 1

        # Poll creation tests
        total_tests += 1
        create_success, new_poll_id = test_create_poll(client)
        if create_success:
            tests_passed += 1

        # Use created poll ID or fallback to existing poll
        test_poll_id = new_poll_id if new_poll_id else (existing_polls[0].get('id') if existing_polls else 1)

        # Get specific poll test
        total_tests += 1
        get_success, poll_options = test_get_specific_poll(client, test_poll_id)
        if get_success:
            tests_passed += 1

        # Voting tests
        total_tests += 1
        if test_vote_on_poll(client, test_poll_id, poll_options):
            tests_passed += 1

        # Poll results test
        total_tests += 1
        if test_poll_results(client, test_poll_id):
            tests_passed += 1

        # Error case tests
        test_error_cases(client)

        # Final results
        print("\n" + "="*60)
        print("🏁 TEST RESULTS SUMMARY")
        print("="*60)
        print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
        print(f"❌ Tests Failed: {total_tests - tests_passed}/{total_tests}")

        success_rate = (tests_passed / total_tests) * 100
        print(f"📊 Success Rate: {success_rate:.1f}%")

        if success_rate >= 80:
            print("🎉 Overall Status: GOOD - Most functionality working!")
        elif success_rate >= 60:
            print("⚠️  Overall Status: MODERATE - Some issues detected")
        else:
            print("❌ Overall Status: POOR - Significant issues detected")

    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error during tests: {e}")
    finally:
        # Stop server
        if server_process:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            server_process.wait()
            print("✅ Server stopped")


if __name__ == "__main__":
    run_comprehensive_tests()
