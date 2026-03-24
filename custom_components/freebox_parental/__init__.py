from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import FreeboxAPI
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    api = FreeboxAPI(
        entry.data["host"],
        app_token=entry.data["app_token"]
    )

    await api.login()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = api

    return True