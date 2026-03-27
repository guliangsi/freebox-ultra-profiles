import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback

_LOGGER = logging.getLogger(__name__)

DOMAIN = "freebox_ultra"


async def async_setup_entry(hass, entry, async_add_entities):
    api = hass.data[DOMAIN]["api"]
    coordinator = hass.data[DOMAIN]["coordinator"]

    entities = [
        FreeboxProfileSwitch(api, coordinator, profile_id)
        for profile_id in coordinator.data
    ]
    async_add_entities(entities)


class FreeboxProfileSwitch(SwitchEntity):
    """Switch Freebox Ultra basé sur NetworkControl."""

    def __init__(self, api, coordinator, profile_id):
        self.api = api
        self.coordinator = coordinator
        self.profile_id = profile_id
        self._attr_should_poll = False

    # -------------------------------------------------------
    # PROPRIÉTÉS DE BASE
    # -------------------------------------------------------

    @property
    def name(self):
        return self._p("profile_name")

    @property
    def unique_id(self):
        return f"freebox_profile_{self.profile_id}"

    @property
    def is_on(self):
        """
        allumé = allowed
        éteint = denied
        """
        return self._p("current_mode") == "allowed"

    # -------------------------------------------------------
    # ICONES
    # -------------------------------------------------------

    @property
    def icon(self):
        """
        Si la Freebox fournit une icône → on l'utilise via entity_picture (None ici).
        Sinon → on met une icône MDI intelligente.
        """
        if self._p("profile_icon"):
            return None  # entity_picture fera le boulot

        return (
            "mdi:account-lock"
            if self._p("current_mode") == "denied"
            else "mdi:account-check"
        )

    @property
    def entity_picture(self):
        """
        Utilisation de l’icône native Freebox Ultra.
        Exemple: /resources/images/profile/profile_12.png
        """
        icon_path = self._p("profile_icon")
        if not icon_path:
            return None

        # construction URL complète HTTPS
        return f"https://{self.api.host}:{self.api.port}{icon_path}"

    # -------------------------------------------------------
    # ATTRIBUTS ENRICHIS
    # -------------------------------------------------------

    @property
