import math
import random
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass

@dataclass
class SwarmAgent:
    id: str
    position: Tuple[float, float]
    capabilities: Set[str]
    current_role: str = None
    current_task: str = None

class SwarmCoordinator:
    def __init__(self):
        self.agents: Dict[str, SwarmAgent] = {}
        self.tasks: Dict[str, Dict] = {}
        self.role_requirements = {
            'scout': {'min_agents': 2, 'capabilities': {'movement', 'sensing'}},
            'worker': {'min_agents': 3, 'capabilities': {'movement', 'manipulation'}},
            'relay': {'min_agents': 2, 'capabilities': {'communication'}}
        }

    def register_agent(self, agent: SwarmAgent) -> None:
        self.agents[agent.id] = agent
        self._rebalance_roles()

    def add_task(self, task_id: str, requirements: Dict, position: Tuple[float, float]) -> None:
        self.tasks[task_id] = {
            'requirements': requirements,
            'position': position,
            'status': 'pending',
            'assigned_agents': set()
        }
        self._rebalance_tasks()

    def _calculate_agent_fitness(self, agent: SwarmAgent, role: str) -> float:
        required_capabilities = self.role_requirements[role]['capabilities']
        capability_match = len(agent.capabilities.intersection(required_capabilities)) / len(required_capabilities)
        
        # Consider current role to avoid unnecessary switching
        role_stability = 1.5 if agent.current_role == role else 1.0
        
        return capability_match * role_stability

    def _rebalance_roles(self) -> None:
        unassigned_agents = [a for a in self.agents.values() if not a.current_role]
        current_distribution = self._get_role_distribution()

        for role, requirements in self.role_requirements.items():
            needed = requirements['min_agents'] - current_distribution.get(role, 0)
            if needed <= 0:
                continue

            # Calculate fitness scores for unassigned agents
            fitness_scores = [(agent, self._calculate_agent_fitness(agent, role))
                            for agent in unassigned_agents]
            fitness_scores.sort(key=lambda x: x[1], reverse=True)

            # Assign roles to best-fitting agents
            for agent, score in fitness_scores[:needed]:
                if score > 0.5:  # Minimum fitness threshold
                    agent.current_role = role
                    unassigned_agents.remove(agent)

    def _rebalance_tasks(self) -> None:
        for task_id, task in self.tasks.items():
            if task['status'] == 'completed':
                continue

            required_roles = task['requirements'].get('roles', {})
            for role, count in required_roles.items():
                available_agents = [
                    agent for agent in self.agents.values()
                    if agent.current_role == role and agent.current_task is None
                ]

                # Sort by distance to task
                available_agents.sort(key=lambda a: self._calculate_distance(
                    a.position, task['position']))

                # Assign needed agents
                for agent in available_agents[:count]:
                    agent.current_task = task_id
                    task['assigned_agents'].add(agent.id)

    def _get_role_distribution(self) -> Dict[str, int]:
        distribution = {}
        for agent in self.agents.values():
            if agent.current_role:
                distribution[agent.current_role] = distribution.get(agent.current_role, 0) + 1
        return distribution

    def _calculate_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        return math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)

    def get_agent_status(self, agent_id: str) -> Dict:
        agent = self.agents.get(agent_id)
        if not agent:
            return {'error': 'Agent not found'}
        
        return {
            'id': agent.id,
            'position': agent.position,
            'role': agent.current_role,
            'task': agent.current_task,
            'capabilities': list(agent.capabilities)
        }

    def update_agent_position(self, agent_id: str, new_position: Tuple[float, float]) -> None:
        if agent_id in self.agents:
            self.agents[agent_id].position = new_position
            self._rebalance_tasks()  # Potentially reassign tasks based on new positions