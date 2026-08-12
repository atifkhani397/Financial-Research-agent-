"""
ARA-1 API Tool Registry Routes (Day 16)
Returns live tool registry schemas, descriptions, and usage metadata.
"""

from typing import List
from fastapi import APIRouter
from api.schemas import ToolItem

router = APIRouter(prefix="/api/tools", tags=["Tool Registry"])

SOURCE_TIER_MAP = {
    "sec_filing_search": "Tier 1 (SEC EDGAR)",
    "company_profile": "Tier 2 (Financial API)",
    "financial_data_api": "Tier 2 (Financial API)",
    "peer_comparison": "Tier 2 (Financial API)",
    "earnings_transcript": "Tier 3 (Transcripts)",
    "news_sentiment": "Tier 4 (News Outlets)",
    "web_search": "Tier 5 (General Web)",
    "vector_db_search": "Internal (Memory)",
    "vector_db_store": "Internal (Memory)",
    "calculation_engine": "Internal (Deterministic)",
    "fact_checker": "Internal (Validation)",
    "report_generator": "Internal (Synthesis)",
}


@router.get("", response_model=List[ToolItem])
async def get_tool_registry():
    """Returns the live tool registry with descriptions, parameter schemas, and source tiers."""
    from tools.tool_registry import ToolRegistry
    registry = ToolRegistry()
    all_schemas = registry.get_all_schemas()

    tool_items = []
    for schema in all_schemas:
        name = schema.get("name", "unknown")
        desc = schema.get("description", "No description.")
        params = schema.get("parameters", {})
        tier = SOURCE_TIER_MAP.get(name, "Internal")

        tool_items.append(
            ToolItem(
                name=name,
                description=desc,
                parameters=params,
                source_tier=tier,
                usage_count=0
            )
        )

    return tool_items
