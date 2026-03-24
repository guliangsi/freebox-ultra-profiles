from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    devices = coordinator.data["devices"]
    profiles = coordinator.data["profiles"]

    entities = []

    for d in devices:
        entities.append(FreeboxDeviceSwitch(coordinator, d))

    for p in profiles:
        entities.append(FreeboxProfileSwitch(coordinator, p))

    async_add_entities(entities)


class FreeboxDeviceSwitch(SwitchEntity):
    def __init__(self, coordinator, device):
        self.coordinator = coordinator
        self.api = coordinator.api
        self.device = device

    @property
    def name(self):
        return f"{self.device['primary_name']}"

    @property
    def is_on(self):
        return self.device["active"]

    async def async_turn_on(self):
        self.api.set_device(self.device["id"], True)

    async def async_turn_off(self):
        self.api.set_device(self.device["id"], False)


class FreeboxProfileSwitch(SwitchEntity):
    def __init__(self, coordinator, profile):
        self.coordinator = coordinator
        self.api = coordinator.api
        self.profile = profile

    @property
    def name(self):
        return f"Profil {self.profile['name']}"

    @property
    def is_on(self):
        return True

    async def async_turn_on(self):
        self.api.set_profile(self.profile["id"], True)

    async def async_turn_off(self):
        self.api.set_profile(self.profile["id"], False)