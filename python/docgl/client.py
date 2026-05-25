from __future__ import annotations

from typing import Any, Optional

import httpx

from .types import (
    GenerateRequest,
    GenerateResponse,
    JobStatusResponse,
)

DEFAULT_BASE_URL = "https://api.docgl.com"


class DocglError(Exception):
    """Raised when the Docgl API returns a non-2xx response."""

    def __init__(self, status_code: int, body: Any) -> None:
        self.status_code = status_code
        self.body = body
        super().__init__(f"Docgl API error {status_code}: {body}")


def _raise_for_status(response: httpx.Response) -> None:
    if response.is_error:
        try:
            body = response.json()
        except Exception:
            body = response.text
        raise DocglError(response.status_code, body)


class DocglClient:
    """
    Synchronous Docgl API client.

    Example::

        from docgl import DocglClient, DocumentInput, GenerateRequest

        client = DocglClient("your-api-token")

        response = client.generate(
            GenerateRequest(
                documents=[
                    DocumentInput(
                        uuid="template-uuid",
                        filename="invoice.pdf",
                        data=[{"customer_name": "Acme Corp", "total": 1500}],
                    )
                ]
            )
        )

        job_id = response.queued[0].job_id
        status = client.get_status(job_id)
        print(status.status)  # "completed"
    """

    def __init__(
        self,
        token: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        if not token:
            raise ValueError("Docgl API token is required")
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {token}"},
            timeout=timeout,
        )

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        """
        Queue one or more documents for generation.

        The API responds immediately with ``202 Accepted``.
        Use :meth:`get_status` to poll each ``job_id``.
        """
        response = self._client.post(
            "/api/generate",
            json=request.to_dict(),
        )
        _raise_for_status(response)
        return GenerateResponse.from_dict(response.json())

    def get_status(self, job_id: str) -> JobStatusResponse:
        """
        Return the current status of a queued generation job.

        :param job_id: The ``job_id`` returned by :meth:`generate`.
        """
        response = self._client.get(f"/api/generate/{job_id}")
        _raise_for_status(response)
        return JobStatusResponse.from_dict(response.json())

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()

    def __enter__(self) -> "DocglClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncDocglClient:
    """
    Async Docgl API client (requires ``httpx``).

    Example::

        import asyncio
        from docgl import AsyncDocglClient, DocumentInput, GenerateRequest

        async def main():
            async with AsyncDocglClient("your-api-token") as client:
                response = await client.generate(
                    GenerateRequest(
                        documents=[
                            DocumentInput(
                                uuid="template-uuid",
                                filename="invoice.pdf",
                                data=[{"customer_name": "Acme Corp"}],
                            )
                        ]
                    )
                )
                status = await client.get_status(response.queued[0].job_id)
                print(status.status)

        asyncio.run(main())
    """

    def __init__(
        self,
        token: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        if not token:
            raise ValueError("Docgl API token is required")
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {token}"},
            timeout=timeout,
        )

    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        """Async version of :meth:`DocglClient.generate`."""
        response = await self._client.post(
            "/api/generate",
            json=request.to_dict(),
        )
        _raise_for_status(response)
        return GenerateResponse.from_dict(response.json())

    async def get_status(self, job_id: str) -> JobStatusResponse:
        """Async version of :meth:`DocglClient.get_status`."""
        response = await self._client.get(f"/api/generate/{job_id}")
        _raise_for_status(response)
        return JobStatusResponse.from_dict(response.json())

    async def aclose(self) -> None:
        """Close the underlying async HTTP connection pool."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncDocglClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()
