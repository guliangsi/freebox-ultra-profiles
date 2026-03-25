from datetime import timedelta
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .freebox_api_wrapper import FreeboxAPIWrapper

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
    host = entry.data["host"]
    api = FreeboxAPIWrapper(host)
    await api.login()

    # DataUpdateCoordinator pour refresher les profils
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="freebox_parental",
        update_method=api.get_profiles,
        update_interval=timedelta(seconds=30)
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault("freebox_parental", {})[entry.entry_id] = {
        "api": api,
        "coordinator": coordinator
    }

    # Forward vers switch
    await hass.config_entries.async_forward_entry_setups(entry, ["switch"])
    return True