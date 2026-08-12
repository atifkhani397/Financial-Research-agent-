"""
ARA-1 API Routes Subpackage (Day 16)
Exposes REST routers for research queries, challenges, tool registry, memory search, evaluation metrics, and trace gallery.
"""

from api.routes.research import router as research_router
from api.routes.challenges import router as challenges_router
from api.routes.tools import router as tools_router
from api.routes.memory import router as memory_router
from api.routes.evaluation import router as evaluation_router
from api.routes.traces import router as traces_router

__all__ = [
    "research_router",
    "challenges_router",
    "tools_router",
    "memory_router",
    "evaluation_router",
    "traces_router",
]
