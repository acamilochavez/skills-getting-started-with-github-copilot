# Plan: Add Backend FastAPI Tests

## TL;DR
Create a `tests/` directory with `conftest.py` (pytest fixtures) and `test_app.py` (endpoint tests). Tests will use FastAPI's TestClient to verify all endpoints handle happy paths, edge cases, and errors correctly. No dependency changes needed since `httpx` is already installed.

## Steps

1. Create the `tests/` directory and `__init__.py` (marks it as a Python package)
2. Create `tests/conftest.py` with pytest fixtures:
   - FastAPI TestClient fixture for the app
   - Clear/reset in-memory database before each test (optional: fixture to restore initial state)
3. Create `tests/test_app.py` with comprehensive test cases:
   - **Root endpoint tests** (GET `/`) — redirect to static HTML
   - **Get activities tests** (GET `/activities`) — returns activities dict with correct structure
   - **Signup endpoint tests** (POST `/activities/{activity_name}/signup`) — covers:
     - Successful signup
     - Activity not found (404)
     - Duplicate signup (400 error)
     - Email validation if desired
   - **Remove endpoint tests** (DELETE `/activities/{activity_name}/signup`) — covers:
     - Successful removal
     - Activity not found (404)
     - Student not in activity (404)
4. Run tests with pytest to verify all pass

## Relevant Files
- Create `tests/conftest.py` — fixture setup with TestClient initialization
- Create `tests/test_app.py` — test functions for all endpoints and error cases  
- Existing `src/app.py` — no changes (tests import it)
- Existing `pytest.ini` — already configured, no changes needed

## Verification
1. Run `pytest` to execute all tests and verify they pass
2. Run `pytest -v` for detailed output showing each test case
3. Run `pytest --cov=src` to check code coverage of `app.py`

## Decisions
- Test structure: One conftest for fixtures, one test_app.py for all endpoint tests (simple; can be split if it grows)
- Database state: Each test will use the same in-memory database, so order might matter — recommend resetting via fixture or using independent test data per test
- Error handling: Tests will validate both successful responses and HTTPException error cases (404, 400)

## Further Considerations
1. **Database isolation**: Should each test start with fresh data or modify a shared state? 
   - Recommendation: Add a fixture that resets activities to initial state before each test to avoid test interdependence
2. **Capacity testing**: The current endpoint doesn't check `max_participants` — should tests enforce this validation or just test current behavior?
   - Recommendation: Test current behavior first; if you want to add capacity validation, that's a separate feature

## Project Context

### Complete src/ Directory Structure
```
src/
├── app.py
├── README.md
└── static/
    ├── app.js
    ├── index.html
    └── styles.css
```

### Current pytest.ini Configuration
```
[pytest]
pythonpath = .
```
Simple configuration that adds the current directory to the Python path for test discovery.

### Dependencies in requirements.txt
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **httpx** - HTTP client (useful for testing)
- **watchfiles** - File monitoring for development

### Main Endpoints and Functions to Test in app.py

The application is a High School Management System API with these endpoints:

| Endpoint | Method | Function | Purpose |
|----------|--------|----------|---------|
| `/` | GET | `root()` | Redirects to static/index.html |
| `/activities` | GET | `get_activities()` | Returns all activities with details |
| `/activities/{activity_name}/signup` | POST | `signup_for_activity(activity_name, email)` | Sign up a student for an activity |
| `/activities/{activity_name}/signup` | DELETE | `remove_from_activity(activity_name, email)` | Remove a student from an activity |

**Key validation logic to test:**
- Activity existence validation
- Participant capacity limits (max_participants)
- Duplicate signup prevention
- Student removal from activities

### Existing Tests
❌ **No existing tests found** — The project has no `test_*.py` or `*_test.py` files. Testing needs to be set up from scratch.

**Note:** The `httpx` dependency is already included, which is perfect for testing FastAPI endpoints using `TestClient`.
