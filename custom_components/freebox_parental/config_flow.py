import asyncio
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .api import FreeboxAPI
from .const import DOMAIN


class FreeboxFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self.host = None
        self.api = None
        self.track_id = None
        self._task = None

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

        # Start pairing
        pairing = await self.api.open_pairing()
        self.track_id = pairing["result"]["track_id"]

        # Lancer tâche en background (comme HA officiel)
        self._task = self.hass.async_create_task(
            self._async_wait_for_pairing()
        )

        return self.async_show_progress(
            step_id="pairing",
            progress_action="waiting_for_validation",
        )

    async def _async_wait_for_pairing(self):
        """Attend validation Freebox"""
        while True:
            status = await self.api.get_pairing_status(self.track_id)
            result = status.get("result", {})

            if result.get("status") == "granted":
                token = result.get("app_token")

                # 🔥 fallback Ultra
                if not token:
                    token = await self.api.get_app_token_from_list()

                if token:
                    return token

            elif result.get("status") == "denied":
                raise Exception("access_denied")

            await asyncio.sleep(2)

    async def async_step_pairing(self, user_input=None):
        """Fin du progress"""
        if self._task.done():
            try:
                token = self._task.result()
            except Exception as e:
                return self.async_abort(reason=str(e))

            return self.async_create_entry(
                title="Freebox",
                data={
                    "host": self.host,
                    "app_token": token
                }
            )

        return self.async_show_progress(
            step_id="pairing",
            progress_action="waiting_for_validation",
        )

    @callback
    def async_abort(self, reason):
        return super().async_abort(reason=reason)