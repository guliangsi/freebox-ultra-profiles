import asyncio
import voluptuous as vol
from homeassistant import config_entries
from .api import FreeboxAPI
from .const import DOMAIN


class FreeboxFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Flow de configuration pour Freebox Parental"""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Step initial: demander l’URL de la Freebox"""
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
        track_id = pairing["result"]["track_id"]

        # Attendre que l'app_token soit disponible
        try:
            token = await self.api.wait_for_app_token(track_id)
        except Exception as e:
            return self.async_abort(reason=str(e))

        # Création de l'entrée Home Assistant
        return self.async_create_entry(
            title="Freebox",
            data={
                "host": self.host,
                "app_token": token
            }
        )