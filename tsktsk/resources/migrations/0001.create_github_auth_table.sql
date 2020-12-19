CREATE TABLE IF NOT EXISTS github_auth(
    discord_id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    token TEXT NOT NULL
);
