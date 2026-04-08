from __future__ import annotations

from models import SocAction, SocState, SocStepResult
from simulator import SocGuardianEnv


class EnvironmentService:
    def __init__(self) -> None:
        self._env: SocGuardianEnv | None = None

    async def reset(self, task_name: str, seed: int) -> SocStepResult:
        self._env = SocGuardianEnv(task_name=task_name, seed=seed)
        return await self._env.reset()

    async def step(self, action: SocAction) -> SocStepResult:
        if self._env is None:
            raise RuntimeError("Environment not initialized. Call reset first.")
        return await self._env.step(action)

    async def state(self) -> SocState:
        if self._env is None:
            raise RuntimeError("Environment not initialized. Call reset first.")
        return await self._env.state()

    async def close(self) -> None:
        if self._env is not None:
            await self._env.close()
        self._env = None
