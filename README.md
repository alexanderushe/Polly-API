# Polly-API: FastAPI Poll Application

A simple poll application built with FastAPI, SQLite, and JWT authentication. Users can register, log in, create, retrieve, vote on, and delete polls. The project follows best practices with modular code in the `api/` directory.

## Quick Start

Get up and running in 3 minutes:

```bash
# 1. Clone and setup
git clone <your-repo-url>
cd Polly-API
pip install -r requirements.txt

# 2. Start the API server
uvicorn main:app --reload

# 3. Use the Python client
python3 example_client_usage.py
```

The API will be available at `http://127.0.0.1:8000` with interactive docs at `http://127.0.0.1:8000/docs`.

## Features

- User registration and login (JWT authentication)
- Create, retrieve, and delete polls
- Add options to polls (minimum of two options required)
- Vote on polls (authenticated users only)
- View poll results with vote counts
- SQLite database with SQLAlchemy ORM
- Modular code structure for maintainability

## Project Structure

```
Polly-API/
├── api/
│   ├── __init__.py
│   ├── auth.py
│   ├── database.py
│   ├── models.py
│   ├── routes.py
│   └── schemas.py
├── main.py
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Clone the repository**

```bash
git clone <your-repo-url>
cd Polly-API
```

2. **Set up a Python virtual environment (recommended)**

A virtual environment helps isolate your project dependencies.

- **On Unix/macOS:**

  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

- **On Windows (cmd):**

  ```cmd
  python -m venv venv
  venv\Scripts\activate
  ```

- **On Windows (PowerShell):**

  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```

To deactivate the virtual environment, simply run:

```bash
deactivate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set environment variables (optional)**

Create a `.env` file in the project root to override the default secret key:

```
SECRET_KEY=your_super_secret_key
```

5. **Run the application**

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Usage

### 1. Register a new user

- **Endpoint:** `POST /register`
- **Body:**

```json
{
  "username": "yourusername",
  "password": "yourpassword"
}
```

### 2. Login

- **Endpoint:** `POST /login`
- **Body (form):**
  - `username`: yourusername
  - `password`: yourpassword
- **Response:**

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

### 3. Get all polls

- **Endpoint:** `GET /polls`
- **Query params:** `skip` (default 0), `limit` (default 10)
- **Authentication:** Not required

### 4. Create a poll

- **Endpoint:** `POST /polls`
- **Headers:** `Authorization: Bearer <access_token>`
- **Body:**

```json
{
  "question": "Your poll question",
  "options": ["Option 1", "Option 2"]
}
```

### 5. Get a specific poll

- **Endpoint:** `GET /polls/{poll_id}`
- **Authentication:** Not required

### 6. Vote on a poll

- **Endpoint:** `POST /polls/{poll_id}/vote`
- **Headers:** `Authorization: Bearer <access_token>`
- **Body:**

```json
{
  "option_id": 1
}
```

### 7. Get poll results

- **Endpoint:** `GET /polls/{poll_id}/results`
- **Authentication:** Not required
- **Response:**

```json
{
  "poll_id": 1,
  "question": "Your poll question",
  "results": [
    {
      "option_id": 1,
      "text": "Option 1",
      "vote_count": 3
    },
    {
      "option_id": 2,
      "text": "Option 2",
      "vote_count": 1
    }
  ]
}
```

### 8. Delete a poll

- **Endpoint:** `DELETE /polls/{poll_id}`
- **Headers:** `Authorization: Bearer <access_token>`

## Python Client Library

The project includes a comprehensive Python client library (`user_client.py`) that provides a convenient interface for interacting with the Polly API.

### Key Features

- **🔐 Automatic Authentication Management**: JWT tokens are automatically stored and included in protected requests
- **✅ Response Validation**: All API responses are validated against the OpenAPI schema (UserOut, PollOut, etc.)
- **📝 Comprehensive Logging**: INFO/WARNING/ERROR logs for all operations with meaningful messages
- **🔄 Proper HTTP Status Handling**: Correctly handles 200, 201, 400, 401, 404, and 500+ status codes
- **🛡️ Error Handling**: Structured error responses with error types and detailed messages
- **📊 Request Body Validation**: Validates required fields like username, password, question, and options
- **🔗 Pagination Support**: Built-in pagination with `skip` and `limit` parameters
- **📄 Auto-pagination**: `get_all_polls()` automatically handles pagination to fetch all data
- **⚡ Network Resilience**: Configurable timeouts and proper connection error handling
- **🧪 Testing Support**: Includes comprehensive test suites and examples

### Benefits Over Raw HTTP Requests

1. **Type Safety**: Python class with proper method signatures and return types
2. **OpenAPI Compliance**: Request bodies and response structures match the API specification exactly
3. **Authentication Handling**: No need to manually manage JWT tokens in headers
4. **Error Consistency**: Standardized error response format across all methods
5. **Logging Integration**: Built-in logging helps with debugging and monitoring
6. **Validation**: Client-side validation prevents invalid requests
7. **Convenience Methods**: High-level methods like `get_all_polls()` handle complex operations

### Installation

Make sure you have the `requests` library installed:

```bash
pip install requests
```

### Basic Usage

```python
from user_client import PollyAPIClient

