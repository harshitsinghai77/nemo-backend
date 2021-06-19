from datetime import datetime


def check_google_user(user_dict):
    """A method which return True if all checks are passed."""
    if user_dict["iss"] != "accounts.google.com":
        return False
    if not user_dict["email_verified"]:
        return False
    return True


def create_db_user_from_dict(user_info):
    """Convert google decode token to db dict."""
    return {
        "created_at": datetime.utcnow(),
        "google_id": user_info["sub"],
        "given_name": user_info["given_name"],
        "family_name": user_info["family_name"],
        "email": user_info["email"],
        "profile_pic": user_info["picture"],
        "email_verified": user_info["email_verified"],
    }
