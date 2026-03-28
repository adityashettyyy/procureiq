"""
TinyFish Web Agent API client — REAL implementation.
API: https://agent.tinyfish.ai/v1/automation/run-sse
Docs: https://docs.tinyfish.ai/llms.txt

Uses SSE (Server-Sent Events) streaming — single request, real-time progress.
Auth: X-API-Key header (NOT Bearer token).
"""
import asyncio
import json
import httpx
from core.config import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Real TinyFish endpoint
TINYFISH_SSE_URL = "https://agent.tinyfish.ai/v1/automation/run-sse"

AGENT_GOAL_TEMPLATE = """You are a procurement research agent. Find the best price for a specific product.

PRODUCT TO FIND: {search_string}
ORIGINAL QUERY: {product_description}

YOUR TASK:
1. Find the search bar on this website
2. Search for: "{search_string}"
3. Click on the most relevant product matching: {product_description}
4. Extract from the product page:
   - Unit price (look for bulk/wholesale pricing tables)
   - Minimum order quantity (MOQ)
   - Shipping cost
   - Estimated delivery time in days
   - Stock availability status
5. Return the complete HTML of the final product page

RULES:
- Do NOT add to cart or click Buy Now
- Do NOT fill any forms except the search bar
- If CAPTCHA or login wall appears, stop and report BLOCKED
- If product not found, report NOT_FOUND
- Maximum 45 seconds
"""


def _parse_tinyfish_result(result: dict) -> dict:
    """
    Parse TinyFish structured JSON result into our QuoteData schema.
    TinyFish returns: {product: {name, unit_price, availability, moq, shipping_delivery},
                       supplier: {name, location}, page_summary: str}
    """
    if not result or not isinstance(result, dict):
        return {}

    product = result.get("product") or {}
    supplier = result.get("supplier") or {}
    shipping = product.get("shipping_delivery") or {}

    # Parse price — "6 - 200 INR" or "₹45" or "USD 3.50" etc.
    unit_price = None
    currency = "INR"
    raw_price = str(product.get("unit_price") or "")
    if raw_price:
        import re
        # Detect currency
        if "USD" in raw_price or "$" in raw_price:
            currency = "USD"
        elif "INR" in raw_price or "₹" in raw_price or "Rs" in raw_price:
            currency = "INR"
        # Extract first number (lowest price in a range)
        nums = re.findall(r"[\d,]+\.?\d*", raw_price.replace(",", ""))
        if nums:
            try:
                unit_price = float(nums[0])
            except ValueError:
                pass

    # Parse MOQ
    moq = None
    raw_moq = str(product.get("minimum_order_quantity") or
                  product.get("moq") or
                  product.get("min_order") or "")
    if raw_moq:
        import re
        nums = re.findall(r"[\d,]+", raw_moq.replace(",", ""))
        if nums:
            try:
                moq = int(nums[0])
            except ValueError:
                pass

    # Parse delivery days
    shipping_days_min = None
    shipping_days_max = None
    raw_delivery = str(shipping.get("delivery_time") or
                       product.get("delivery_time") or
                       product.get("lead_time") or "")
    if raw_delivery:
        import re
        nums = re.findall(r"\d+", raw_delivery)
        if len(nums) >= 2:
            shipping_days_min = int(nums[0])
            shipping_days_max = int(nums[1])
        elif len(nums) == 1:
            shipping_days_min = int(nums[0])
            shipping_days_max = int(nums[0])

    # Availability
    availability = (product.get("availability") or
                    product.get("stock_status") or "Unknown")

    # Supplier name
    supplier_name = (supplier.get("name") or
                     supplier.get("company_name") or None)

    # Product name
    product_name = product.get("name") or product.get("title") or None

    # Confidence based on how much data we got
    fields_found = sum(1 for x in [unit_price, availability, moq, shipping_days_min] if x)
    if fields_found >= 3:
        confidence = "HIGH"
    elif fields_found >= 2:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return {
        "supplier_name": supplier_name,
        "product_name": product_name,
        "product_url": None,
        "unit_price": unit_price,
        "currency": currency,
        "price_per_unit_label": "per piece",
        "moq": moq,
        "shipping_cost": None,
        "shipping_days_min": shipping_days_min,
        "shipping_days_max": shipping_days_max,
        "availability": availability,
        "product_matches_query": True,
        "confidence": confidence,
        "confidence_reason": f"Extracted from TinyFish structured result. Fields found: {fields_found}/4",
    }


