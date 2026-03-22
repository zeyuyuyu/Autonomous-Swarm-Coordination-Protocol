import numpy as np

class SwarmAgent:
    def __init__(self, id, position, neighbors):
        self.id = id
        self.position = position
        self.neighbors = neighbors
        self.state = 0
        self.target_position = None
        
    def update_state(self):
        # Consensus protocol to determine target position
        neighbor_states = [n.state for n in self.neighbors]
        self.state = np.mean(neighbor_states)
        self.target_position = np.mean([n.position for n in self.neighbors], axis=0)
        
    def move(self):
        # Move towards target position
        direction = self.target_position - self.position
        self.position += 0.1 * direction
        
class SwarmCoordinator:
    def __init__(self, agents):
        self.agents = agents
        
    def step(self):
        for agent in self.agents:
            agent.update_state()
            agent.move()
            
if __name__ == '__main__':
    # Example usage
    agent1 = SwarmAgent(1, np.array([0, 0]), [])
    agent2 = SwarmAgent(2, np.array([1, 1]), [agent1])
    agent3 = SwarmAgent(3, np.array([2, 2]), [agent1, agent2])
    coordinator = SwarmCoordinator([agent1, agent2, agent3])
    
    for _ in range(10):
        coordinator.step()
        print([agent.position for agent in coordinator.agents])