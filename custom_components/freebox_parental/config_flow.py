import voluptuous as vol
from homeassistant import config_entries

class FreeboxFlowHandler(config_entries.ConfigFlow, domain="freebox_parental"):

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Freebox Parental",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("host", default="mafreebox.freebox.fr"): str,
            }),
        )