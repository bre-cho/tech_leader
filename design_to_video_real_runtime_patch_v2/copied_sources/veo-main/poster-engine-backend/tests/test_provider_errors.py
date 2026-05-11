from packages.provider_adapters.base import ProviderError


def test_provider_error_contract():
    err = ProviderError("adobe", "RATE_LIMIT", retryable=True, message="Too many requests")
    payload = err.to_dict()
    assert payload == {
        "provider": "adobe",
        "error_code": "RATE_LIMIT",
        "retryable": True,
        "message": "Too many requests",
    }


# C6: Mock adapter async tests ─────────────────────────────────────────────────
# Note: These tests use asyncio.run() to call async methods from synchronous
# pytest functions.  This is the correct approach for our setup (plain pytest,
# no pytest-asyncio).  asyncio.run() creates a fresh event loop per call so
# there is no conflict with the test framework.

import asyncio
from packages.provider_adapters.adobe import AdobeMockAdapter
from packages.provider_adapters.canva import CanvaMockAdapter


def test_adobe_mock_adapter_sync():
    """AdobeMockAdapter.generate_visual returns a deterministic mock result."""
    adapter = AdobeMockAdapter()
    result = adapter.generate_visual("Product hero", {"brand": "Test"})
    assert result["provider"] == "adobe_mock"
    assert result["adobe_asset_id"].startswith("adobe_mock_")
    assert result["image_url"].startswith("mock://adobe/")
    assert result["metadata"]["mode"] == "mock"


def test_adobe_mock_adapter_async():
    """AdobeMockAdapter.generate_visual_async returns the same result as sync."""
    adapter = AdobeMockAdapter()
    sync_result = adapter.generate_visual("Product hero", {"brand": "Test"})
    async_result = asyncio.run(adapter.generate_visual_async("Product hero", {"brand": "Test"}))
    assert async_result["provider"] == sync_result["provider"]
    assert async_result["adobe_asset_id"] == sync_result["adobe_asset_id"]
    assert async_result["image_url"] == sync_result["image_url"]
    assert async_result["metadata"]["mode"] == "mock"


def test_adobe_mock_adapter_deterministic():
    """Same prompt always produces the same mock asset id."""
    adapter = AdobeMockAdapter()
    r1 = adapter.generate_visual("Prompt A")
    r2 = adapter.generate_visual("Prompt A")
    r3 = adapter.generate_visual("Prompt B")
    assert r1["adobe_asset_id"] == r2["adobe_asset_id"]
    assert r1["adobe_asset_id"] != r3["adobe_asset_id"]


def test_canva_mock_adapter_sync():
    """CanvaMockAdapter.create_layout returns a deterministic mock result."""
    adapter = CanvaMockAdapter()
    payload = {"prompt": "Layout prompt", "template_id": "tpl_1"}
    result = adapter.create_layout(payload)
    assert result["provider"] == "canva_mock"
    assert result["canva_design_id"].startswith("canva_mock_")
    assert result["export_url"].startswith("mock://canva/")
    assert result["metadata"]["mode"] == "mock"


def test_canva_mock_adapter_async():
    """CanvaMockAdapter.create_layout_async returns the same result as sync."""
    adapter = CanvaMockAdapter()
    payload = {"prompt": "Layout prompt", "template_id": "tpl_1"}
    sync_result = adapter.create_layout(payload)
    async_result = asyncio.run(adapter.create_layout_async(payload))
    assert async_result["provider"] == sync_result["provider"]
    assert async_result["canva_design_id"] == sync_result["canva_design_id"]
    assert async_result["export_url"] == sync_result["export_url"]
    assert async_result["metadata"]["mode"] == "mock"


def test_canva_mock_adapter_deterministic():
    """Same payload always produces the same mock design id."""
    adapter = CanvaMockAdapter()
    payload = {"prompt": "Same", "template_id": "tpl_x"}
    r1 = adapter.create_layout(payload)
    r2 = adapter.create_layout(payload)
    other = adapter.create_layout({"prompt": "Different"})
    assert r1["canva_design_id"] == r2["canva_design_id"]
    assert r1["canva_design_id"] != other["canva_design_id"]
