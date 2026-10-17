from datetime import date

from scraper.dedupe import deduplicate_records
from scraper.normalize import build_record


def test_deduplicate_exact_url():
    r1 = build_record(
        title="DataCrunch Equity Market Neutral #2",
        platform="CrunchDAO",
        source="crunchdao",
        url="https://hub.crunchdao.com/competitions/datacrunch-2",
        prize="1,000 $USDC/week",
        prize_usd_override=52000.0,
        end_date="2026-12-31",
        teams_count=1321,
        today=date(2026, 10, 17),
    )
    r2 = build_record(
        title="Predict Cross-sectional Equity Returns",
        platform="CrunchDAO",
        source="mlcontests",
        url="https://hub.crunchdao.com/competitions/datacrunch-2?ref=mlcontests",
        prize="$52,000",
        end_date="2026-12-31",
        description="Predict weekly cross-sectional equity returns for CrunchDAO.",
        today=date(2026, 10, 17),
    )
    assert r1 and r2
    deduped = deduplicate_records([r1, r2])
    assert len(deduped) == 1
    assert deduped[0].teams_count == 1321
    assert "cross-sectional" in deduped[0].description.lower()


def test_deduplicate_fuzzy_title_same_platform():
    r1 = build_record(
        title="Wunder Fund Connectome Limit Order Book Prediction",
        platform="Wunder Fund",
        source="quantcontests",
        url="https://wundernn.io/connectome",
        prize="$13,600",
        end_date="2026-11-15",
        today=date(2026, 10, 17),
    )
    r2 = build_record(
        title="Wunder Fund Connectome: Limit Order Book Prediction 2026",
        platform="Wunder Fund",
        source="mlcontests",
        url="https://wundernn.io/connectome-2026",
        prize="Knowledge",
        end_date="2026-11-15",
        today=date(2026, 10, 17),
    )
    assert r1 and r2
    deduped = deduplicate_records([r1, r2])
    assert len(deduped) == 1
    assert deduped[0].prize_usd == 13600.0

