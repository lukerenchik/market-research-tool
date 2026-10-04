"""Tests for the Sentinel agent's deterministic logic.

Outlier detection and data gathering are plain SQL + Python; only the final
narrative step calls the LLM. None of these tests touch the network.
"""
from decimal import Decimal

import pytest

from market_intelligence.agents import sentinel_agent
from market_intelligence.agents.sentinel_agent import OUTLIER_THRESHOLD, SentinelAgent


@pytest.fixture
def agent(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    return SentinelAgent(pool=None)


def sector(name, perf_30d, perf_7d=0.0, tickers=10):
    return {
        "sector_name": name,
        "ticker_count": tickers,
        "performance": {7: perf_7d, 30: perf_30d, 90: 1.0, 365: 5.0, 1825: 50.0},
    }


def sub(sector_name, sub_name, pct_30d, tickers=3):
    return {
        "sector_name": sector_name,
        "sub_industry_name": sub_name,
        "ticker_count": tickers,
        "avg_change_pct_30d": pct_30d,
    }


def market(baseline_30d=2.0, baseline_7d=0.5, sectors=(), subs=()):
    return {
        "baseline": {7: baseline_7d, 30: baseline_30d},
        "sector_perf": {s["sector_name"]: s for s in sectors},
        "subindustry_perf": list(subs),
    }


# --- _detect_outliers ------------------------------------------------------


def test_no_baseline_means_nothing_can_be_flagged(agent):
    data = market(sectors=[sector("Energy", -20.0)])
    data["baseline"] = {7: 0.5}  # no 30d window
    assert agent._detect_outliers(data) == []


def test_sectors_within_threshold_are_not_flagged(agent):
    data = market(sectors=[sector("Energy", 2.0 + OUTLIER_THRESHOLD - 0.01)])
    assert agent._detect_outliers(data) == []


def test_threshold_is_inclusive_at_exactly_the_limit(agent):
    data = market(baseline_30d=2.0, sectors=[sector("Energy", 2.0 + OUTLIER_THRESHOLD)])
    assert [f["sector"] for f in agent._detect_outliers(data)] == ["Energy"]


def test_selloff_is_flagged_with_worst_subindustry_as_driver(agent):
    data = market(
        sectors=[sector("Energy", -6.0)],
        subs=[
            sub("Energy", "Oil & Gas Drilling", -12.0),
            sub("Energy", "Coal & Consumable Fuels", -3.0),
            sub("Utilities", "Electric Utilities", -50.0),  # other sector: ignored
        ],
    )
    (flag,) = agent._detect_outliers(data)
    assert flag["direction"] == "selloff"
    assert flag["vs_market_30d"] == pytest.approx(-8.0)
    assert flag["driver_subsector"] == "Oil & Gas Drilling"
    assert flag["performance"]["30d"] == -6.0


def test_growth_is_flagged_with_best_subindustry_as_driver(agent):
    data = market(
        sectors=[sector("Information Technology", 10.0)],
        subs=[
            sub("Information Technology", "Semiconductors", 18.0),
            sub("Information Technology", "IT Consulting & Other Services", 4.0),
        ],
    )
    (flag,) = agent._detect_outliers(data)
    assert flag["direction"] == "growth"
    assert flag["driver_subsector"] == "Semiconductors"


def test_sector_without_subindustries_has_no_driver(agent):
    data = market(sectors=[sector("Energy", -6.0)])
    (flag,) = agent._detect_outliers(data)
    assert flag["driver_subsector"] is None


def test_selloff_acceleration_when_recent_week_is_worse_than_the_month(agent):
    # vs market: 30d = -8.0, 7d = -9.0 - 0.5 = -9.5 (worse) -> accelerating
    data = market(sectors=[sector("Energy", -6.0, perf_7d=-9.0)])
    (flag,) = agent._detect_outliers(data)
    assert flag["acceleration"] is True


def test_no_acceleration_when_recent_week_is_milder(agent):
    data = market(sectors=[sector("Energy", -6.0, perf_7d=-1.0)])
    (flag,) = agent._detect_outliers(data)
    assert flag["acceleration"] is False


def test_growth_acceleration(agent):
    data = market(sectors=[sector("Information Technology", 10.0, perf_7d=12.0)])
    (flag,) = agent._detect_outliers(data)
    assert flag["acceleration"] is True


def test_results_sorted_worst_selloff_first_then_strongest_growth(agent):
    data = market(
        sectors=[
            sector("Information Technology", 12.0),
            sector("Energy", -6.0),
            sector("Utilities", -15.0),
            sector("Financials", 2.5),  # inside threshold
        ]
    )
    flagged = [f["sector"] for f in agent._detect_outliers(data)]
    assert flagged == ["Utilities", "Energy", "Information Technology"]


def test_sector_missing_30d_data_is_skipped(agent):
    s = sector("Energy", 0.0)
    del s["performance"][30]
    assert agent._detect_outliers(market(sectors=[s])) == []


# --- _get_subsectors_for_investigation -------------------------------------


def test_subsectors_only_from_flagged_sectors_and_beyond_threshold(agent):
    flagged = [{"sector": "Energy"}]
    subs = [
        sub("Energy", "Oil & Gas Drilling", -12.0),   # -14 vs market: kept
        sub("Energy", "Coal & Consumable Fuels", 1.0),  # -1 vs market: dropped
        sub("Utilities", "Electric Utilities", -40.0),  # sector not flagged: dropped
    ]
    result = agent._get_subsectors_for_investigation(flagged, subs, baseline_30d=2.0)
    assert [r["subsector"] for r in result] == ["Oil & Gas Drilling"]
    assert result[0]["direction"] == "selloff"
    assert "-14.0% vs market" in result[0]["reason"]


def test_subsector_with_no_data_is_treated_as_flat(agent):
    flagged = [{"sector": "Energy"}]
    subs = [sub("Energy", "Oil & Gas Drilling", None)]
    # flat (0.0) vs a +10 baseline is a -10 deviation
    result = agent._get_subsectors_for_investigation(flagged, subs, baseline_30d=10.0)
    assert result[0]["vs_market_30d"] == pytest.approx(-10.0)


# --- LLM step is skipped when there is nothing to report -------------------


def test_notes_skip_the_llm_when_nothing_is_flagged(agent):
    class Boom:
        def __getattr__(self, name):
            raise AssertionError("LLM must not be called when nothing is flagged")

    agent.client = Boom()
    notes = agent._write_notes([], [], market())
    assert "No sectors outside threshold" in notes


# --- _gather_market_data ---------------------------------------------------


class FakeConn:
    def __init__(self, responses):
        self.responses = responses

    async def fetch(self, sql):
        return self.responses[sql]


class FakePool:
    def __init__(self, responses):
        self.conn = FakeConn(responses)

    def acquire(self):
        conn = self.conn

        class Ctx:
            async def __aenter__(self_inner):
                return conn

            async def __aexit__(self_inner, *exc):
                return False

        return Ctx()


async def test_gather_market_data_shapes_rows_and_converts_decimals(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    responses = {
        sentinel_agent.MARKET_BASELINE_SQL: [
            {"window_days": 7, "avg_change_pct": Decimal("0.5")},
            {"window_days": 30, "avg_change_pct": Decimal("2.0")},
        ],
        sentinel_agent.SECTOR_PERFORMANCE_SQL: [
            {"sector_name": "Energy", "window_days": 7, "avg_change_pct": Decimal("-1.5"), "ticker_count": 22},
            {"sector_name": "Energy", "window_days": 30, "avg_change_pct": Decimal("-6.0"), "ticker_count": 22},
            {"sector_name": "Utilities", "window_days": 30, "avg_change_pct": None, "ticker_count": 30},
        ],
        sentinel_agent.SUBINDUSTRY_PERFORMANCE_SQL: [
            {
                "sector_name": "Energy",
                "sub_industry_name": "Oil & Gas Drilling",
                "ticker_count": 3,
                "avg_change_pct_30d": Decimal("-12.0"),
            }
        ],
    }
    agent = SentinelAgent(pool=FakePool(responses))

    data = await agent._gather_market_data()

    assert data["baseline"] == {7: 0.5, 30: 2.0}
    assert all(isinstance(v, float) for v in data["baseline"].values())
    assert data["sector_perf"]["Energy"]["performance"] == {7: -1.5, 30: -6.0}
    assert data["sector_perf"]["Energy"]["ticker_count"] == 22
    assert data["sector_perf"]["Utilities"]["performance"] == {30: None}
    assert data["subindustry_perf"][0]["avg_change_pct_30d"] == -12.0
