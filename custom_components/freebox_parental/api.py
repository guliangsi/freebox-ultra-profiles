import aiohttp
import asyncio
import hashlib


class FreeboxAPI:
    def __init__(self, host, app_id="homeassistant.freebox"):
        self.host = host.rstrip("/")
        self.app_id = app_id
        self.app_token = None
        self.session_token = None
        self._session = aiohttp.ClientSession()

    async def open_pairing(self):
        async with self._session.post(f"{self.host}/api/v8/login/authorize/", json={
            "app_id": self.app_id,
            "app_name": "Home Assistant",
            "device_name": "HA",
            "app_version": "1.0"
        }) as resp:
            return await resp.json()

    async def get_pairing_status(self, track_id):
        async with self._session.get(f"{self.host}/api/v8/login/authorize/{track_id}") as resp:
            return await resp.json()

    async def wait_for_app_token(self, track_id, timeout=10):
        """Check rapide sans bloquer HA"""
        for _ in range(timeout):
            data = await self.get_pairing_status(track_id)
            result = data.get("result", {})

            if result.get("status") == "granted":
                token = result.get("app_token")
                if token:
                    return token

            await asyncio.sleep(1)

        raise Exception("not_ready")