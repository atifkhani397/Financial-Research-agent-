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
    assert result["tool"] == "sec_filing_search"

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
    assert result["inputs"]["query"] == "AI trends"

def test_stub_earnings_transcript():
    registry = ToolRegistry()
    result = registry.execute_tool("earnings_transcript", {"ticker": "NVDA", "year": 2023, "quarter": "Q3"})
    assert result["_mock"] is True
    assert result["inputs"]["ticker"] == "NVDA"
