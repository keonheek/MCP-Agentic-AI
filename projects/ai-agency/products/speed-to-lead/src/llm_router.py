"""
LLM Router — selects model based on client tier.

Tier mapping:
    Lite  -> triage: haiku-4-5  | reply: haiku-4-5
    Pro   -> triage: haiku-4-5  | reply: sonnet-4-5   (default)
    Tier P -> triage: haiku-4-5  | reply: opus-4-5  + PIPA audit flag

The router returns model IDs that the pipeline passes directly to the
Anthropic client. No external dependencies beyond the existing stack.
"""

from __future__ import annotations

TIER_MODELS: dict[str, dict[str, str]] = {
    "lite": {
        "triage": "claude-haiku-4-5",
        "reply": "claude-haiku-4-5",
    },
    "pro": {
        "triage": "claude-haiku-4-5",
        "reply": "claude-sonnet-4-5",
    },
    "tier_p": {
        "triage": "claude-haiku-4-5",
        "reply": "claude-opus-4-5",
    },
}

DEFAULT_TIER = "pro"


def get_models(tier: str | None) -> dict[str, str]:
    """
    Return triage and reply model IDs for a given tier string.

    Args:
        tier: "lite", "pro", or "tier_p". Case-insensitive.
              Defaults to "pro" if None or unrecognised.

    Returns:
        dict with keys "triage" and "reply".
    """
    if tier is None:
        return TIER_MODELS[DEFAULT_TIER]
    normalised = tier.lower().replace("-", "_").replace(" ", "_")
    return TIER_MODELS.get(normalised, TIER_MODELS[DEFAULT_TIER])


def requires_pipa_audit(tier: str | None) -> bool:
    """Return True if the tier requires PIPA compliance audit features."""
    if tier is None:
        return False
    return tier.lower().replace("-", "_") == "tier_p"
