from dotenv import load_dotenv
import sys
import os
from unittest.mock import patch
import pytest
from flask_jwt_extended import create_access_token

# Load .env.test from the project root
load_dotenv(".env.test")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, get_db_connection

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers():
    """Create a JWT for a known test user."""
    with app.app_context():
        token = create_access_token(identity="test_steam_id")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def clean_test_user():
    """Clean up test users before and after each test."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE steam_id LIKE 'test_steam_id%'")
    conn.commit()
    cur.close()
    conn.close()
    yield
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE steam_id LIKE 'test_steam_id%'")
    conn.commit()
    cur.close()
    conn.close()

def test_hello(client):
    """Test the hello endpoint."""
    resp = client.get("/api/hello")
    assert resp.status_code == 200
    assert resp.json == {"message": "Hello from Flask!"}

def test_signup_and_login(client):
    """Test user signup and login flow."""
    resp = client.post("/api/signup", json={
        "steam_id": "test_steam_id",
        "account_display_name": "testuser",
        "password": "testpass"
    })
    assert resp.status_code in (200, 201)
    assert "id" in resp.json
    # Login
    resp = client.post("/api/login", json={
        "account_display_name": "testuser",
        "password": "testpass"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json

def test_signup_missing_fields(client):
    """Test signup with missing fields returns 400."""
    resp = client.post("/api/signup", json={})
    assert resp.status_code == 400
    assert "error" in resp.json

def test_login_invalid_credentials(client):
    """Test login with invalid credentials returns 401."""
    resp = client.post("/api/login", json={
        "account_display_name": "notarealuser",
        "password": "wrongpass"
    })
    assert resp.status_code == 401
    assert "error" in resp.json

def test_get_users(client):
    """Test getting all users returns a list."""
    resp = client.get("/api/users")
    assert resp.status_code == 200
    assert isinstance(resp.json, list)

def test_add_user_requires_jwt(client):
    """Test that adding a user requires JWT."""
    resp = client.post("/api/users", json={
        "steam_id": "test_steam_id2",
        "display_name": "Test User 2"
    })
    assert resp.status_code == 401

def test_add_user_success(client, auth_headers):
    """Test adding a user with JWT."""
    resp = client.post("/api/users", headers=auth_headers, json={
        "steam_id": "test_steam_id2",
        "display_name": "Test User 2"
    })
    assert resp.status_code in (200, 201)
    assert "id" in resp.json

@patch("app.requests.get")
def test_get_steam_raw(mock_get, client):
    """Test /steam_raw endpoint with mocked Steam API."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"response": {"games": []}}
    resp = client.get("/api/users/76561198846382485/steam_raw")
    assert resp.status_code == 200
    assert "response" in resp.json

