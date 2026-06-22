# Agent Data Toolkit (MCP)

**One install — your AI agent gets neutral, cross-rail data about the agent economy:** live token prices, "is this counterparty safe to pay?", and a real-demand map. Not owned by any chain or facilitator. Powered by one live service on Base.

```json
{ "mcpServers": { "agent-data": { "command": "python3", "args": ["/full/path/to/server.py"] } } }
```

---

## Tools

### `get_token_price(token, network="Base")`  · stable
Live, outlier-filtered USD price, volume, and market cap for any token. For agents that trade, manage DeFi positions, or need a price to make a decision.

```json
get_token_price("0x4200000000000000000000000000000000000006", "Base")
→ { "found": true, "symbol": "WETH", "price_usd": 1710.21,
    "volume_usd": 22302.85, "market_cap": 2.06e11, "as_of": "2026-06-21T23:41Z" }
```

### `check_counterparty(pay_to)`  · stable
Before your agent **pays** another agent, check its **verifiable on-chain payment reputation** — not self-reported catalog counts. We look at who actually paid this wallet in USDC on Base, strip known crawler/router wallets, check for self-washing concentration, and **abstain honestly** when the evidence is thin. The verdict is one of:

- `established` — many distinct real payers, well-distributed → genuine paid usage
- `thin` — only a handful of real payers → minimal track record
- `no_onchain_history` — no verifiable payments → **unverified, pay at your own risk**
- `concentrated` — payers exist but one wallet dominates → possible self-generated demand
- `infrastructure` — a known router/contract, not an agent service
- `unknown` — on-chain lookup temporarily unavailable

```json
check_counterparty("0x0e84...b808")
→ { "verdict": "established", "confidence": "high",
    "summary": "131 independent payers with well-distributed usage — strong evidence of genuine demand.",
    "evidence": { "independent_payers": 131, "total_usd": 4.3, "top_payer_tx_share": 0.02,
                  "catalog_claimed_payers": 210, "flags": [] } }
```
The verdict method is open and auditable — see [verdict_reference.py](verdict_reference.py).

### `agent_demand_map()`  · stable
Where genuine demand sits across the agent-services economy — thousands of live services, ranked by real payers per category, farm operators excluded. Use it to decide what to build or where to point an agent.

```json
agent_demand_map()
→ { "genuineServices": 18365, "farmOperatorsExcluded": 17,
    "categories": [ { "category": "Blockchain Data", "services": 485,
                      "uniquePayers": 6452, "demandPerService": 13.3 }, … ] }
```

### `agent_economy_changes()`  · experimental
Day-over-day deltas: new services, demand shifts, newly-flagged farms. **Status:** maturing — diff accuracy improves as the snapshot history fills in; treat output as directional, not exact, for now.

---

## Install
```bash
pip install mcp
python3 server.py
```
Then add the JSON config above to Claude Desktop, Cursor, or any MCP client and restart it.

## Notes
- **Neutral & cross-rail.** Not affiliated with any chain, wallet, or payment facilitator. The point is an independent read.
- **Pay-as-you-go, later.** Endpoints are open now to drive adoption. Tools that see real recurring use will move behind a fractional-cent x402 micropayment.
- **Live service:** `https://judicious-earnest-vaporware.replit.app` (Base mainnet).

## License
MIT — see [LICENSE](LICENSE).
