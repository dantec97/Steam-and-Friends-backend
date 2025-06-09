CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    steam_id VARCHAR(32) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    avatar_url TEXT,
    password_hash TEXT,
    account_display_name VARCHAR(100),
    last_steam_update TIMESTAMP
);



-- this query saved my life : 
-- INSERT INTO friends (user_id, friend_steam_id, friend_since)
-- SELECT u2.id, u1.steam_id, f.friend_since
-- FROM friends f
-- JOIN users u1 ON f.user_id = u1.id
-- JOIN users u2 ON f.friend_steam_id = u2.steam_id
-- ON CONFLICT (user_id, friend_steam_id) DO NOTHING;