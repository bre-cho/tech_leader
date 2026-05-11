"""Tests for production hardening changes:
- P2: production guards in config
- P5: Canva polling (multi-poll until ready)
- P10: pre-flight billing quota in generate endpoint
- P4: export manifest includes real provider URLs
"""

import asyncio
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import apps.api.main as main_module
import apps.worker.celery_app as worker_module
from apps.api.core.config import Settings
from apps.api.core.config import settings
from apps.api.db.session import Base, get_db
from packages.export_engine.exporter import export_variant_pack, _is_real_url

# ---------------------------------------------------------------------------
# P2 – Production guards
# ---------------------------------------------------------------------------

def test_production_guard_rejects_mock_adobe():
    with pytest.raises(ValueError, match="ADOBE_MODE cannot be 'mock' in production"):
        Settings(
            app_env="production",
            adobe_mode="mock",
            canva_mode="production",
            auth_jwt_secret="strong-secret-xyz",
            dev_internal_token_secret="strong-dev-secret",
            database_url="postgresql://user:pass@host/db",
        )


def test_production_guard_rejects_mock_canva():
    with pytest.raises(ValueError, match="CANVA_MODE cannot be 'mock' in production"):
        Settings(
            app_env="production",
            adobe_mode="production",
            canva_mode="mock",
            auth_jwt_secret="strong-secret-xyz",
            dev_internal_token_secret="strong-dev-secret",
            database_url="postgresql://user:pass@host/db",
        )


def test_production_guard_rejects_weak_jwt_secret():
    with pytest.raises(ValueError, match="AUTH_JWT_SECRET must be changed"):
        Settings(
            app_env="production",
            adobe_mode="production",
            canva_mode="production",
            auth_jwt_secret="change-me",
            dev_internal_token_secret="strong-dev-secret",
            database_url="postgresql://user:pass@host/db",
        )


def test_production_guard_rejects_sqlite():
    with pytest.raises(ValueError, match="SQLite"):
        Settings(
            app_env="production",
            adobe_mode="production",
            canva_mode="production",
            auth_jwt_secret="strong-secret-xyz",
            dev_internal_token_secret="strong-dev-secret",
            database_url="sqlite:///./poster_engine.db",
        )


def test_production_guard_passes_for_local():
    # Local env should not trigger any guard.
    s = Settings(app_env="local")
    assert s.app_env == "local"


# ---------------------------------------------------------------------------
# P5 – Canva polling (multi-poll until job is ready)
# ---------------------------------------------------------------------------

from collections import defaultdict
import packages.provider_adapters.canva as canva_module
from packages.provider_adapters.canva import CanvaProductionAdapter
from packages.provider_adapters.base import ProviderError


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class _FakeAsyncHttpClient:
    """Async context manager that simulates httpx.AsyncClient for Canva/Adobe adapter tests."""

    def __init__(self, routes: dict, calls: list):
        self.routes = routes
        self.calls = calls

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url: str, headers: dict | None = None, json: dict | None = None):
        self.calls.append({"method": "POST", "url": url})
        key = ("POST", url)
        return self.routes[key].pop(0)

    async def get(self, url: str, headers: dict | None = None):
        self.calls.append({"method": "GET", "url": url})
        key = ("GET", url)
        return self.routes[key].pop(0)


class _ClientFactory:
    def __init__(self, routes: dict):
        self.routes = defaultdict(list)
        for key, responses in routes.items():
            self.routes[key].extend(responses)
        self.calls: list[dict] = []

    def __call__(self, *args, **kwargs):
        return _FakeAsyncHttpClient(self.routes, self.calls)


