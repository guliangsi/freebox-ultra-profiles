import asyncio
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResult

from .freebox_api import FreeboxAPI

DOMAIN = "freebox_parental"


class FreeboxFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._host = None
        self._api = None
        self._track_id = None
        self._app_token = None

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is not None:
            self._host = user_input[CONF_HOST]
            self._api = FreeboxAPI(self._host)

            try:
                # Lancer autorisation
                res = await self._api.authorize()

                self._track_id = res["track_id"]
                self._app_token = res["app_token"]

                return self.async_show_progress(
                    step_id="authorize",
                    progress_action="waiting_for_user",
                )

            except Exception as e:
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._get_schema(),
                    errors={"base": "cannot_connect"},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_schema(),
        )

    async def async_step_authorize(self, user_input=None) -> FlowResult:
        """Attente validation sur Freebox"""

        while True:
            status = await self._api.check_authorization(self._track_id)

            if status == "granted":
                break

            if status == "denied":
                return self.async_abort(reason="access_denied")

            await asyncio.sleep(2)

        return self.async_show_progress_done(
            next_step_id="finish"
        )

    async def async_step_finish(self, user_input=None) -> FlowResult:
        """Login + création entrée"""

        # injecter le token dans l'API
        self._api._app_token = self._app_token

        try:
            await self._api.login()
        except Exception:
            return self.async_abort(reason="cannot_connect")

        return self.async_create_entry(
            title="Freebox Parental",
            data={
                CONF_HOST: self._host,
                "app_token": self._app_token,
            },
        )

    def _get_schema(self):
        return vol.Schema({
            vol.Required(CONF_HOST, default="mafreebox.freebox.fr"): str,
        })