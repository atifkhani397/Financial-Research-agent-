import pytest
from agent.query_analyzer import QueryAnalyzer, QueryType, AmbiguityLevel
from agent.disambiguation import DisambiguationEngine


def test_query_classification_factual_vs_analytical():
    analyzer = QueryAnalyzer()

    factual_res = analyzer.analyze("What was Tesla Q3 2023 revenue and net income?")
    assert factual_res["query_type"] == QueryType.FACTUAL_PRECISION.name

    analytical_res = analyzer.analyze("What's happening with the banks?")
    assert analytical_res["query_type"] == QueryType.ANALYTICAL_BREADTH.name


def test_ambiguity_detection_levels():
    analyzer = QueryAnalyzer()

    high_res = analyzer.analyze("What's happening with the banks?")
    assert high_res["ambiguity_level"] == AmbiguityLevel.HIGH.name

    low_res = analyzer.analyze("Research Microsoft Corporation (MSFT) financial metrics and growth outlook")
    assert low_res["ambiguity_level"] == AmbiguityLevel.LOW.name


def test_stated_assumptions_generation():
    engine = DisambiguationEngine()

    amazon_res = engine.resolve_query_ambiguity("What is Amazon doing in cloud?", ambiguity_level="MEDIUM")
    assert amazon_res["ambiguity_detected"] is True
    assert "AMZN" in amazon_res["stated_assumption"]
    assert "Amazon.com Inc." in amazon_res["stated_assumption"]


def test_private_company_non_fabrication():
    engine = DisambiguationEngine()
    disc = engine.format_private_company_disclosure("Stripe Inc.")

    assert disc["is_private"] is True
    assert "zero 10-K financial figures were fabricated" in disc["disclosure_text"]
    assert "Stripe Inc." in disc["disclosure_text"]


def test_recent_ipo_adaptation():
    engine = DisambiguationEngine()
    disc = engine.format_recent_ipo_disclosure("Arm Holdings plc", ipo_year="2023")

    assert disc["is_recent_ipo"] is True
    assert "less than 1 year of 10-K filing history" in disc["disclosure_text"]


def test_rate_of_change_flagging():
    engine = DisambiguationEngine()
    flag = engine.detect_rate_of_change("The company announced an in-progress M&A acquisition and CEO transition.")

    assert flag is not None
    assert flag["rate_of_change_detected"] is True
    assert "M&A" in flag["banner_markdown"] or "m&a" in str(flag["triggers"]).lower()
    assert "High Temporal Sensitivity Notice" in flag["banner_markdown"]
