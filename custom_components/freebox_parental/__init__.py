from homeassistant.helpers.aiohttp_client import async_create_clientsession
from .api import FreeboxUltraAPI
from .coordinator import FreeboxProfilesCoordinator

DOMAIN = "freebox_parental"

async def async_setup_entry(hass, entry):
    session = async_create_clientsession(hass)

    api = FreeboxUltraAPI(
        entry.data["host"],
        entry.data["port"],
        "fr.freebox.ha_ultra",
        entry.data["app_token"]
    )
    await api.init(session)
    await api.login()

    # Create coordinator
    coordinator = FreeboxProfilesCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["api"] = api
    hass.data[DOMAIN]["coordinator"] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["switch"])
    
    return True