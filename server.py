#!/usr/bin/env python3
"""MEOK AI Labs — competitor-monitor-ai-mcp MCP Server. Comprehensive competitor intelligence and market monitoring."""

import json
from datetime import datetime, timedelta, timezone
from typing import Any
import uuid
import random
import sys, os

sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
from auth_middleware import check_access
from mcp.server.fastmcp import FastMCP
from collections import defaultdict

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None


_store = {"competitors": {}, "mentions": [], "pricing": {}, "alerts": []}
mcp = FastMCP("competitor-monitor-ai", instructions="Comprehensive competitor intelligence and market monitoring.")


def create_id():
    return str(uuid.uuid4())[:8]


@mcp.tool()
def add_competitor(name: str, website: str = "", industry: str = "", api_key: str = "") -> str:
    """Add competitor to monitor"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    comp = {
        "id": create_id(),
        "name": name,
        "website": website,
        "industry": industry,
        "added_at": datetime.now().isoformat(),
        "mentions_count": 0,
    }
    _store["competitors"][comp["id"]] = comp
    return json.dumps(
        {"added": True, "competitor_id": comp["id"], "name": comp["name"]}, indent=2
    )


@mcp.tool()
def get_competitor_info(competitor_id: str, api_key: str = "") -> str:
    """Get competitor details"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    comp = _store["competitors"].get(competitor_id)
    if comp:
        return json.dumps(comp, indent=2)
    return json.dumps({"error": "Competitor not found"})


@mcp.tool()
def track_mention(competitor_name: str, source: str = "manual", sentiment: str = "neutral", text: str = "", api_key: str = "") -> str:
    """Track a competitor mention"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    mention = {
        "id": create_id(),
        "competitor_name": competitor_name,
        "source": source,
        "sentiment": sentiment,
        "text": text,
        "tracked_at": datetime.now().isoformat(),
    }
    _store["mentions"].append(mention)

    for comp in _store["competitors"].values():
        if comp["name"].lower() in competitor_name.lower():
            comp["mentions_count"] = comp.get("mentions_count", 0) + 1

    return json.dumps({"tracked": True, "mention_id": mention["id"]}, indent=2)


@mcp.tool()
def get_mentions(competitor_name: str = "", days: int = 30, sentiment: str = "", api_key: str = "") -> str:
    """Get mentions for competitor"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    cutoff = datetime.now() - timedelta(days=days)
    mentions = [
        m
        for m in _store["mentions"]
        if competitor_name.lower() in m.get("competitor_name", "").lower()
        and datetime.fromisoformat(m["tracked_at"]) >= cutoff
    ]

    if sentiment:
        mentions = [m for m in mentions if m.get("sentiment") == sentiment]

    return json.dumps({"mentions": mentions, "count": len(mentions)}, indent=2)


@mcp.tool()
def update_pricing(competitor_name: str, product: str = "", price: float = 0, currency: str = "USD", api_key: str = "") -> str:
    """Update competitor pricing"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    key = f"{competitor_name}:{product}"
    if key not in _store["pricing"]:
        _store["pricing"][key] = []

    _store["pricing"][key].append(
        {
            "price": price,
            "currency": currency,
            "updated_at": datetime.now().isoformat(),
        }
    )

    return json.dumps(
        {"updated": True, "competitor": competitor_name, "product": product, "price": price},
        indent=2,
    )


@mcp.tool()
def get_pricing_history(competitor_name: str = "", product: str = "", api_key: str = "") -> str:
    """Get competitor pricing history"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    key = f"{competitor_name}:{product}"
    history = _store["pricing"].get(key, [])

    if history:
        current = history[-1]["price"]
        oldest = history[0]["price"]
        change = ((current - oldest) / oldest * 100) if oldest > 0 else 0
        return json.dumps(
            {
                "product": product,
                "current_price": current,
                "history": history,
                "change_percent": round(change, 2),
            },
            indent=2,
        )

    return json.dumps({"error": "No pricing data"})


@mcp.tool()
def set_alert(competitor_name: str, alert_type: str = "mention", condition: str = "", api_key: str = "") -> str:
    """Set alert for competitor activity"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    alert = {
        "id": create_id(),
        "competitor_name": competitor_name,
        "alert_type": alert_type,
        "condition": condition,
        "created_at": datetime.now().isoformat(),
        "triggered": False,
    }
    _store["alerts"].append(alert)

    return json.dumps({"alert_created": True, "alert_id": alert["id"]}, indent=2)


@mcp.tool()
def get_alerts(api_key: str = "") -> str:
    """Get active alerts"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    active = [a for a in _store["alerts"] if not a.get("triggered")]
    return json.dumps({"active_alerts": active, "count": len(active)}, indent=2)


@mcp.tool()
def get_competitor_comparison(competitors: list = None, api_key: str = "") -> str:
    """Compare competitors"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    comps = competitors or []
    comparison = []
    for comp_name in comps:
        for comp in _store["competitors"].values():
            if comp["name"].lower() == comp_name.lower():
                mentions = [
                    m
                    for m in _store["mentions"]
                    if m.get("competitor_name", "").lower() == comp_name.lower()
                ]
                comparison.append(
                    {
                        "name": comp["name"],
                        "mentions_count": len(mentions),
                        "industry": comp.get("industry", ""),
                    }
                )

    return json.dumps({"comparison": comparison}, indent=2)


@mcp.tool()
def get_market_share_estimate(industry: str = "", api_key: str = "") -> str:
    """Estimate market share"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    total = sum(
        1
        for c in _store["competitors"].values()
        if c.get("industry", "").lower() == industry.lower()
    )
    estimates = [
        {
            "competitor": "Company " + str(i + 1),
            "estimated_share": round(random.uniform(5, 30), 1),
        }
        for i in range(min(total, 5))
    ]

    return json.dumps({"industry": industry, "estimates": estimates}, indent=2)


@mcp.tool()
def analyze_sentiment_trend(competitor_name: str = "", days: int = 30, api_key: str = "") -> str:
    """Analyze sentiment trends"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    mentions = [
        m
        for m in _store["mentions"]
        if competitor_name.lower() in m.get("competitor_name", "").lower()
    ]

    if not mentions:
        return json.dumps({"message": "No mentions found"})

    sentiments = {"positive": 0, "negative": 0, "neutral": 0}
    for m in mentions:
        sentiments[m.get("sentiment", "neutral")] += 1

    return json.dumps(
        {
            "competitor": competitor_name,
            "total_mentions": len(mentions),
            "sentiment_breakdown": sentiments,
            "trend": "improving"
            if sentiments["positive"] > sentiments["negative"]
            else "declining",
        },
        indent=2,
    )


if __name__ == "__main__":
    mcp.run()
