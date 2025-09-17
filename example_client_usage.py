#!/usr/bin/env python3
"""
Example usage of the Polly API Python client.

This script demonstrates all the main features of the PollyAPIClient
including user registration, authentication, poll management, and voting.
"""

from user_client import PollyAPIClient, format_poll_summary
import time


def main():
    """Demonstrate the Polly API client functionality."""
    print("🗳️  Polly API Python Client Example")
    print("=" * 50)

    # Initialize the client
    client = PollyAPIClient("http://127.0.0.1:8000")

    # Step 1: User Registration
    print("\n📝 Step 1: User Registration")
    print("-" * 30)

    username = f"demo_user_{int(time.time())}"  # Unique username
    password = "secure_password_123"

    print(f"Registering user: {username}")
    registration_result = client.register_user(username, password)

    if registration_result["success"]:
        user_data = registration_result["data"]
        print(f"✅ Registration successful!")
        print(f"   User ID: {user_data['id']}")
        print(f"   Username: {user_data['username']}")
    else:
        print(f"❌ Registration failed: {registration_result['message']}")
        if registration_result.get('status_code') != 400:  # 400 might be duplicate user
            return

    # Step 2: User Login
    print("\n🔐 Step 2: User Login")
    print("-" * 20)

    login_result = client.login(username, password)

    if login_result["success"]:
        token_data = login_result["data"]
        print("✅ Login successful!")
        print(f"   Token type: {token_data['token_type']}")
        print(f"   Token stored: {bool(client.token)}")
    else:
        print(f"❌ Login failed: {login_result['message']}")
        return

    # Step 3: Fetch Existing Polls
    print("\n📋 Step 3: Fetching Existing Polls")
    print("-" * 35)

    polls_result = client.fetch_polls(skip=0, limit=5)

    if polls_result["success"]:
        polls = polls_result["polls"]
        print(f"✅ Found {len(polls)} polls:")
        for i, poll in enumerate(polls, 1):
            print(f"   {i}. {poll['question'][:40]}... (ID: {poll['id']})")
    else:
        print(f"❌ Failed to fetch polls: {polls_result['message']}")

    # Step 4: Create a New Poll
    print("\n🆕 Step 4: Creating a New Poll")
    print("-" * 30)

    new_poll_question = "What's the best way to learn programming?"
    new_poll_options = [
        "Online tutorials and courses",
        "Books and documentation",
        "Practice projects",
        "Coding bootcamps",
        "University computer science"
    ]

    create_result = client.create_poll(new_poll_question, new_poll_options)

    if create_result["success"]:
        new_poll = create_result["data"]
        poll_id = new_poll["id"]
        print("✅ Poll created successfully!")
        print(f"   Poll ID: {poll_id}")
        print(f"   Question: {new_poll['question']}")
        print(f"   Options: {len(new_poll['options'])}")
    else:
        print(f"❌ Failed to create poll: {create_result['message']}")
        return

    # Step 5: Get Poll Details
    print("\n🔍 Step 5: Getting Poll Details")
    print("-" * 32)

    poll_details = client.get_poll(poll_id)

    if poll_details["success"]:
        poll_data = poll_details["data"]
        print("✅ Poll details retrieved!")
        print("\n📊 Poll Summary:")
        print(format_poll_summary(poll_data))
    else:
        print(f"❌ Failed to get poll details: {poll_details['message']}")
        return

    # Step 6: Vote on the Poll
    print("\n🗳️  Step 6: Voting on the Poll")
    print("-" * 30)

    # Vote for the first option (Practice projects)
    first_option = poll_data["options"][2]  # "Practice projects"
    option_id = first_option["id"]

    print(f"Voting for: '{first_option['text']}'")
    vote_result = client.vote_on_poll(poll_id, option_id)

    if vote_result["success"]:
        print("✅ Vote recorded successfully!")
    else:
        print(f"❌ Voting failed: {vote_result['message']}")

    # Step 7: Get Poll Results
    print("\n📊 Step 7: Poll Results")
    print("-" * 25)

    results = client.get_poll_results(poll_id)

    if results["success"]:
        results_data = results["data"]
        print("✅ Poll results retrieved!")
        print(f"\n🗳️  Results for: {results_data['question']}")
        print("-" * 50)

        total_votes = sum(r['vote_count'] for r in results_data['results'])
        print(f"Total votes: {total_votes}")
        print()

        for i, result in enumerate(results_data['results'], 1):
            votes = result['vote_count']
            percentage = (votes / total_votes * 100) if total_votes > 0 else 0
            bar_length = int(percentage / 2)  # Scale to max 50 chars
            bar = "█" * bar_length

            print(f"{i}. {result['text']}")
            print(f"   {votes} votes ({percentage:.1f}%) {bar}")
            print()
    else:
        print(f"❌ Failed to get results: {results['message']}")

    # Step 8: Demonstrate Pagination
    print("\n📄 Step 8: Pagination Example")
    print("-" * 30)

    print("Fetching all polls using pagination...")
    all_polls = client.get_all_polls(page_size=3)

    if all_polls["success"]:
        total_polls = all_polls["total_count"]
        print(f"✅ Retrieved all {total_polls} polls from the API")

        if total_polls > 0:
            print("\nFirst 3 polls:")
            for poll in all_polls["polls"][:3]:
                print(f"   • {poll['question'][:50]}...")
    else:
        print(f"❌ Failed to get all polls: {all_polls['message']}")

    # Step 9: Error Handling Example
    print("\n⚠️  Step 9: Error Handling Demo")
    print("-" * 35)

    # Try to access a non-existent poll
    error_result = client.get_poll(99999)
    if not error_result["success"]:
        print("✅ Error handling works correctly!")
        print(f"   Error type: {error_result.get('error', 'unknown')}")
        print(f"   Message: {error_result['message']}")
        print(f"   Status code: {error_result.get('status_code', 'N/A')}")

    # Step 10: Summary
    print("\n🎉 Example Complete!")
    print("-" * 20)
    print("This example demonstrated:")
    print("• User registration and authentication")
    print("• Poll creation with multiple options")
    print("• Voting on polls")
    print("• Retrieving poll results with statistics")
    print("• Pagination and error handling")
    print("• Comprehensive logging and validation")
    print()
    print("Check the logs above for detailed API interactions!")


if __name__ == "__main__":
    print("🚀 Starting Polly API Client Example")
    print("Make sure the Polly API server is running at http://127.0.0.1:8000")
    print()

    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Example interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
