import asyncio
import voluptuous as vol
from homeassistant import config_entries

from .api import FreeboxAPI
from .const import DOMAIN

class FreeboxFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("host", default="http://mafreebox.freebox.fr"): str
            })
        )

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

        return self.async_show_progress(
            step_id="pairing",
            progress_action="waiting_for_validation"
        )

    async def async_step_pairing(self, user_input=None):
        for _ in range(30):  # ~60 secondes
            status = await self.api.get_pairing_status(self.track_id)
            result = status.get("result", {})

            if result.get("status") == "granted":
                token = result.get("app_token")

                return self.async_create_entry(
                    title="Freebox",
                    data={
                        "host": self.host,
                        "app_token": token
                    }
                )

            if result.get("status") == "denied":
                return self.async_abort(reason="access_denied")

            await asyncio.sleep(2)

        return self.async_abort(reason="timeout")