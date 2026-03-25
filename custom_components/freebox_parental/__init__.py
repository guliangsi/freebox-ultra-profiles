from .freebox_api import FreeboxAPI
from .coordinator import FreeboxParentalCoordinator

async def async_setup_entry(hass, entry):
    api = FreeboxAPI(entry.data["host"])
    await api.login()

    coordinator = FreeboxParentalCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault("freebox_parental", {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["switch"])

    return True