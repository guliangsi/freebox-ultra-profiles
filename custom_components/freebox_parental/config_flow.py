import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST

from .freebox_api import FreeboxAPI

DOMAIN = "freebox_parental"


class FreeboxFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            host = user_input[CONF_HOST]

            api = FreeboxAPI(host)

            try:
                # 🔥 magie: la lib gère l’auth complète
                await api.authorize()

            except Exception:
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._schema(),
                    errors={"base": "cannot_connect"},
                )

            return self.async_create_entry(
                title="Freebox Parental",
                data={CONF_HOST: host},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=self._schema(),
        )

    def _schema(self):
        return vol.Schema({
            vol.Required(CONF_HOST, default="mafreebox.freebox.fr"): str,
        })