def test_canva_polls_multiple_times_until_ready(monkeypatch):
    """Canva adapter must retry polling when the job is not yet complete."""
    base_url = "https://canva.test"
    # First poll returns no design_id/export_url (job still pending),
    # second poll returns completed job.
    routes = {
        ("POST", f"{base_url}/rest/v1/autofills"): [
            _FakeResponse(200, {"job_id": "job_multi"}),
        ],
        ("GET", f"{base_url}/rest/v1/autofills/job_multi"): [
            _FakeResponse(200, {}),  # pending – no design_id yet
            _FakeResponse(
                200,
                {
                    "design_id": "design_multi",
                    "exports": [{"url": "https://cdn.canva.test/multi.png"}],
                    "template_id": "tpl_1",
                    "brand_id": "brand_1",
                },
            ),
        ],
    }
    factory = _ClientFactory(routes)
    monkeypatch.setattr(canva_module.httpx, "AsyncClient", factory)
    # Prevent real async sleeps between polls.
    async def _no_sleep(_): pass
    monkeypatch.setattr(canva_module.asyncio, "sleep", _no_sleep)

    adapter = CanvaProductionAdapter(access_token="token", base_url=base_url)
    result = adapter.create_layout(
        {
            "prompt": "product dominates with CTA button",
            "offer": "Deal",
            "brand": "Demo",
            "brand_id": "brand_1",
            "template_id": "tpl_1",
        }
    )

    assert result["canva_design_id"] == "design_multi"
    assert result["export_url"] == "https://cdn.canva.test/multi.png"
    poll_calls = [c for c in factory.calls if c["method"] == "GET"]
    assert len(poll_calls) == 2, "Expected exactly 2 poll attempts"


def test_canva_raises_on_polling_timeout(monkeypatch):
    """Canva adapter raises ProviderError when max polls exhausted."""
    base_url = "https://canva.test"
    routes = {
        ("POST", f"{base_url}/rest/v1/autofills"): [
            _FakeResponse(200, {"job_id": "job_timeout"}),
        ],
        # Return pending responses up to max_attempts times.
        ("GET", f"{base_url}/rest/v1/autofills/job_timeout"): [
            _FakeResponse(200, {}) for _ in range(50)
        ],
    }
    factory = _ClientFactory(routes)
    monkeypatch.setattr(canva_module.httpx, "AsyncClient", factory)
    async def _no_sleep(_): pass
    monkeypatch.setattr(canva_module.asyncio, "sleep", _no_sleep)

    # Pass poll_max_attempts directly to the adapter rather than mutating the
    # global settings object (avoids potential Pydantic v2 immutability issues).
    adapter = CanvaProductionAdapter(access_token="token", base_url=base_url, poll_max_attempts=3)
    with pytest.raises(ProviderError) as err:
        adapter.create_layout(
            {
                "prompt": "product dominates with CTA button",
                "offer": "Deal",
                "brand": "Demo",
                "brand_id": "brand_1",
                "template_id": "tpl_1",
            }
        )
    assert err.value.error_code == "PROVIDER_DOWN"
    assert "timeout" in err.value.message.lower()


# ---------------------------------------------------------------------------
# P4 – _is_real_url helper
# ---------------------------------------------------------------------------

def test_is_real_url_rejects_mock_schemes():
    assert not _is_real_url("mock://adobe/abc.png")
    assert not _is_real_url("file:///data/exports/abc.txt")
    assert not _is_real_url(None)
    assert not _is_real_url("")


def test_is_real_url_accepts_https():
    assert _is_real_url("https://cdn.adobe.io/generated/abc.png")
    assert _is_real_url("https://cdn.canva.test/export.png")


def test_export_manifest_includes_real_urls(tmp_path: Path):
    settings.storage_provider = "local"

    result = export_variant_pack(
        str(tmp_path),
        {
            "id": "var_real",
            "brand_id": "brand_1",
            "project_id": "proj_1",
            "provider": "adobe+canva",
            "canva_design_id": "canva_1",
            "adobe_asset_id": "adobe_1",
            "image_url": "https://img.adobe.io/generated/abc.png",
            "export_url": "https://cdn.canva.test/export.png",
        },
    )

    poster_asset = next(a for a in result["manifest"]["assets"] if a["name"] == "poster_4x5.txt")
    assert poster_asset["source_image_url"] == "https://img.adobe.io/generated/abc.png"
    assert poster_asset["source_export_url"] == "https://cdn.canva.test/export.png"


