# Define simplified rate limits for different API tiers (RPM = Requests Per Minute, TPM = Tokens Per Minute)
# These are based on Gemini 2.5 Pro for paid tiers, and a common free tier estimate.

RATE_LIMITS = {
    "free": {
        "RPM": 15,
        "TPM": 1000,
        "RPD": 1000 # Requests Per Day (estimated for free tier)
    },
    "tier1": { # Based on Gemini 2.5 Pro
        "RPM": 150,
        "TPM": 2_000_000,
        "RPD": 10_000
    },
    "tier2": { # Based on Gemini 2.5 Pro
        "RPM": 1000,
        "TPM": 5_000_000,
        "RPD": 50_000
    },
    "tier3": { # Estimated, as specific 2.5 Pro numbers for Tier 3 were not explicitly listed in the provided text.
        "RPM": 2000,
        "TPM": 10_000_000,
        "RPD": 100_000
    }
}

VALID_TIERS = list(RATE_LIMITS.keys())

def get_rate_limits(tier: str):
    """Returns the rate limits for a given tier."""
    return RATE_LIMITS.get(tier)
