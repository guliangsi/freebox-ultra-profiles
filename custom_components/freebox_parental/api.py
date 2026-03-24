import aiohttp
import hashlib
import asyncio

class FreeboxAPI:
    def __init__(self, host, app_id="homeassistant.freebox"):
        self.host = host
        self.app_id = app_id
        self.app_token = None
        self.session_token = None
        self._session = None

    async def login(self):
        # 🔥 évite double login
        if self.session_token:
            return

        if self._session is None:
            self._session = aiohttp.ClientSession()

        # Challenge
        async with self._session.get(f"{self.host}/api/v8/login/") as resp:
            result = await resp.json()
            challenge = result["result"]["challenge"]

        # Pairing si pas encore fait
        if self.app_token is None:
            async with self._session.post(f"{self.host}/api/v8/login/authorize/", json={
                "app_id": self.app_id,
                "app_name": "Home Assistant Freebox",
                "device_name": "HA",
                "app_version": "1.0"
            }) as r:
                res = await r.json()
                track_id = res["result"]["track_id"]
                print(f"👉 Valide l'app sur ta Freebox (track_id={track_id})")

            # Attente validation
            while True:
                async with self._session.get(f"{self.host}/api/v8/login/authorize/{track_id}") as status_r:
                    status_json = await status_r.json()
                    status = status_json["result"]["status"]

                    if status == "granted":
                        self.app_token = status_json["result"]["app_token"]
                        break

                    elif status == "denied":
                        raise Exception("Autorisation refusée sur la Freebox")

                await asyncio.sleep(2)

        # Session login
        password = hashlib.sha1((challenge + self.app_token).encode()).hexdigest()

        async with self._session.post(f"{self.host}/api/v8/login/session/", json={
            "app_id": self.app_id,
            "password": password
        }) as resp:
            result = await resp.json()
            self.session_token = result["result"]["session_token"]

    async def request(self, method, path, data=None):
        headers = {"X-Fbx-App-Auth": self.session_token}

        async with self._session.request(
            method,
            f"{self.host}/api/v8{path}",
            headers=headers,
            json=data
        ) as resp:
            return await resp.json()

    async def get_devices(self):
        return await self.request("GET", "/lan/browser/pub/")

    async def get_profiles(self):
        return await self.request("GET", "/parental/profile/")

    async def set_device(self, device_id, state):
        return await self.request(
            "PUT",
            f"/lan/browser/pub/{device_id}",
            {"active": state}
        )

    async def set_profile(self, profile_id, enable):
        week = (
            {d: [["00:00", "23:59"]] for d in [
                "monday","tuesday","wednesday","thursday",
                "friday","saturday","sunday"
            ]}
            if enable else
            {d: [] for d in [
                "monday","tuesday","wednesday","thursday",
                "friday","saturday","sunday"
            ]}
        )

        return await self.request(
            "PUT",
            f"/parental/profile/{profile_id}",
            {"week": week}
        )

    async def close(self):
        if self._session:
            await self._session.close()