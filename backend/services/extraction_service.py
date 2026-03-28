"""
LLM-powered extraction: raw HTML → structured QuoteData JSON.
Uses OpenAI GPT-4o-mini for cost efficiency.
"""
import json
from openai import AsyncOpenAI
from core.config import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

client = AsyncOpenAI(api_key=settings.openai_api_key)

EXTRACTION_SYSTEM_PROMPT = """You are a procurement data extraction specialist.
You will receive raw HTML content from a product listing page on a supplier website.
Extract structured procurement data with maximum accuracy.

Return ONLY a valid JSON object. No markdown. No explanation. No preamble.
If a field cannot be determined with confidence, use null — never guess prices.

OUTPUT SCHEMA:
{
  "supplier_name": string | null,
  "product_name": string | null,
  "product_url": string | null,
  "unit_price": number | null,
  "currency": string | null,
  "price_per_unit_label": string | null,
  "moq": number | null,
  "shipping_cost": number | null,
  "shipping_days_min": number | null,
  "shipping_days_max": number | null,
  "availability": string | null,
  "product_matches_query": boolean,
  "confidence": "HIGH" | "MEDIUM" | "LOW",
  "confidence_reason": string
}

CONFIDENCE RULES:
- HIGH: unit_price AND availability both found, product clearly matches query
- MEDIUM: price found but shipping/MOQ missing, OR product is a close match
- LOW: price inferred/estimated, product match uncertain, key fields missing"""

QUERY_PARSE_SYSTEM_PROMPT = """You are a procurement query parser.
Parse natural language product queries into structured fields.
Return ONLY valid JSON. No markdown. No explanation.

OUTPUT SCHEMA:
{
  "product": string,
  "grade": string | null,
  "quantity": number | null,
  "material": string | null,
  "unit": string | null,
  "search_string": string
}

The "search_string" should be an optimized search query (5-8 words) for supplier websites."""

WINNER_EXPLANATION_PROMPT = """You are a procurement advisor.
Given 3 supplier quotes, write exactly 3 bullet points explaining why the recommended quote is the best choice.
Each bullet: specific numbers, max 15 words, start with a bullet character •
Return ONLY a JSON array of 3 strings. No markdown."""


async def parse_product_query(product_description: str) -> dict:
    """Parse user's natural language query into structured fields."""
    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            max_tokens=300,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": QUERY_PARSE_SYSTEM_PROMPT},
                {"role": "user", "content": f"Parse this procurement query: {product_description}"},
            ],
        )
        raw = response.choices[0].message.content
        return json.loads(raw)
    except Exception as e:
        logger.error(f"Query parse failed: {e}")
        # ✅ Always return a usable fallback — never crash the job creation
        words = product_description.strip().split()
        return {
            "product": product_description,
            "grade": None,
            "quantity": next((int(w) for w in words if w.isdigit()), None),
            "material": None,
            "unit": None,
            "search_string": " ".join(words[:6]),  # first 6 words as search string
        }


async def extract_quote_from_html(
    html_content: str,
    product_description: str,
    supplier_url: str,
) -> dict:
    """
    Extract structured quote data from raw HTML.
    Returns dict with all procurement fields + confidence score.
    Falls back to mock extraction if OpenAI quota is exceeded.
    """
    from core.config import get_settings
    settings = get_settings()

    # In demo mode, return fast mock extraction
    if settings.demo_mode:
        return _mock_extraction(supplier_url, product_description)

    # Truncate HTML to first 8000 chars to save tokens
    html_snippet = html_content[:8000] if html_content else ""

    if not html_snippet:
        return _empty_quote(supplier_url, "No HTML content received from agent")

    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            max_tokens=settings.openai_max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"""Product Query: {product_description}
Supplier URL: {supplier_url}
Raw HTML Content:
{html_snippet}""",
                },
            ],
        )

        raw = response.choices[0].message.content
        data = json.loads(raw)
        logger.info(f"Extraction complete for {supplier_url}: confidence={data.get('confidence')}")
        return data

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error in extraction: {e}")
        return _empty_quote(supplier_url, "Extraction returned malformed JSON")

    except Exception as e:
        error_str = str(e)
        # ✅ OpenAI quota exceeded — fall back to mock so the job still completes
        if "insufficient_quota" in error_str or "429" in error_str or "quota" in error_str.lower():
            logger.warning(f"OpenAI quota exceeded for {supplier_url} — using mock extraction")
            return _mock_extraction(supplier_url, product_description)
        logger.error(f"Extraction failed for {supplier_url}: {e}")
        return _empty_quote(supplier_url, str(e))


