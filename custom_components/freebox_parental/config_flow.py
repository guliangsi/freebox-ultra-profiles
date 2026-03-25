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

        host = user_input["host"]
        api = FreeboxAPI(host)

        try:
            pairing = await api.open_pairing()
            track_id = pairing["result"]["track_id"]

            token = await api.wait_for_app_token(track_id)

        except Exception as e:
            return self.async_abort(reason=str(e))

        return self.async_create_entry(
            title="Freebox",
            data={
                "host": host,
                "app_token": token
            }
        )