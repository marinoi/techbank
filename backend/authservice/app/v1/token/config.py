import enum


class JWTConfig:
    JWT_MAX_AUTO_REFRESH_ALLOWED = 4
    JWT_REFRESH_BUFFER_TIME = 60
    JWT_TOKEN_EXP_TIME = 180


class JWTField(str, enum.Enum):
    SUB = "sub"
    ROLE = "role"
    REFRESH_COUNTER = "refresh_counter"
    IAT = "iat"
    EXP = "exp"
    JTI = "jti"
