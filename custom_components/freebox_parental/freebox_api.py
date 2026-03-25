from aiofreepybox import Freepybox

class FreeboxAPI:
    def __init__(self, host):
        self._fbx = Freepybox(host)

    async def authorize(self):
        return await self._fbx.open()

    async def login(self):
        await self._fbx.open()

    async def get_profiles(self):
        return await self._fbx.parental.get_filters()

    async def pause_profile(self, profile_id):
        return await self._fbx.parental.set_filter(
            profile_id,
            {"forced": True, "forced_mode": "denied"}
        )

    async def resume_profile(self, profile_id):
        return await self._fbx.parental.set_filter(
            profile_id,
            {"forced": False}
        )