def test_export_manifest_no_real_urls_when_mock(tmp_path: Path):
    settings.storage_provider = "local"

    result = export_variant_pack(
        str(tmp_path),
        {
            "id": "var_mock",
            "brand_id": "brand_1",
            "project_id": "proj_1",
            "provider": "adobe_mock+canva_mock",
            "canva_design_id": "canva_mock_abc",
            "adobe_asset_id": "adobe_mock_abc",
            "image_url": "mock://adobe/abc.png",
            "export_url": "mock://canva/abc.pdf",
        },
    )

    poster_asset = next(a for a in result["manifest"]["assets"] if a["name"] == "poster_4x5.txt")
    assert "source_image_url" not in poster_asset
    assert "source_export_url" not in poster_asset


# ---------------------------------------------------------------------------
# P10 – Pre-flight billing quota check in generate endpoint
# ---------------------------------------------------------------------------

class _InMemoryRedis:
    def __init__(self):
        self.store: dict[str, str] = {}

    def get(self, key: str):
        return self.store.get(key)

    def setex(self, key: str, _ttl: int, value):
        if not isinstance(value, str):
            value = json.dumps(value) if isinstance(value, dict) else str(value)
        self.store[key] = value


def _make_client_with_db(monkeypatch, tmp_path):
    """Helper: create an in-memory DB TestClient with all infra monkeypatched."""
    settings.app_env = "local"
    settings.auth_jwt_secret = "billing-test-secret"
    settings.auth_jwt_algorithm = "HS256"
    settings.dev_internal_token_secret = "billing-dev-secret"
    settings.storage_provider = "local"
    settings.storage_dir = str(tmp_path / "storage")
    settings.adobe_mode = "mock"
    settings.canva_mode = "mock"

    db_path = tmp_path / "billing.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    fake_redis = _InMemoryRedis()

    def immediate_delay(**kwargs):
        return worker_module.generate_project_job(**kwargs)

    monkeypatch.setattr(main_module, "_run_migrations", lambda: None)
    monkeypatch.setattr(main_module, "_redis", lambda: fake_redis)
    monkeypatch.setattr(worker_module, "_redis", lambda: fake_redis)
    monkeypatch.setattr(worker_module, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(main_module.generate_project_job, "delay", immediate_delay)
    main_module.app.dependency_overrides[get_db] = override_get_db

    return TestClient(main_module.app), TestingSessionLocal


def test_generate_blocked_when_quota_exceeded(monkeypatch, tmp_path: Path):
    client, TestingSessionLocal = _make_client_with_db(monkeypatch, tmp_path)
    # Set a very low quota so the first generate attempt exceeds it.
    monkeypatch.setattr(settings, "billing_default_quota_per_month", 0)

    try:
        token_res = client.post(
            "/internal/dev/token",
            json={"user_id": "quota-user", "expires_in_seconds": 3600},
            headers={"x-dev-internal-secret": settings.dev_internal_token_secret},
        )
        assert token_res.status_code == 200
        auth_headers = {"Authorization": f"Bearer {token_res.json()['access_token']}"}

        brand_res = client.post("/api/v1/brands", json={"name": "Quota Brand"}, headers=auth_headers)
        assert brand_res.status_code == 200

        project_res = client.post(
            "/api/v1/projects",
            json={"brand_id": brand_res.json()["id"], "product_name": "Quota Product"},
            headers=auth_headers,
        )
        assert project_res.status_code == 200
        project_id = project_res.json()["id"]

        generate_res = client.post(f"/api/v1/projects/{project_id}/generate", headers=auth_headers)
        assert generate_res.status_code == 402
        assert "quota" in generate_res.json()["detail"].lower()
    finally:
        main_module.app.dependency_overrides.clear()
