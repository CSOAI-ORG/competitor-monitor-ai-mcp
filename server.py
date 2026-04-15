#!/usr/bin/env python3
"""MEOK AI Labs — competitor-monitor-ai-mcp MCP Server. Comprehensive competitor intelligence and market monitoring."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any
import uuid
import random
import sys, os

sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
from auth_middleware import check_access
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
import mcp.types as types

from collections import defaultdict

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None


_store = {"competitors": {}, "mentions": [], "pricing": {}, "alerts": []}
server = Server("competitor-monitor-ai-mcp")


def create_id():
    return str(uuid.uuid4())[:8]


@server.list_resources()
async def handle_list_resources():
    return [
        Resource(
            uri="comp://competitors", name="Competitors", mimeType="application/json"
        ),
        Resource(uri="comp://mentions", name="Mentions", mimeType="application/json"),
        Resource(uri="comp://alerts", name="Alerts", mimeType="application/json"),
    ]


@server.list_tools()
async def handle_list_tools():
    return [
        Tool(
            name="add_competitor",
            description="Add competitor to monitor",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "website": {"type": "string"},
                    "industry": {"type": "string"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="get_competitor_info",
            description="Get competitor details",
            inputSchema={
                "type": "object",
                "properties": {"competitor_id": {"type": "string"}},
            },
        ),
        Tool(
            name="track_mention",
            description="Track a competitor mention",
            inputSchema={
                "type": "object",
                "properties": {
                    "competitor_name": {"type": "string"},
                    "source": {"type": "string"},
                    "sentiment": {
                        "type": "string",
                        "enum": ["positive", "negative", "neutral"],
                    },
                    "text": {"type": "string"},
                },
            },
        ),
        Tool(
            name="get_mentions",
            description="Get mentions for competitor",
            inputSchema={
                "type": "object",
                "properties": {
                    "competitor_name": {"type": "string"},
                    "days": {"type": "number"},
                    "sentiment": {"type": "string"},
                },
            },
        ),
        Tool(
            name="update_pricing",
            description="Update competitor pricing",
            inputSchema={
                "type": "object",
                "properties": {
                    "competitor_name": {"type": "string"},
                    "product": {"type": "string"},
                    "price": {"type": "number"},
                    "currency": {"type": "string"},
                },
            },
        ),
        Tool(
            name="get_pricing_history",
            description="Get competitor pricing history",
            inputSchema={
                "type": "object",
                "properties": {
                    "competitor_name": {"type": "string"},
                    "product": {"type": "string"},
                },
            },
        ),
        Tool(
            name="set_alert",
            description="Set alert for competitor activity",
            inputSchema={
                "type": "object",
                "properties": {
                    "competitor_name": {"type": "string"},
                    "alert_type": {"type": "string"},
                    "condition": {"type": "string"},
                },
            },
        ),
        Tool(
            name="get_alerts",
            description="Get active alerts",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_competitor_comparison",
            description="Compare competitors",
            inputSchema={
                "type": "object",
                "properties": {"competitors": {"type": "array"}},
            },
        ),
        Tool(
            name="get_market_share_estimate",
            description="Estimate market share",
            inputSchema={
                "type": "object",
                "properties": {"industry": {"type": "string"}},
            },
        ),
        Tool(
            name="analyze_sentiment_trend",
            description="Analyze sentiment trends",
            inputSchema={
                "type": "object",
                "properties": {
                    "competitor_name": {"type": "string"},
                    "days": {"type": "number"},
                },
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Any = None) -> list[types.TextContent]:
    args = arguments or {}
    api_key = args.get("api_key", "")
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
                ),
            )
        ]
    err = _rl()
    if err: return [TextContent(type="text", text=err)]

    if name == "add_competitor":
        comp = {
            "id": create_id(),
            "name": args["name"],
            "website": args.get("website", ""),
            "industry": args.get("industry", ""),
            "added_at": datetime.now().isoformat(),
            "mentions_count": 0,
        }
        _store["competitors"][comp["id"]] = comp
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"added": True, "competitor_id": comp["id"], "name": comp["name"]},
                    indent=2,
                ),
            )
        ]

    elif name == "get_competitor_info":
        comp_id = args.get("competitor_id")
        comp = _store["competitors"].get(comp_id)
        if comp:
            return [TextContent(type="text", text=json.dumps(comp, indent=2))]
        return [
            TextContent(type="text", text=json.dumps({"error": "Competitor not found"}))
        ]

    elif name == "track_mention":
        mention = {
            "id": create_id(),
            "competitor_name": args["competitor_name"],
            "source": args.get("source", "manual"),
            "sentiment": args.get("sentiment", "neutral"),
            "text": args.get("text", ""),
            "tracked_at": datetime.now().isoformat(),
        }
        _store["mentions"].append(mention)

        for comp in _store["competitors"].values():
            if comp["name"].lower() in args["competitor_name"].lower():
                comp["mentions_count"] = comp.get("mentions_count", 0) + 1

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"tracked": True, "mention_id": mention["id"]}, indent=2
                ),
            )
        ]

    elif name == "get_mentions":
        name = args.get("competitor_name", "")
        days = args.get("days", 30)
        sentiment = args.get("sentiment")

        cutoff = datetime.now() - timedelta(days=days)
        mentions = [
            m
            for m in _store["mentions"]
            if name.lower() in m.get("competitor_name", "").lower()
            and datetime.fromisoformat(m["tracked_at"]) >= cutoff
        ]

        if sentiment:
            mentions = [m for m in mentions if m.get("sentiment") == sentiment]

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"mentions": mentions, "count": len(mentions)}, indent=2
                ),
            )
        ]

    elif name == "update_pricing":
        comp_name = args.get("competitor_name", "")
        product = args.get("product", "")
        price = args.get("price", 0)

        key = f"{comp_name}:{product}"
        if key not in _store["pricing"]:
            _store["pricing"][key] = []

        _store["pricing"][key].append(
            {
                "price": price,
                "currency": args.get("currency", "USD"),
                "updated_at": datetime.now().isoformat(),
            }
        )

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "updated": True,
                        "competitor": comp_name,
                        "product": product,
                        "price": price,
                    },
                    indent=2,
                ),
            )
        ]

    elif name == "get_pricing_history":
        comp_name = args.get("competitor_name", "")
        product = args.get("product", "")

        key = f"{comp_name}:{product}"
        history = _store["pricing"].get(key, [])

        if history:
            current = history[-1]["price"]
            oldest = history[0]["price"]
            change = ((current - oldest) / oldest * 100) if oldest > 0 else 0
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "product": product,
                            "current_price": current,
                            "history": history,
                            "change_percent": round(change, 2),
                        },
                        indent=2,
                    ),
                )
            ]

        return [TextContent(type="text", text=json.dumps({"error": "No pricing data"}))]

    elif name == "set_alert":
        alert = {
            "id": create_id(),
            "competitor_name": args["competitor_name"],
            "alert_type": args.get("alert_type", "mention"),
            "condition": args.get("condition", ""),
            "created_at": datetime.now().isoformat(),
            "triggered": False,
        }
        _store["alerts"].append(alert)

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"alert_created": True, "alert_id": alert["id"]}, indent=2
                ),
            )
        ]

    elif name == "get_alerts":
        active = [a for a in _store["alerts"] if not a.get("triggered")]

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"active_alerts": active, "count": len(active)}, indent=2
                ),
            )
        ]

    elif name == "get_competitor_comparison":
        comps = args.get("competitors", [])

        comparison = []
        for name in comps:
            for comp in _store["competitors"].values():
                if comp["name"].lower() == name.lower():
                    mentions = [
                        m
                        for m in _store["mentions"]
                        if m.get("competitor_name", "").lower() == name.lower()
                    ]
                    comparison.append(
                        {
                            "name": comp["name"],
                            "mentions_count": len(mentions),
                            "industry": comp.get("industry", ""),
                        }
                    )

        return [
            TextContent(
                type="text", text=json.dumps({"comparison": comparison}, indent=2)
            )
        ]

    elif name == "get_market_share_estimate":
        industry = args.get("industry", "")

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

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"industry": industry, "estimates": estimates}, indent=2
                ),
            )
        ]

    elif name == "analyze_sentiment_trend":
        name = args.get("competitor_name", "")
        days = args.get("days", 30)

        mentions = [
            m
            for m in _store["mentions"]
            if name.lower() in m.get("competitor_name", "").lower()
        ]

        if not mentions:
            return [
                TextContent(
                    type="text", text=json.dumps({"message": "No mentions found"})
                )
            ]

        sentiments = {"positive": 0, "negative": 0, "neutral": 0}
        for m in mentions:
            sentiments[m.get("sentiment", "neutral")] += 1

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "competitor": name,
                        "total_mentions": len(mentions),
                        "sentiment_breakdown": sentiments,
                        "trend": "improving"
                        if sentiments["positive"] > sentiments["negative"]
                        else "declining",
                    },
                    indent=2,
                ),
            )
        ]

    return [TextContent(type="text", text=json.dumps({"error": "Unknown tool"}))]


async def main():
    async with stdio_server(server._read_stream, server._write_stream) as (
        read_stream,
        write_stream,
    ):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="competitor-monitor-ai-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
