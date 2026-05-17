import os
import json
import asyncpg
import anthropic
from datetime import date
from decimal import Decimal
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

AGENT_DIR = Path(__file__).parent

PROMPT                   = (AGENT_DIR / "sentinel_agent.md").read_text()
MARKET_BASELINE_SQL      = (AGENT_DIR / "sentinel_market_baseline.sql").read_text()
SECTOR_PERFORMANCE_SQL   = (AGENT_DIR / "sentinel_sector_performance.sql").read_text()
SUBINDUSTRY_PERFORMANCE_SQL = (AGENT_DIR / "sentinel_subindustry_performance.sql").read_text()

OUTLIER_THRESHOLD = 5.0

def _serialize(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def _to_float(val) -> float | None:
    if val is None:
        return None
    return float(val)

class SentinelAgent:

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

    # ------------------------------------------------------------------
    # DATA GATHERING — hardcoded SQL, zero token cost
    # ------------------------------------------------------------------
 
    async def _gather_market_data(self) -> dict:
        """Execute hardcoded queries directly against the database."""
        async with self.pool.acquire() as conn:
            baseline_rows       = await conn.fetch(MARKET_BASELINE_SQL)
            sector_rows         = await conn.fetch(SECTOR_PERFORMANCE_SQL)
            subindustry_rows    = await conn.fetch(SUBINDUSTRY_PERFORMANCE_SQL)
 
        # index baseline by window_days for easy lookup
        baseline = {
            row["window_days"]: _to_float(row["avg_change_pct"])
            for row in baseline_rows
        }
 
        # group sector performance by sector name
        sector_perf = {}
        for row in sector_rows:
            name = row["sector_name"]
            if name not in sector_perf:
                sector_perf[name] = {
                    "sector_name":   name,
                    "ticker_count":  row["ticker_count"],
                    "performance":   {}
                }
            sector_perf[name]["performance"][row["window_days"]] = (
                _to_float(row["avg_change_pct"])
            )
 
        subindustry_perf = [
            {
                "sector_name":      row["sector_name"],
                "sub_industry_name": row["sub_industry_name"],
                "ticker_count":     row["ticker_count"],
                "avg_change_pct_30d": _to_float(row["avg_change_pct_30d"])
            }
            for row in subindustry_rows
        ]
 
        return {
            "baseline":         baseline,
            "sector_perf":      sector_perf,
            "subindustry_perf": subindustry_perf
        }



    # ------------------------------------------------------------------
    # OUTLIER DETECTION — pure logic, no LLM
    # ------------------------------------------------------------------
 
    def _detect_outliers(self, market_data: dict) -> list[dict]:
        """
        Compare each sector's 30d performance against the market baseline.
        Flag sectors that deviate by more than OUTLIER_THRESHOLD percent.
        Also detect acceleration — 7d move amplifying the 30d trend.
        """
        baseline_30d = market_data["baseline"].get(30)
        flagged      = []
 
        if baseline_30d is None:
            return flagged
 
        for sector_name, data in market_data["sector_perf"].items():
            perf    = data["performance"]
            perf_30d = perf.get(30)
 
            if perf_30d is None:
                continue
 
            vs_market = perf_30d - baseline_30d
 
            if abs(vs_market) < OUTLIER_THRESHOLD:
                continue
 
            # acceleration: 7d move is in the same direction and larger
            perf_7d      = perf.get(7)
            acceleration = False
            if perf_7d is not None and baseline_30d is not None:
                vs_market_7d = perf_7d - market_data["baseline"].get(7, 0)
                # accelerating if 7d relative move is stronger than 30d
                acceleration = (
                    vs_market > 0 and vs_market_7d > vs_market
                ) or (
                    vs_market < 0 and vs_market_7d < vs_market
                )
 
            # find the worst/best performing sub-industry in this sector
            sector_subindustries = [
                s for s in market_data["subindustry_perf"]
                if s["sector_name"] == sector_name
            ]
 
            if vs_market < 0:
                # selling off — find worst sub-industry
                driver = min(
                    sector_subindustries,
                    key=lambda x: x["avg_change_pct_30d"],
                    default=None
                )
            else:
                # growing — find best sub-industry
                driver = max(
                    sector_subindustries,
                    key=lambda x: x["avg_change_pct_30d"],
                    default=None
                )
 
            flagged.append({
                "sector":           sector_name,
                "direction":        "selloff" if vs_market < 0 else "growth",
                "vs_market_30d":    round(vs_market, 4),
                "acceleration":     acceleration,
                "performance": {
                    "7d":   perf.get(7),
                    "30d":  perf.get(30),
                    "90d":  perf.get(90),
                    "1yr":  perf.get(365),
                    "5yr":  perf.get(1825)
                },
                "driver_subsector": (
                    driver["sub_industry_name"] if driver else None
                ),
                "ticker_count":     data["ticker_count"]
            })
 
        # sort — worst selloffs first, then strongest growth
        flagged.sort(key=lambda x: x["vs_market_30d"])
        return flagged
 
    def _get_subsectors_for_investigation(
        self,
        flagged_sectors: list[dict],
        subindustry_perf: list[dict],
        baseline_30d: float
    ) -> list[dict]:
        """
        For each flagged sector find the sub-industries most responsible
        for the move — these are what the Analyst Agent will investigate.
        """
        investigation = []
        flagged_names = {s["sector"] for s in flagged_sectors}
 
        for sub in subindustry_perf:
            if sub["sector_name"] not in flagged_names:
                continue
 
            vs_market = (sub["avg_change_pct_30d"] or 0) - baseline_30d
 
            if abs(vs_market) >= OUTLIER_THRESHOLD:
                investigation.append({
                    "subsector":    sub["sub_industry_name"],
                    "sector":       sub["sector_name"],
                    "vs_market_30d": round(vs_market, 4),
                    "direction":    "selloff" if vs_market < 0 else "growth",
                    "ticker_count": sub["ticker_count"],
                    "reason": (
                        f"{round(vs_market, 1):+.1f}% vs market over 30 days "
                        f"({sub['ticker_count']} tickers)"
                    )
                })
 
        investigation.sort(key=lambda x: x["vs_market_30d"])
        return investigation

    # ------------------------------------------------------------------
    # LLM ANALYSIS — narrative notes and judgement
    # ------------------------------------------------------------------
 
    def _write_notes(
        self,
        flagged_sectors:  list[dict],
        subsectors:       list[dict],
        market_data:      dict
    ) -> str:
        """
        Ask Claude to write compressed analytical notes and flag any sectors
        that warrant especially close attention with reasoning.
        Only called when there are flagged sectors worth writing about.
        """
        if not flagged_sectors:
            return "No sectors outside threshold. Market moving broadly in line."
 
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": (
                    f"{PROMPT}\n\n"
                    f"Today's date: {date.today()}\n\n"
                    f"MARKET BASELINE:\n"
                    f"{json.dumps(market_data['baseline'], indent=2, default=_serialize)}\n\n"
                    f"FLAGGED SECTORS:\n"
                    f"{json.dumps(flagged_sectors, indent=2, default=_serialize)}\n\n"
                    f"SUBSECTORS FOR INVESTIGATION:\n"
                    f"{json.dumps(subsectors, indent=2, default=_serialize)}\n\n"
                    f"Write your compressed analytical notes following the format "
                    f"in your instructions. Flag any sectors that should be "
                    f"especially prioritized for the Analyst Agent and explain why."
                )
            }]
        )
 
        return response.content[0].text.strip()
 
    # ------------------------------------------------------------------
    # PERSISTENCE
    # ------------------------------------------------------------------
 
    async def _save_log(
        self,
        flagged_sectors: list[dict],
        subsectors:      list[dict],
        notes:           str,
        baseline_30d:    float | None
    ) -> int:
        """Persist sentinel run to sentinel_logs."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO sentinel_logs
                    (run_date, market_baseline, flagged_sectors,
                     notes, passed_to_analyst)
                VALUES ($1, $2, $3, $4, FALSE)
                RETURNING id
                """,
                date.today(),
                baseline_30d,
                json.dumps({
                    "flagged_sectors": flagged_sectors,
                    "subsectors_for_investigation": subsectors
                }, default=_serialize),
                notes
            )
            return row["id"]

    # ------------------------------------------------------------------
    # MAIN ENTRY POINT
    # ------------------------------------------------------------------
 
    async def run(self, write_notes: bool = True) -> dict:
        """
        Full sentinel run:
          1. Gather market data (hardcoded SQL — no token cost)
          2. Detect outliers (pure logic — no token cost)
          3. Identify subsectors for investigation (pure logic)
          4. Write analytical notes (LLM — only if write_notes=True)
          5. Save to sentinel_logs
          6. Return full result
        """
        print("Sentinel: gathering market data...")
        market_data = await self._gather_market_data()
 
        print("Sentinel: detecting outliers...")
        flagged = self._detect_outliers(market_data)
        print(f"Sentinel: {len(flagged)} sectors flagged")
 
        baseline_30d = market_data["baseline"].get(30)
        subsectors   = self._get_subsectors_for_investigation(
            flagged,
            market_data["subindustry_perf"],
            baseline_30d or 0
        )
        print(f"Sentinel: {len(subsectors)} subsectors flagged for investigation")
 
        notes = ""
        if write_notes:
            print("Sentinel: writing analytical notes...")
            notes = self._write_notes(flagged, subsectors, market_data)
 
        print("Sentinel: saving log...")
        log_id = await self._save_log(
            flagged, subsectors, notes, baseline_30d
        )
 
        print(f"Sentinel: complete — log id {log_id}")
 
        return {
            "log_id":                       log_id,
            "run_date":                     str(date.today()),
            "market_baseline":              market_data["baseline"],
            "flagged_sectors":              flagged,
            "subsectors_for_investigation": subsectors,
            "notes":                        notes
        }
