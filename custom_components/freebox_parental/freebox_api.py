import aiohttp
import asyncio
import hashlib
import time

class FreeboxAPI:
    def __init__(self, host):
        self._host = host
        self._base = f"http://{host}/api/v4"
        self._session_token = None
        self._app_id = "hass.freebox_parental"
        self._app_name = "Home Assistant Parental"
        self._app_version = "1.0"

    async def _request(self, method, path, data=None):
        headers = {}
        if self._session_token:
            headers["X-Fbx-App-Auth"] = self._session_token

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                f"{self._base}{path}",
                json=data,
                headers=headers
            ) as resp:
                return await resp.json()

    async def login(self):
        # étape 1: challenge
        challenge = await self._request("GET", "/login/")
        challenge = challenge["result"]["challenge"]

        password = ""  # ⚠️ pas utilisé (token flow)

        h = hashlib.sha1()
        h.update((challenge + password).encode())
        password_hash = h.hexdigest()

        res = await self._request("POST", "/login/session/", {
            "app_id": self._app_id,
            "password": password_hash
        })

        self._session_token = res["result"]["session_token"]

    async def get_profiles(self):
        return await self._request("GET", "/parental/filter/")

    async def pause_profile(self, profile_id):
        return await self._request("PUT", f"/parental/filter/{profile_id}", {
            "forced": True,
            "forced_mode": "denied"
        })

    async def resume_profile(self, profile_id):
        return await self._request("PUT", f"/parental/filter/{profile_id}", {
            "forced": False
        })