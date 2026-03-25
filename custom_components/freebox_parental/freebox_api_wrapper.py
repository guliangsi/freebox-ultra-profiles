from freebox_api import Freebox
import logging

_LOGGER = logging.getLogger(__name__)

class FreeboxAPIWrapper:
    """Wrapper autour de freebox-api pour parental control."""

    def __init__(self, host):
        self.fbx = Freebox(host=host)

    async def login(self):
        """Login et validation écran Freebox si première fois."""
        try:
            await self.fbx.login()
        except Exception as e:
            _LOGGER.error("Erreur login Freebox: %s", e)
            raise

    async def get_profiles(self):
        """Retourne la liste des profils parental."""
        return await self.fbx.parental.get_filters()

    async def pause_profile(self, profile_id: int):
        """Pause un profil (internet denied)."""
        await self.fbx.parental.set_filter(
            profile_id=profile_id,
            forced=True,
            forced_mode="denied"
        )

    async def resume_profile(self, profile_id: int):
        """Reprend le profil (planning normal)."""
        await self.fbx.parental.set_filter(
            profile_id=profile_id,
            forced=False
        )