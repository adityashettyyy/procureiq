"""RFQ email generation using OpenAI."""
import json
from openai import AsyncOpenAI
from core.config import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)
client = AsyncOpenAI(api_key=settings.openai_api_key)

RFQ_SYSTEM_PROMPT = """You are a professional procurement officer writing a formal
Request for Quotation (RFQ) email to a supplier.
Write in professional business English. Be concise and specific.
Standard opening only — no excessive pleasantries.

Return ONLY a JSON object with exactly these fields:
{
  "subject": string,
  "body": string,
  "recipient_hint": string
}"""


async def generate_rfq_email(
    product_description: str,
    supplier_name: str,
    unit_price: float | None,
    currency: str,
    moq: int | None,
    availability: str | None,
    shipping_days_min: int | None,
    shipping_days_max: int | None,
) -> dict:
    """Generate a formal RFQ email for the selected supplier."""
    try:
        moq_str = str(moq) if moq else "as quoted"
        bulk_qty = (moq or 100) * 5
        price_str = f"{unit_price} {currency}/unit" if unit_price else "as quoted"
        lead_str = (
            f"{shipping_days_min}–{shipping_days_max} days"
            if shipping_days_min and shipping_days_max
            else "as quoted"
        )

        prompt = f"""Generate an RFQ email for this procurement requirement:

Product: {product_description}
Supplier: {supplier_name}
Quoted Price: {price_str}
MOQ: {moq_str}
Availability: {availability or "unknown"}
Lead Time: {lead_str}

We are evaluating 3 vendors and will place a purchase order within 5 business days.
Request confirmation of:
1. Confirmed unit pricing for quoted quantity
2. Delivery timeline
3. Payment terms
4. Bulk discount applicability for {bulk_qty}+ units"""

        response = await client.chat.completions.create(
            model=settings.openai_model,
            max_tokens=600,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": RFQ_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        data = json.loads(response.choices[0].message.content)
        return {
            "subject": data.get("subject", f"RFQ: {product_description}"),
            "body": data.get("body", ""),
            "recipient_hint": data.get("recipient_hint", f"Contact {supplier_name} via their website"),
        }

    except Exception as e:
        logger.error(f"RFQ generation failed: {e}")
        return {
            "subject": f"Request for Quotation — {product_description}",
            "body": f"Dear {supplier_name} Team,\n\nWe are interested in procuring {product_description}. Please provide your best pricing, lead time, and payment terms.\n\nBest regards",
            "recipient_hint": "Contact supplier via their website",
        }
