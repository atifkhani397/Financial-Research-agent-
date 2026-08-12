import os
import json
import random
import logging
import importlib
from jsonschema import validate
from jsonschema.exceptions import ValidationError

logger = logging.getLogger("ara1.tools.tool_registry")


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
                logger.warning(f"Failed to load tool implementation for {tool_name}: {e}")

    def get_all_schemas(self):
        return list(self.schemas.values())

    def execute_tool(self, tool_name: str, kwargs: dict, simulate_failure_rate: float = 0.0) -> dict:
        if tool_name not in self.schemas:
            raise ToolExecutionError(f"Tool {tool_name} not found in registry.")

        schema = self.schemas[tool_name].get("parameters", {})

        try:
            validate(instance=kwargs, schema=schema)
        except ValidationError as e:
            raise InputValidationError(f"Input validation failed for {tool_name}: {e.message}")

        failure_rate = 0.0
        if isinstance(simulate_failure_rate, dict):
            failure_rate = simulate_failure_rate.get(tool_name, 0.0)
        elif isinstance(simulate_failure_rate, (int, float)):
            failure_rate = float(simulate_failure_rate)

        if failure_rate > 0.0 and random.random() < failure_rate:
            logger.warning(f"[SIMULATED FAILURE INJECTED] Primary tool '{tool_name}' failed (Simulated 500 API Error, rate={failure_rate}).")
            return {
                "error": f"Simulated 500 API Error for primary tool '{tool_name}'",
                "_simulated_failure": True,
                "_source": f"simulated_{tool_name}",
            }

        try:
            return self.tools[tool_name](**kwargs)
        except Exception as e:
            raise ToolExecutionError(f"Tool {tool_name} execution failed: {str(e)}")
