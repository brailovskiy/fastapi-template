from types import TracebackType
from typing import Any

import loguru
from httpx import URL, AsyncClient, Response

logger = loguru.logger


class HTTPClient:
    async def __aenter__(self) -> "HTTPClient":
        self.client = AsyncClient()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.client.aclose()

    async def _log_response(
        self,
        method: str,
        request_url: URL,
        params: dict[str, Any] | None,
        response: Response,
        api_name: str,
    ) -> None:
        total_seconds = response.elapsed.total_seconds()
        logger.info(
            "response from {api_name} api for request {method} {request_url}{params} "
            "=> {status_code} {content} {total_seconds}",
            api_name=api_name,
            method=method,
            request_url=request_url,
            params=params,
            status_code=response.status_code,
            content=response.content,
            total_seconds=total_seconds,
        )
        if total_seconds > 5:  # pragma: no cover
            logger.error(
                "response to {api_name} took too long {total_seconds}, {method} {request_url}{params} "
                "=> {status_code} {content}",
                api_name=api_name,
                method=method,
                request_url=request_url,
                params=params,
                status_code=response.status_code,
                content=response.content,
                total_seconds=total_seconds,
            )

    async def make_request(
        self,
        route: str,
        api_url: str,
        api_name: str,
        method: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Response:
        request_url = URL(api_url).join(route)
        logger.info("request to %s api: %s %s %s", api_name, method, request_url, params)
        response = await self.client.request(method, request_url, params=params, data=data, json=json, timeout=10.0)
        await self._log_response(method, request_url, params, response, api_name)
        return response
