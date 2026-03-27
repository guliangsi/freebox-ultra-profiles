import logging
_LOGGER = logging.getLogger(__name__)

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import voluptuous as vol
import asyncio

from .const import DOMAIN, APP_ID, APP_NAME

API_VERSION_URL = "http://mafreebox.freebox.fr/api_version"
LOCAL = "http://mafreebox.freebox.fr"

class FreeboxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        _LOGGER.debug("CONFIG_FLOW: async_step_user() called")

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=vol.Schema({}))

        session = async_create_clientsession(self.hass)

        #
        # 1) Lire api_version
        #
        try:
            async with session.get(API_VERSION_URL, timeout=5) as r:
                info = await r.json()
        except Exception:
            return self.async_abort(reason="cannot_connect")

        api_domain = info.get("api_domain")
        https_port = info.get("https_port")

        if not api_domain or not https_port:
            return self.async_abort(reason="cannot_connect")

        #
        # 2) Demande d’autorisation (LOCAL HTTP)
        #
        req = {
            "app_id": APP_ID,
            "app_name": APP_NAME,
            "app_version": "1.0",
            "device_name": "Home Assistant"
        }

        try:
            async with session.post(f"{LOCAL}/api/v8/login/authorize/", json=req, timeout=5) as r:
                auth = await r.json()
                _LOGGER.debug("DEBUG AUTH RESPONSE: %s", auth)
                track_id = auth["result"]["track_id"]
                saved_app_token = auth["result"].get("app_token")  # <-- On sauve ici
        except Exception:
            return self.async_abort(reason="cannot_connect")

        if not saved_app_token:
            return self.async_abort(reason="cannot_connect")

        #
        # 3) Polling (LOCAL HTTP)
        #
        poll_url = f"{LOCAL}/api/v8/login/authorize/{track_id}"

        for _ in range(30):
            await asyncio.sleep(2)

            try:
                async with session.get(poll_url, timeout=5) as r:
                    data = await r.json()
                    _LOGGER.debug("DEBUG POLL RESPONSE: %s", data)
            except Exception:
                return self.async_abort(reason="cannot_connect")

            status = data["result"]["status"]

            if status == "granted":
                # NE PAS CHERCHER app_token ICI : il n'est pas renvoyé par Ultra
                return self.async_create_entry(
                    title="Freebox Ultra",
                    data={
                        "host": api_domain,
                        "port": https_port,
                        "app_token": saved_app_token
                    }
                )

            if status in ("denied", "timeout"):
                return self.async_abort(reason="auth_failed")

        return self.async_abort(reason="timeout")