import enum

class OutBoxEventStatus(str, enum.Enum):
    SENT = "sent"
    PENDING = "pending"
    FAILED = "failed"