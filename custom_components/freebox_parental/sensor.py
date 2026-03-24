from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        FreeboxDeviceCountSensor(coordinator)
    ])


class FreeboxDeviceCountSensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def name(self):
        return "Freebox Devices Online"

    @property
    def state(self):
        return len([d for d in self.coordinator.data["devices"] if d["active"]])