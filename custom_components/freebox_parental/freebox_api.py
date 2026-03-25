import aiohttp
import asyncio
import hashlib
import logging

_LOGGER = logging.getLogger(__name__)


class FreeboxAPI:
    def __init__(self, host):
        self._host = host
        self._base = f"http://{host}/api/v4"
        self._session_token = None
        self._app_token = None

        self._app_id = "hass.freebox_parental"
        self._app_name = "Home Assistant Freebox Parental"
        self._app_version = "1.0"
        self._device_name = "Home Assistant"

        self._http = aiohttp.ClientSession()

    # ---------------------------
    # HTTP CORE
    # ---------------------------
    async def _request(self, method, path, data=None):
        url = f"{self._base}{path}"

        headers = {}
        if self._session_token:
            headers["X-Fbx-App-Auth"] = self._session_token

        try:
            async with self._http.request(
                method,
                url,
                json=data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                res = await resp.json()

        except asyncio.TimeoutError:
            raise Exception("Timeout Freebox API")

        except aiohttp.ClientError as err:
            raise Exception(f"HTTP error: {err}")

        if not res.get("success", False):
            _LOGGER.debug("Freebox API error: %s", res)
            raise Exception(res)

        return res

    async def close(self):
        await self._http.close()

    # ---------------------------
    # AUTHORIZE (1 seule fois)
    # ---------------------------
    async def authorize(self):
        res = await self._request("POST", "/login/authorize/", {
            "app_id": self._app_id,
            "app_name": self._app_name,
            "app_version": self._app_version,
            "device_name": self._device_name,
        })

        return {
            "track_id": res["result"]["track_id"],
            "app_token": res["result"]["app_token"],
        }

    async def check_authorization(self, track_id):
        res = await self._request("GET", f"/login/authorize/{track_id}")
        return res["result"]["status"]

    # ---------------------------
    # LOGIN (session)
    # ---------------------------
    async def login(self):
        if not self._app_token:
            raise Exception("Missing app_token")

        # 1. récupérer challenge
        res = await self._request("GET", "/login/")
        challenge = res["result"]["challenge"]

        # 2. générer password
        password = hashlib.sha1(
            (challenge + self._app_token).encode()
        ).hexdigest()

        # 3. ouvrir session
        res = await self._request("POST", "/login/session/", {
            "app_id": self._app_id,
            "password": password,
        })

        self._session_token = res["result"]["session_token"]

    # ---------------------------
    # UTILS
    # ---------------------------
    async def ensure_logged_in(self):
        if not self._session_token:
            await self.login()

    async def _safe_request(self, method, path, data=None):
        try:
            await self.ensure_logged_in()
            return await self._request(method, path, data)

        except Exception:
            _LOGGER.debug("Session expirée, relogin…")
            self._session_token = None
            await self.login()
            return await self._request(method, path, data)

    # ---------------------------
    # PARENTAL CONTROL
    # ---------------------------
    async def get_profiles(self):
        res = await self._safe_request("GET", "/parental/filter/")
        return res["result"]

    async def pause_profile(self, profile_id):
        return await self._safe_request(
            "PUT",
            f"/parental/filter/{profile_id}",
            {
                "forced": True,
                "forced_mode": "denied",
            },
        )

    async def resume_profile(self, profile_id):
        return await self._safe_request(
            "PUT",
            f"/parental/filter/{profile_id}",
            {
                "forced": False,
            },
        )

    async def set_profile_mode(self, profile_id, mode):
        """
        mode:
        - allowed
        - denied
        - webonly
        """
        return await self._safe_request(
            "PUT",
            f"/parental/filter/{profile_id}",
            {
                "forced": True,
                "forced_mode": mode,
            },
        )