import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .api import FreeboxAPI
from .const import DOMAIN


class FreeboxFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Étape 1 : demander host + lancer pairing"""
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

        # 👉 on passe à l'étape suivante sans attendre
        return self.async_show_form(
            step_id="pairing",
            description_placeholders={
                "message": "Valide la demande sur ta Freebox puis clique sur Continuer"
            }
        )

    async def async_step_pairing(self, user_input=None):
        """Étape 2 : récupération token après validation"""
        try:
            token = await self.api.wait_for_app_token(self.track_id, timeout=10)
        except Exception:
            return self.async_show_form(
                step_id="pairing",
                errors={"base": "not_validated"},
                description_placeholders={
                    "message": "Toujours en attente de validation sur la Freebox"
                }
            )

        return self.async_create_entry(
            title="Freebox",
            data={
                "host": self.host,
                "app_token": token
            }
        )