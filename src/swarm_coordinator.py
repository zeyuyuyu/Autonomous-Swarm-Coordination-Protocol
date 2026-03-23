from typing import Dict, List, Optional
from dataclasses import dataclass
import random

@dataclass
class SwarmAgent:
    id: str
    role: str
    position: tuple
    status: str
    current_task: Optional[str] = None

@dataclass 
class Task:
    id: str
    priority: int
    requirements: List[str]
    status: str
    assigned_agents: List[str]

class SwarmCoordinator:
    def __init__(self):
        self.agents: Dict[str, SwarmAgent] = {}
        self.tasks: Dict[str, Task] = {}
        self.roles = ['scout', 'worker', 'transporter', 'defender']
    
    def register_agent(self, agent_id: str, position: tuple) -> None:
        """Register a new agent with the swarm"""
        role = random.choice(self.roles)
        self.agents[agent_id] = SwarmAgent(
            id=agent_id,
            role=role,
            position=position,
            status='idle'
        )

    def add_task(self, task_id: str, priority: int, requirements: List[str]) -> None:
        """Add a new task to the coordination system"""
        self.tasks[task_id] = Task(
            id=task_id,
            priority=priority,
            requirements=requirements,
            status='pending',
            assigned_agents=[]
        )

    def assign_tasks(self) -> None:
        """Dynamically assign tasks to available agents based on roles and priorities"""
        available_agents = [a for a in self.agents.values() if a.status == 'idle']
        pending_tasks = sorted(
            [t for t in self.tasks.values() if t.status == 'pending'],
            key=lambda x: x.priority,
            reverse=True
        )

        for task in pending_tasks:
            suitable_agents = [
                agent for agent in available_agents
                if agent.role in task.requirements
            ]

            if len(suitable_agents) >= len(task.requirements):
                selected_agents = suitable_agents[:len(task.requirements)]
                task.assigned_agents = [agent.id for agent in selected_agents]
                task.status = 'in_progress'

                for agent in selected_agents:
                    agent.status = 'busy'
                    agent.current_task = task.id
                    available_agents.remove(agent)

    def update_agent_status(self, agent_id: str, status: str) -> None:
        """Update the status of an agent and reassign tasks if needed"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.status = status
            
            if status == 'idle':
                agent.current_task = None
                self.assign_tasks()

    def get_task_status(self, task_id: str) -> Optional[str]:
        """Get the current status of a specific task"""
        return self.tasks[task_id].status if task_id in self.tasks else None

    def optimize_roles(self) -> None:
        """Dynamically optimize role distribution based on current needs"""
        role_counts = {role: 0 for role in self.roles}
        for agent in self.agents.values():
            role_counts[agent.role] += 1

        # Find underutilized roles
        total_agents = len(self.agents)
        for role, count in role_counts.items():
            if count / total_agents < 0.1:  # Less than 10% of agents
                idle_agents = [a for a in self.agents.values() 
                              if a.status == 'idle' and a.role != role]
                if idle_agents:
                    agent = random.choice(idle_agents)
                    agent.role = role
