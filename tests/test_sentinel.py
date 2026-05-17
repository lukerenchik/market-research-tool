# tests/test_sentinel.py
import asyncio
import os
import json
import asyncpg
from dotenv import load_dotenv
from market_intelligence.agents.sentinel_agent import SentinelAgent

load_dotenv()

async def test():
    pool     = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    sentinel = SentinelAgent(pool=pool)

    result = await sentinel.run(write_notes=True)

    print("\n=== SENTINEL REPORT ===\n")
    print(f"Log ID:    {result['log_id']}")
    print(f"Run Date:  {result['run_date']}")

    print(f"\n--- Market Baseline ---")
    for window, pct in result["market_baseline"].items():
        label = {7: "7d", 30: "30d", 90: "90d", 365: "1yr", 1825: "5yr"}.get(window, str(window))
        print(f"  {label:>4}: {pct:+.2f}%" if pct is not None else f"  {label:>4}: N/A")

    print(f"\n--- Flagged Sectors ({len(result['flagged_sectors'])}) ---")
    if result["flagged_sectors"]:
        for s in result["flagged_sectors"]:
            accel = " ⚡ ACCELERATING" if s["acceleration"] else ""
            print(f"  [{s['direction'].upper()}] {s['sector']}{accel}")
            print(f"    vs market: {s['vs_market_30d']:+.2f}%")
            print(f"    30d: {s['performance']['30d']:+.2f}%  "
                  f"7d: {s['performance']['7d']:+.2f}%  "
                  f"90d: {s['performance']['90d']:+.2f}%")
            print(f"    driver: {s['driver_subsector']}")
    else:
        print("  No sectors outside threshold.")

    print(f"\n--- Subsectors for Investigation ({len(result['subsectors_for_investigation'])}) ---")
    if result["subsectors_for_investigation"]:
        for sub in result["subsectors_for_investigation"]:
            print(f"  [{sub['direction'].upper()}] {sub['subsector']} ({sub['sector']})")
            print(f"    {sub['reason']}")
    else:
        print("  None.")

    print(f"\n--- Analytical Notes ---")
    print(result["notes"])

    await pool.close()

asyncio.run(test())