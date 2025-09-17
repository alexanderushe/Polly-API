import requests
import logging
from typing import Dict, Any, Optional, List, Tuple
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PollyAPIClient:
    """Client for interacting with the Polly API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None

    def _get_headers(self, include_auth: bool = False) -> Dict[str, str]:
        """Get request headers with optional authentication."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if include_auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        return headers

    def _handle_response(self, response: requests.Response, endpoint: str) -> Dict[str, Any]:
        """Handle HTTP response with proper logging and error handling."""
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON response from {endpoint}: {response.text}")
            response_data = {"detail": "Invalid JSON response"}

        if response.status_code == 200:
            logger.info(f"Successfully called {endpoint}")
            return {
                "success": True,
                "data": response_data,
                "status_code": response.status_code
            }
        elif response.status_code == 201:
            logger.info(f"Successfully created resource at {endpoint}")
            return {
                "success": True,
                "data": response_data,
                "status_code": response.status_code
            }
        elif response.status_code == 400:
            error_msg = response_data.get("detail", "Bad request")
            logger.warning(f"Bad request to {endpoint}: {error_msg}")
            return {
                "success": False,
                "error": "bad_request",
                "message": error_msg,
                "status_code": response.status_code,
                "details": response_data
            }
        elif response.status_code == 401:
            error_msg = response_data.get("detail", "Unauthorized")
            logger.warning(f"Unauthorized request to {endpoint}: {error_msg}")
            return {
                "success": False,
                "error": "unauthorized",
                "message": error_msg,
                "status_code": response.status_code
            }
        elif response.status_code == 404:
            error_msg = response_data.get("detail", "Not found")
            logger.warning(f"Resource not found at {endpoint}: {error_msg}")
            return {
                "success": False,
                "error": "not_found",
                "message": error_msg,
                "status_code": response.status_code
            }
        else:
            error_msg = response_data.get("detail", f"HTTP {response.status_code}")
            logger.error(f"Unexpected response from {endpoint}: {response.status_code} - {error_msg}")
            return {
                "success": False,
                "error": "server_error",
                "message": error_msg,
                "status_code": response.status_code,
                "details": response_data
            }

    def _validate_user_out(self, data: Dict[str, Any]) -> bool:
        """Validate UserOut response structure."""
        required_fields = ["id", "username"]
        return all(field in data for field in required_fields) and \
               isinstance(data["id"], int) and isinstance(data["username"], str)

    def _validate_poll_out(self, data: Dict[str, Any]) -> bool:
        """Validate PollOut response structure."""
        required_fields = ["id", "question", "created_at", "owner_id", "options"]
        if not all(field in data for field in required_fields):
            return False

        # Validate field types
        if not (isinstance(data["id"], int) and
                isinstance(data["question"], str) and
                isinstance(data["owner_id"], int) and
                isinstance(data["options"], list)):
            return False

        # Validate options structure
        for option in data["options"]:
            if not self._validate_option_out(option):
                return False

        return True

    def _validate_option_out(self, data: Dict[str, Any]) -> bool:
        """Validate OptionOut response structure."""
        required_fields = ["id", "text", "poll_id"]
        return all(field in data for field in required_fields) and \
               isinstance(data["id"], int) and \
               isinstance(data["text"], str) and \
               isinstance(data["poll_id"], int)

    def register_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        Register a new user via the /register endpoint.

        Args:
            username (str): The username for the new user
            password (str): The password for the new user

        Returns:
            Dict[str, Any]: Response with user data or error information
        """
        if not username or not password:
            logger.error("Username and password are required")
            return {
                "success": False,
                "error": "validation_error",
                "message": "Username and password are required"
            }

        url = f"{self.base_url}/register"
        payload = {
            "username": username,
            "password": password
        }

        logger.info(f"Attempting to register user: {username}")

        try:
            response = requests.post(
                url=url,
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )

            result = self._handle_response(response, "/register")

            # Validate UserOut structure on success
            if result.get("success") and "data" in result:
                if not self._validate_user_out(result["data"]):
                    logger.error("Invalid UserOut response structure")
                    result["validation_warning"] = "Response structure doesn't match UserOut schema"

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during registration: {str(e)}")
            return {
                "success": False,
                "error": "network_error",
                "message": f"Request failed: {str(e)}"
            }

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login and get JWT token via the /login endpoint.

        Args:
            username (str): The username
            password (str): The password

        Returns:
            Dict[str, Any]: Response with token or error information
        """
        if not username or not password:
            logger.error("Username and password are required for login")
            return {
                "success": False,
                "error": "validation_error",
                "message": "Username and password are required"
            }

        url = f"{self.base_url}/login"

        # Use form data as specified in OpenAPI spec
        headers = {"Accept": "application/json"}
        data = {
            "username": username,
            "password": password
        }

        logger.info(f"Attempting to login user: {username}")

        try:
            response = requests.post(
                url=url,
                data=data,  # Form data, not JSON
                headers=headers,
                timeout=30
            )

            result = self._handle_response(response, "/login")

            # Store token if login successful
            if result.get("success") and "data" in result:
                token_data = result["data"]
                if "access_token" in token_data:
                    self.token = token_data["access_token"]
                    logger.info("Successfully stored authentication token")
                else:
                    logger.warning("No access_token in login response")

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during login: {str(e)}")
            return {
                "success": False,
                "error": "network_error",
                "message": f"Request failed: {str(e)}"
            }

    def fetch_polls(self, skip: int = 0, limit: int = 10) -> Dict[str, Any]:
        """
        Fetch paginated poll data from the /polls endpoint.

        Args:
            skip (int): Number of items to skip (default: 0)
            limit (int): Maximum number of items to return (default: 10)

        Returns:
            Dict[str, Any]: Response with polls array or error information
        """
        if skip < 0 or limit <= 0:
            logger.error("Skip must be >= 0 and limit must be > 0")
            return {
                "success": False,
                "error": "validation_error",
                "message": "Skip must be >= 0 and limit must be > 0"
            }

        url = f"{self.base_url}/polls"
        params = {
            "skip": skip,
            "limit": limit
        }

        logger.info(f"Fetching polls with skip={skip}, limit={limit}")

        try:
            response = requests.get(
                url=url,
                params=params,
                headers={"Accept": "application/json"},
                timeout=30
            )

            result = self._handle_response(response, "/polls")

            # Validate response structure on success
            if result.get("success") and "data" in result:
                polls = result["data"]
                if not isinstance(polls, list):
                    logger.error("Expected polls to be an array")
                    result["validation_warning"] = "Response is not an array"
                else:
                    # Validate each poll structure
                    valid_polls = 0
                    for poll in polls:
                        if self._validate_poll_out(poll):
                            valid_polls += 1
                        else:
                            logger.warning(f"Poll {poll.get('id', 'unknown')} has invalid structure")

                    result["polls"] = polls
                    result["count"] = len(polls)
                    result["valid_polls"] = valid_polls
                    result["skip"] = skip
                    result["limit"] = limit

                    logger.info(f"Successfully fetched {len(polls)} polls ({valid_polls} valid)")

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during polls fetch: {str(e)}")
            return {
                "success": False,
                "error": "network_error",
                "message": f"Request failed: {str(e)}"
            }

    def create_poll(self, question: str, options: List[str]) -> Dict[str, Any]:
        """
        Create a new poll via the /polls endpoint (requires authentication).

        Args:
            question (str): The poll question
            options (List[str]): List of poll options

        Returns:
            Dict[str, Any]: Response with created poll or error information
        """
        if not self.token:
            logger.error("Authentication required for creating polls")
            return {
                "success": False,
                "error": "authentication_required",
                "message": "Please login first to create polls"
            }

        if not question or not options or len(options) < 2:
            logger.error("Question and at least 2 options are required")
            return {
                "success": False,
                "error": "validation_error",
                "message": "Question and at least 2 options are required"
            }

        url = f"{self.base_url}/polls"
        payload = {
            "question": question,
            "options": options
        }

        logger.info(f"Creating poll with question: {question[:50]}...")

        try:
            response = requests.post(
                url=url,
                json=payload,
                headers=self._get_headers(include_auth=True),
                timeout=30
            )

            result = self._handle_response(response, "/polls")

            # Validate PollOut structure on success
            if result.get("success") and "data" in result:
                if not self._validate_poll_out(result["data"]):
                    logger.error("Invalid PollOut response structure")
                    result["validation_warning"] = "Response structure doesn't match PollOut schema"
                else:
                    logger.info(f"Successfully created poll with ID: {result['data'].get('id')}")

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during poll creation: {str(e)}")
            return {
                "success": False,
                "error": "network_error",
                "message": f"Request failed: {str(e)}"
            }

    def get_poll(self, poll_id: int) -> Dict[str, Any]:
        """
        Get a specific poll by ID.

        Args:
            poll_id (int): The poll ID

        Returns:
            Dict[str, Any]: Response with poll data or error information
        """
        if not isinstance(poll_id, int) or poll_id <= 0:
            logger.error("Poll ID must be a positive integer")
            return {
                "success": False,
                "error": "validation_error",
                "message": "Poll ID must be a positive integer"
            }

        url = f"{self.base_url}/polls/{poll_id}"

        logger.info(f"Fetching poll with ID: {poll_id}")

        try:
            response = requests.get(
                url=url,
                headers={"Accept": "application/json"},
                timeout=30
            )

            result = self._handle_response(response, f"/polls/{poll_id}")

            # Validate PollOut structure on success
            if result.get("success") and "data" in result:
                if not self._validate_poll_out(result["data"]):
                    logger.error("Invalid PollOut response structure")
                    result["validation_warning"] = "Response structure doesn't match PollOut schema"

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during poll fetch: {str(e)}")
            return {
                "success": False,
                "error": "network_error",
                "message": f"Request failed: {str(e)}"
            }

    def vote_on_poll(self, poll_id: int, option_id: int) -> Dict[str, Any]:
        """
        Vote on a poll option (requires authentication).

        Args:
            poll_id (int): The poll ID
            option_id (int): The option ID to vote for

        Returns:
            Dict[str, Any]: Response with vote data or error information
        """
        if not self.token:
            logger.error("Authentication required for voting")
            return {
                "success": False,
                "error": "authentication_required",
                "message": "Please login first to vote on polls"
            }

        if not isinstance(poll_id, int) or poll_id <= 0:
            logger.error("Poll ID must be a positive integer")
            return {
                "success": False,
                "error": "validation_error",
                "message": "Poll ID must be a positive integer"
            }

        if not isinstance(option_id, int) or option_id <= 0:
            logger.error("Option ID must be a positive integer")
            return {
                "success": False,
                "error": "validation_error",
                "message": "Option ID must be a positive integer"
            }

        url = f"{self.base_url}/polls/{poll_id}/vote"
        payload = {
            "option_id": option_id
        }

        logger.info(f"Voting on poll {poll_id}, option {option_id}")

        try:
            response = requests.post(
                url=url,
                json=payload,
                headers=self._get_headers(include_auth=True),
                timeout=30
            )

            result = self._handle_response(response, f"/polls/{poll_id}/vote")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during voting: {str(e)}")
            return {
                "success": False,
                "error": "network_error",
                "message": f"Request failed: {str(e)}"
            }

    def get_poll_results(self, poll_id: int) -> Dict[str, Any]:
        """
        Get poll results.

        Args:
            poll_id (int): The poll ID

        Returns:
            Dict[str, Any]: Response with poll results or error information
        """
        if not isinstance(poll_id, int) or poll_id <= 0:
            logger.error("Poll ID must be a positive integer")
            return {
                "success": False,
                "error": "validation_error",
                "message": "Poll ID must be a positive integer"
            }

        url = f"{self.base_url}/polls/{poll_id}/results"

        logger.info(f"Fetching results for poll {poll_id}")

        try:
            response = requests.get(
                url=url,
                headers={"Accept": "application/json"},
                timeout=30
            )

            result = self._handle_response(response, f"/polls/{poll_id}/results")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during results fetch: {str(e)}")
            return {
                "success": False,
                "error": "network_error",
                "message": f"Request failed: {str(e)}"
            }

    def get_all_polls(self, page_size: int = 50) -> Dict[str, Any]:
        """
        Fetch all polls by automatically handling pagination.

        Args:
            page_size (int): Number of polls to fetch per request (default: 50)

        Returns:
            Dict[str, Any]: Response with all polls or error information
        """
        all_polls = []
        skip = 0

        logger.info("Starting to fetch all polls with pagination")

        try:
            while True:
                result = self.fetch_polls(skip=skip, limit=page_size)

                if not result.get("success"):
                    logger.error(f"Failed to fetch polls at skip={skip}: {result.get('message')}")
                    return result

                polls = result.get("polls", [])
                if not polls:
                    break

                all_polls.extend(polls)
                logger.info(f"Fetched {len(polls)} polls (total so far: {len(all_polls)})")

                # If we got fewer polls than requested, we've reached the end
                if len(polls) < page_size:
                    break

                skip += page_size

            logger.info(f"Successfully fetched all {len(all_polls)} polls")
            return {
                "success": True,
                "polls": all_polls,
                "total_count": len(all_polls)
            }

        except Exception as e:
            logger.error(f"Unexpected error fetching all polls: {str(e)}")
            return {
                "success": False,
                "error": "unexpected_error",
                "message": f"Error fetching all polls: {str(e)}"
            }


