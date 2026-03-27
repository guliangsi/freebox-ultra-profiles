import hashlib, hmac, ssl, aiohttp

class FreeboxUltraAPI:
    def __init__(self, host, port, app_id, app_token):
        self.base = f"https://{host}:{port}"
        self.session = None
        self.app_id = app_id
        self.app_token = app_token
        self.session_token = None

        self.ssl_ctx = ssl.create_default_context()
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.verify_mode = ssl.CERT_NONE

    async def init(self, session):
        self.session = session

    async def _call(self, method, endpoint, json=None):
        headers = {"X-Fbx-App-Auth": self.session_token} if self.session_token else {}
        async with self.session.request(
            method,
            self.base + endpoint,
            json=json,
            headers=headers,
            ssl=self.ssl_ctx,
        ) as r:
            data = await r.json()
            if not data.get("success", False):
                raise Exception(data)
            return data["result"]

    async def login(self):
        # Step 1: Get challenge
        result = await self._call("GET", "/api/v8/login/")
        challenge = result["challenge"]

        # Step 2: Compute password HMAC
        password = hmac.new(
            self.app_token.encode(),
            challenge.encode(),
            hashlib.sha1
        ).hexdigest()

        # Step 3: Start session
        session = await self._call("POST", "/api/v8/login/session/", {
            "app_id": self.app_id,
            "password": password
        })

        self.session_token = session["session_token"]
        return True

    async def list_profiles(self):
        # Returns ALL profiles
        return await self._call("GET", "/api/v8/network_control/")

    async def get_profile(self, profile_id):
        return await self._call("GET", f"/api/v8/network_control/{profile_id}")

    async def set_profile(self, profile_id, override, mode=None):
        # Get full object
        obj = await self.get_profile(profile_id)

        obj["override"] = override
        if mode:
            obj["override_mode"] = mode

        return await self._call(
            "PUT",
            f"/api/v8/network_control/{profile_id}",
            json=obj
        )

    async def pause_profile(self, profile_id):
        return await self.set_profile(profile_id, True, "denied")

    async def resume_profile(self, profile_id):
        return await self.set_profile(profile_id, True, "allowed")