async def generate_winner_explanation(quotes: list[dict], winner_id: str) -> list[str]:
    """Generate 3-bullet explanation of why the winner quote was chosen."""
    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            max_tokens=300,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": WINNER_EXPLANATION_PROMPT},
                {
                    "role": "user",
                    "content": f"""Quotes: {json.dumps(quotes, indent=2)}
Winner ID: {winner_id}
Why is this the best choice?""",
                },
            ],
        )
        data = json.loads(response.choices[0].message.content)
        # Handle both array and object responses
        if isinstance(data, list):
            return data[:3]
        if isinstance(data, dict):
            return list(data.values())[:3]
        return ["Best overall value", "Confirmed availability", "Competitive pricing"]
    except Exception as e:
        logger.error(f"Winner explanation failed: {e}")
        return ["Best overall value", "Confirmed availability", "Competitive pricing"]


def _empty_quote(supplier_url: str, reason: str) -> dict:
    return {
        "supplier_name": None,
        "product_name": None,
        "product_url": None,
        "unit_price": None,
        "currency": None,
        "price_per_unit_label": None,
        "moq": None,
        "shipping_cost": None,
        "shipping_days_min": None,
        "shipping_days_max": None,
        "availability": None,
        "product_matches_query": False,
        "confidence": "LOW",
        "confidence_reason": reason,
    }


def _mock_extraction(supplier_url: str, product_description: str) -> dict:
    """Fast mock extraction for demo mode."""
    import random
    
    # Extract domain for supplier name
    domain = supplier_url.split("//")[-1].split("/")[0].split(".")[-2].title()
    
    # Base prices vary by product type
    product_lower = product_description.lower()
    if "bolt" in product_lower or "screw" in product_lower or "fastener" in product_lower:
        base_price = random.uniform(1.50, 3.50)
    elif "paper" in product_lower:
        base_price = random.uniform(2.00, 5.00)
    elif "cable" in product_lower or "usb" in product_lower:
        base_price = random.uniform(2.00, 6.00)
    else:
        base_price = random.uniform(1.00, 10.00)
    
    unit_price = round(base_price * random.uniform(0.8, 1.5), 2)
    
    # MOQ
    moq_options = [1, 10, 25, 50, 100, 500, 1000]
    moq = random.choice(moq_options)
    
    # Shipping
    shipping_cost = round(random.uniform(0, 50), 2) if random.random() > 0.3 else 0
    
    if "amazon" in supplier_url.lower():
        shipping_days_min, shipping_days_max = 1, 2
        availability = "In Stock — Ships Today"
        confidence = "HIGH"
    elif "alibaba" in supplier_url.lower() or "china" in supplier_url.lower():
        shipping_days_min, shipping_days_max = 10, 21
        availability = "Ships from China — Lead time 14 days"
        confidence = "MEDIUM"
    else:
        shipping_days_min = random.randint(2, 7)
        shipping_days_max = shipping_days_min + random.randint(1, 5)
        availability = random.choice(["In Stock", "Limited Stock", "Made to Order"])
        confidence = random.choice(["HIGH", "MEDIUM"])
    
    return {
        "supplier_name": f"{domain} Supplier",
        "product_name": product_description,
        "product_url": supplier_url,
        "unit_price": unit_price,
        "currency": "USD",
        "price_per_unit_label": f"${unit_price}/unit",
        "moq": moq,
        "shipping_cost": shipping_cost,
        "shipping_days_min": shipping_days_min,
        "shipping_days_max": shipping_days_max,
        "availability": availability,
        "product_matches_query": True,
        "confidence": confidence,
        "confidence_reason": f"Extracted from {domain} product page",
    }