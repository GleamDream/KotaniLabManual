import numpy as np

class Agent:
    def __init__(self, name = None, pos = None, vel = None, SIZE = 10, VEL = 1,
            RANGE_SEPARATE = 1, RANGE_ALIGNMENT = 1, RANGE_COHESION = 1, color = "gray"):
        self.name = name
        self.pos = pos if pos else np.random.uniform(-SIZE, SIZE, 2)
        self.vel = vel if vel else np.random.uniform(-VEL, VEL, 2)
        self.SIZE = SIZE
        self.VEL = VEL
        self.RANGE_SEPARATE = RANGE_SEPARATE
        self.RANGE_ALIGNMENT = RANGE_ALIGNMENT
        self.RANGE_COHESION = RANGE_COHESION
        self.vel_tmp = np.zeros(2)
        self.color = color
    
    def distance(self, other):
        return np.linalg.norm(self.pos - other.pos)
    
    def ruleSeparate(self, others, ratio = 1):
        others = [other for other in others if self.distance(other) < self.RANGE_SEPARATE]
        v = np.zeros(2)
        for i, p in enumerate(self.pos):
            for s in [-1, 1]:
                v[i] -= 1 / (s * self.SIZE - p)
        if not others:
            return v
        for other in others:
            v += self.pos - other.pos
        self.vel_tmp += v * ratio
        return v * ratio
    
    def ruleAlignment(self, others, ratio = 1):
        others = [other for other in others if self.distance(other) < self.RANGE_ALIGNMENT]
        v = np.zeros(2)
        if not others:
            return 0
        for other in others:
            v += other.vel
        self.vel_tmp += (v / len(others) - self.vel) * ratio
        return (v / len(others) - self.vel) * ratio

    def ruleCohesion(self, others, ratio = 1):
        others = [other for other in others if self.distance(other) < self.RANGE_COHESION]
        p = np.zeros(2)
        if not others:
            return 0
        for other in others:
            p += other.pos
        self.vel_tmp += (p / len(others) - self.pos) * ratio
        return (p / len(others) - self.pos) * ratio
    
    def calculate(self, others):
        self.ruleSeparate(others, 0.5)
        self.ruleAlignment(others, 0.9)
        self.ruleCohesion(others, 0.9)
    
    def update(self) -> bool:
        self.vel += self.vel_tmp
        #v = np.linalg.norm(self.vel)
        l1 = lambda x: 0.9 * x if abs(x) > self.VEL * 1.2 else x
        l2 = lambda x: 1.1 * x if abs(x) < self.VEL / 1.2 else x
        self.vel[0] = l1(l2(self.vel[0]))
        self.vel[1] = l1(l2(self.vel[1]))

        
        if (abs(self.pos + self.vel)[0] > self.SIZE):
            self.vel[0] = -self.vel[0]
        if (abs(self.pos + self.vel)[1] > self.SIZE):
            self.vel[1] = -self.vel[1]
        
        self.pos += self.vel
        self.vel_tmp = np.zeros(2)
        return True

class AgentInverse(Agent):
    def __init__(self, *args, **kwargs):
        super(AgentInverse, self).__init__(*args, **kwargs)
        self.color = kwargs.get("color", "red")
    
    def calculate(self, others):
        self.ruleSeparate(others, 0.6)
        self.ruleAlignment(others, -0.4)
        self.ruleCohesion(others, 0.5)

class Boids:
    def __init__(self, AGENT = 20):
        self.agents = [Agent() for _ in range(AGENT)]
    
    def calculate(self):
        for agent in self.agents:
            agent.calculate([other for other in self.agents if agent != other])
    
    def update(self):
        self.agents = [agent for agent in self.agents if agent.update()]
    
    def simulation(self):
        self.calculate()
        self.update()
    
    def positions(self):
        x, y, c = list(), list(), list()
        for agent in self.agents:
            x.append(agent.pos[0])
            y.append(agent.pos[1])
            c.append(agent.color)
        return (np.array(x), np.array(y)), c

if __name__ == "__main__":
    from matplotlib import pyplot as plt
    from matplotlib import animation

    boids = Boids(AGENT = 200)
    for i in range(5):
        boids.agents.append(AgentInverse("Crazy"))

    fig, ax = plt.subplots(figsize = (8, 8))
    arrowprops = {
        "shrink": 0,
        "width": 1,
        "headwidth": 8,
        "headlength": 10,
        "facecolor": 'gray',
        "edgecolor": 'gray'
    }
    def plot(data):
        plt.cla()
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)
        boids.simulation()
        pos, color = boids.positions()
        ax.scatter(*pos, marker = "o", s = 5, c = color)
        for agent in boids.agents:
            arrowprops["facecolor"] = agent.color
            arrowprops["edgecolor"] = agent.color
            ax.annotate(agent.name, xy = agent.pos + agent.vel, xytext = agent.pos, arrowprops = arrowprops)
    anim = animation.FuncAnimation(fig, plot, interval = 100)
    plt.show()