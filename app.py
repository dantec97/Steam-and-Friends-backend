import os
from flask import Flask, jsonify, request, redirect, g, url_for, session
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv
import requests
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import re
import urllib.parse
import urllib.request
import json
import datetime
from datetime import timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address




# comment out the line below for testing, remember to uncomment it when deploying!!!!
load_dotenv()

app = Flask(__name__)
CORS(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[]
)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")  # Use a strong secret in production!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)
jwt = JWTManager(app)
def get_db_connection():
    # uncomment the line below to debug the connection
    # print("Connecting to DB:", os.getenv("DB_NAME")) 

    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )



@app.route("/api/hello")
def hello():
    return jsonify({"message": "Hello from Flask!"})


@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()
    steam_id = data.get("steam_id")
    account_display_name = data.get("account_display_name")
    password = data.get("password")
    if not steam_id or not account_display_name or not password:
        return jsonify({"error": "steam_id, account_display_name, and password are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE steam_id = %s;", (steam_id,))
        user = cur.fetchone()
        hashed_pw = generate_password_hash(password)
        if user:
            # Update existing user
            cur.execute(
                "UPDATE users SET password_hash = %s, account_display_name = %s WHERE steam_id = %s;",
                (hashed_pw, account_display_name, steam_id)
            )
            user_id = user[0]
        else:
            # Insert new user
            cur.execute(
                "INSERT INTO users (steam_id, password_hash, account_display_name) VALUES (%s, %s, %s) RETURNING id;",
                (steam_id, hashed_pw, account_display_name)
            )
            user_id = cur.fetchone()[0]
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()

    return jsonify({"id": user_id, "steam_id": steam_id, "account_display_name": account_display_name}), 201

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    account_display_name = data.get("account_display_name")
    password = data.get("password")
    if not account_display_name or not password:
        return jsonify({"error": "Missing credentials"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash, steam_id FROM users WHERE account_display_name = %s;", (account_display_name,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if not user or not check_password_hash(user[1], password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user[2])  # user[2] is steam_id
    return jsonify(access_token=access_token, steam_id=user[2])

# Example endpoint to test DB connection
@app.route("/api/users")
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, steam_id, display_name FROM users;")
    users = [
        {"id": row[0], "steam_id": row[1], "display_name": row[2]}
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return jsonify(users)


@app.route("/api/users", methods=["POST"])
@jwt_required()
def add_user():
    data = request.get_json()
    steam_id = data.get("steam_id")
    display_name = data.get("display_name")
    if not steam_id or not display_name:
        return jsonify({"error": "steam_id and display_name are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (steam_id, display_name) VALUES (%s, %s) RETURNING id;",
            (steam_id, display_name)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()

    return jsonify({"id": user_id, "steam_id": steam_id, "display_name": display_name}), 201


@app.route("/api/users/<steam_id>/fetch_games", methods=["POST"])
@jwt_required()
@limiter.limit("10 per day")
def fetch_games(steam_id):
    # Call Steam API, update DB
    update_games_info(steam_id)
    return jsonify({"message": "Games synced successfully."}), 200

@app.route("/api/users/<friend_steam_id>/fetch_games", methods=["POST"])
@jwt_required()
@limiter.limit("10 per day")
def fetch_friend_games(friend_steam_id):
    update_games_info(friend_steam_id)
    return jsonify({"message": "Friend's games synced successfully."}), 200

@app.route("/api/users/<steam_id>/steam_raw", methods=["GET"])
def get_steam_raw(steam_id):
    steam_api_key = os.getenv("STEAM_API_KEY")
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {
        "key": steam_api_key,
        "steamid": steam_id,
        "include_appinfo": True,
        "include_played_free_games": True,
        "format": "json"
    }
    response = requests.get(url, params=params)
    print("Status code:", response.status_code)
    print("Response text:", response.text)  # <-- Add this line
    try:
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": "Failed to decode JSON", "details": response.text}), 500
    
@app.route("/api/users/<steam_id>/games", methods=["GET"])
@jwt_required()
def get_games(steam_id):
    conn = get_db_connection()
    cur = conn.cursor()
    # Get user_id
    cur.execute("SELECT id FROM users WHERE steam_id = %s;", (steam_id,))
    user_row = cur.fetchone()
    if not user_row:
        cur.close()
        conn.close()
        return jsonify({"games": []})
    user_id = user_row[0]
    # Join user_games and games to get all games for this user
    cur.execute("""
        SELECT g.appid, g.name, g.image_url, ug.playtime_minutes, g.id
        FROM user_games ug
        JOIN games g ON ug.game_id = g.id
        WHERE ug.user_id = %s
        ORDER BY ug.playtime_minutes DESC
    """, (user_id,))
    games = [
        {
            "appid": row[0],
            "name": row[1],
            "image_url": row[2],
            "playtime_minutes": row[3],
            "id": row[4]
        }
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return jsonify({"games": games})
    
@app.route("/api/users/<steam_id>/total_playtime", methods=["GET"])
@jwt_required()
def get_total_playtime(steam_id):
    identity = get_jwt_identity()
    if identity != steam_id:
        return jsonify({"error": "Forbidden"}), 403
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COALESCE(SUM(ug.playtime_minutes), 0)
        FROM users u
        JOIN user_games ug ON u.id = ug.user_id
        WHERE u.steam_id = %s
    """, (steam_id,))
    total_minutes = cur.fetchone()[0] or 0
    cur.close()
    conn.close()
    return jsonify({"total_playtime_minutes": total_minutes})

@app.route("/api/users/<steam_id>/friends", methods=["GET"])
@jwt_required()
def get_friends(steam_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE steam_id = %s;", (steam_id,))
    user_row = cur.fetchone()
    if not user_row:
        cur.close()
        conn.close()
        return jsonify({"friends": []})
    user_id = user_row[0]
    cur.execute("""
        SELECT f.friend_steam_id, u.display_name, u.avatar_url, f.friend_since
        FROM friends f
        LEFT JOIN users u ON f.friend_steam_id = u.steam_id
        JOIN users owner ON f.user_id = owner.id
        WHERE owner.steam_id = %s
        ORDER BY f.friend_since DESC
    """, (steam_id,))
    friends = [
        {
            "steam_id": row[0],
            "display_name": row[1],
            "avatar_url": row[2],
        }
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return jsonify({"friends": friends})

@app.route("/api/users/<steam_id>/friends_top_games", methods=["GET"])
@jwt_required()
def get_friends_top_games(steam_id):
    identity = get_jwt_identity()
    if identity != steam_id:
        return jsonify({"error": "Forbidden"}), 403

    conn = get_db_connection()
    cur = conn.cursor()
    # Get user_id
    cur.execute("SELECT id FROM users WHERE steam_id = %s", (steam_id,))
    user_row = cur.fetchone()
    if not user_row:
        cur.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404
    user_id = user_row[0]

    # Get friends' steam_ids
    cur.execute("SELECT friend_steam_id FROM friends WHERE user_id = %s", (user_id,))
    friend_ids = [row[0] for row in cur.fetchall()]
    if not friend_ids:
        cur.close()
        conn.close()
        return jsonify([])

    # Get top games among friends by total playtime
    cur.execute("""
        SELECT g.appid, g.name, g.image_url, SUM(ug.playtime_minutes) as total_playtime
        FROM users u
        JOIN user_games ug ON u.id = ug.user_id
        JOIN games g ON ug.game_id = g.id
        WHERE u.steam_id = ANY(%s)
        GROUP BY g.appid, g.name, g.image_url
        ORDER BY total_playtime DESC
        LIMIT 5
    """, (friend_ids,))
    games = [
        {
            "appid": row[0],
            "name": row[1],
            "image_url": row[2],
            "total_playtime": row[3]
        }
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return jsonify(games)

@app.route("/api/users/<steam_id>/friends_cached", methods=["GET"])
@jwt_required()
def get_friends_cached(steam_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE steam_id = %s;", (steam_id,))
    user_row = cur.fetchone()
    if not user_row:
        cur.close()
        conn.close()
        return jsonify({"friends": []})
    user_id = user_row[0]
    cur.execute("""
        SELECT f.friend_steam_id, u.display_name, u.avatar_url, f.friend_since
        FROM friends f
        LEFT JOIN users u ON f.friend_steam_id = u.steam_id
        WHERE f.user_id = %s
        ORDER BY f.friend_since DESC
    """, (user_id,))
    friends = [
        {
            "steam_id": row[0],
            "display_name": row[1],
            "avatar_url": row[2],
        }
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return jsonify({"friends": friends})



@app.route("/api/users/<steam_id>/summary", methods=["GET"])
def get_player_summary(steam_id):
    steam_api_key = os.getenv("STEAM_API_KEY")
    url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    params = {
        "key": steam_api_key,
        "steamids": steam_id
    }
    response = requests.get(url, params=params)
    if response.status_code == 429:
        return jsonify({"error": "Steam is rate limiting us. Please try again later."}), 429
    try:
        data = response.json()
        players = data.get("response", {}).get("players", [])
        if not players:
            return jsonify({"error": "No player found"}), 404
        return jsonify(players[0])
    except Exception as e:
        return jsonify({"error": "Failed to decode JSON", "details": response.text}), 500
    

@app.route("/api/users/<steam_id>/summary_local", methods=["GET"])
@jwt_required()
def get_player_summary_local(steam_id):
    identity = get_jwt_identity()
    if identity != steam_id:
        # Check if identity is a friend of steam_id
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE steam_id = %s;", (steam_id,))
        user_row = cur.fetchone()
        if not user_row:
            cur.close()
            conn.close()
            return jsonify({"error": "User not found"}), 404
        user_id = user_row[0]
        cur.execute("SELECT 1 FROM friends WHERE user_id = %s AND friend_steam_id = %s;", (user_id, identity))
        is_friend = cur.fetchone()
        cur.close()
        conn.close()
        if not is_friend:
            return jsonify({"error": "YOURE NOT FRIENDS Forbidden"}), 403
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT display_name, avatar_url FROM users WHERE steam_id = %s;",
        (steam_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "display_name": row[0],
        "avatar_url": row[1],
        "steam_id": steam_id
    })

@app.route("/api/compare/<steam_id>/<friend_steam_id>", methods=["GET"])
def compare_games(steam_id, friend_steam_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT g.appid, g.name, g.image_url,
               ug1.playtime_minutes AS user_playtime,
               ug2.playtime_minutes AS friend_playtime
        FROM users u1
        JOIN user_games ug1 ON u1.id = ug1.user_id
        JOIN games g ON ug1.game_id = g.id
        JOIN users u2 ON u2.steam_id = %s
        JOIN user_games ug2 ON u2.id = ug2.user_id AND ug1.game_id = ug2.game_id
        WHERE u1.steam_id = %s
        ORDER BY (ug1.playtime_minutes + ug2.playtime_minutes) DESC
    """, (friend_steam_id, steam_id))
    games = [
        {
            "appid": row[0],
            "name": row[1],
            "image_url": row[2],
            "user_playtime": row[3],
            "friend_playtime": row[4]
        }
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return jsonify(games)


@app.route("/api/groups/<int:group_id>/picture", methods=["POST"])
@jwt_required()
def update_group_picture(group_id):
    data = request.get_json()
    picture_url = data.get("picture_url")
    if not picture_url:
        return jsonify({"error": "picture_url required"}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE groups SET picture_url = %s WHERE id = %s;", (picture_url, group_id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"group_id": group_id, "picture_url": picture_url}), 200

@app.route("/api/groups/<int:group_id>/members/<steam_id>", methods=["DELETE"])
@jwt_required()
def remove_group_member(group_id, steam_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE steam_id = %s;", (steam_id,))
    user = cur.fetchone()
    if user:
        cur.execute("DELETE FROM group_members WHERE group_id = %s AND user_id = %s;", (group_id, user[0]))
        conn.commit()
    cur.close()
    conn.close()
    return jsonify({"removed": steam_id}), 200


@app.route("/api/groups/<int:group_id>", methods=["GET"])
@jwt_required()
def get_group(group_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, owner_id, picture_url FROM groups WHERE id = %s;", (group_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return jsonify({"error": "Group not found"}), 404
    return jsonify({
        "group_id": row[0],
        "name": row[1],
        "owner_id": row[2],
        "picture_url": row[3]
    })

@app.route("/api/sync_group_games", methods=["POST"])
@jwt_required()
@limiter.limit("10 per day")
def sync_group_games():
    data = request.get_json()
    steam_ids = data.get("steam_ids")
    if not steam_ids or not isinstance(steam_ids, list):
        return jsonify({"error": "steam_ids (list) required"}), 400

    synced = []
    for friend_steam_id in steam_ids:
        # Ensure friend is in users table
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE steam_id = %s;", (friend_steam_id,))
        if not cur.fetchone():
            cur.execute("INSERT INTO users (steam_id, display_name) VALUES (%s, %s) RETURNING id;", (friend_steam_id, None))
            conn.commit()
        cur.close()
        conn.close()
        # Call the fetch logic directly
        success, message = fetch_and_store_games_for_steam_id(friend_steam_id)
        synced.append({"steam_id": friend_steam_id, "success": success, "message": message})

    return jsonify({"synced": synced})


def fetch_and_store_games_for_steam_id(steam_id):
    steam_api_key = os.getenv("STEAM_API_KEY")
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {
        "key": steam_api_key,
        "steamid": steam_id,
        "include_appinfo": True,
        "include_played_free_games": True,
        "format": "json"
    }
    response = requests.get(url, params=params)
    try:
        data = response.json()
    except Exception as e:
        print(f"Failed to decode JSON for steam_id={steam_id}: {e}")
        print(f"Response text: {response.text}")
        return False, f"Steam API error or invalid response for {steam_id}"
    games = data.get("response", {}).get("games", [])

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE steam_id = %s;", (steam_id,))
    user_row = cur.fetchone()
    if not user_row:
        cur.close()
        conn.close()
        return False, "User not found"
    user_id = user_row[0]

    for game in games:
        cur.execute(
            "INSERT INTO games (appid, name, image_url) VALUES (%s, %s, %s) ON CONFLICT (appid) DO NOTHING;",
            (game["appid"], game["name"], f"http://media.steampowered.com/steamcommunity/public/images/apps/{game['appid']}/{game.get('img_icon_url', '')}.jpg")
        )
        cur.execute("SELECT id FROM games WHERE appid = %s;", (game["appid"],))
        game_id = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO user_games (user_id, game_id, playtime_minutes) VALUES (%s, %s, %s) ON CONFLICT (user_id, game_id) DO UPDATE SET playtime_minutes = EXCLUDED.playtime_minutes;",
            (user_id, game_id, game.get("playtime_forever", 0))
        )
    conn.commit()
    cur.close()
    conn.close()
    return True, f"Fetched and stored {len(games)} games for user {steam_id}."


#***** group logic *****
@app.route("/api/groups", methods=["POST"])
@jwt_required()
#CREATE GROUP
def create_group():
    data = request.get_json()
    name = data.get("name")
    owner_steam_id = data.get("owner_steam_id")
    if not name or not owner_steam_id:
        return jsonify({"error": "name and owner_steam_id required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE steam_id = %s;", (owner_steam_id,))
    owner = cur.fetchone()
    if not owner:
        cur.close()
        conn.close()
        return jsonify({"error": "Owner not found"}), 404
    owner_id = owner[0]
    cur.execute("INSERT INTO groups (name, owner_id) VALUES (%s, %s) RETURNING id;", (name, owner_id))
    group_id = cur.fetchone()[0]
    # Add the owner as a member
    cur.execute("INSERT INTO group_members (group_id, user_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;", (group_id, owner_id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"group_id": group_id, "name": name}), 201



@app.route("/api/groups/<int:group_id>/members", methods=["POST"])
@jwt_required()
# ADD GROUP MEMBERS
def add_group_members(group_id):
    data = request.get_json()
    steam_ids = data.get("steam_ids")
    if not steam_ids or not isinstance(steam_ids, list):
        return jsonify({"error": "steam_ids (list) required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    for steam_id in steam_ids:
        cur.execute("SELECT id FROM users WHERE steam_id = %s;", (steam_id,))
        user = cur.fetchone()
        if user:
            cur.execute("INSERT INTO group_members (group_id, user_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;", (group_id, user[0]))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"group_id": group_id, "added": steam_ids}), 200

@app.route("/api/groups/<int:group_id>/shared_games", methods=["GET"])
@jwt_required()
def get_group_shared_games(group_id):
    conn = get_db_connection()
    cur = conn.cursor()
    # Get all user_ids and steam_ids in the group
    cur.execute("SELECT u.id, u.steam_id FROM group_members gm JOIN users u ON gm.user_id = u.id WHERE gm.group_id = %s;", (group_id,))
    user_rows = cur.fetchall()
    user_ids = [row[0] for row in user_rows]
    steam_ids = [row[1] for row in user_rows]
    if not user_ids:
        cur.close()
        conn.close()
        return jsonify({"error": "No members in group"}), 404

    # Find games owned by all group members and get playtime per member
    sql = """
        SELECT g.appid, g.name, g.image_url,
               SUM(ug.playtime_minutes) as total_playtime,
               json_object_agg(u.steam_id, ug.playtime_minutes) as playtimes
        FROM user_games ug
        JOIN games g ON ug.game_id = g.id
        JOIN users u ON ug.user_id = u.id
        WHERE ug.user_id = ANY(%s)
        GROUP BY g.appid, g.name, g.image_url
        HAVING COUNT(ug.user_id) = %s
        ORDER BY total_playtime DESC
    """
    cur.execute(sql, (user_ids, len(user_ids)))
    games = [
        {
            "appid": row[0],
            "name": row[1],
            "image_url": row[2],
            "total_playtime": row[3],
            "playtimes": row[4]  # {steam_id: playtime_minutes, ...}
        }
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return jsonify(games)



@app.route("/api/users/<steam_id>/games/<int:game_id>/playtime", methods=["GET"])
@jwt_required()
def get_user_playtime_for_game(steam_id, game_id):
    """
    Return the playtime (in minutes) for a specific user and game.
    Requires JWT for the user.
    """
    identity = get_jwt_identity()
    if identity != steam_id:
        return jsonify({"error": "Forbidden"}), 403
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT ug.playtime_minutes, g.name
        FROM user_games ug
        JOIN games g ON ug.game_id = g.id
        JOIN users u ON ug.user_id = u.id
        WHERE u.steam_id = %s AND g.id = %s
    """, (steam_id, game_id))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return jsonify({"playtime_minutes": 0, "game_name": ""})
    return jsonify({"playtime_minutes": row[0], "game_name": row[1]})

@app.route("/api/users/<steam_id>/groups", methods=["GET"])
@jwt_required()
# GET ALL GROUPS USER IS A MEMBER OF
def get_user_groups(steam_id):
    identity = get_jwt_identity()
    if identity != steam_id:
        return jsonify({"error": "Forbidden"}), 403
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE steam_id = %s;", (steam_id,))
    user = cur.fetchone()
    if not user:
        cur.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404
    user_id = user[0]
    cur.execute("""
        SELECT g.id, g.name, g.owner_id, g.picture_url
        FROM groups g
        JOIN group_members gm ON g.id = gm.group_id
        WHERE gm.user_id = %s
        ORDER BY g.name
    """, (user_id,))
    groups = [
        {
            "group_id": row[0],
            "name": row[1],
            "owner_id": row[2],
            "picture_url": row[3]
        }
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return jsonify(groups)

@app.route("/api/users/<steam_id>/groups_owned", methods=["GET"])
@jwt_required()
#GET ALL GROUPS USER OWNS
def get_groups_owned(steam_id):
    identity = get_jwt_identity()
    if identity != steam_id:
        return jsonify({"error": "Forbidden"}), 403
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE steam_id = %s;", (steam_id,))
    user = cur.fetchone()
    if not user:
        cur.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404
    user_id = user[0]
    cur.execute("""
        SELECT id, name, picture_url
        FROM groups
        WHERE owner_id = %s
        ORDER BY name
    """, (user_id,))
    groups = [
        {"group_id": row[0], "name": row[1], "picture_url": row[2]}
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return jsonify(groups)


@app.route("/api/groups/<int:group_id>/members", methods=["GET"])
@jwt_required()
def get_group_members(group_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.id, u.steam_id, u.display_name, u.avatar_url
        FROM group_members gm
        JOIN users u ON gm.user_id = u.id
        WHERE gm.group_id = %s
    """, (group_id,))
    members = [
        {
            "user_id": row[0],
            "steam_id": row[1],
            "display_name": row[2],
            "avatar_url": row[3]
        }
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return jsonify(members)


def update_friends_info(steam_id):
    steam_api_key = os.getenv("STEAM_API_KEY")
    # 1. Get friend list from Steam
    url = "http://api.steampowered.com/ISteamUser/GetFriendList/v1/"
    params = {"key": steam_api_key, "steamid": steam_id, "relationship": "friend"}
    response = requests.get(url, params=params)
    friends = response.json().get("friendslist", {}).get("friends", [])
    friend_ids = [f['steamid'] for f in friends]
    if not friend_ids:
        return

    conn = get_db_connection()
    cur = conn.cursor()

    # Get the user_id for the owner
    cur.execute("SELECT id FROM users WHERE steam_id = %s;", (steam_id,))
    owner_row = cur.fetchone()
    if not owner_row:
        cur.close()
        conn.close()
        return
    owner_id = owner_row[0]

    # Delete old friends for this user
    cur.execute("DELETE FROM friends WHERE user_id = %s;", (owner_id,))

    # Insert or update friend relationships and upsert friend info
    for f in friends:
        # Insert owner -> friend
        cur.execute("""
            INSERT INTO friends (user_id, friend_steam_id, friend_since)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, friend_steam_id) DO UPDATE SET friend_since = EXCLUDED.friend_since
        """, (owner_id, f['steamid'], f.get('friend_since')))

    # 2. Get player summaries in batches of 100 and upsert into users
    for i in range(0, len(friend_ids), 100):
        chunk = friend_ids[i:i+100]
        url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
        params = {"key": steam_api_key, "steamids": ",".join(chunk)}
        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            print(f"Steam API error: {resp.status_code} {resp.text}")
            continue
        try:
            players = resp.json().get("response", {}).get("players", [])
        except Exception as e:
            print(f"Failed to parse JSON: {e}, response: {resp.text}")
            continue
        for player in players:
            cur.execute("""
                INSERT INTO users (steam_id, display_name, avatar_url)
                VALUES (%s, %s, %s)
                ON CONFLICT (steam_id) DO UPDATE SET display_name = EXCLUDED.display_name, avatar_url = EXCLUDED.avatar_url
            """, (player['steamid'], player.get('personaname', ''), player.get('avatarfull', '')))
    conn.commit()
    cur.close()
    conn.close()

@app.route("/api/users/<steam_id>/games/<int:game_id>/friends", methods=["GET"])
@jwt_required()
def friends_who_own_game(steam_id, game_id):
    identity = get_jwt_identity()
    if identity != steam_id:
        return jsonify({"error": "Forbidden"}), 403
    conn = get_db_connection()
    cur = conn.cursor()
    # Get user_id
    cur.execute("SELECT id FROM users WHERE steam_id = %s", (steam_id,))
    user_row = cur.fetchone()
    if not user_row:
        cur.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404
    user_id = user_row[0]
    # Get friends' steam_ids
    cur.execute("SELECT friend_steam_id FROM friends WHERE user_id = %s", (user_id,))
    friend_ids = [row[0] for row in cur.fetchall()]
    if not friend_ids:
        cur.close()
        conn.close()
        return jsonify([])
    # Get friends who own the game, including avatar_url and other info
    cur.execute("""
        SELECT u.display_name, u.steam_id, u.avatar_url, u.account_display_name, ug.playtime_minutes
        FROM users u
        JOIN user_games ug ON u.id = ug.user_id
        WHERE u.steam_id = ANY(%s) AND ug.game_id = %s
        ORDER BY ug.playtime_minutes DESC
    """, (friend_ids, game_id))
    friends = [
        {
            "display_name": row[0],
            "steam_id": row[1],
            "avatar_url": row[2],
            "account_display_name": row[3],
            "playtime_minutes": row[4]
        }
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return jsonify(friends)

# Steam OpenID config
steam_openid_url = 'https://steamcommunity.com/openid/login'
steam_id_re = re.compile(r'https://steamcommunity.com/openid/id/(\d+)$')

def get_user_info(steam_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT display_name, avatar_url, last_steam_update FROM users WHERE steam_id = %s;", (steam_id,))
    row = cur.fetchone()
    now = datetime.datetime.utcnow()
    # If we have user info and it's less than 24 hours old, use it
    if row and row[2] and (now - row[2]).total_seconds() < 86400:
        cur.close()
        conn.close()
        return {"personaname": row[0], "avatarfull": row[1]}
    # Otherwise, fetch from Steam API
    steam_api_key = os.getenv("STEAM_API_KEY")
    options = {
        'key': steam_api_key,
        'steamids': steam_id
    }
    url = 'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
    response = requests.get(url, params=options)
    print("Steam API status:", response.status_code)
    print("Steam API response:", response.text)
    if response.status_code == 429:
        cur.close()
        conn.close()
        raise Exception("Steam is rate limiting us. Please try again later.")
    if response.status_code != 200:
        cur.close()
        conn.close()
        raise Exception(f"Steam API error: {response.status_code} {response.text}")
    data = response.json()
    players = data['response']['players']
    steam_data = players[0] if players else {"personaname": "", "avatarfull": ""}
    # Update DB with new info and timestamp
    cur.execute(
        "UPDATE users SET display_name = %s, avatar_url = %s, last_steam_update = %s WHERE steam_id = %s;",
        (steam_data.get('personaname', ''), steam_data.get('avatarfull', ''), now, steam_id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return steam_data

@app.route("/auth/steam")
def steam_login():
    # Use environment variable for backend URL
    BACKEND_URL = os.getenv("BACKEND_URL")
    params = {
        'openid.ns': "http://specs.openid.net/auth/2.0",
        'openid.identity': "http://specs.openid.net/auth/2.0/identifier_select",
        'openid.claimed_id': "http://specs.openid.net/auth/2.0/identifier_select",
        'openid.mode': 'checkid_setup',
        'openid.return_to': f'{BACKEND_URL}/auth/steam/authorize',
        'openid.realm': BACKEND_URL
    }
    param_string = urllib.parse.urlencode(params)
    auth_url = steam_openid_url + "?" + param_string
    return redirect(auth_url)

@app.route("/auth/steam/authorize")
def steam_authorize():
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

    openid_identity = request.args.get('openid.identity')
    if not openid_identity:
        app.logger.error("Missing openid.identity in callback")
        return jsonify({"error": "Steam response missing identity"}), 400

    match = steam_id_re.match(openid_identity)
    if not match:
        app.logger.error(f"Invalid openid.identity: {openid_identity}")
        return jsonify({"error": "Steam login failed"}), 400

    steam_id = match.group(1)

    try:
        steam_data = get_user_info(steam_id)
        if not steam_data:
            raise ValueError("No data returned from Steam API")
    except Exception as e:
        app.logger.error(f"Failed to get user info: {str(e)}")
        return jsonify({"error": "Steam user info failed"}), 500

    display_name = steam_data.get('personaname', '')
    avatar_url = steam_data.get('avatarfull', '')

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE steam_id = %s;", (steam_id,))
        user = cur.fetchone()
        if user:
            cur.execute(
                "UPDATE users SET display_name = %s, avatar_url = %s WHERE steam_id = %s;",
                (display_name, avatar_url, steam_id)
            )
            user_id = user[0]
        else:
            cur.execute(
                "INSERT INTO users (steam_id, display_name, avatar_url) VALUES (%s, %s, %s) RETURNING id;",
                (steam_id, display_name, avatar_url)
            )
            user_id = cur.fetchone()[0]
        conn.commit()
    except Exception as e:
        app.logger.error(f"DB error: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    token = create_access_token(identity=steam_id)
    return redirect(f"{FRONTEND_URL}/steam-auth-success?token={token}&steam_id={steam_id}")

@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(500)
def handle_error(e):
    code = getattr(e, 'code', 500)
    return jsonify({"error": str(e)}), code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)

@app.route("/api/users/<steam_id>/sync_friends", methods=["POST"])
@jwt_required()
@limiter.limit("10 per day")
def sync_friends(steam_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE steam_id = %s;", (steam_id,))
    user_row = cur.fetchone()
    if not user_row:
        cur.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404
    user_id = user_row[0]
    cur.close()
    conn.close()
    update_friends_info(steam_id)
    return jsonify({"message": "Friends synced successfully."}), 200

def get_user_from_db(steam_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE steam_id = %s;", (steam_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def create_user_in_db(steam_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (steam_id, created_at) VALUES (%s, %s) ON CONFLICT DO NOTHING;", (steam_id, datetime.datetime.utcnow()))
    conn.commit()
    cur.close()
    conn.close()

def update_games_info(steam_id):
    STEAM_API_KEY = os.getenv("STEAM_API_KEY")
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&steamid={steam_id}&format=json&include_appinfo=1"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch games from Steam API")
    games_data = response.json().get("response", {}).get("games", [])

    conn = get_db_connection()
    cur = conn.cursor()
    # Get user_id
    cur.execute("SELECT id FROM users WHERE steam_id = %s;", (steam_id,))
    print("Steam API status:", response.status_code)

    user_row = cur.fetchone()
    if not user_row:
        cur.close()
        conn.close()
        raise Exception("User not found")
    user_id = user_row[0]

    # Delete user's old games from user_games
    cur.execute("DELETE FROM user_games WHERE user_id = %s;", (user_id,))

    for game in games_data:
        # Insert game metadata if not exists
        cur.execute(
            "INSERT INTO games (appid, name) VALUES (%s, %s) ON CONFLICT (appid) DO NOTHING;",
            (game["appid"], game["name"])
        )
        # Get game id
        cur.execute("SELECT id FROM games WHERE appid = %s;", (game["appid"],))
        game_row = cur.fetchone()
        if not game_row:
            continue
        game_id = game_row[0]
        # Insert user-game link
        cur.execute(
            "INSERT INTO user_games (user_id, game_id, playtime_minutes) VALUES (%s, %s, %s) "
            "ON CONFLICT (user_id, game_id) DO UPDATE SET playtime_minutes = EXCLUDED.playtime_minutes;",
            (user_id, game_id, game.get("playtime_forever", 0))
        )
    conn.commit()
    cur.close()
    conn.close()
    return True, f"Fetched and stored {len(games_data)} games for user {steam_id}."