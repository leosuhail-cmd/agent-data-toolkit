#!/usr/bin/env python3
"""
agent-data-toolkit — reference implementation of the /clear verdict.

This is the open, auditable scoring method behind `check_counterparty`. A neutral trust
layer should be transparent about how it scores, so here it is.

Principle: don't guess "scam vs genuine" from pollutable catalog counts. REPORT verifiable
on-chain evidence — how many distinct real wallets actually paid this counterparty in USDC
on Base — strip known crawler/infra wallets, check concentration for self-washing, and
ABSTAIN (no_onchain_history / thin / unknown) when evidence is too thin to stand behind.

Verdict states:
  infrastructure     - payTo is a known router/infra contract, not an agent service
  no_onchain_history - 0 independent payers on-chain -> unverified, pay at your own risk
  thin               - 1..9 independent payers -> minimal verifiable usage
  concentrated       - >=10 payers but one wallet dominates -> possible self-generated demand
  established        - >=10 independent payers, well-distributed -> verifiable paid usage
  unknown            - on-chain lookup failed; never crash, always return JSON

Env: BITQUERY_TOKEN must be set. Denylist read from crawler_wallets.json beside this file.
"""
import json, os, time, urllib.request, urllib.error

USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
EP = "https://streaming.bitquery.io/graphql"
MIN_ESTABLISHED = 10
CONCENTRATION_MAX = 0.60
LISTING_SPAM = 100
CLAIM_INFLATION = 5
HERE = os.path.dirname(os.path.abspath(__file__))

def _token():
    return os.environ.get("BITQUERY_TOKEN")

def _denylist():
    try:
        return {a.lower() for a in json.load(open(os.path.join(HERE, "crawler_wallets.json")))}
    except Exception:
        return set()

def _gql(q, tok, retries=2):
    last = None
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(EP, data=json.dumps({"query": q}).encode(),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {tok}"})
            return json.load(urllib.request.urlopen(req, timeout=50))
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (403, 429, 500, 502, 503) and i < retries:
                time.sleep(1.5 * (i + 1)); continue
            raise
    raise last

def onchain_senders(addr, tok, days=30):
    addr = addr.lower()
    q = f'''{{ EVM(dataset: combined, network: base) {{
      Transfers(where: {{ Block: {{Time: {{since_relative: {{days_ago: {days}}}}}}}
          Transfer: {{ Currency: {{SmartContract: {{is: "{USDC_BASE}"}}}}
                       Receiver: {{is: "{addr}"}} }} }}
        limit: {{count: 1000}} orderBy: {{descendingByField: "cnt"}}
      ) {{ Transfer {{ Sender }} cnt: count amtUSD: sum(of: Transfer_AmountInUSD) }} }} }}'''
    r = _gql(q, tok)
    if "errors" in r:
        raise RuntimeError(json.dumps(r["errors"])[:200])
    return [{"sender": x["Transfer"]["Sender"].lower(), "tx": int(x["cnt"]),
             "usd": float(x["amtUSD"] or 0)} for x in r["data"]["EVM"]["Transfers"]]

def verdict(pay_to, tok=None, days=30, catalog_index=None):
    """catalog_index: optional {payTo_lower: {listings, claimed_payers}} for spam/inflation flags."""
    tok = tok or _token(); deny = _denylist(); addr = pay_to.lower()
    listings = claimed = None
    if catalog_index is not None:
        ci = catalog_index.get(addr)
        if ci:
            listings = ci.get("listings"); claimed = ci.get("claimed_payers")
    if addr in deny:
        return {"payTo": pay_to, "verdict": "infrastructure", "confidence": "high",
                "summary": "Known router/infrastructure contract, not an agent service.",
                "evidence": {"on_denylist": True, "catalog_listings": listings},
                "method": "onchain-usdc-base", "window_days": days}
    try:
        rows = onchain_senders(addr, tok, days)
    except Exception as e:
        return {"payTo": pay_to, "verdict": "unknown", "confidence": "low",
                "summary": "On-chain lookup temporarily unavailable; could not verify. Treat as unverified.",
                "evidence": {"catalog_listings": listings, "catalog_claimed_payers": claimed,
                             "error": str(e)[:120]}, "method": "onchain-usdc-base", "window_days": days}
    indep = [r for r in rows if r["sender"] not in deny]
    stripped = len(rows) - len(indep); n = len(indep)
    txs = sum(r["tx"] for r in indep); usd = round(sum(r["usd"] for r in indep), 4)
    top_share = round(max((r["tx"] for r in indep), default=0) / txs, 3) if txs else 0.0
    flags = []
    if listings and listings >= LISTING_SPAM:
        flags.append(f"listing_spam ({listings} listings)")
    if claimed and n and claimed >= CLAIM_INFLATION * max(n, 1):
        flags.append(f"claim_inflation (catalog claims {claimed}, on-chain {n})")
    if n == 0:
        state, conf, msg = "no_onchain_history", "high", "No independent on-chain payments found. Unverified — pay at your own risk."
    elif n < MIN_ESTABLISHED:
        state, conf, msg = "thin", "medium", f"Minimal verifiable usage: {n} independent payer(s) on-chain."
    elif top_share >= CONCENTRATION_MAX:
        state, conf, msg = "concentrated", "medium", f"{n} payers but top wallet is {int(top_share*100)}% of activity — possible self-generated demand."
    else:
        state, conf, msg = "established", "high", f"Verifiable distributed paid usage: {n} independent payers, ${usd} over {days}d."
    if flags and state == "established":
        conf = "medium"; msg += " Caution: " + "; ".join(flags) + "."
    ev = {"independent_payers": n, "transactions": txs, "total_usd": usd, "top_payer_tx_share": top_share,
          "crawler_wallets_stripped": stripped, "catalog_listings": listings,
          "catalog_claimed_payers": claimed, "flags": flags}
    return {"payTo": pay_to, "verdict": state, "confidence": conf, "summary": msg,
            "evidence": ev, "method": "onchain-usdc-base", "window_days": days}

if __name__ == "__main__":
    import sys
    addr = sys.argv[1] if len(sys.argv) > 1 else "0x0e84ddedaae6a779c462c22a59f301ec31b6b808"
    print(json.dumps(verdict(addr), indent=2))
