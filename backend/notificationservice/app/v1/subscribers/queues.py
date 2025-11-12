import enum

from faststream.rabbit import RabbitQueue


class NotificationFanoutQueues(enum.Enum):
    NOTIFICATION_USER_CREATED = RabbitQueue("notification-user-created", durable=True)
    NOTIFICATION_USER_DELETED = RabbitQueue("notification-user-deleted", durable=True)
    NOTIFICATION_TOKEN_REVOKED = RabbitQueue("notification-user-revoked", durable=True)
