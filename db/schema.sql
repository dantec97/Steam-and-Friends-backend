CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    steam_id VARCHAR(32) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    avatar_url TEXT,
    password_hash TEXT,
    account_display_name VARCHAR(100),
    last_steam_update TIMESTAMP
);
