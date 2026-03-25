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

    async def close(self):
        await self._session.close()

    async def open_pairing(self):
        """Démarre le pairing"""
        async with self._session.post(f"{self.host}/api/v8/login/authorize/", json={
            "app_id": self.app_id,
            "app_name": "Home Assistant Freebox",
            "device_name": "Home Assistant",
            "app_version": "1.0"
        }) as resp:
            return await resp.json()

    async def get_pairing_status(self, track_id):
        """Récupère le statut du pairing"""
        async with self._session.get(f"{self.host}/api/v8/login/authorize/{track_id}") as resp:
            return await resp.json()

    async def wait_for_app_token(self, track_id, timeout=120):
        """
        Attend que la Freebox retourne le app_token
        Compatible Freebox Ultra (token retardé)
        """
        elapsed = 0

        while elapsed < timeout:
            status_json = await self.get_pairing_status(track_id)
            result = status_json.get("result", {})

            status = result.get("status")

            if status == "granted":
                # ⚠️ Sur Freebox Ultra le token arrive APRES le granted
                token = result.get("app_token")
                if token:
                    self.app_token = token
                    return token

            elif status == "denied":
                raise Exception("access_denied")

            await asyncio.sleep(2)
            elapsed += 2

        raise Exception("timeout")

    async def login(self):
        """Login avec app_token"""
        if not self.app_token:
            raise Exception("missing_app_token")

        # 1. récupérer challenge
        async with self._session.get(f"{self.host}/api/v8/login/") as resp:
            challenge = (await resp.json())["result"]["challenge"]

        # 2. générer password
        password = hashlib.sha1(
            (challenge + self.app_token).encode()
        ).hexdigest()

        # 3. ouvrir session
        async with self._session.post(f"{self.host}/api/v8/login/session/", json={
            "app_id": self.app_id,
            "password": password
        }) as resp:
            data = await resp.json()
            self.session_token = data["result"]["session_token"]

    async def request(self, method, path, data=None):
        """Requête authentifiée"""
        headers = {"X-Fbx-App-Auth": self.session_token}

        async with self._session.request(
            method,
            f"{self.host}{path}",
            json=data,
            headers=headers
        ) as resp:
            return await resp.json()