from homeassistant.components.switch import SwitchEntity

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data["freebox_parental"][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]

    entities = []
    for profile in coordinator.data:
        entities.append(FreeboxProfileSwitch(coordinator, api, profile))

    async_add_entities(entities)

class FreeboxProfileSwitch(SwitchEntity):
    def __init__(self, coordinator, api, profile):
        self.coordinator = coordinator
        self.api = api
        self.profile = profile
        self._attr_name = f"Freebox {profile['desc']}"
        self._attr_unique_id = f"freebox_profile_{profile['id']}"

    @property
    def is_on(self):
        return self.profile["filter_state"] == "allowed"

    async def async_turn_off(self, **kwargs):
        await self.api.pause_profile(self.profile["id"])
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs):
        await self.api.resume_profile(self.profile["id"])
        await self.coordinator.async_request_refresh()