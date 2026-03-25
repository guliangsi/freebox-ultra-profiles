from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from datetime import timedelta

class FreeboxParentalCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api):
        super().__init__(
            hass,
            _LOGGER,
            name="freebox_parental",
            update_interval=timedelta(seconds=30),
        )
        self.api = api

    async def _async_update_data(self):
        return await self.api.get_profiles()