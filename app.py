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
    # Get user id from steam_id
    cur.execute("SELECT id FROM users WHERE steam_id = %s;", (steam_id,))
    user_row = cur.fetchone()
    if not user_row:
        cur.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404
    user_id = user_row[0]

    for game in games:
        # Insert game if not exists
        cur.execute(
            "INSERT INTO games (appid, name, image_url) VALUES (%s, %s, %s) ON CONFLICT (appid) DO NOTHING;",
            (game["appid"], game["name"], f"http://media.steampowered.com/steamcommunity/public/images/apps/{game['appid']}/{game.get('img_icon_url', '')}.jpg")
        )
        # Get game id
        cur.execute("SELECT id FROM games WHERE appid = %s;", (game["appid"],))
        game_id = cur.fetchone()[0]
        # Insert or update user_games
        cur.execute(
            "INSERT INTO user_games (user_id, game_id, playtime_minutes) VALUES (%s, %s, %s) ON CONFLICT (user_id, game_id) DO UPDATE SET playtime_minutes = EXCLUDED.playtime_minutes;",
            (user_id, game_id, game.get("playtime_forever", 0))
        )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": f"Fetched and stored {len(games)} games for user {steam_id}."})

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