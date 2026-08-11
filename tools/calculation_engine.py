"""
ARA-1 Tool: calculation_engine (Real Math & DCF Engine)

Performs deterministic, safe math operations and financial model calculations.

DCF Valuation Formula:
  PV(Cash Flows) = sum_{t=1..n} [ CF_t / (1 + r)^t ]
  Terminal Value (TV) = [ CF_n * (1 + g) ] / (r - g)
  PV(TV) = TV / (1 + r)^n
  Enterprise Value = PV(Cash Flows) + PV(TV)
  Equity Value = Enterprise Value - Net Debt
  Intrinsic Value Per Share = Equity Value / Shares Outstanding

  where:
    CF_t = projected cash flow in year t
    r = discount rate / WACC (e.g., 0.08)
    g = terminal perpetual growth rate (e.g., 0.025)
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("ara1.tools.calculation_engine")


def execute(
    operation: str = "add",
    operands: Optional[List[float]] = None,
    projected_cash_flows: Optional[List[float]] = None,
    discount_rate: float = 0.08,
    terminal_growth_rate: float = 0.025,
    net_debt: float = 0.0,
    shares_outstanding: Optional[float] = None,
    **kwargs,
) -> Dict[str, Any]:
    """Execute safe arithmetic, financial ratios, or DCF valuation model."""
    op = operation.strip().lower()
    ops = operands or []

    try:
        if op == "add":
            if len(ops) < 2:
                return {"error": "add operation requires at least 2 operands"}
            res = sum(ops)

        elif op == "subtract":
            if len(ops) < 2:
                return {"error": "subtract operation requires at least 2 operands"}
            res = ops[0] - sum(ops[1:])

        elif op == "multiply":
            if len(ops) < 2:
                return {"error": "multiply operation requires at least 2 operands"}
            res = 1.0
            for x in ops:
                res *= x

        elif op == "divide":
            if len(ops) < 2:
                return {"error": "divide operation requires at least 2 operands"}
            res = ops[0]
            for x in ops[1:]:
                if x == 0:
                    return {"error": "Division by zero"}
                res /= x

        elif op == "ratio":
            if len(ops) < 2 or ops[1] == 0:
                return {"error": "ratio operation requires 2 operands with non-zero denominator"}
            res = ops[0] / ops[1]

        elif op == "growth_rate":
            if len(ops) < 2 or ops[0] == 0:
                return {"error": "growth_rate requires [base, current] with non-zero base"}
            res = (ops[1] - ops[0]) / abs(ops[0])

        elif op == "gross_margin":
            if len(ops) < 2 or ops[0] == 0:
                return {"error": "gross_margin requires [revenue, cogs] or [revenue, gross_profit]"}
            # If ops = [revenue, gross_profit]
            if ops[1] < ops[0] and ops[1] > 0:
                res = ops[1] / ops[0]
            else:
                # If ops = [revenue, cogs]
                res = (ops[0] - ops[1]) / ops[0]

        elif op == "operating_margin":
            if len(ops) < 2 or ops[0] == 0:
                return {"error": "operating_margin requires [revenue, operating_income]"}
            res = ops[1] / ops[0]

        elif op == "net_margin":
            if len(ops) < 2 or ops[0] == 0:
                return {"error": "net_margin requires [revenue, net_income]"}
            res = ops[1] / ops[0]

        elif op == "roe":
            if len(ops) < 2 or ops[1] == 0:
                return {"error": "roe requires [net_income, shareholders_equity]"}
            res = ops[0] / ops[1]

        elif op == "current_ratio":
            if len(ops) < 2 or ops[1] == 0:
                return {"error": "current_ratio requires [current_assets, current_liabilities]"}
            res = ops[0] / ops[1]

        elif op == "dcf":
            cfs = projected_cash_flows or ops
            if not cfs:
                return {"error": "dcf operation requires projected_cash_flows list"}

            r = discount_rate
            g = terminal_growth_rate
            if r <= g:
                return {"error": "Discount rate must be strictly greater than terminal growth rate (r > g)"}

            pv_cash_flows = 0.0
            pv_breakdown = []
            for t, cf in enumerate(cfs, 1):
                pv = cf / ((1.0 + r) ** t)
                pv_cash_flows += pv
                pv_breakdown.append({"year": t, "cash_flow": cf, "pv": round(pv, 2)})

            cf_n = cfs[-1]
            terminal_value = (cf_n * (1.0 + g)) / (r - g)
            pv_terminal_value = terminal_value / ((1.0 + r) ** len(cfs))
            enterprise_value = pv_cash_flows + pv_terminal_value
            equity_value = enterprise_value - net_debt

            per_share_value = None
            if shares_outstanding and shares_outstanding > 0:
                per_share_value = equity_value / shares_outstanding

            return {
                "operation": "dcf",
                "projected_cash_flows": cfs,
                "discount_rate": r,
                "terminal_growth_rate": g,
                "pv_cash_flows": round(pv_cash_flows, 2),
                "terminal_value": round(terminal_value, 2),
                "pv_terminal_value": round(pv_terminal_value, 2),
                "enterprise_value": round(enterprise_value, 2),
                "equity_value": round(equity_value, 2),
                "intrinsic_value_per_share": round(per_share_value, 2) if per_share_value else None,
                "pv_breakdown": pv_breakdown,
                "_source": "calculation_engine_dcf",
                "_mock": False,
            }

        else:
            return {"error": f"Unsupported operation: {op}"}

        return {
            "operation": op,
            "operands": ops,
            "result": round(res, 6) if isinstance(res, float) else res,
            "_source": "calculation_engine_real",
            "_mock": False,
        }

    except Exception as e:
        logger.error(f"Calculation engine error: {e}")
        return {"error": str(e), "_source": "calculation_engine", "_mock": False}
