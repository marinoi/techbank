import enum



PUBLIC_ROUTER_PREFIX = "/api/wallet/v1"

class PublicRoutes(str, enum.Enum):
    HEALTH_CHECK = "/health-check"


PRIVATE_ROUTER_PREFIX = "/api/wallet/v1/private"

class PrivateRoutes(str, enum.Enum):
    WALLET = "/wallet"
    TRANSACTIONS = "/transactions"
    TRANSACTION = "/transactions/{transaction_id}"
    DEPOSIT = "/deposit"
    PAYMENT = "/payment"

ADMIN_ROUTER_PREFIX = "/api/wallet/v1/admin"

class AdminRoutes(str, enum.Enum):
    WALLETS = "/wallets"
    WALLET = "/wallet/{user_id}"
    WALLET_DETAILS = "/wallets/{wallet_id}"
    WALLET_TRANSACTIONS = "/transactions/{wallet_id}"
    TRANSACTION_DETAILS = "/transactions/{wallet_id}/{transaction_id}"
    BLOCK_WALLET = "/block/{wallet_id}"
    UNBLOCK_WALLET = "/unblock/{wallet_id}"
