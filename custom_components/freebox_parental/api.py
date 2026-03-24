import aiohttp
import hashlib

class FreeboxAPI:
    def __init__(self, host, app_id="homeassistant.freebox", app_token=None):
        self.host = host
        self.app_id = app_id
        self.app_token = app_token
        self.session_token = None
        self._session = aiohttp.ClientSession()

    async def get_challenge(self):
        async with self._session.get(f"{self.host}/api/v8/login/") as resp:
            return (await resp.json())["result"]["challenge"]

    async def open_pairing(self):
        async with self._session.post(
            f"{self.host}/api/v8/login/authorize/",
            json={
                "app_id": self.app_id,
                "app_name": "Home Assistant Freebox",
                "device_name": "HA",
                "app_version": "1.0",
            },
        ) as resp:
            return await resp.json()

    async def get_pairing_status(self, track_id):
        async with self._session.get(
            f"{self.host}/api/v8/login/authorize/{track_id}"
        ) as resp:
            return await resp.json()

    async def login(self):
        challenge = await self.get_challenge()

        password = hashlib.sha1((challenge + self.app_token).encode()).hexdigest()

        async with self._session.post(
            f"{self.host}/api/v8/login/session/",
            json={
                "app_id": self.app_id,
                "password": password,
            },
        ) as resp:
            data = await resp.json()

            if not data.get("success"):
                raise Exception(data)

            self.session_token = data["result"]["session_token"]

    async def request(self, method, path, data=None):
        headers = {"X-Fbx-App-Auth": self.session_token}

        async with self._session.request(
            method,
            f"{self.host}/api/v8{path}",
            headers=headers,
            json=data,
        ) as resp:
            result = await resp.json()

            if not result.get("success"):
                raise Exception(result)

            return result