"""
Comparison engine: scores quotes, tags winners, builds recommendation.
Pure Python — no AI needed here. Fast and predictable.
"""
from models.quote_result import QuoteResult


def compute_scores(results: list[QuoteResult]) -> list[QuoteResult]:
    """
    Score each result and tag Best Value, Fastest, and Recommended.

    Scoring weights:
    - Price:        50% (lower is better)
    - Speed:        30% (fewer days = better)
    - Availability: 20% (in stock = full score)
    """
    valid = [r for r in results if r.status == "COMPLETE" and r.unit_price is not None]

    if not valid:
        return results

    # Normalise price (0–1, lower is better)
    prices = [r.unit_price for r in valid]
    min_price, max_price = min(prices), max(prices)
    price_range = max_price - min_price or 1

    # Normalise speed (0–1, fewer days is better)
    speeds = [r.shipping_days_max or r.shipping_days_min or 99 for r in valid]
    min_speed, max_speed = min(speeds), max(speeds)
    speed_range = max_speed - min_speed or 1

    for r in valid:
        price_score = 1 - (r.unit_price - min_price) / price_range
        days = r.shipping_days_max or r.shipping_days_min or 99
        speed_score = 1 - (days - min_speed) / speed_range
        avail_score = 1.0 if r.availability and "stock" in r.availability.lower() else 0.4
        r.composite_score = round(
            (price_score * 0.5) + (speed_score * 0.3) + (avail_score * 0.2), 4
        )

    # Tag Best Value (cheapest unit price)
    cheapest = min(valid, key=lambda r: r.unit_price)
    cheapest.is_best_value = True

    # Tag Fastest (lowest shipping days)
    fastest = min(valid, key=lambda r: r.shipping_days_max or r.shipping_days_min or 99)
    fastest.is_fastest = True

    # Tag Recommended (highest composite score)
    recommended = max(valid, key=lambda r: r.composite_score or 0)
    recommended.is_recommended = True

    return results


def estimate_minutes_saved(human_benchmark_minutes: int = 150) -> int:
    """
    Return estimated human minutes saved per quote job.
    Hardcoded benchmark: manual quote hunt = 150 minutes.
    """
    return human_benchmark_minutes


def build_comparison_summary(results: list[QuoteResult]) -> dict:
    """Build a summary dict for the frontend dashboard."""
    valid = [r for r in results if r.status == "COMPLETE" and r.unit_price is not None]
    if not valid:
        return {}

    recommended = next((r for r in valid if r.is_recommended), valid[0])
    return {
        "winner_supplier": recommended.supplier_name,
        "winner_price": recommended.unit_price,
        "winner_currency": recommended.currency,
        "price_spread_pct": _price_spread(valid),
        "total_valid_quotes": len(valid),
    }


def _price_spread(results: list[QuoteResult]) -> float:
    if len(results) < 2:
        return 0.0
    prices = [r.unit_price for r in results if r.unit_price]
    if not prices:
        return 0.0
    return round((max(prices) - min(prices)) / min(prices) * 100, 1)
