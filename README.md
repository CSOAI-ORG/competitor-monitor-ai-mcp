# Competitor Monitor AI MCP Server

> By [MEOK AI Labs](https://meok.ai) — Comprehensive competitor intelligence, pricing tracking, and market monitoring

## Installation

```bash
pip install competitor-monitor-ai-mcp
```

## Usage

```bash
python server.py
```

## Tools

### `add_competitor`
Add a competitor to monitor.

**Parameters:**
- `name` (str): Competitor name
- `website` (str): Website URL
- `industry` (str): Industry

### `get_competitor_info`
Get competitor details.

**Parameters:**
- `competitor_id` (str): Competitor identifier

### `track_mention`
Track a competitor mention with sentiment.

**Parameters:**
- `competitor_name` (str): Competitor name
- `source` (str): Mention source
- `sentiment` (str): Sentiment — 'positive', 'negative', 'neutral'
- `text` (str): Mention text

### `get_mentions`
Get mentions filtered by competitor, timeframe, and sentiment.

**Parameters:**
- `competitor_name` (str): Competitor name
- `days` (int): Lookback days (default 30)
- `sentiment` (str): Sentiment filter

### `update_pricing`
Update competitor pricing data.

**Parameters:**
- `competitor_name` (str): Competitor name
- `product` (str): Product name
- `price` (float): Price
- `currency` (str): Currency (default 'USD')

### `get_pricing_history`
Get competitor pricing history with trend analysis.

**Parameters:**
- `competitor_name` (str): Competitor name
- `product` (str): Product name

### `set_alert`
Set alert for competitor activity.

**Parameters:**
- `competitor_name` (str): Competitor name
- `alert_type` (str): Alert type (default 'mention')
- `condition` (str): Alert condition

### `get_alerts`
Get all active alerts.

### `get_competitor_comparison`
Compare multiple competitors side by side.

**Parameters:**
- `competitors` (list): List of competitor names

### `get_market_share_estimate`
Estimate market share for an industry.

**Parameters:**
- `industry` (str): Industry name

### `analyze_sentiment_trend`
Analyze sentiment trends for a competitor over time.

**Parameters:**
- `competitor_name` (str): Competitor name
- `days` (int): Lookback days (default 30)

## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT — MEOK AI Labs
