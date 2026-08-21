"""
Step 8 - Natural language explanation layer.

Uses the Anthropic API (model: claude-sonnet-5) to compare the top ranked
options and explain the recommendation. Falls back to a deterministic,
template-based explanation if no ANTHROPIC_API_KEY is configured or the
API call fails for any reason -- so the endpoint always returns something
useful, and the demo works out of the box without a key.

NOTE ON "langchain": the tech stack lists LangChain as the AI/explanation
orchestration layer. For a single-call, single-prompt explanation like
this, a bare Anthropic SDK call is simpler and has no meaningful behavior
difference from wrapping it in a LangChain LLMChain. The function below is
written so a LangChain PromptTemplate + LLMChain (or LangChain's
ChatAnthropic wrapper) can be dropped in with no change to the calling
code in main.py -- swap the body of `generate_explanation` when you want
LangChain-specific features (memory, multi-step chains, output parsers).
"""

import os
from typing import List

SYSTEM_PROMPT = (
    "You are an agricultural waste-to-value advisor for Indian sugarcane "
    "farmers, mills and cooperatives. Given ranked industry options for "
    "processing sugarcane waste, write a short, plain-language explanation "
    "(120-180 words) comparing the top options and stating the reasoning "
    "behind the top recommendation. Be concrete: reference the actual "
    "numbers given. No headers, no markdown, 1-2 short paragraphs."
)


def _template_fallback(results: List[dict], disposal_method: str) -> str:
    if not results:
        return (
            "No matching industries were found for the waste generated at this "
            "location. Try a different location or check nearby buyer coverage."
        )
    top = results[0]
    lines = [
        f"Based on your inputs, {top['industry_label']} is the top recommendation, "
        f"processing {top['waste_quantity_tons']:.0f} tonnes of {top['waste_stream'].replace('_', ' ')} "
        f"through {top['buyer_name']} ({top['distance_km']:.0f} km away). "
        f"This route needs {top['trucks_required']} truck trip(s), costs about "
        f"₹{top['transport_cost_inr']:,.0f} in transport, and nets an estimated "
        f"₹{top['net_revenue_inr']:,.0f} after transport, versus your current "
        f"'{disposal_method.replace('_', ' ')}' method. It scores "
        f"{top['sustainability_score']:.0f}/100 on sustainability, factoring in net "
        f"revenue per tonne, distance, and estimated CO2 avoided."
    ]
    if len(results) > 1:
        runner_up = results[1]
        lines.append(
            f" {runner_up['industry_label']} is the next best option "
            f"(score {runner_up['sustainability_score']:.0f}/100, net revenue "
            f"₹{runner_up['net_revenue_inr']:,.0f}), but ranks lower mainly due to "
            f"{'a longer haul' if runner_up['distance_km'] > top['distance_km'] else 'lower net revenue per tonne'}."
        )
    return "".join(lines)


def generate_explanation(results: List[dict], disposal_method: str, is_peak_season: bool) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return _template_fallback(results, disposal_method)

    try:
        import anthropic  # lazy import so the app runs without the package installed

        client = anthropic.Anthropic(api_key=api_key)
        top_n = results[:4]
        summary_lines = []
        for r in top_n:
            summary_lines.append(
                f"- {r['industry_label']} via {r['buyer_name']} ({r['distance_km']} km): "
                f"{r['waste_quantity_tons']} t {r['waste_stream']}, "
                f"transport cost Rs {r['transport_cost_inr']}, "
                f"net revenue Rs {r['net_revenue_inr']}, "
                f"CO2 avoided {r['co2_avoided_kg']} kg, "
                f"score {r['sustainability_score']}/100"
            )
        user_prompt = (
            f"Current disposal method: {disposal_method}. "
            f"Peak harvest season: {is_peak_season}. Ranked options:\n"
            + "\n".join(summary_lines)
        )
        msg = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=400,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text_parts = [b.text for b in msg.content if getattr(b, "type", None) == "text"]
        return "".join(text_parts).strip() or _template_fallback(results, disposal_method)
    except Exception:
        return _template_fallback(results, disposal_method)
