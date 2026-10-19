"""Exercise the real provider without network access or a running server."""
import os
from pathlib import Path
import sys
import httpx
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from mock_provider import main

@pytest.fixture(autouse=True)
def provider_http(monkeypatch):
    main.ACTIVE_VERSION = os.getenv("API_VERSION", "v2")
    main.request_logs.clear()
    with TestClient(main.app) as provider:
        def convert(response):
            # This environment's TestClient uses httpx2; services use httpx.
            # Preserve the real HTTP body/status at that transport boundary.
            return httpx.Response(response.status_code, content=response.content,
                                  headers=response.headers,
                                  request=httpx.Request(response.request.method, str(response.request.url)))
        def post(url, **kwargs):
            return convert(provider.post(httpx.URL(url).raw_path.decode(), **{key: value for key, value in kwargs.items() if key != "timeout"}))
        def get(url, **kwargs):
            return convert(provider.get(httpx.URL(url).raw_path.decode(), **{key: value for key, value in kwargs.items() if key != "timeout"}))
        monkeypatch.setattr(httpx, "post", post)
        monkeypatch.setattr(httpx, "get", get)
        yield provider
