from homeassistant.components.switch import SwitchEntity

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["freebox_parental"][entry.entry_id]

    entities = []
    for profile in coordinator.data["result"]:
        entities.append(FreeboxProfileSwitch(coordinator, profile))

    async_add_entities(entities)


class FreeboxProfileSwitch(SwitchEntity):
    def __init__(self, coordinator, profile):
        self.coordinator = coordinator
        self.profile = profile
        self._attr_name = f"Freebox {profile['desc']}"
        self._attr_unique_id = f"freebox_profile_{profile['id']}"

    @property
    def is_on(self):
        return self.profile["filter_state"] == "allowed"

    async def async_turn_off(self):
        await self.coordinator.api.pause_profile(self.profile["id"])
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self):
        await self.coordinator.api.resume_profile(self.profile["id"])
        await self.coordinator.async_request_refresh()