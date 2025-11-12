import enum


PUBLIC_ROUTER_PREFIX = "/api/notification/v1"

class PublicRoutes(str, enum.Enum):
    HEALTH_CHECK = "/health-check"

PRIVATE_ROUTER_PREFIX = "/api/notification/v1/private"

class PrivateRoutes(str, enum.Enum):
    NOTIFICATIONS = "/notifications"
    NOTIFICATION = "/notifications/{notification_id}"

ADMIN_ROUTER_PREFIX = "/api/notification/v1/admin"

class AdminRoutes(str, enum.Enum):
    NOTIFICATIONS = "/notifications/{user_id}"
    NOTIFICATION = "/notifications/{user_id}/{notification_id}"
