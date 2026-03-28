"""Unit tests for comparison engine."""
import pytest
from unittest.mock import MagicMock
from services.comparison_engine import compute_scores, estimate_minutes_saved, _price_spread


def make_result(**kwargs):
    r = MagicMock()
    r.status = kwargs.get("status", "COMPLETE")
    r.unit_price = kwargs.get("unit_price", None)
    r.shipping_days_min = kwargs.get("shipping_days_min", None)
    r.shipping_days_max = kwargs.get("shipping_days_max", None)
    r.availability = kwargs.get("availability", "In Stock")
    r.is_best_value = False
    r.is_fastest = False
    r.is_recommended = False
    r.composite_score = None
    return r


def test_compute_scores_tags_cheapest_as_best_value():
    results = [
        make_result(unit_price=5.00, shipping_days_max=3),
        make_result(unit_price=2.00, shipping_days_max=7),
        make_result(unit_price=3.50, shipping_days_max=5),
    ]
    scored = compute_scores(results)
    best_value = next(r for r in scored if r.is_best_value)
    assert best_value.unit_price == 2.00


def test_compute_scores_tags_fastest():
    results = [
        make_result(unit_price=5.00, shipping_days_max=10),
        make_result(unit_price=4.00, shipping_days_max=2),
        make_result(unit_price=3.00, shipping_days_max=7),
    ]
    scored = compute_scores(results)
    fastest = next(r for r in scored if r.is_fastest)
    assert fastest.shipping_days_max == 2


def test_compute_scores_single_result():
    results = [make_result(unit_price=3.00, shipping_days_max=5)]
    scored = compute_scores(results)
    assert scored[0].is_recommended is True
    assert scored[0].is_best_value is True
    assert scored[0].is_fastest is True


def test_compute_scores_empty_results():
    result = compute_scores([])
    assert result == []


def test_compute_scores_no_valid_results():
    results = [make_result(status="FAILED", unit_price=None)]
    scored = compute_scores(results)
    assert scored[0].is_recommended is False


def test_estimate_minutes_saved():
    assert estimate_minutes_saved(150) == 150
    assert estimate_minutes_saved(200) == 200


def test_price_spread_calculation():
    results = [
        make_result(unit_price=2.00),
        make_result(unit_price=3.00),
        make_result(unit_price=4.00),
    ]
    spread = _price_spread(results)
    assert spread == 100.0  # (4-2)/2 * 100


def test_price_spread_single_result():
    results = [make_result(unit_price=3.00)]
    spread = _price_spread(results)
    assert spread == 0.0
