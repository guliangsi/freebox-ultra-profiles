import aiohttp
import asyncio
import hashlib
import logging

_LOGGER = logging.getLogger(__name__)


class FreeboxAPI:
    def __init__(self, host, app_id="homeassistant.freebox"):
        self.host = host.rstrip("/")
        self.app_id = app_id
        self.session = aiohttp.ClientSession()
        self.app_token = None
        self.session_token = None

    async def close(self):
        await self.session.close()

    # --------------------------------------------------
    # 🔹 PAIRING
    # --------------------------------------------------

    async def open_pairing(self):
        _LOGGER.debug("🔐 Opening pairing with Freebox...")

        async with self.session.post(
            f"{self.host}/api/v8/login/authorize/",
            json={
                "app_id": self.app_id,
                "app_name": "Home Assistant",
                "device_name": "HA",
                "app_version": "1.0",
            },
        ) as resp:
            data = await resp.json()

        _LOGGER.debug("📡 Pairing response: %s", data)

        return data

    async def get_pairing_status(self, track_id):
        async with self.session.get(
            f"{self.host}/api/v8/login/authorize/{track_id}"
        ) as resp:
            data = await resp.json()

        _LOGGER.debug("📡 Pairing status (%s): %s", track_id, data)

        return data

    # --------------------------------------------------
    # 🔹 TOKEN (ULTRA FIX)
    # --------------------------------------------------

    async def get_apps(self):
        """Liste toutes les apps autorisées"""
        async with self.session.get(f"{self.host}/api/v8/login/") as resp:
            data = await resp.json()

        _LOGGER.debug("📡 Apps list: %s", data)

        return data

    async def get_app_token_from_list(self):
        """Fallback Ultra"""
        data = await self.get_apps()

        apps = data.get("result", {}).get("apps", [])

        for app in apps:
            _LOGGER.debug("🔍 Checking app: %s", app)

            if app.get("app_id") == self.app_id:
                token = app.get("app_token")

                if token:
                    _LOGGER.debug("✅ Token found in app list")
                    return token

        _LOGGER.debug("❌ Token not found in app list")
        return None

    async def wait_for_app_token(self, track_id, timeout=120):
        """
        Méthode robuste :
        - check authorize
        - fallback apps list
        """
        elapsed = 0

        while elapsed < timeout:
            status_json = await self.get_pairing_status(track_id)
            result = status_json.get("result", {})

            status = result.get("status")
            _LOGGER.debug("🔄 Pairing status: %s", status)

            # ✅ cas normal
            if status == "granted":
                token = result.get("app_token")

                if token:
                    _LOGGER.debug("✅ Token received via authorize")
                    self.app_token = token
                    return token

                # 🔥 fallback Ultra
                _LOGGER.debug("⚠️ No token in authorize, trying apps list...")
                token = await self.get_app_token_from_list()

                if token:
                    self.app_token = token
                    return token

            elif status == "denied":
                _LOGGER.error("❌ Pairing denied by user")
                raise Exception("access_denied")

            await asyncio.sleep(2)
            elapsed += 2

        _LOGGER.error("⏱ Timeout waiting for token")
        raise Exception("timeout")

    # --------------------------------------------------
    # 🔹 LOGIN SESSION
    # --------------------------------------------------

    async def login(self, app_token=None):
        if app_token:
            self.app_token = app_token

        if not self.app_token:
            raise Exception("missing_app_token")

        _LOGGER.debug("🔐 Starting login session...")

        # 1. challenge
        async with self.session.get(f"{self.host}/api/v8/login/") as resp:
            data = await resp.json()

        challenge = data["result"]["challenge"]
        _LOGGER.debug("📡 Challenge: %s", challenge)

        # 2. password
        password = hashlib.sha1(
            (challenge + self.app_token).encode()
        ).hexdigest()

        # 3. session
        async with self.session.post(
            f"{self.host}/api/v8/login/session/",
            json={
                "app_id": self.app_id,
                "password": password,
            },
        ) as resp:
            session_data = await resp.json()

        _LOGGER.debug("📡 Session response: %s", session_data)

        self.session_token = session_data["result"]["session_token"]

        _LOGGER.debug("✅ Logged in successfully")

    # --------------------------------------------------
    # 🔹 GENERIC REQUEST
    # --------------------------------------------------

    async def request(self, method, path, data=None):
        if not self.session_token:
            raise Exception("not_authenticated")

        headers = {"X-Fbx-App-Auth": self.session_token}

        _LOGGER.debug("📡 Request %s %s", method, path)

        async with self.session.request(
            method,
            f"{self.host}{path}",
            json=data,
            headers=headers,
        ) as resp:
            result = await resp.json()

        _LOGGER.debug("📡 Response: %s", result)

        return result