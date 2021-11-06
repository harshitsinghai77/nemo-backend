import os

# GOOGLE OAUTH
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

# JWT
JWT_ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_DAYS", 30))

# COOKIE
COOKIE_AUTHORIZATION_NAME: str = os.getenv("COOKIE_AUTHORIZATION_NAME", "Authorization")
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", "https://nemo-app.netlify.app/")

# SPOTIFY
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_USER_URL = "https://api.spotify.com/v1/me"
GRANT_TYPE = "authorization_code"
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
