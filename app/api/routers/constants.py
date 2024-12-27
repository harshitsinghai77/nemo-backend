import os

# GOOGLE OAUTH
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

# JWT TOKEN Expiry
JWT_ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_DAYS", 30))

# COOKIE
COOKIE_AUTHORIZATION_NAME: str = os.getenv("COOKIE_AUTHORIZATION_NAME", "Authorization")
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", "https://nemo-app.netlify.app/")

# Nemo Backend
NEMO_BACKEND_URL = "https://nemo-1-z3661706.deta.app"
