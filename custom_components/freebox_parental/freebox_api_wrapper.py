from freebox_api.api import Freebox
import logging

_LOGGER = logging.getLogger(__name__)

class FreeboxAPIWrapper:
    def __init__(self, host):
        self.fbx = Freebox(host=host)

    async def login(self):
        await self.fbx.login()

    async def get_profiles(self):
        return await self.fbx.parental.get_filters()

    async def pause_profile(self, profile_id: int):
        await self.fbx.parental.set_filter(profile_id=profile_id, forced=True, forced_mode="denied")

    async def resume_profile(self, profile_id: int):
        await self.fbx.parental.set_filter(profile_id=profile_id, forced=False)