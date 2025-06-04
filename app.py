import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv
import requests
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash



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
def fetch_and_store_games(steam_id):
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
def get_user_games(steam_id):
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
def get_friends(steam_id):
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
def get_friends_cached(steam_id):
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
def get_player_summary_local(steam_id):
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
# Endpoint to sync games for a group of friends, avoids numerous API calls by letting the user refine the group they play with. 
# call with:
# POST /api/sync_group_games
# {
#   "steam_ids": ["friend_id1", "friend_id2", ...]
# }
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
#GROUP COMMON GAMES, returns games owned by all members of the group in order of total playtime
def get_group_shared_games(group_id):
    conn = get_db_connection()
    cur = conn.cursor()
    # Get all user_ids in the group
    cur.execute("SELECT user_id FROM group_members WHERE group_id = %s;", (group_id,))
    user_ids = [row[0] for row in cur.fetchall()]
    if not user_ids:
        cur.close()
        conn.close()
        return jsonify({"error": "No members in group"}), 404

    # Find games owned by all group members
    sql = """
        SELECT g.appid, g.name, g.image_url, COUNT(ug.user_id) as owners, SUM(ug.playtime_minutes) as total_playtime
        FROM user_games ug
        JOIN games g ON ug.game_id = g.id
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
            "owners": row[3],
            "total_playtime": row[4]
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
# GET ALL GROUPS USER IS A MEMBER OF
def get_user_groups(steam_id):
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
#GET ALL GROUPS USER OWNS
def get_groups_owned(steam_id):
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
def friends_who_own_game(steam_id, game_id):
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

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
    # might need: flask run --with-threads


    # 76561198079997160 weezbud