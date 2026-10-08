"""
backend.app.knowledge - LeafLens Condition Knowledge & Safe Advisory Module
Deterministic, source-backed agricultural reference layer.
"""

from .service import ConditionKnowledgeService, knowledge_service, get_condition_knowledge

__all__ = [
    "ConditionKnowledgeService",
    "knowledge_service",
    "get_condition_knowledge",
]
