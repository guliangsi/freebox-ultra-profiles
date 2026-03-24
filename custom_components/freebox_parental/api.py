import aiohttp
import hashlib
import asyncio

class FreeboxAPI:
    def __init__(self, host, app_id="homeassistant.freebox"):
        self.host = host
        self.app_id = app_id
        self.app_token = None
        self.session_token = None

    async def login(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.host}/api/v8/login/") as resp:
                challenge = (await resp.json())["result"]["challenge"]

            if self.app_token is None:
                # Flow pairing automatique
                async with session.post(f"{self.host}/api/v8/login/authorize/", json={
                    "app_id": self.app_id,
                    "app_name": "Home Assistant Freebox",
                    "device_name": "HA",
                    "app_version": "1.0"
                }) as r:
                    res = await r.json()
                    track_id = res["result"]["track_id"]
                    print(f"Valide l'app sur ta Freebox pour track_id={track_id}")
                    # Attente de validation manuelle sur Freebox OS
                    while True:
                        async with session.get(f"{self.host}/api/v8/login/authorize/{track_id}") as status_r:
                            status = (await status_r.json())["result"]["status"]
                            if status == "granted":
                                self.app_token = (await status_r.json())["result"]["app_token"]
                                break
                        await asyncio.sleep(2)

            password = hashlib.sha1((challenge + self.app_token).encode()).hexdigest()
            async with session.post(f"{self.host}/api/v8/login/session/", json={
                "app_id": self.app_id,
                "password": password
            }) as resp:
                self.session_token = (await resp.json())["result"]["session_token"]

    # toutes les fonctions request/get/set restent async comme précédemment