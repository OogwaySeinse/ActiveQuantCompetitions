from datetime import date, datetime, timezone

from scraper.normalize import (
    build_record,
    canonicalize_url,
    infer_category,
    is_active_competition,
    is_quant_competition,
    parse_date,
    parse_prize,
)


def test_parse_prize_usd_and_crypto():
    display, usd, curr = parse_prize("$100,000")
    assert display == "$100,000"
    assert usd == 100000.0
    assert curr == "USD"

    display_usdc, usd_usdc, curr_usdc = parse_prize("100,000 $USDC")
    assert usd_usdc == 100000.0
    assert curr_usdc in ("USD", "USDC")

    display_k, usd_k, _ = parse_prize("30k $USDC and Ongoing Mining Rewards")
    assert usd_k == 30000.0

    display_eur, usd_eur, curr_eur = parse_prize("€30,000")
    assert curr_eur == "EUR"
    assert usd_eur > 30000.0
    assert "~$" in display_eur

    display_know, usd_know, _ = parse_prize("Knowledge")
    assert display_know == "Knowledge"
    assert usd_know == 0.0


def test_parse_date_formats():
    now = datetime(2026, 10, 17, tzinfo=timezone.utc)
    assert parse_date("2026-11-30", reference_now=now) == "2026-11-30"
    assert parse_date("Nov 15, 2026", reference_now=now) == "2026-11-15"
    assert parse_date("10 days left", reference_now=now) == "2026-10-27"
    assert parse_date("Ongoing", reference_now=now) is None


def test_is_active_competition_filtering():
    ref = date(2026, 10, 17)
    active, status, days = is_active_competition("2026-10-10", today=ref)
    assert active is False
    assert status == "ended"

    active2, status2, days2 = is_active_competition("2026-10-20", today=ref)
    assert active2 is True
    assert status2 == "ending_soon"
    assert days2 == 3

    active3, status3, days3 = is_active_competition("2026-12-31", today=ref)
    assert active3 is True
    assert status3 == "active"
    assert days3 == 75


def test_is_quant_competition_filter():
    # True positives
    assert is_quant_competition("Predict Price Movements from Limit Order Book Data", source_name="mlcontests") is True
    assert is_quant_competition("ADIA Lab Structural Break Challenge", source_name="crunchdao") is True
    assert is_quant_competition("Asset Allocation Performance forecasting", organizer="QRT", source_name="ens") is True
    assert is_quant_competition("Memecoins: Pump or Dump? Predict Pump.fun Launches on Solana", source_name="kaggle") is True
    assert is_quant_competition("Credit Risk modelling (CRM)", source_name="kaggle") is True

    # False positives that must be excluded
    assert is_quant_competition(
        "The Pokémon Company - PTCG AI Battle Challenge Playground",
        source_name="kaggle",
    ) is False
    assert is_quant_competition(
        "Bias Bounty Mapping Equity Challenge",
        source_name="zindi",
    ) is False
    assert is_quant_competition(
        "Autoimmune Disease Machine Learning Challenge #3 - Broad Obesity",
        source_name="crunchdao",
    ) is False
    assert is_quant_competition(
        "Property price prediction challenge 2026_Closed",
        source_name="kaggle",
    ) is False


def test_infer_quant_categories():
    assert infer_category("Predict Price Movements from Limit Order Book Data", "", []) == "Market Microstructure & HFT"
    assert infer_category("BTC Implied Volatility Prediction Competition", "Deribit DVOL", []) == "Crypto, DeFi & Digital Assets"
    assert infer_category("CME Group University Futures Trading Challenge", "", []) == "Macro, Commodities & Derivatives"
    assert infer_category("Xentiment: Social Sentiment Trading Signals", "", []) == "Financial NLP & Sentiment"
    assert infer_category("InsurPrime: Can You Guess the Insurance Premium?", "", []) == "Credit, Risk & Insurance"
    assert infer_category("McGill International Portfolio Challenge (MIPC)", "", []) == "Valuation, Portfolio & Case Arenas"
    assert infer_category("DataCrunch Equity Market Neutral #2", "Cross-sectional alpha", []) == "Alpha & Equity Prediction"
    assert infer_category("ADIA Lab Structural Break Challenge", "Time series regime shifts", []) == "Time Series & Econometrics"


def test_canonicalize_url_strips_tracking():
    raw = "https://www.hub.crunchdao.com/competitions/datacrunch-2/?utm_source=twitter&ref=mlcontests"
    assert canonicalize_url(raw) == "https://hub.crunchdao.com/competitions/datacrunch-2"


def test_build_record_returns_none_when_expired():
    rec = build_record(
        title="Expired Quant Challenge",
        platform="Kaggle",
        source="kaggle",
        url="https://kaggle.com/competitions/expired-quant",
        prize="$10,000",
        end_date="2020-01-01",
        today=date(2026, 10, 17),
    )
    assert rec is None

