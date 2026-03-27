import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback

_LOGGER = logging.getLogger(__name__)

DOMAIN = "freebox_parental"


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
        return f"{self.api.base}{icon_path}"
    # -------------------------------------------------------
    # ATTRIBUTS ENRICHIS
    # -------------------------------------------------------

    @property
    def extra_state_attributes(self):
        p = self._profile()

        # Liste des noms d'appareils associés
        hosts = []
        for h in p.get("hosts", []):
            if "primary_name" in h:
                hosts.append(h["primary_name"])
            elif h.get("names"):
                hosts.append(h["names"][0]["name"])
            else:
                hosts.append(h["l2ident"]["id"])

        return {
            "macs": p.get("macs", []),
            "hosts": hosts,
            "override": p.get("override"),
            "override_mode": p.get("override_mode"),
            "current_mode": p.get("current_mode"),
            "rule_mode": p.get("rule_mode"),
            "next_change": p.get("next_change"),
            "resolution": p.get("resolution"),
            "profile_icon": p.get("profile_icon"),
        }

    # -------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------

    async def async_turn_off(self):
        """Couper Internet pour le profil."""
        await self.api.pause_profile(self.profile_id)
        await self._refresh()

    async def async_turn_on(self):
        """Autoriser Internet pour le profil."""
        await self.api.resume_profile(self.profile_id)
        await self._refresh()

    async def async_update(self):
        """Update triggered by HA - delegated to coordinator."""
        await self._refresh()

    @callback
    async def _refresh(self):
        await self.coordinator.async_request_refresh()

    # -------------------------------------------------------
    # UTILS
    # -------------------------------------------------------

    def _profile(self):
        """Shorthand."""
        return self.coordinator.data[self.profile_id]

    def _p(self, key):
        """Shorthand accès champ profil."""
        return self._profile().get(key)