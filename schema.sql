CREATE TABLE IF NOT EXISTS users (id STRING PRIMARY KEY, access_token STRING, access_token_expiry INT, refresh_token STRING);
CREATE INDEX IF NOT EXISTS users_id ON users (id);
