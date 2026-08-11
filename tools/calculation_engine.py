"""Mock stub for calculation_engine tool."""


def execute(**kwargs):
    """Perform actual safe math operations — this one works for real."""
    operation = kwargs.get("operation", "add")
    operands = kwargs.get("operands", [])

    if not operands or len(operands) < 2:
        return {"error": "Need at least 2 operands", "_mock": True}

    try:
        if operation == "add":
            result = sum(operands)
        elif operation == "subtract":
            result = operands[0] - sum(operands[1:])
        elif operation == "multiply":
            result = 1
            for x in operands:
                result *= x
        elif operation == "divide":
            result = operands[0]
            for x in operands[1:]:
                if x == 0:
                    return {"error": "Division by zero", "_mock": True}
                result /= x
        elif operation == "ratio":
            if operands[1] == 0:
                return {"error": "Division by zero in ratio", "_mock": True}
            result = operands[0] / operands[1]
        elif operation == "growth_rate":
            if operands[0] == 0:
                return {"error": "Base value is zero", "_mock": True}
            result = (operands[1] - operands[0]) / abs(operands[0])
        else:
            return {"error": f"Unknown operation: {operation}", "_mock": True}

        return {
            "operation": operation,
            "operands": operands,
            "result": result,
            "_source": "calculation_engine",
            "_mock": True,
        }
    except Exception as e:
        return {"error": str(e), "_mock": True}
