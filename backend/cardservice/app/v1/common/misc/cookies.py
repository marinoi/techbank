import enum


class Cookies(str, enum.Enum):
    JWT_TOKEN = "jwt_token"


COOKIES_CONFIG = {"httponly": True,
                  "secure": False}
