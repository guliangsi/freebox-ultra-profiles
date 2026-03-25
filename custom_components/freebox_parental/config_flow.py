import asyncio
import voluptuous as vol
from homeassistant import config_entries

from .api import FreeboxAPI
from .const import DOMAIN


class FreeboxFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self.host = None
        self.api = None
        self.track_id = None

    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required("host", default="http://mafreebox.freebox.fr"): str
                })
            )

        self.host = user_input["host"]
        self.api = FreeboxAPI(self.host)

        pairing = await self.api.open_pairing()
        self.track_id = pairing["result"]["track_id"]

        # 🔥 création de la task EXACTEMENT comme HA core
        return self.async_show_progress(
            step_id="pairing",
            progress_action="waiting_for_validation",
            progress_task=self.hass.async_create_task(
                self._async_wait_for_pairing()
            ),
        )

    async def _async_wait_for_pairing(self):
        """Tâche de fond (pattern officiel)"""
        while True:
            status = await self.api.get_pairing_status(self.track_id)
            result = status.get("result", {})

            if result.get("status") == "granted":
                token = result.get("app_token")

                # 🔥 fallback Freebox Ultra
                if not token:
                    token = await self.api.get_app_token_from_list()

                if token:
                    self.context["app_token"] = token
                    return

            elif result.get("status") == "denied":
                raise Exception("access_denied")

            await asyncio.sleep(2)

    async def async_step_pairing(self, user_input=None):
        """Step appelé automatiquement quand task finie"""
        return self.async_show_progress_done(
            next_step_id="finish"
        )

    async def async_step_finish(self, user_input=None):
        token = self.context.get("app_token")

        if not token:
            return self.async_abort(reason="no_token")

        return self.async_create_entry(
            title="Freebox",
            data={
                "host": self.host,
                "app_token": token
            }
        )