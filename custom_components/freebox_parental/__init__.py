from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .coordinator import FreeboxCoordinator
from .api import FreeboxAPI
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    api = FreeboxAPI(entry.data["host"], "homeassistant.freebox")

    # 🔥 LOGIN UNE SEULE FOIS ICI
    await api.login()

    coordinator = FreeboxCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["switch", "sensor"])

    return True