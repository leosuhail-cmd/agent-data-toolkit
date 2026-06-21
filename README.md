# agent-data-toolkit
Neutral cross-rail agent-economy data as one MCP install: live token prices, counterparty farm/scam check, demand map, change feed."
# Agent Data Toolkit (MCP)

Install once - your AI agent gets four neutral, pay-as-you-go data tools for the agent economy:

- **get_token_price** - live crypto/token price, volume, market cap (for agents that trade or run DeFi)
- **check_counterparty** - is this address a real service or a farm/scam? (before your agent PAYS another agent)
- **agent_demand_map** - where genuine demand is, farms stripped (to decide what to build)
- **agent_economy_changes** - what changed: new services, demand shifts, new farms (to stay current)

Neutral and cross-rail - not owned by any chain or facilitator. Powered by one live service.

## Install
    pip install mcp
    python3 server.py

### Add to Claude Desktop / Cursor
    { "mcpServers": { "agent-data": { "command": "python3", "args": ["/full/path/to/server.py"] } } }
