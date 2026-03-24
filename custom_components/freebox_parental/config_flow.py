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

        # 🔥 LANCE tâche arrière-plan
        self.hass.async_create_task(self._wait_for_pairing())

        return self.async_show_progress(
            step_id="pairing",
            progress_action="waiting_for_validation"
        )

    async def _wait_for_pairing(self):
        """Attente validation Freebox"""
        for _ in range(30):
            status = await self.api.get_pairing_status(self.track_id)
            result = status.get("result", {})

            if result.get("status") == "granted":
                token = result.get("app_token")

                # 🔥 FIN DIRECTE DU FLOW (clé du fix)
                self.hass.config_entries.flow.async_create_entry(
                    self.flow_id,
                    title="Freebox",
                    data={
                        "host": self.host,
                        "app_token": token
                    }
                )
                return

            if result.get("status") == "denied":
                self.hass.config_entries.flow.async_abort(
                    self.flow_id,
                    reason="access_denied"
                )
                return

            await asyncio.sleep(2)

        # timeout
        self.hass.config_entries.flow.async_abort(
            self.flow_id,
            reason="timeout"
        )