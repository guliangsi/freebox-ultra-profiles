import aiohttp
import hashlib
import asyncio

class FreeboxAPI:
    def __init__(self, host, app_id):
        self.host = host
        self.app_id = app_id
        self.session_token = None
        self.app_token = None

    async def login(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.host}/api/v8/login/") as resp:
                result = await resp.json()
                challenge = result["result"]["challenge"]

            password = hashlib.sha1((challenge + self.app_token).encode()).hexdigest()

            async with session.post(f"{self.host}/api/v8/login/session/", json={
                "app_id": self.app_id,
                "password": password
            }) as resp:
                result = await resp.json()
                self.session_token = result["result"]["session_token"]

    async def request(self, method, path, data=None):
        headers = {"X-Fbx-App-Auth": self.session_token} if self.session_token else {}
        async with aiohttp.ClientSession() as session:
            async with session.request(method, f"{self.host}/api/v8{path}", headers=headers, json=data) as resp:
                return await resp.json()

    async def get_devices(self):
        return await self.request("GET", "/lan/browser/pub/")

    async def get_profiles(self):
        return await self.request("GET", "/parental/profile/")

    async def set_device(self, device_id, state):
        return await self.request("PUT", f"/lan/browser/pub/{device_id}", {"active": state})

    async def set_profile(self, profile_id, enable):
        week = (
            {d: [["00:00", "23:59"]] for d in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]}
            if enable else
            {d: [] for d in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]}
        )
        return await self.request("PUT", f"/parental/profile/{profile_id}", {"week": week})