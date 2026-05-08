<div align="center">

# Competitor Monitor Ai MCP

**MCP server for competitor monitor ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-competitor-monitor-ai-mcp)](https://pypi.org/project/meok-competitor-monitor-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Competitor Monitor Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `add_competitor` | Add competitor to monitor |
| `get_competitor_info` | Get competitor details |
| `track_mention` | Track a competitor mention |
| `get_mentions` | Get mentions for competitor |
| `update_pricing` | Update competitor pricing |
| `get_pricing_history` | Get competitor pricing history |
| `set_alert` | Set alert for competitor activity |
| `get_alerts` | Get active alerts |
| `get_competitor_comparison` | Compare competitors |
| `get_market_share_estimate` | Estimate market share |
| `analyze_sentiment_trend` | Analyze sentiment trends |

## Installation

```bash
pip install meok-competitor-monitor-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "competitor-monitor-ai": {
      "command": "python",
      "args": ["-m", "meok_competitor_monitor_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 11 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
