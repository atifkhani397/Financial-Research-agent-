import os
import json

# Create directories
os.makedirs("tools/schemas", exist_ok=True)
os.makedirs("tests", exist_ok=True)

tools = {
    "sec_filing_search": {
        "name": "sec_filing_search",
        "description": "Searches SEC EDGAR for official filings like 10-K or 10-Q. Use this when you need the most authoritative, Tier 1 financial data and direct management statements from official filings.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "The stock ticker symbol (e.g., AAPL)."},
                "filing_type": {"type": "string", "enum": ["10-K", "10-Q", "8-K"], "description": "The type of SEC filing."},
                "year": {"type": "integer", "description": "The year of the filing."}
            },
            "required": ["ticker", "filing_type"]
        }
    },
    "web_search": {
        "name": "web_search",
        "description": "Performs a general web search. Use this for macro trends, recent news that hasn't hit financial APIs, or general context gathering (Tier 5 reliability).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query."}
            },
            "required": ["query"]
        }
    },
    "earnings_transcript": {
        "name": "earnings_transcript",
        "description": "Fetches management commentary from earnings calls. Use this to gauge management sentiment, forward guidance, and qualitative explanations of financial results (Tier 3).",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "The stock ticker symbol."},
                "year": {"type": "integer", "description": "The year of the earnings call."},
                "quarter": {"type": "string", "enum": ["Q1", "Q2", "Q3", "Q4"], "description": "The quarter."}
            },
            "required": ["ticker", "year", "quarter"]
        }
    },
    "financial_data_api": {
        "name": "financial_data_api",
        "description": "Retrieves structured financial metrics and historical pricing data. Use this for quantitative data like P/E ratios, revenue figures, and historical prices (Tier 2).",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "The stock ticker symbol."},
                "metric": {"type": "string", "description": "The specific financial metric requested (e.g., 'revenue', 'pe_ratio')."}
            },
            "required": ["ticker", "metric"]
        }
    },
    "news_sentiment": {
        "name": "news_sentiment",
        "description": "Aggregates and scores sentiment from financial news. Use this to understand market perception and recent media coverage impact (Tier 4).",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "The stock ticker symbol."},
                "days_back": {"type": "integer", "default": 7, "description": "Number of days to look back for news."}
            },
            "required": ["ticker"]
        }
    },
    "vector_db_search": {
        "name": "vector_db_search",
        "description": "Searches the agent's long-term memory for previously chunked and stored findings. Use this to recall context from earlier in the session or past sessions.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The semantic search query."},
                "top_k": {"type": "integer", "default": 5, "description": "Number of results to return."}
            },
            "required": ["query"]
        }
    },
    "vector_db_store": {
        "name": "vector_db_store",
        "description": "Stores new findings into the agent's long-term memory. Use this to save important extracted facts for later retrieval.",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "The text content to store."},
                "metadata": {"type": "object", "description": "Associated metadata (ticker, source_type, date, etc.)."}
            },
            "required": ["content", "metadata"]
        }
    },
    "company_profile": {
        "name": "company_profile",
        "description": "Retrieves static metadata about a company. Use this to get background information, sector, industry, and executive details (Tier 2).",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "The stock ticker symbol."}
            },
            "required": ["ticker"]
        }
    },
    "peer_comparison": {
        "name": "peer_comparison",
        "description": "Fetches industry peers and comparative metrics. Use this for relative valuation and industry benchmarking (Tier 2).",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "The primary stock ticker symbol."},
                "metric": {"type": "string", "description": "The metric to compare against peers."}
            },
            "required": ["ticker", "metric"]
        }
    },
    "report_generator": {
        "name": "report_generator",
        "description": "Formats verified data into the final structured research report. Use this ONLY at the very end of the planning loop to synthesize the final output.",
        "parameters": {
            "type": "object",
            "properties": {
                "sections": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The sections of the report to generate, including title and verified content."
                }
            },
            "required": ["sections"]
        }
    },
    "fact_checker": {
        "name": "fact_checker",
        "description": "Verifies synthesized claims against the highest-tier source context available. Use this to validate conflicting information before adding it to the report.",
        "parameters": {
            "type": "object",
            "properties": {
                "claim": {"type": "string", "description": "The factual claim to verify."},
                "source_context": {"type": "string", "description": "The text from the authoritative source to check against."}
            },
            "required": ["claim", "source_context"]
        }
    },
    "calculation_engine": {
        "name": "calculation_engine",
        "description": "Performs safe math operations. Use this to calculate ratios, growth rates, or aggregates rather than attempting mental math in the LLM.",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide", "ratio", "growth_rate"], "description": "The math operation to perform."},
                "operands": {"type": "array", "items": {"type": "number"}, "description": "The numbers to operate on."}
            },
            "required": ["operation", "operands"]
        }
    }
}

for name, schema in tools.items():
    with open(f"tools/schemas/{name}.json", "w") as f:
        json.dump(schema, f, indent=4)

    stub = f'''def execute(**kwargs):
    """Stub implementation for {name}."""
    return {{
        "_mock": True,
        "tool": "{name}",
        "data": f"Structurally realistic mock data for {name}",
        "inputs": kwargs
    }}
'''
    with open(f"tools/{name}.py", "w") as f:
        f.write(stub)

with open("tools/__init__.py", "w") as f: pass
with open("tests/__init__.py", "w") as f: pass

registry = '''import os
import json
import importlib
from jsonschema import validate
from jsonschema.exceptions import ValidationError

class InputValidationError(Exception):
    pass

class ToolExecutionError(Exception):
    pass

class ToolRegistry:
    def __init__(self, schemas_dir="tools/schemas"):
        self.schemas_dir = schemas_dir
        self.schemas = {}
        self.tools = {}
        self._load_tools()

    def _load_tools(self):
        schema_files = [f for f in os.listdir(self.schemas_dir) if f.endswith(".json")]
        for filename in schema_files:
            tool_name = filename[:-5]
            with open(os.path.join(self.schemas_dir, filename), "r") as f:
                self.schemas[tool_name] = json.load(f)
            
            try:
                module = importlib.import_module(f"tools.{tool_name}")
                self.tools[tool_name] = getattr(module, "execute")
            except Exception as e:
                print(f"Warning: Failed to load tool implementation for {tool_name}: {e}")

    def get_all_schemas(self):
        return list(self.schemas.values())

    def execute_tool(self, tool_name, kwargs):
        if tool_name not in self.schemas:
            raise ToolExecutionError(f"Tool {tool_name} not found in registry.")

        schema = self.schemas[tool_name].get("parameters", {})
        
        try:
            validate(instance=kwargs, schema=schema)
        except ValidationError as e:
            raise InputValidationError(f"Input validation failed for {tool_name}: {e.message}")
            
        try:
            return self.tools[tool_name](**kwargs)
        except Exception as e:
            raise ToolExecutionError(f"Tool {tool_name} execution failed: {str(e)}")
'''
with open("tools/tool_registry.py", "w") as f:
    f.write(registry)

test = '''import pytest
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
'''
with open("tests/test_tools.py", "w") as f:
    f.write(test)
