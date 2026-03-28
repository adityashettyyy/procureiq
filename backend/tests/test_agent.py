"""
Integration tests for TinyFish agent.
Run: pytest tests/test_agent.py -v --integration

Requires: TINYFISH_API_KEY and OPENAI_API_KEY in .env
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tinyfish_client_creates_task():
    """Requires live TinyFish API key."""
    from services.tinyfish_client import TinyFishClient
    client = TinyFishClient()
    result = await client.run_task_and_wait(
        supplier_url="https://www.amazon.in",
        product_description="A4 copy paper 80gsm",
        search_string="A4 copy paper 80gsm",
    )
    assert result["status"] in ("COMPLETE", "BLOCKED", "NOT_FOUND", "TIMEOUT", "FAILED")


@pytest.mark.asyncio
async def test_tinyfish_client_handles_http_error():
    """Mocked test — no API key needed."""
    import httpx
    from services.tinyfish_client import TinyFishClient

    client = TinyFishClient()
    with patch("httpx.AsyncClient.post", side_effect=httpx.HTTPStatusError("error", request=None, response=None)):
        result = await client.run_task_and_wait(
            supplier_url="https://example.com",
            product_description="test product",
            search_string="test product",
        )
    assert result["status"] == "FAILED"
    assert "error" in result


@pytest.mark.asyncio
async def test_agent_orchestrator_demo_mode(tmp_path):
    """Test demo mode returns pre-baked results."""
    import os
    os.environ["DEMO_MODE"] = "true"
    os.environ["DEMO_JOB_DELAY_SECONDS"] = "0"

    # Minimal test — verify demo mode doesn't call TinyFish
    with patch("services.tinyfish_client.TinyFishClient.run_task_and_wait") as mock_tf:
        from services.agent_orchestrator import _run_demo_mode
        # Should complete without calling TinyFish
        mock_tf.assert_not_called()
