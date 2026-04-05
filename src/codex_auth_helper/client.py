from __future__ import annotations as _annotations

import httpx
from openai import AsyncOpenAI, Omit
from typing_extensions import override

from .auth import CodexAuthConfig, CodexAuthStore, CodexTokenManager

__all__ = ("CodexAsyncOpenAI", "create_codex_async_openai")


class CodexAsyncOpenAI(AsyncOpenAI):
    def __init__(
        self,
        *,
        base_url: str,
        http_client: httpx.AsyncClient,
        token_manager: CodexTokenManager,
    ) -> None:
        self.token_manager = token_manager
        super().__init__(
            api_key=token_manager.get_access_token,
            base_url=base_url,
            http_client=http_client,
        )

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        headers = dict(super().default_headers)
        account_id = self.token_manager.current_account_id
        if account_id is not None:
            headers["ChatGPT-Account-Id"] = account_id
        return headers


def create_codex_async_openai(
    *,
    config: CodexAuthConfig | None = None,
    http_client: httpx.AsyncClient | None = None,
) -> CodexAsyncOpenAI:
    resolved_config = config or CodexAuthConfig()
    owns_http_client = http_client is None
    resolved_http_client = http_client or httpx.AsyncClient(
        follow_redirects=True,
        timeout=resolved_config.timeout_seconds,
    )
    token_manager = CodexTokenManager(
        config=resolved_config,
        store=CodexAuthStore(resolved_config.auth_path),
        http_client=resolved_http_client,
        owns_http_client=owns_http_client,
    )
    return CodexAsyncOpenAI(
        base_url=resolved_config.api_base_url,
        http_client=resolved_http_client,
        token_manager=token_manager,
    )
