import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv
import requests


load_dotenv()

app = Flask(__name__)
CORS(app)

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

if __name__ == "__main__":
    app.run(debug=True)


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
        SELECT g.appid, g.name, g.image_url, ug.playtime_minutes
        FROM users u
        JOIN user_games ug ON u.id = ug.user_id
        JOIN games g ON ug.game_id = g.id
        WHERE u.steam_id = %s
        ORDER BY ug.playtime_minutes DESC
    """, (steam_id,))
    games = [
        {"appid": row[0], "name": row[1], "image_url": row[2], "playtime_minutes": row[3]}
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return jsonify(games)

@app.route("/api/users/<steam_id>/friends", methods=["GET"])
def get_friends(steam_id):
    steam_api_key = os.getenv("STEAM_API_KEY")
    url = "http://api.steampowered.com/ISteamUser/GetFriendList/v1/"
    params = {
        "key": steam_api_key,
        "steamid": steam_id,
        "relationship": "friend"
    }
    response = requests.get(url, params=params)
    return jsonify(response.json())

@app.route("/api/users/<steam_id>/summary", methods=["GET"])
def get_player_summary(steam_id):
    steam_api_key = os.getenv("STEAM_API_KEY")
    url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    params = {
        "key": steam_api_key,
        "steamids": steam_id
    }
    response = requests.get(url, params=params)
    try:
        data = response.json()
        # The response is a dict with a "response" key containing "players" list
        players = data.get("response", {}).get("players", [])
        if not players:
            return jsonify({"error": "No player found"}), 404
        return jsonify(players[0])  # Return the first (and only) player summary
    except Exception as e:
        return jsonify({"error": "Failed to decode JSON", "details": response.text}), 500
    

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

@app.route("/api/users/<steam_id>/groups", methods=["GET"])
#GET ALL GROUPS
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
        SELECT g.id, g.name, g.owner_id
        FROM groups g
        JOIN group_members gm ON g.id = gm.group_id
        WHERE gm.user_id = %s
        ORDER BY g.name
    """, (user_id,))
    groups = [
        {"group_id": row[0], "name": row[1], "owner_id": row[2]}
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return jsonify(groups)

@app.route("/api/groups/<int:group_id>/members", methods=["GET"])
def get_group_members(group_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.steam_id, u.display_name
        FROM group_members gm
        JOIN users u ON gm.user_id = u.id
        WHERE gm.group_id = %s
    """, (group_id,))
    members = [{"steam_id": row[0], "display_name": row[1]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(members)




if __name__ == "__main__":
    app.run(debug=True, threaded=True)
    # might need: flask run --with-threads


    # 76561198079997160 weezbud