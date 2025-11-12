import enum



PUBLIC_ROUTER_PREFIX = "/api/card/v1"

class PublicRoutes(str, enum.Enum):
    HEALTH_CHECK = "/health-check"


PRIVATE_ROUTER_PREFIX = "/api/card/v1/private"

class PrivateRoutes(str, enum.Enum):
    CARDS = "/cards"
    CARD = "/cards/{card_id}"
    TRANSACTIONS = "/transactions/{card_id}"
    TRANSACTION = "/transactions/{card_id}/{transaction_id}"
    NEW_CARD = "/new-card"
    CARD_RECHARGE = "/recharge/{card_id}"
    DISMISS_CARD = "/dismiss/{card_id}"
    PAYMENT = "/payment/{card_id}"


ADMIN_ROUTER_PREFIX = "/api/card/v1/admin"

class AdminRoutes(str, enum.Enum):
    CARDS = "/cards"
    CARD = "/card/{user_id}"
    CARD_DETAILS = "/cards/{card_id}"
    CARD_TRANSACTIONS = "/transactions/{card_id}"
    TRANSACTION_DETAILS = "/transactions/{card_id}/{transaction_id}"
    BLOCK_CARD = "/block/{card_id}"
    UNBLOCK_CARD = "/unblock/{card_id}"
