from passlib.context import CryptContext

from .config import HasherConfig
from ..common.misc.singleton import SingletonMeta


class PasswordHasher(CryptContext, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__(schemes=HasherConfig.SCHEMES)