# Initialize the client
client = PollyAPIClient("http://127.0.0.1:8000")

# Register a new user
result = client.register_user("username", "password")
if result["success"]:
    print(f"User registered! ID: {result['data']['id']}")
else:
    print(f"Registration failed: {result['message']}")

# Login to get authentication token
login_result = client.login("username", "password")
if login_result["success"]:
    print("Login successful! Token stored automatically.")
else:
    print(f"Login failed: {login_result['message']}")

# Fetch polls with pagination
polls_result = client.fetch_polls(skip=0, limit=10)
if polls_result["success"]:
    polls = polls_result["polls"]
    print(f"Found {len(polls)} polls")
    for poll in polls:
        print(f"- {poll['question']} (ID: {poll['id']})")

# Create a poll (requires authentication)
if client.token:
    create_result = client.create_poll(
        question="What's your favorite programming language?",
        options=["Python", "JavaScript", "Java", "C++"]
    )
    if create_result["success"]:
        poll_id = create_result["data"]["id"]
        print(f"Poll created with ID: {poll_id}")

# Vote on a poll (requires authentication)
if client.token and poll_id:
    # Get poll details to find option IDs
    poll_details = client.get_poll(poll_id)
    if poll_details["success"]:
        first_option_id = poll_details["data"]["options"][0]["id"]
        
        vote_result = client.vote_on_poll(poll_id, first_option_id)
        if vote_result["success"]:
            print("Vote recorded successfully!")

# Get poll results
results = client.get_poll_results(poll_id)
if results["success"]:
    print(f"Results for: {results['data']['question']}")
    for result in results["data"]["results"]:
        print(f"- {result['text']}: {result['vote_count']} votes")
```

### Client Methods

#### Authentication Methods

- **`register_user(username, password)`**
  - Registers a new user
  - Returns: `{"success": bool, "data": UserOut, "status_code": int}`

- **`login(username, password)`**
  - Authenticates user and stores JWT token
  - Returns: `{"success": bool, "data": Token, "status_code": int}`

#### Poll Methods

- **`fetch_polls(skip=0, limit=10)`**
  - Fetches polls with pagination
  - Returns: `{"success": bool, "polls": [PollOut], "count": int}`

- **`get_poll(poll_id)`**
  - Gets a specific poll by ID
  - Returns: `{"success": bool, "data": PollOut, "status_code": int}`

- **`create_poll(question, options)`** *(requires authentication)*
  - Creates a new poll
  - Args: `question` (str), `options` (List[str])
  - Returns: `{"success": bool, "data": PollOut, "status_code": int}`

- **`vote_on_poll(poll_id, option_id)`** *(requires authentication)*
  - Votes on a poll option
  - Returns: `{"success": bool, "data": VoteOut, "status_code": int}`

- **`get_poll_results(poll_id)`**
  - Gets poll results with vote counts
  - Returns: `{"success": bool, "data": PollResults, "status_code": int}`

- **`get_all_polls(page_size=50)`**
  - Fetches all polls using automatic pagination
  - Returns: `{"success": bool, "polls": [PollOut], "total_count": int}`

### Error Handling

The client provides structured error responses:

```python
{
    "success": False,
    "error": "bad_request",  # Error type: bad_request, unauthorized, not_found, etc.
    "message": "Username already registered",  # Human-readable message
    "status_code": 400,      # HTTP status code
    "details": {...}         # Additional error details from API
}
```

### Response Validation

The client automatically validates API responses against the OpenAPI schema:

- **UserOut**: `{id: int, username: str}`
- **PollOut**: `{id: int, question: str, created_at: datetime, owner_id: int, options: [OptionOut]}`
- **OptionOut**: `{id: int, text: str, poll_id: int}`

### Logging

The client includes comprehensive logging:

```python
import logging
logging.basicConfig(level=logging.INFO)

# The client will log:
# INFO: Successful operations and progress
# WARNING: Client errors (400, 401, 404) 
# ERROR: Server errors and network issues
```

### Utility Functions

- **`format_poll_summary(poll)`** - Formats poll data into a readable summary
- **`PollyAPIClient.token`** - Access the stored JWT token
- **`PollyAPIClient.base_url`** - Get/set the API base URL

### Example Usage

See the complete example in `example_client_usage.py`:

```bash
python3 example_client_usage.py
```

### Testing

Run the comprehensive test suite:

```bash
python3 test_client.py
```

Or use the minimal test for basic functionality:

```bash
python3 minimal_test.py
```

### Client Implementation Highlights

The client implementation follows best practices:

- **Correct Request Format**: Uses JSON for most endpoints, form data for login (as per OpenAPI spec)
- **Proper HTTP Methods**: POST for registration/login/voting, GET for fetching, DELETE for removal
- **Authentication Headers**: `Authorization: Bearer <token>` for protected endpoints
- **Response Code Handling**: Different logic for 200 (success), 400 (bad request), 401 (unauthorized), etc.
- **Schema Validation**: Validates UserOut, PollOut, OptionOut response structures
- **Error Logging**: Logs network errors, validation failures, and unexpected responses
- **Request Validation**: Checks for required fields before making API calls

## Interactive API Docs

Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive Swagger UI.

## License

MIT License
