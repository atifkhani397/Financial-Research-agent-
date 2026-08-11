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
    assert result["_mock"] is True
    assert result["_source"] == "sec_filing_search"

def test_input_validation_failure_missing_required():
    registry = ToolRegistry()
    with pytest.raises(InputValidationError):
        registry.execute_tool("sec_filing_search", {"ticker": "AAPL"})

def test_input_validation_failure_wrong_type():
    registry = ToolRegistry()
    with pytest.raises(InputValidationError):
        registry.execute_tool("calculation_engine", {"operation": "add", "operands": ["not", "a", "number"]})

def test_stub_web_search():
    registry = ToolRegistry()
    result = registry.execute_tool("web_search", {"query": "AI trends"})
    assert result["_mock"] is True
    assert result["query"] == "AI trends"

def test_stub_earnings_transcript():
    registry = ToolRegistry()
    result = registry.execute_tool("earnings_transcript", {"ticker": "NVDA", "year": 2023, "quarter": "Q3"})
    assert result["_mock"] is True
    assert result["ticker"] == "NVDA"

def test_company_profile_msft():
    """Test the upgraded MSFT company profile mock data."""
    registry = ToolRegistry()
    result = registry.execute_tool("company_profile", {"ticker": "MSFT"})
    assert result["_mock"] is True
    assert result["name"] == "Microsoft Corporation"
    assert result["ceo"] == "Satya Nadella"
    assert len(result["executives"]) >= 6

def test_financial_data_api_msft():
    """Test the upgraded MSFT financial data mock."""
    registry = ToolRegistry()
    result = registry.execute_tool("financial_data_api", {"ticker": "MSFT", "metric": "overview"})
    assert result["_mock"] is True
    assert result["revenue"] == 245122000000
    assert result["pe_ratio"] == 35.2

def test_calculation_engine_actual_math():
    """Test that calculation_engine performs real math."""
    registry = ToolRegistry()
    result = registry.execute_tool("calculation_engine", {"operation": "add", "operands": [10, 20]})
    assert result["result"] == 30
    
    result = registry.execute_tool("calculation_engine", {"operation": "growth_rate", "operands": [100, 150]})
    assert abs(result["result"] - 0.5) < 0.001
