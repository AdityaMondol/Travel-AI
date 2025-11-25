from typing import Dict, Any, List, Optional
from datetime import datetime
from app.agents.base_agent import BaseAgent
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class HierarchyManager:
    def __init__(self):
        self.hierarchy: Dict[str, List[str]] = {}
        self.agent_levels: Dict[str, int] = {}
        self.max_depth = 10
    
    def register_agent(self, agent: BaseAgent, parent_id: Optional[str] = None, level: int = 0):
        if level > self.max_depth:
            raise ValueError(f"Max hierarchy depth {self.max_depth} exceeded")
        
        self.agent_levels[agent.id] = level
        
        if parent_id:
            if parent_id not in self.hierarchy:
                self.hierarchy[parent_id] = []
            self.hierarchy[parent_id].append(agent.id)
        
        logger.info(f"Registered agent {agent.name} at level {level}")
    
    async def spawn_child_recursive(
        self, 
        parent: BaseAgent, 
        role: str, 
        task: str,
        max_children: int = 5
    ) -> BaseAgent:
        parent_level = self.agent_levels.get(parent.id, 0)
        child_level = parent_level + 1
        
        if child_level > self.max_depth:
            logger.warning(f"Cannot spawn child: max depth reached")
            return None
        
        current_children = len(self.hierarchy.get(parent.id, []))
        if current_children >= max_children:
            logger.warning(f"Cannot spawn child: max children ({max_children}) reached")
            return None
        
        child = await parent.spawn_child(f"{role}_{child_level}", role)
        self.register_agent(child, parent.id, child_level)
        
        return child
    
    def get_subtree(self, agent_id: str) -> List[str]:
        subtree = []
        queue = [agent_id]
        
        while queue:
            current = queue.pop(0)
            subtree.append(current)
            
            children = self.hierarchy.get(current, [])
            queue.extend(children)
        
        return subtree
    
    def promote_agent(self, agent_id: str):
        if agent_id in self.agent_levels:
            self.agent_levels[agent_id] = max(0, self.agent_levels[agent_id] - 1)
            logger.info(f"Promoted agent {agent_id} to level {self.agent_levels[agent_id]}")
    
    def demote_agent(self, agent_id: str):
        if agent_id in self.agent_levels:
            self.agent_levels[agent_id] = min(self.max_depth, self.agent_levels[agent_id] + 1)
            logger.info(f"Demoted agent {agent_id} to level {self.agent_levels[agent_id]}")
    
    def get_hierarchy_stats(self) -> Dict[str, Any]:
        level_counts = {}
        for level in self.agent_levels.values():
            level_counts[level] = level_counts.get(level, 0) + 1
        
        return {
            "total_agents": len(self.agent_levels),
            "max_depth": max(self.agent_levels.values()) if self.agent_levels else 0,
            "level_distribution": level_counts,
            "total_relationships": sum(len(children) for children in self.hierarchy.values())
        }