def format_poll_summary(poll: Dict[str, Any]) -> str:
    """
    Format a poll object into a readable summary string.

    Args:
        poll (Dict[str, Any]): Poll object from the API response

    Returns:
        str: Formatted poll summary
    """
    poll_id = poll.get("id", "Unknown")
    question = poll.get("question", "No question")
    created_at = poll.get("created_at", "Unknown")
    owner_id = poll.get("owner_id", "Unknown")
    options = poll.get("options", [])

    # Format the creation date if available
    formatted_date = created_at
    try:
        if created_at != "Unknown" and isinstance(created_at, str):
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        pass  # Keep original format if parsing fails

    summary = f"Poll ID: {poll_id}\n"
    summary += f"Question: {question}\n"
    summary += f"Created: {formatted_date}\n"
    summary += f"Owner ID: {owner_id}\n"
    summary += f"Options ({len(options)}):\n"

    for i, option in enumerate(options, 1):
        option_text = option.get("text", "No text")
        option_id = option.get("id", "Unknown")
        summary += f"  {i}. {option_text} (ID: {option_id})\n"

    return summary


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = PollyAPIClient("http://localhost:8000")

    print("=== User Registration Example ===")
    result = client.register_user("testuser123", "securepassword")
    if result["success"]:
        user_data = result["data"]
        print(f"User registered successfully!")
        print(f"User ID: {user_data.get('id')}")
        print(f"Username: {user_data.get('username')}")
    else:
        print(f"Registration failed: {result['message']}")

    print("\n=== User Login Example ===")
    login_result = client.login("testuser123", "securepassword")
    if login_result["success"]:
        token_data = login_result["data"]
        print(f"Login successful!")
        print(f"Token type: {token_data.get('token_type')}")
        print("Authentication token stored in client")
    else:
        print(f"Login failed: {login_result['message']}")

    print("\n=== Fetch Polls Example ===")
    polls_result = client.fetch_polls(skip=0, limit=5)
    if polls_result["success"]:
        polls = polls_result.get("polls", [])
        print(f"Successfully fetched {len(polls)} polls:")
        for poll in polls:
            print(f"- {poll.get('question', 'No question')} (ID: {poll.get('id')})")
    else:
        print(f"Failed to fetch polls: {polls_result['message']}")

    print("\n=== Create Poll Example (requires login) ===")
    if client.token:
        create_result = client.create_poll(
            question="What's your favorite programming language?",
            options=["Python", "JavaScript", "Java", "C++", "Go"]
        )
        if create_result["success"]:
            poll_data = create_result["data"]
            print(f"Poll created successfully!")
            print(f"Poll ID: {poll_data.get('id')}")
            print(f"Question: {poll_data.get('question')}")
        else:
            print(f"Failed to create poll: {create_result['message']}")
    else:
        print("Skipping poll creation - not authenticated")

    print("\n=== Get Specific Poll Example ===")
    poll_result = client.get_poll(1)
    if poll_result["success"]:
        poll_data = poll_result["data"]
        print("Poll details:")
        print(format_poll_summary(poll_data))
    else:
        print(f"Failed to get poll: {poll_result['message']}")

    print("\n=== Vote Example (requires login) ===")
    if client.token:
        vote_result = client.vote_on_poll(poll_id=1, option_id=1)
        if vote_result["success"]:
            print("Vote recorded successfully!")
        else:
            print(f"Failed to vote: {vote_result['message']}")
    else:
        print("Skipping vote - not authenticated")

    print("\n=== Get Poll Results Example ===")
    results = client.get_poll_results(1)
    if results["success"]:
        results_data = results["data"]
        print(f"Poll Results for: {results_data.get('question')}")
        for result in results_data.get("results", []):
            print(f"- {result.get('text')}: {result.get('vote_count')} votes")
    else:
        print(f"Failed to get results: {results['message']}")
