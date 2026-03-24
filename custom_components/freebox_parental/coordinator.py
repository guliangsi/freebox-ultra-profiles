from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

class FreeboxCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api):
        super().__init__(
            hass,
            logger=None,
            name="freebox_parental",
            update_interval=timedelta(seconds=30),
        )
        self.api = api

    async def _async_update_data(self):
        self.api.login()
        devices = self.api.get_devices()
        profiles = self.api.get_profiles()

        return {
            "devices": devices["result"],
            "profiles": profiles["result"],
        }