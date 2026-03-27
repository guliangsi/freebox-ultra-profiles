from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import logging

_LOGGER = logging.getLogger(__name__)

class FreeboxProfilesCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api):
        super().__init__(
            hass,
            _LOGGER,
            name="freebox_profiles",
            update_interval=timedelta(seconds=30),
        )
        self.api = api

    async def _async_update_data(self):
        try:
            profiles = await self.api.list_profiles()
            return {p["profile_id"]: p for p in profiles}
        except Exception as err:
            raise UpdateFailed(f"Freebox update failed: {err}")