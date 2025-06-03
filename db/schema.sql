CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    steam_id VARCHAR(32) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    avatar_url TEXT,
    password_hash TEXT,
    account_display_name VARCHAR(100)
);

CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    appid INTEGER UNIQUE NOT NULL,
    name VARCHAR(255),
    image_url TEXT
);

CREATE TABLE user_games (
    user_id INTEGER REFERENCES users(id),
    game_id INTEGER REFERENCES games(id),
    playtime_minutes INTEGER,
    PRIMARY KEY (user_id, game_id)
);
CREATE TABLE friends (
    user_id INTEGER REFERENCES users(id),
    friend_steam_id VARCHAR(32),
    friend_since BIGINT,
    PRIMARY KEY (user_id, friend_steam_id)
);

-- Groups table: stores group info
CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    owner_id INTEGER REFERENCES users(id) -- user who created the group
);

-- Group members: links groups to users (many-to-many)
CREATE TABLE group_members (
    group_id INTEGER REFERENCES groups(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    PRIMARY KEY (group_id, user_id)
);