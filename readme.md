# 🎮 Steam and Friends – Backend

A robust Flask REST API for syncing, analyzing, and sharing your Steam game library and playtime with friends and groups.

---

## 🚀 Features

- **User Authentication**
  - Secure JWT-based login/signup
  - Steam OpenID login support

- **Game Sync**
  - Sync your Steam games and playtime
  - Fetch and cache game data from the Steam API

- **Friends & Groups**
  - Sync your Steam friends
  - See which friends play which games
  - Create and manage groups, compare shared games

- **Playtime & Comparison**
  - View your total playtime
  - Compare games and playtime with friends
  - See which friends own/play a specific game

- **Rate Limiting**
  - Prevents abuse of Steam API endpoints

---

## 🛠️ Tech Stack

- **Python 3.13**
- **Flask** (REST API)
- **PostgreSQL** (database)
- **psycopg2** (Postgres driver)
- **Flask-JWT-Extended** (JWT authentication)
- **Flask-Limiter** (rate limiting)
- **python-dotenv** (environment variables)
- **requests** (HTTP requests to Steam API)
- **pytest** (testing)

---

## ⚡ Setup

1. **Clone the Repo**
   ```sh
   git clone <your-repo-url>
   cd back_end
   ```

2. **Create and Activate a Virtual Environment**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   - Copy `.env.test` to `.env` and update values as needed for local development:
     ```
     STEAM_API_KEY=your_steam_api_key
     DB_HOST=localhost
     DB_NAME=steam_friends
     DB_USER=your_db_user
     DB_PASSWORD=your_db_password
     DB_PORT=5432
     JWT_SECRET_KEY=your_jwt_secret
     FRONTEND_URL=http://localhost:5173
     ```

5. **Set Up the Database**
   - Create a PostgreSQL database and user.
   - Run your schema SQL to create tables (`users`, `games`, `user_games`, `friends`, `groups`, `group_members`, etc.).
   - Optionally, seed with test data.

6. **Run the App**
   ```sh
   python app.py
   ```
   The API will be available at [http://localhost:5000](http://localhost:5000).

---

## 📚 API Overview

### 🔐 Authentication
- `POST /api/signup` – Register with Steam ID, display name, and password
- `POST /api/login` – Login with display name and password
- `GET /auth/steam` – Steam OpenID login

### 🎮 Games
- `POST /api/users/<steam_id>/fetch_games` – Sync your games from Steam
- `GET /api/users/<steam_id>/games` – Get your games (JWT required)
- `GET /api/users/<steam_id>/games/<game_id>/playtime` – Get your playtime for a game (JWT required)

### 👥 Friends
- `POST /api/users/<steam_id>/sync_friends` – Sync your Steam friends
- `GET /api/users/<steam_id>/friends` – Get your friends (JWT required)
- `GET /api/users/<steam_id>/games/<game_id>/friends` – Friends who own a specific game (JWT required)

### 🏷️ Groups
- `POST /api/groups` – Create a group (JWT required)
- `POST /api/groups/<group_id>/members` – Add members to a group (JWT required)
- `GET /api/groups/<group_id>/members` – Get group members (JWT required)
- `GET /api/groups/<group_id>/shared_games` – Get games shared by all group members (JWT required)

### 📊 Comparison & Stats
- `GET /api/compare/<steam_id>/<friend_steam_id>` – Compare games and playtime with a friend
- `GET /api/users/<steam_id>/total_playtime` – Get your total playtime (JWT required)
- `GET /api/users/<steam_id>/friends_top_games` – Top games among your friends (JWT required)

---

## 🧪 Testing

- Tests are in the `tests/` directory.
- Use a separate test database and `.env.test` for testing.
- Run tests with:
  ```sh
  PYTHONPATH=. pytest -s
  ```

---

## 🚦 Deployment

- **Never use Flask’s built-in server in production.**
- Use a WSGI server like Gunicorn or uWSGI.
- Set all environment variables securely.
- Use HTTPS in production.

---

## 🌐 Frontend

The frontend is a separate project (see its own README).  
It communicates with this backend via REST API.

---

## 👤 Author

Dante Cancellieri  
https://www.linkedin.com/in/dante-cancellieri/

---

## 📄 License

idk pls don't sue me Steam, I love you <3

---

> **Capstone Project – 2025**  
> Built from scratch with Python, Flask, PostgreSQL, and a lot of passion for games and learning!