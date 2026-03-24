from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_call_later
from .coordinator import FreeboxCoordinator
from .api import FreeboxAPI
from .const import DOMAIN

# Placeholder minimal pour HA
async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the integration (required placeholder)."""
    return True

# Vrai setup depuis la config flow / UI
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    api = FreeboxAPI(entry.data["host"], "homeassistant.freebox")

    coordinator = FreeboxCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    async def handle_pause(call):
        entity_id = call.data["entity_id"]
        duration = call.data["duration"]

        await hass.services.async_call("switch", "turn_off", {"entity_id": entity_id})

        async def turn_on_again(_):
            await hass.services.async_call("switch", "turn_on", {"entity_id": entity_id})

        async_call_later(hass, duration, turn_on_again)

    hass.services.async_register("freebox_parental", "pause_device", handle_pause)

    await hass.config_entries.async_forward_entry_setups(entry, ["switch", "sensor"])

    return True