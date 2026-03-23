import numpy as np
import networkx as nx
from typing import List

class SwarmCoordinator:
    def __init__(self, num_agents: int, comm_radius: float):
        self.num_agents = num_agents
        self.comm_radius = comm_radius
        self.positions = np.random.uniform(-1, 1, size=(num_agents, 2))
        self.velocities = np.zeros((num_agents, 2))
        self.neighbors = self.compute_neighbors()

    def compute_neighbors(self) -> List[List[int]]:
        G = nx.Graph()
        G.add_nodes_from(range(self.num_agents))
        for i in range(self.num_agents):
            for j in range(i+1, self.num_agents):
                if np.linalg.norm(self.positions[i] - self.positions[j]) <= self.comm_radius:
                    G.add_edge(i, j)
        return [list(G.neighbors(i)) for i in range(self.num_agents)]

    def update_positions(self):
        for i in range(self.num_agents):
            neighbor_positions = [self.positions[j] for j in self.neighbors[i]]
            self.velocities[i] = np.mean(neighbor_positions, axis=0) - self.positions[i]
            self.positions[i] += self.velocities[i]

    def run(self, num_steps: int):
        for _ in range(num_steps):
            self.update_positions()
            self.neighbors = self.compute_neighbors()

if __name__ == '__main__':
    coordinator = SwarmCoordinator(num_agents=50, comm_radius=0.2)
    coordinator.run(num_steps=100)
