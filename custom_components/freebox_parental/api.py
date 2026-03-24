import aiohttp
import hashlib
import asyncio

class FreeboxAPI:
    def __init__(self, host, app_id="homeassistant.freebox"):
        self.host = host
        self.app_id = app_id
        self.app_token = None
        self.session_token = None

    async def open_pairing(self):
        """Crée la demande de pairing, renvoie track_id"""
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.host}/api/v8/login/authorize/", json={
                "app_id": self.app_id,
                "app_name": "Home Assistant Freebox",
                "device_name": "HA",
                "app_version": "1.0"
            }) as r:
                res = await r.json()
                return res  # contient result["track_id"]

    async def get_pairing_status(self, track_id):
        """Récupère le status actuel du pairing"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.host}/api/v8/login/authorize/{track_id}") as r:
                return await r.json()

    async def login(self):
        """Finalise la connexion pour obtenir session_token"""
        async with aiohttp.ClientSession() as session:
            # Récupère challenge
            async with session.get(f"{self.host}/api/v8/login/") as resp:
                challenge = (await resp.json())["result"]["challenge"]

            if not self.app_token:
                raise Exception("App token manquant, pairing non validé")

            password = hashlib.sha1((challenge + self.app_token).encode()).hexdigest()

            async with session.post(f"{self.host}/api/v8/login/session/", json={
                "app_id": self.app_id,
                "password": password
            }) as resp:
                self.session_token = (await resp.json())["result"]["session_token"]