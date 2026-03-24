from typing import List, Dict, Optional
import numpy as np
from dataclasses import dataclass
from enum import Enum

class SwarmRole(Enum):
    SCOUT = 'scout'
    WORKER = 'worker'
    COORDINATOR = 'coordinator'
    RESERVE = 'reserve'

@dataclass
class SwarmAgent:
    id: str
    role: SwarmRole
    position: np.ndarray
    capabilities: List[str]
    current_task: Optional[str] = None
    energy_level: float = 100.0

class SwarmCoordinator:
    def __init__(self):
        self.agents: Dict[str, SwarmAgent] = {}
        self.tasks: Dict[str, float] = {}  # task_id -> priority
        self.role_distributions = {
            SwarmRole.SCOUT: 0.2,
            SwarmRole.WORKER: 0.6,
            SwarmRole.COORDINATOR: 0.1,
            SwarmRole.RESERVE: 0.1
        }

    def register_agent(self, agent_id: str, capabilities: List[str], position: np.ndarray) -> None:
        role = self._assign_optimal_role()
        self.agents[agent_id] = SwarmAgent(
            id=agent_id,
            role=role,
            position=position,
            capabilities=capabilities
        )

    def _assign_optimal_role(self) -> SwarmRole:
        current_distribution = self._get_role_distribution()
        
        # Find most needed role based on target distribution
        max_deficit = -1
        chosen_role = SwarmRole.RESERVE
        
        for role in SwarmRole:
            target = self.role_distributions[role]
            current = current_distribution.get(role, 0)
            deficit = target - current
            
            if deficit > max_deficit:
                max_deficit = deficit
                chosen_role = role
                
        return chosen_role

    def _get_role_distribution(self) -> Dict[SwarmRole, float]:
        total = len(self.agents) or 1
        distribution = {}
        
        for role in SwarmRole:
            count = sum(1 for agent in self.agents.values() if agent.role == role)
            distribution[role] = count / total
            
        return distribution

    def add_task(self, task_id: str, priority: float) -> None:
        self.tasks[task_id] = priority
        self._optimize_task_allocation()

    def _optimize_task_allocation(self) -> None:
        # Sort tasks by priority
        sorted_tasks = sorted(
            self.tasks.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Find available workers
        available_workers = [
            agent for agent in self.agents.values()
            if agent.role == SwarmRole.WORKER and agent.current_task is None
        ]
        
        # Assign highest priority tasks to available workers
        for task_id, _ in sorted_tasks:
            if not available_workers:
                break
                
            worker = available_workers.pop(0)
            worker.current_task = task_id

    def update_agent_status(self, agent_id: str, position: np.ndarray, energy_level: float) -> None:
        if agent_id in self.agents:
            self.agents[agent_id].position = position
            self.agents[agent_id].energy_level = energy_level
            
            # Reassign role if energy is critically low
            if energy_level < 20.0 and self.agents[agent_id].role != SwarmRole.RESERVE:
                self.agents[agent_id].role = SwarmRole.RESERVE
                self._optimize_task_allocation()

    def get_nearest_agents(self, position: np.ndarray, n: int = 3) -> List[SwarmAgent]:
        distances = [
            (agent, np.linalg.norm(agent.position - position))
            for agent in self.agents.values()
        ]
        distances.sort(key=lambda x: x[1])
        return [agent for agent, _ in distances[:n]]

    def get_swarm_centroid(self) -> np.ndarray:
        if not self.agents:
            return np.zeros(2)
        positions = np.array([agent.position for agent in self.agents.values()])
        return np.mean(positions, axis=0)