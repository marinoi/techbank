import os
import httpx
import aiofiles

from ..misc.singleton import SingletonMeta


class KeysLoader(metaclass=SingletonMeta):
    def __init__(self, public_key_endpoint: str = None):
        self._private_key = None
        self._public_key = None
        self._public_key_endpoint = public_key_endpoint
        self._keys_dir = "./app/v1/keys" if not public_key_endpoint else None

    async def load_keys(self):
        if self._public_key_endpoint:
            async with httpx.AsyncClient() as client:
                data = await client.get(self._public_key_endpoint)
                self._public_key = data.text

        else:
            async with aiofiles.open(os.path.join(self._keys_dir, "private.pem"), "r") as private_key_file:
                self._private_key = await private_key_file.read()

            async with aiofiles.open(os.path.join(self._keys_dir, "public.pem"), "r") as public_key_file:
                self._public_key = await public_key_file.read()

    @property
    def private_key(self) -> str:
        if self._public_key_endpoint:
            raise AttributeError("private_key getter is defined only for the auth service")

        return self._private_key

    @property
    def public_key(self) -> str:
        return self._public_key
