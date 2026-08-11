import pytest
from synthesis import ConflictResolver, NarrativeBuilder, SynthesisEngine


def test_source_hierarchy_weights():
    resolver = ConflictResolver()
    assert resolver.get_source_weight("sec_filing") == 1.00
    assert resolver.get_source_weight("financial_api") == 0.85
    assert resolver.get_source_weight("earnings_transcript") == 0.75
    assert resolver.get_source_weight("social_forum") == 0.50
    assert resolver.get_source_weight("news_outlet") == 0.30


def test_conflict_resolution_sec_over_news():
    resolver = ConflictResolver()
    res = resolver.resolve(
        metric_name="Revenue",
        value_a="$2.23B",
        source_a="sec_filing",
        value_b="$1.80B",
        source_b="news_outlet",
    )
    assert res["conflict_detected"] is True
    assert res["resolved_value"] == "$2.23B"
    assert res["primary_source"] == "sec_filing"
    assert "higher authority tier" in res["transparency_note"]


def test_temporal_restatement_resolution():
    resolver = ConflictResolver()
    res = resolver.resolve(
        metric_name="Net Income",
        value_a="$450M (Restated 10-K/A)",
        source_a="sec_filing",
        date_a="2024-03-15",
        value_b="$500M (Original 10-K)",
        source_b="sec_filing",
        date_b="2024-01-30",
    )
    assert res["conflict_detected"] is True
    assert res["resolved_value"] == "$450M (Restated 10-K/A)"
    assert res["resolution_method"] in ["restatement", "temporal_difference"]


def test_quantitative_triangulation():
    builder = NarrativeBuilder()

    # Small variance (< 2%) -> single triangulated value
    sources_tight = [
        {"source": "sec_filing", "value": 100.0},
        {"source": "financial_api", "value": 101.0},
    ]
    res_tight = builder.triangulate_numeric_claims("Operating Profit", sources_tight, unit="M")
    assert res_tight["is_range"] is False
    assert res_tight["confidence"] >= 0.90

    # Large variance (> 2%) -> explicit range
    sources_wide = [
        {"source": "sec_filing", "value": 100.0},
        {"source": "news_outlet", "value": 150.0},
    ]
    res_wide = builder.triangulate_numeric_claims("Operating Profit", sources_wide, unit="M")
    assert res_wide["is_range"] is True
    assert "100.00 M to 150.00 M" in res_wide["triangulated_value"]


def test_sentiment_fact_alignment_divergence():
    engine = SynthesisEngine()

    news_output = {
        "overall_sentiment": "bearish",
        "sentiment_score": -0.45,
        "headlines": ["Palantir shares slump as recent news suggests company is struggling"],
    }
    financial_output = {
        "ticker": "PLTR",
        "revenue": 2230000000.0,
        "net_income": 210000000.0,
        "operating_margin": 0.18,
    }

    alignment = engine.analyze_sentiment_fact_alignment(news_output, financial_output)
    assert alignment["divergence_detected"] is True
    assert "apparent contradiction" in alignment["detail"].lower() or "disconnect" in alignment["detail"].lower()
