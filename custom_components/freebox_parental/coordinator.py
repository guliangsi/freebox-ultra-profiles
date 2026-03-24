from datetime import timedelta
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .api import FreeboxAPI

_LOGGER = logging.getLogger(__name__)

class FreeboxCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api: FreeboxAPI):
        super().__init__(
            hass,
            logger=_LOGGER,
            name="freebox_parental",
            update_interval=timedelta(seconds=30),
        )
        self.api = api

    async def _async_update_data(self):
        await self.api.login()
        devices = await self.api.get_devices()
        profiles = await self.api.get_profiles()

        return {
            "devices": devices["result"],
            "profiles": profiles["result"],
        }