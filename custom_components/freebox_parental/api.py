import aiohttp
import hashlib
import asyncio


class FreeboxAPI:
    def __init__(self, host, app_id="homeassistant.freebox", app_name="Home Assistant Freebox"):
        self.host = host.rstrip("/")
        self.app_id = app_id
        self.app_name = app_name
        self.device_name = "HA"
        self.app_version = "1.0"
        self.app_token = None
        self.session_token = None

    async def open_pairing(self):
        """Crée la demande de pairing et renvoie le track_id"""
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.host}/api/v8/login/authorize/", json={
                "app_id": self.app_id,
                "app_name": self.app_name,
                "device_name": self.device_name,
                "app_version": self.app_version
            }) as resp:
                data = await resp.json()
                return data  # contient result["track_id"]

    async def get_pairing_status(self, track_id):
        """Récupère le status actuel du pairing"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.host}/api/v8/login/authorize/{track_id}") as resp:
                return await resp.json()

    async def wait_for_app_token(self, track_id, timeout=60):
        """Boucle jusqu'à ce que app_token soit disponible ou timeout"""
        for _ in range(timeout // 2):  # pause 2s entre chaque try
            status = await self.get_pairing_status(track_id)
            result = status.get("result", {})
            if result.get("status") == "granted" and "app_token" in result:
                self.app_token = result["app_token"]
                return self.app_token
            if result.get("status") == "denied":
                raise Exception("Pairing denied on Freebox")
            await asyncio.sleep(2)
        raise Exception("Timeout waiting for app_token")

    async def login(self):
        """Finalise la connexion et obtient le session_token"""
        if not self.app_token:
            raise Exception("App token missing, pairing not validated")

        async with aiohttp.ClientSession() as session:
            # Récupère le challenge
            async with session.get(f"{self.host}/api/v8/login/") as resp:
                challenge = (await resp.json())["result"]["challenge"]

            # Génère le mot de passe pour la session
            password = hashlib.sha1((challenge + self.app_token).encode()).hexdigest()

            # Crée la session
            async with session.post(f"{self.host}/api/v8/login/session/", json={
                "app_id": self.app_id,
                "password": password
            }) as resp:
                data = await resp.json()
                self.session_token = data["result"]["session_token"]
                return self.session_token