@patch("app.requests.get")
def test_get_player_summary_success(mock_get, client):
    """Test /summary endpoint with mocked Steam API."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "response": {"players": [{"steamid": "76561198846382485", "personaname": "TestUser"}]}
    }
    resp = client.get("/api/users/76561198846382485/summary")
    assert resp.status_code == 200
    assert "steamid" in resp.json

@patch("app.requests.get")
def test_get_player_summary_rate_limited(mock_get, client):
    """Test /summary endpoint when Steam API rate limits."""
    mock_get.return_value.status_code = 429
    mock_get.return_value.json.return_value = {}
    resp = client.get("/api/users/76561198846382485/summary")
    assert resp.status_code == 429
    assert "error" in resp.json

def test_get_games_unauthorized(client):
    """Test /games endpoint requires JWT."""
    resp = client.get("/api/users/test_steam_id/games")
    assert resp.status_code == 401

def test_get_games_authorized(client, auth_headers):
    """Test /games endpoint with JWT."""
    resp = client.get("/api/users/test_steam_id/games", headers=auth_headers)
    assert resp.status_code in (200, 404)  # 404 if user not found

def test_get_total_playtime_forbidden(client, auth_headers):
    """Test /total_playtime endpoint with mismatched JWT."""
    resp = client.get("/api/users/other_steam_id/total_playtime", headers=auth_headers)
    assert resp.status_code == 403

def test_get_total_playtime_authorized(client, auth_headers):
    """Test /total_playtime endpoint with correct JWT."""
    resp = client.get("/api/users/test_steam_id/total_playtime", headers=auth_headers)
    assert resp.status_code in (200, 404)

# --- Expand coverage for friends, groups, and error cases below ---

def test_get_friends_unauthorized(client):
    """Test /friends endpoint requires JWT."""
    resp = client.get("/api/users/test_steam_id/friends")
    assert resp.status_code == 401

def test_get_friends_authorized(client, auth_headers):
    """Test /friends endpoint with JWT."""
    resp = client.get("/api/users/test_steam_id/friends", headers=auth_headers)
    assert resp.status_code in (200, 404)

def test_get_groups_unauthorized(client):
    """Test /groups endpoint requires JWT."""
    resp = client.get("/api/users/test_steam_id/groups")
    assert resp.status_code == 401

def test_get_groups_authorized(client, auth_headers):
    """Test /groups endpoint with JWT."""
    resp = client.get("/api/users/test_steam_id/groups", headers=auth_headers)
    assert resp.status_code in (200, 404)

def test_create_group_requires_jwt(client):
    """Test creating a group requires JWT."""
    resp = client.post("/api/groups", json={"name": "Test Group"})
    assert resp.status_code == 401

def test_create_group_success(client, auth_headers):
    """Test creating a group with JWT."""
    resp = client.post("/api/groups", headers=auth_headers, json={"name": "Test Group"})
    assert resp.status_code in (200, 201, 400)  # 400 if group already exists

def test_signup_duplicate_user(client):
    """Test that signing up with the same steam_id updates the user."""
    # First signup
    resp1 = client.post("/api/signup", json={
        "steam_id": "test_steam_id_dup",
        "account_display_name": "dupuser",
        "password": "pass1"
    })
    assert resp1.status_code in (200, 201)
    # Second signup with same steam_id but different display name
    resp2 = client.post("/api/signup", json={
        "steam_id": "test_steam_id_dup",
        "account_display_name": "dupuser2",
        "password": "pass2"
    })
    assert resp2.status_code in (200, 201)
    # Login with new display name and password
    resp3 = client.post("/api/login", json={
        "account_display_name": "dupuser2",
        "password": "pass2"
    })
    assert resp3.status_code == 200
    assert "access_token" in resp3.json

def test_create_group_missing_fields(client, auth_headers):
    """Test creating a group with missing fields returns 400."""
    resp = client.post("/api/groups", headers=auth_headers, json={})
    assert resp.status_code == 400
    assert "error" in resp.json

def test_create_group_invalid_owner(client, auth_headers):
    """Test creating a group with a non-existent owner returns 404."""
    resp = client.post("/api/groups", headers=auth_headers, json={
        "name": "Invalid Owner Group",
        "owner_steam_id": "nonexistent_steam_id"
    })
    assert resp.status_code == 404
    assert "error" in resp.json

def test_jwt_required_on_protected(client):
    """Test that protected endpoints require JWT."""
    resp = client.get("/api/users/test_steam_id/games")
    assert resp.status_code == 401
    resp = client.get("/api/users/test_steam_id/groups")
    assert resp.status_code == 401

def test_invalid_jwt_on_protected(client):
    """Test that invalid JWT returns 422 or 401."""
    headers = {"Authorization": "Bearer notarealtoken"}
    resp = client.get("/api/users/test_steam_id/games", headers=headers)
    assert resp.status_code in (401, 422)

def test_get_friends_empty(client, auth_headers):
    """Test getting friends for a user with no friends returns empty list."""
    # Add user
    client.post("/api/users", headers=auth_headers, json={
        "steam_id": "test_steam_id_emptyfriends",
        "display_name": "No Friends"
    })
    resp = client.get("/api/users/test_steam_id_emptyfriends/friends", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json.get("friends", []), list)
    assert len(resp.json.get("friends", [])) == 0