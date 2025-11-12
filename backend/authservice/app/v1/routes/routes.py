import enum


PUBLIC_ROUTER_PREFIX = "/api/auth/v1"

class PublicRoutes(str, enum.Enum):
    SIGNUP = "/signup"
    LOGIN = "/login"
    PUBLIC_KEY = "/public-key"
    REFRESH_TOKEN = "/refresh-token"
    HEALTH_CHECK = "/health-check"


PRIVATE_ROUTER_PREFIX = "/api/auth/v1/private"

class PrivateRoutes(str, enum.Enum):
    LOGOUT = "/logout"
    ME = "/me"


ADMIN_ROUTER_PREFIX = "/api/auth/v1/admin"

class AdminRoutes(str, enum.Enum):
    USERS = "/users"
    USER = "/users/{user_id}"
    NEW_USER = "/user/new"
    DELETE_USER = "/users/delete/{user_id}"
    BAN_USER = "/users/ban/{user_id}"
    UPDATE_USER = "/users/update/{user_id}"
