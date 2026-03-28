"""
Unit tests for extraction service.
Run: pytest tests/test_extraction.py -v
"""
import pytest
import asyncio
from services.extraction_service import _empty_quote, parse_product_query


def test_empty_quote_structure():
    result = _empty_quote("https://example.com", "Test error")
    assert result["confidence"] == "LOW"
    assert result["unit_price"] is None
    assert result["confidence_reason"] == "Test error"
    assert result["product_matches_query"] is False


def test_empty_quote_has_all_fields():
    result = _empty_quote("https://example.com", "reason")
    required_fields = [
        "supplier_name", "product_name", "product_url", "unit_price",
        "currency", "moq", "shipping_cost", "shipping_days_min",
        "shipping_days_max", "availability", "confidence", "confidence_reason"
    ]
    for field in required_fields:
        assert field in result, f"Missing field: {field}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_parse_product_query_integration():
    """Requires OPENAI_API_KEY in environment."""
    result = await parse_product_query("500 units M8 hex bolts zinc plated")
    assert "search_string" in result
    assert result["search_string"]
    assert "product" in result
