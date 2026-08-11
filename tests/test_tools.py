import pytest
from tools.tool_registry import ToolRegistry, InputValidationError, ToolExecutionError


def test_registry_loads_all_tools():
    registry = ToolRegistry()
    assert len(registry.schemas) == 12
    assert len(registry.tools) == 12
    assert "sec_filing_search" in registry.schemas


def test_input_validation_success():
    registry = ToolRegistry()
    result = registry.execute_tool("sec_filing_search", {"ticker": "AAPL", "filing_type": "10-K"})
    assert result["_mock"] is False
    assert result["_source"] == "sec_edgar"
    assert result["ticker"] == "AAPL"


def test_input_validation_failure_missing_required():
    registry = ToolRegistry()
    with pytest.raises(InputValidationError):
        registry.execute_tool("sec_filing_search", {"ticker": "AAPL"})


def test_input_validation_failure_wrong_type():
    registry = ToolRegistry()
    with pytest.raises(InputValidationError):
        registry.execute_tool("calculation_engine", {"operation": "add", "operands": ["not", "a", "number"]})


def test_web_search_real():
    registry = ToolRegistry()
    result = registry.execute_tool("web_search", {"query": "Microsoft latest AI news"})
    assert result["_mock"] is False
    assert result["query"] == "Microsoft latest AI news"
    assert "results" in result


def test_news_sentiment_real():
    registry = ToolRegistry()
    result = registry.execute_tool("news_sentiment", {"ticker": "MSFT", "days_back": 7})
    assert result["_mock"] is False
    assert result["ticker"] == "MSFT"
    assert "overall_sentiment" in result


def test_company_profile_real_msft():
    registry = ToolRegistry()
    result = registry.execute_tool("company_profile", {"ticker": "MSFT"})
    assert result["_mock"] is False
    assert "Microsoft" in result.get("name", "")


def test_financial_data_api_real_msft():
    registry = ToolRegistry()
    result = registry.execute_tool("financial_data_api", {"ticker": "MSFT", "metric": "overview"})
    assert result["_mock"] is False
    assert result["ticker"] == "MSFT"
    assert result.get("revenue") is not None or result.get("price") is not None


def test_earnings_transcript_real():
    registry = ToolRegistry()
    result = registry.execute_tool("earnings_transcript", {"ticker": "TSLA", "year": 2024, "quarter": "Q3"})
    assert result["_mock"] is False
    assert result["ticker"] == "TSLA"
    assert "key_quotes" in result or "guidance" in result


def test_peer_comparison_real():
    registry = ToolRegistry()
    result = registry.execute_tool("peer_comparison", {"ticker": "TSLA", "metric": "market_cap"})
    assert result["_mock"] is False
    assert result["ticker"] == "TSLA"
    assert len(result["peers"]) >= 2


def test_calculation_engine_dcf_and_ratios():
    registry = ToolRegistry()
    result = registry.execute_tool("calculation_engine", {"operation": "add", "operands": [10, 20]})
    assert result["result"] == 30

    result = registry.execute_tool("calculation_engine", {"operation": "growth_rate", "operands": [100, 150]})
    assert abs(result["result"] - 0.5) < 0.001

    dcf_res = registry.execute_tool(
        "calculation_engine",
        {
            "operation": "dcf",
            "projected_cash_flows": [10.0, 12.0, 14.5, 17.0, 20.0],
            "discount_rate": 0.08,
            "terminal_growth_rate": 0.025,
            "net_debt": 5.0,
            "shares_outstanding": 2.0,
        },
    )
    assert dcf_res["_mock"] is False
    assert dcf_res["enterprise_value"] > 0
    assert dcf_res["intrinsic_value_per_share"] is not None


def test_fact_checker_real():
    registry = ToolRegistry()
    claim = "Tesla revenue reached 25.18 billion in Q3 2024"
    context = "Tesla reported total revenue of 25.18 billion for Q3 2024."
    result = registry.execute_tool("fact_checker", {"claim": claim, "source_context": context})
    assert result["_mock"] is False
    assert result["verified"] is True
    assert result["confidence"] >= 0.90


def test_report_generator_real():
    registry = ToolRegistry()
    result = registry.execute_tool(
        "report_generator",
        {
            "sections": [
                "Executive Summary: Tesla Q3 performance was strong.",
                "Risk Assessment: Battery supply chain volatility.",
            ]
        },
    )
    assert result["_mock"] is False
    assert "## Executive Summary" in result["markdown_report"]
    assert "## Risk Assessment" in result["markdown_report"]
