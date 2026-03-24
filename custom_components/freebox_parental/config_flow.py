import asyncio
import voluptuous as vol
from homeassistant import config_entries

from .api import FreeboxAPI
from .const import DOMAIN


class FreeboxFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

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

        # 🔥 lance la tâche en arrière-plan
        self.hass.async_create_task(self._wait_for_pairing())

        return self.async_show_progress(
            step_id="pairing",
            progress_action="waiting_for_validation"
        )

    async def async_step_pairing(self, user_input=None):
        # 🔥 appelé APRÈS progress_done
        if not getattr(self, "app_token", None):
            return self.async_abort(reason="access_denied")

        return self.async_create_entry(
            title="Freebox",
            data={
                "host": self.host,
                "app_token": self.app_token
            }
        )

    async def _wait_for_pairing(self):
        """Attente validation Freebox"""
        for _ in range(30):  # ~60s
            status = await self.api.get_pairing_status(self.track_id)
            result = status.get("result", {})

            if result.get("status") == "granted":
                self.app_token = result.get("app_token")
                break

            if result.get("status") == "denied":
                self.app_token = None
                break

            await asyncio.sleep(2)

        # 🔥 🔥 LA LIGNE QUI CHANGE TOUT
        self.hass.config_entries.flow.async_configure(
            flow_id=self.flow_id,
            user_input=None
        )