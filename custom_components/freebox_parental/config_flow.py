import asyncio
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .api import FreeboxAPI
from .const import DOMAIN


class FreeboxFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self.host = None
        self.api = None
        self.track_id = None
        self._task = None
        self._token = None

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

        # 🔥 Lancement tâche async EXACT comme HA
        self._task = self.hass.async_create_task(
            self._async_wait_for_pairing()
        )

        return self.async_show_progress(
            step_id="pairing",
            progress_action="waiting_for_validation",
        )

    async def _async_wait_for_pairing(self):
        """Attente validation Freebox"""
        while True:
            status = await self.api.get_pairing_status(self.track_id)
            result = status.get("result", {})

            if result.get("status") == "granted":
                token = result.get("app_token")

                # 🔥 fallback Ultra
                if not token:
                    token = await self.api.get_app_token_from_list()

                if token:
                    self._token = token
                    return

            elif result.get("status") == "denied":
                raise Exception("access_denied")

            await asyncio.sleep(2)

    async def async_step_pairing(self, user_input=None):
        if self._task.done():
            try:
                await self._task
            except Exception as e:
                return self.async_abort(reason=str(e))

            # 🔥 CRUCIAL : fin du spinner
            return self.async_show_progress_done(
                next_step_id="finish"
            )

        return self.async_show_progress(
            step_id="pairing",
            progress_action="waiting_for_validation",
        )

    async def async_step_finish(self, user_input=None):
        """Création finale"""
        if not self._token:
            return self.async_abort(reason="no_token")

        return self.async_create_entry(
            title="Freebox",
            data={
                "host": self.host,
                "app_token": self._token
            }
        )