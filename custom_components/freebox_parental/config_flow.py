import asyncio
import voluptuous as vol
from homeassistant import config_entries
from .api import FreeboxAPI
from .const import DOMAIN


class FreeboxFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Step initial: demander l'URL de la Freebox"""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required("host", default="http://mafreebox.freebox.fr"): str
                })
            )

        self.host = user_input["host"]
        self.api = FreeboxAPI(self.host)

        # Ouvre le pairing et récupère track_id
        pairing = await self.api.open_pairing()
        self.track_id = pairing["result"]["track_id"]

        # Passe directement à l'étape de polling
        return await self.async_step_pairing()

    async def async_step_pairing(self, user_input=None):
        """Step de polling pour attendre la validation Freebox"""
        for _ in range(30):  # ~60 secondes max
            status = await self.api.get_pairing_status(self.track_id)
            result = status.get("result", {})

            if result.get("status") == "granted":
                token = result.get("app_token")
                if not token:
                    # fallback si token absent
                    return self.async_abort(reason="app_token_missing")

                return self.async_create_entry(
                    title="Freebox",
                    data={
                        "host": self.host,
                        "app_token": token
                    }
                )

            if result.get("status") == "denied":
                return self.async_abort(reason="access_denied")

            await asyncio.sleep(2)  # pause entre deux vérifications

        return self.async_abort(reason="timeout")