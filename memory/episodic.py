"""
ARA-1 Episodic Memory

Reflective log storing metadata on completed research sessions:
  - Session ID
  - Query & Query Type
  - Tools used, succeeded, failed
  - Strategy notes (lessons learned, best data sources for query type)
  - Success status & timestamp

Provides retrieval functions for future planning steps to consult past episodes.
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger("ara1.memory.episodic")


class EpisodicMemory:
    """Manages persistent episodic memory log and strategy retrieval."""

    def __init__(self, storage_path: Optional[str] = None):
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            project_root = Path(__file__).resolve().parent.parent
            self.storage_path = project_root / "data" / "episodic_memory.json"

        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._save_episodes([])

    def _load_episodes(self) -> List[Dict[str, Any]]:
        """Load all recorded episodes from disk."""
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load episodic memory from {self.storage_path}: {e}")
            return []

    def _save_episodes(self, episodes: List[Dict[str, Any]]) -> None:
        """Save episode list to disk."""
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(episodes, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save episodic memory to {self.storage_path}: {e}")

    def log_episode(
        self,
        session_id: str,
        query: str,
        tools_used: List[str],
        tools_succeeded: List[str],
        tools_failed: List[str],
        strategy_note: str,
        query_type: str = "general",
        success: bool = True,
    ) -> Dict[str, Any]:
        """
        Record a completed research task episode.

        Returns:
            The episode dictionary.
        """
        episodes = self._load_episodes()

        episode = {
            "episode_id": f"ep_{len(episodes) + 1:04d}",
            "session_id": session_id,
            "timestamp": time.time(),
            "query": query,
            "query_type": query_type,
            "tools_used": list(set(tools_used)),
            "tools_succeeded": list(set(tools_succeeded)),
            "tools_failed": list(set(tools_failed)),
            "strategy_note": strategy_note,
            "success": success,
        }

        episodes.append(episode)
        self._save_episodes(episodes)
        logger.info(f"Logged episode id={episode['episode_id']} session={session_id} query='{query[:40]}...'")
        return episode

    def get_similar_episodes(
        self,
        query: str,
        query_type: Optional[str] = None,
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant past episodes matching query terms or query_type.

        Returns:
            List of matching episode dicts sorted by relevance.
        """
        episodes = self._load_episodes()
        if not episodes:
            return []

        query_words = set(query.lower().split())

        scored = []
        for ep in episodes:
            score = 0
            ep_words = set(ep.get("query", "").lower().split())
            common = query_words.intersection(ep_words)
            score += len(common) * 2

            if query_type and ep.get("query_type") == query_type:
                score += 3

            if ep.get("success"):
                score += 1

            if score > 0:
                scored.append((score, ep))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [item[1] for item in scored[:top_k]]

        logger.info(f"Retrieved {len(results)} similar episodes for query='{query[:40]}...'")
        return results

    def clear(self):
        """Clear all stored episodes (for testing/reset)."""
        self._save_episodes([])
        logger.warning("Episodic memory cleared.")
