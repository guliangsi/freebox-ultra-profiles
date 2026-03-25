import aiohttp
import asyncio
import hashlib


class FreeboxAPI:
    def __init__(self, host, app_id="homeassistant.freebox"):
        self.host = host.rstrip("/")
        self.app_id = app_id
        self.session = aiohttp.ClientSession()

    async def open_pairing(self):
        async with self.session.post(f"{self.host}/api/v8/login/authorize/", json={
            "app_id": self.app_id,
            "app_name": "Home Assistant",
            "device_name": "HA",
            "app_version": "1.0"
        }) as resp:
            return await resp.json()

    async def get_pairing_status(self, track_id):
        async with self.session.get(f"{self.host}/api/v8/login/authorize/{track_id}") as resp:
            return await resp.json()

    async def get_app_token_from_list(self):
        """🔥 fallback Freebox Ultra"""
        async with self.session.get(f"{self.host}/api/v8/login/") as resp:
            data = await resp.json()

        for app in data.get("result", {}).get("apps", []):
            if app.get("app_id") == self.app_id:
                return app.get("app_token")

        return None

    async def login(self, app_token):
        async with self.session.get(f"{self.host}/api/v8/login/") as resp:
            challenge = (await resp.json())["result"]["challenge"]

        password = hashlib.sha1(
            (challenge + app_token).encode()
        ).hexdigest()

        async with self.session.post(f"{self.host}/api/v8/login/session/", json={
            "app_id": self.app_id,
            "password": password
        }) as resp:
            return await resp.json()