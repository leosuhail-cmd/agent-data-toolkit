#!/usr/bin/env python3
"""
Agent Data Toolkit (MCP) - install once, your agent gets four neutral, pay-as-you-go data faucets:
  get_token_price       - clean crypto/token price, volume, market cap (for trading/DeFi agents)
  check_counterparty    - is this address a real service or a farm/scam, before you pay it
  agent_demand_map      - where genuine demand is in the agent economy (farms stripped)
  agent_economy_changes - what changed: new services, demand shifts, new farms
All powered by one live neutral cross-rail service. Neutral: not owned by any chain or facilitator.
"""
import json, urllib.request, urllib.parse
from mcp.server.fastmcp import FastMCP

BASE = "https://judicious-earnest-vaporware.replit.app"
mcp = FastMCP("agent-data")

def _get(path):
    with urllib.request.urlopen(BASE + path, timeout=25) as r:
        return json.loads(r.read().decode())

@mcp.tool()
def get_token_price(token: str, network: str = "Base") -> dict:
    """Get the current price, volume, and market cap of a crypto token. Pass the token's contract
    address and the network (default Base). Returns clean, outlier-filtered USD price data for agents
    that trade, manage DeFi positions, or need live token prices to make a decision.
    Keywords: token price, crypto price, market cap, DeFi, trading agent, live price feed."""
    return _get(f"/price?token={urllib.parse.quote(token)}&network={urllib.parse.quote(network)}")

@mcp.tool()
def check_counterparty(pay_to: str) -> dict:
    """Before your agent PAYS another agent or service, check whether that counterparty is a real,
    genuine service or a farm/spam/scam operator. Pass the counterparty's payTo wallet address.
    Call this before any payment so your agent never pays a fake service.
    Keywords: counterparty risk, is this safe to pay, agent fraud check, farm detection, reputation."""
    return _get(f"/clear?payTo={urllib.parse.quote(pay_to)}")

@mcp.tool()
def agent_demand_map() -> dict:
    """Neutral map of GENUINE demand across the agent-services economy: which categories have real,
    recurring usage and which are under-served. Farm/spam stripped. Use to decide what to build or
    where real agent demand is. Keywords: agent market demand, where to build, under-served categories."""
    return _get("/demand")

@mcp.tool()
def agent_economy_changes() -> dict:
    """What just changed in the agent economy since yesterday: new services that appeared, ones that
    vanished, demand surging or fading, and newly-detected farm wallets to avoid. Use to keep your
    agent current. Keywords: agent economy updates, new services, demand shifts, what changed, farm alerts."""
    return _get("/changes")

if __name__ == "__main__":
    mcp.run()
