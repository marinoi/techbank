import enum

class Role(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
