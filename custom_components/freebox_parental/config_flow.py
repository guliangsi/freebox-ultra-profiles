import asyncio
import voluptuous as vol
from homeassistant import config_entries
from .api import FreeboxAPI
from .const import DOMAIN


class FreeboxFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Flow de configuration pour Freebox Parental"""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Step initial: demande l’URL de la Freebox"""
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

        # Passe directement à l’étape de polling
        return await self.async_step_pairing()

    async def async_step_pairing(self, user_input=None):
        """Step de polling pour attendre la validation Freebox"""
        for _ in range(30):  # ~60 secondes max
            status = await self.api.get_pairing_status(self.track_id)
            result = status.get("result", {})
            status_str = result.get("status")

            if status_str == "granted":
                # 🔹 GET final pour récupérer le vrai app_token
                final = await self.api.get_pairing_status(self.track_id)
                token = final.get("result", {}).get("app_token")

                if not token:
                    # token pas encore prêt, attendre et réessayer
                    await asyncio.sleep(2)
                    continue

                return self.async_create_entry(
                    title="Freebox",
                    data={
                        "host": self.host,
                        "app_token": token
                    }
                )

            if status_str == "denied":
                return self.async_abort(reason="access_denied")

            await asyncio.sleep(2)

        return self.async_abort(reason="timeout")