class TinyFishClient:
    def __init__(self):
        self.api_key = settings.tinyfish_api_key
        self.timeout = settings.agent_timeout_seconds

    async def run_task_and_wait(
        self,
        supplier_url: str,
        product_description: str,
        search_string: str,
        target_quantity: int = 100,
        on_step_callback=None,
    ) -> dict:
        """
        Run a TinyFish automation task using SSE streaming.
        Single request — streams progress events until COMPLETE.
        Returns: { status, html, steps, task_id, error }
        """
        goal = AGENT_GOAL_TEMPLATE.format(
            supplier_url=supplier_url,
            product_description=product_description,
            search_string=search_string,
            target_quantity=target_quantity,
        )

        payload = {
            "url": supplier_url,          # ← real field name
            "goal": goal,                 # ← real field name
            "browser_profile": "stealth", # ← helps bypass bot detection
        }

        headers = {
            "X-API-Key": self.api_key,    # ← real auth header
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }

        steps = []
        run_id = None
        html = ""

        try:
            logger.info(f"TinyFish SSE request → {supplier_url}")

            async with httpx.AsyncClient(timeout=self.timeout + 30) as client:
                async with client.stream(
                    "POST",
                    TINYFISH_SSE_URL,
                    headers=headers,
                    json=payload,
                ) as response:

                    if response.status_code != 200:
                        error_body = await response.aread()
                        error_text = error_body.decode()
                        logger.error(f"TinyFish HTTP {response.status_code}: {error_text}")
                        return {
                            "status": "FAILED",
                            "task_id": None,
                            "html": "",
                            "steps": [],
                            "error": f"HTTP {response.status_code}: {error_text[:200]}",
                        }

                    # Read SSE stream line by line
                    async for line in response.aiter_lines():
                        if not line.startswith("data:"):
                            continue

                        raw = line[5:].strip()
                        if not raw:
                            continue

                        try:
                            event = json.loads(raw)
                        except json.JSONDecodeError:
                            continue

                        event_type = event.get("type", "")

                        # ── STARTED ──────────────────────────
                        if event_type == "STARTED":
                            run_id = event.get("run_id")
                            logger.info(f"TinyFish run started: {run_id}")
                            if on_step_callback:
                                result = on_step_callback(f"Agent started (run_id: {run_id})")
                                if asyncio.iscoroutine(result):
                                    await result

                        # ── STREAMING_URL ─────────────────────
                        elif event_type == "STREAMING_URL":
                            streaming_url = event.get("streaming_url", "")
                            logger.info(f"Browser streaming at: {streaming_url}")
                            if on_step_callback:
                                result = on_step_callback("Browser session active")
                                if asyncio.iscoroutine(result):
                                    await result

                        # ── PROGRESS ──────────────────────────
                        elif event_type == "PROGRESS":
                            purpose = event.get("purpose", "")
                            if purpose:
                                steps.append(purpose)
                                logger.info(f"TinyFish progress: {purpose}")
                                if on_step_callback:
                                    await on_step_callback(purpose)

                        # ── HEARTBEAT ─────────────────────────
                        elif event_type == "HEARTBEAT":
                            pass  # keep-alive, ignore

                        # ── COMPLETE ──────────────────────────
                        elif event_type == "COMPLETE":
                            status = event.get("status", "FAILED").upper()
                            result = event.get("result") or {}
                            error = event.get("error") or ""

                            logger.info(f"TinyFish complete: {status} | run_id={run_id}")

                            if status == "COMPLETED":
                                # TinyFish returns structured JSON, not raw HTML
                                # Parse the structured result directly
                                structured = _parse_tinyfish_result(result)

                                # Also build a fake HTML snippet for the
                                # extraction service fallback (if needed)
                                html = json.dumps(result) if result else ""

                                return {
                                    "status": "COMPLETE",
                                    "task_id": run_id,
                                    "html": html,
                                    "steps": steps,
                                    "error": "",
                                    "raw_result": result,
                                    "structured": structured,
                                }
                            else:
                                # FAILED, CANCELLED, SITE_BLOCKED, etc.
                                mapped = {
                                    "FAILED": "FAILED",
                                    "CANCELLED": "FAILED",
                                    "SITE_BLOCKED": "BLOCKED",
                                    "TASK_FAILED": "FAILED",
                                    "MAX_STEPS_EXCEEDED": "TIMEOUT",
                                    "TIMEOUT": "TIMEOUT",
                                }.get(status, "FAILED")

                                return {
                                    "status": mapped,
                                    "task_id": run_id,
                                    "html": "",
                                    "steps": steps,
                                    "error": error or status,
                                }

            # Stream ended without COMPLETE event
            logger.warning(f"TinyFish stream ended without COMPLETE for {supplier_url}")
            return {
                "status": "FAILED",
                "task_id": run_id,
                "html": html,
                "steps": steps,
                "error": "Stream ended without completion event",
            }

        except httpx.TimeoutException:
            logger.error(f"TinyFish timeout for {supplier_url}")
            return {
                "status": "TIMEOUT",
                "task_id": run_id,
                "html": "",
                "steps": steps,
                "error": "Request timed out",
            }

        except Exception as e:
            logger.error(f"TinyFish unexpected error: {e}")
            return {
                "status": "FAILED",
                "task_id": None,
                "html": "",
                "steps": steps,
                "error": str(e),
            }


# Singleton
_client: TinyFishClient | None = None


def get_tinyfish_client() -> TinyFishClient:
    global _client
    if _client is None:
        _client = TinyFishClient()
    return _client