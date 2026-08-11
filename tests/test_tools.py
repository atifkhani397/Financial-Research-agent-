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

def test_calculation_engine_actual_math():
    registry = ToolRegistry()
    result = registry.execute_tool("calculation_engine", {"operation": "add", "operands": [10, 20]})
    assert result["result"] == 30
    
    result = registry.execute_tool("calculation_engine", {"operation": "growth_rate", "operands": [100, 150]})
    assert abs(result["result"] - 0.5) < 0.001
