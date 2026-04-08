from __future__ import annotations

from typing import Optional

import httpx

from models import SocAction, SocState, SocStepResult


class SocGuardianClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "SocGuardianClient":
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def reset(self, task_name: str, seed: int = 7) -> SocStepResult:
        response = await self._request("post", "/reset", json={"task_name": task_name, "seed": seed})
        return SocStepResult.model_validate(response.json())

    async def step(self, action: SocAction) -> SocStepResult:
        response = await self._request("post", "/step", json=action.model_dump())
        return SocStepResult.model_validate(response.json())

    async def state(self) -> SocState:
        response = await self._request("get", "/state")
        return SocState.model_validate(response.json())

    async def close(self) -> None:
        await self._request("post", "/close")

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
        response = await self._client.request(method, path, **kwargs)
        response.raise_for_status()
        return response
