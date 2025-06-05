import os
from flask import Flask, jsonify, request, redirect, g, url_for
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



load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key")  # Use a strong secret in production!
jwt = JWTManager(app)

def get_db_connection():
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
        return jsonify({"error": "account_display_name and password are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash, steam_id FROM users WHERE account_display_name = %s;", (account_display_name,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if not user or not check_password_hash(user[1], password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity={"user_id": user[0], "steam_id": user[2], "account_display_name": account_display_name})
    return jsonify(access_token=access_token)

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

# if __name__ == "__main__":
#     app.run(debug=True)


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
def fetch_and_store_games(steam_id):
    identity = get_jwt_identity()
    if identity != steam_id:
        return jsonify({"error": "Forbidden"}), 403
    success, message = fetch_and_store_games_for_steam_id(steam_id)
    if not success:
        return jsonify({"error": message}), 404
    return jsonify({"message": message})

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
def get_user_games(steam_id):
    identity = get_jwt_identity()
    if identity != steam_id:
        return jsonify({"error": "Forbidden"}), 403
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT g.id, g.appid, g.name, g.image_url, ug.playtime_minutes
        FROM users u
        JOIN user_games ug ON u.id = ug.user_id
        JOIN games g ON ug.game_id = g.id
        WHERE u.steam_id = %s
        ORDER BY ug.playtime_minutes DESC
    """, (steam_id,))
    games = [
        {
            "id": row[0],           # <-- Add this line
            "appid": row[1],
            "name": row[2],
            "image_url": row[3],
            "playtime_minutes": row[4]
        }
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return jsonify(games)

@app.route("/api/users/<steam_id>/friends", methods=["GET"])
@jwt_required()
def get_friends(steam_id):
    identity = get_jwt_identity()
    if identity != steam_id:
        return jsonify({"error": "Forbidden"}), 403
    # Update friends info in your DB
    update_friends_info(steam_id)

    # Now get the friends from your DB (with names/avatars)
    conn = get_db_connection()
    cur = conn.cursor()
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
            "friend_since": row[3]
        }
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return jsonify(friends)


@app.route("/api/users/<steam_id>/friends_cached", methods=["GET"])
@jwt_required()
def get_friends_cached(steam_id):
    identity = get_jwt_identity()
    if identity != steam_id:
        return jsonify({"error": "Forbidden"}), 403
    """Return friends from the local DB only, no Steam API call."""
    conn = get_db_connection()
    cur = conn.cursor()
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
            "friend_since": row[3]
        }
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return jsonify(friends)



# @app.route("/api/users/<steam_id>/friends_list", methods=["GET"])
# # this returns the friends list from the Steam API
# def get_friends_list(steam_id):
#     steam_api_key = os.getenv("STEAM_API_KEY")
#     url = "http://api.steampowered.com/ISteamUser/GetFriendList/v1/"
#     params = {
#         "key": steam_api_key,
#         "steamid": steam_id,
#         "relationship": "friend"
#     }
#     response = requests.get(url, params=params)
#     return jsonify(response.json())

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
        return jsonify({"error": "Forbidden"}), 403
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
    data = response.json()
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

# @app.route("/api/users/<steam_id>/groups", methods=["GET"])
# #GET ALL GROUPS USER IS A MEMBER OF
# def get_user_groups(steam_id):
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT id FROM users WHERE steam_id = %s;", (steam_id,))
#     user = cur.fetchone()
#     if not user:
#         cur.close()
#         conn.close()
#         return jsonify({"error": "User not found"}), 404
#     user_id = user[0]
#     cur.execute("""
#         SELECT g.id, g.name, g.owner_id
#         FROM groups g
#         JOIN group_members gm ON g.id = gm.group_id
#         WHERE gm.user_id = %s
#         ORDER BY g.name
#     """, (user_id,))
#     groups = [
#         {"group_id": row[0], "name": row[1], "owner_id": row[2]}
#         for row in cur.fetchall()
#     ]
#     cur.close()
#     conn.close()
#     return jsonify(groups)

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

# @app.route("/api/groups/<int:group_id>/members", methods=["GET"])
# def get_group_members(group_id):
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("""
#         SELECT u.steam_id, u.display_name
#         FROM group_members gm
#         JOIN users u ON gm.user_id = u.id
#         WHERE gm.group_id = %s
#     """, (group_id,))
#     members = [{"steam_id": row[0], "display_name": row[1]} for row in cur.fetchall()]
#     cur.close()
#     conn.close()
#     return jsonify(members)

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
    # 1. Get friend list
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

    # Insert or update friend relationships
    for f in friends:
        cur.execute("""
            INSERT INTO friends (user_id, friend_steam_id, friend_since)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, friend_steam_id) DO UPDATE SET friend_since = EXCLUDED.friend_since
        """, (owner_id, f['steamid'], f.get('friend_since')))

    # 2. Get player summaries in batches of 100
    for i in range(0, len(friend_ids), 100):
        chunk = friend_ids[i:i+100]
        url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
        params = {"key": steam_api_key, "steamids": ",".join(chunk)}
        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            print(f"Steam API error: {resp.status_code} {resp.text}")
            continue  # or handle error as needed
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
            """, (player['steamid'], player['personaname'], player['avatarfull']))
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
    print("Friends who own game:", friends)
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
    if response.status_code == 429:
        cur.close()
        conn.close()
        raise Exception("Steam is rate limiting us. Please try again later.")
    response.raise_for_status()
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
    params = {
        'openid.ns': "http://specs.openid.net/auth/2.0",
        'openid.identity': "http://specs.openid.net/auth/2.0/identifier_select",
        'openid.claimed_id': "http://specs.openid.net/auth/2.0/identifier_select",
        'openid.mode': 'checkid_setup',
        'openid.return_to': 'http://127.0.0.1:5000/auth/steam/authorize',
        'openid.realm': 'http://127.0.0.1:5000'
    }
    param_string = urllib.parse.urlencode(params)
    auth_url = steam_openid_url + "?" + param_string
    return redirect(auth_url)

@app.route("/auth/steam/authorize")
def steam_authorize():
    openid_identity = request.args.get('openid.identity')
    match = steam_id_re.match(openid_identity)
    if not match:
        return jsonify({"error": "Steam login failed"}), 400
    steam_id = match.group(1)
    steam_data = get_user_info(steam_id)
    display_name = steam_data.get('personaname', '')
    avatar_url = steam_data.get('avatarfull', '')

    # Upsert user in your DB
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
    cur.close()
    conn.close()

    # Create JWT
    access_token = create_access_token(
    identity=steam_id,
    additional_claims={
        "user_id": user_id,
        "display_name": display_name,
        "avatar_url": avatar_url
    }
)

    # Redirect to frontend with all info as query params
    return redirect(
        f"http://localhost:5173/steam-auth-success"
        f"?steamid={steam_id}"
        f"&display_name={display_name}"
        f"&avatar_url={avatar_url}"
        f"&token={access_token}"
    )



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
# if __name__ == "__main__":
#     app.run(debug=True, threaded=True)
    # might need: flask run --with-threads


    # 76561198079997160 weezbud

    #direct steam sign in link: http://127.0.0.1:5000/auth/steam
    #steam success: http://localhost:5173/steam-auth-success?steamid=76561198846382485&display_name=dantec97&avatar_url=https://avatars.steamstatic.com/3f47c3634c822270cbccf23f4cb4fcf2272e23d1_full.jpg