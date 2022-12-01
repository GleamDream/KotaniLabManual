import numpy as np

survival = dict()

class Agent:
    def __init__(self, name = None, pos = None, vel = None, SIZE = 10, VEL = 1,
            RANGE_SEPARATE = 1, RANGE_ALIGNMENT = 1, RANGE_COHESION = 1, color = 'gray'):
        self.name = name
        self.pos = pos if pos else np.random.uniform(-SIZE, SIZE, 2)
        self.vel = vel if vel else np.random.uniform(-VEL, VEL, 2)
        self.SIZE = SIZE
        self.VEL = VEL
        self.RANGE_SEPARATE = RANGE_SEPARATE
        self.RANGE_ALIGNMENT = RANGE_ALIGNMENT
        self.RANGE_COHESION = RANGE_COHESION
        self.color = color
        self.vel_tmp = np.zeros(2)
        self.cnt = 0
    
    def distance(self, other):
        return np.linalg.norm(self.pos - other.pos)
    
    def ruleSeparate(self, others, ratio = 1):
        others = [other for other in others if self.distance(other) < self.RANGE_SEPARATE]
        v = np.zeros(2)
        for i, p in enumerate(self.pos):
            for s in [-1, 1]:
                #if p + s * 3 > s * self.SIZE:
                v[i] -= 1 / (s * self.SIZE - p)
        if not others:
            return v
        for other in others:
            d = self.pos - other.pos
            v += d / self.distance(other)
        self.vel_tmp += v / len(others) * ratio
        return v / len(others) * ratio
    
    def ruleAlignment(self, others, ratio = 1):
        others = [other for other in others if self.distance(other) < self.RANGE_ALIGNMENT]
        v = np.zeros(2)
        if not others:
            return 0
        for other in others:
            v -= self.vel - other.vel
        self.vel_tmp += v / len(others) * ratio
        return v / len(others) * ratio

    def ruleCohesion(self, others, ratio = 1):
        others = [other for other in others if self.distance(other) < self.RANGE_COHESION]
        p = np.zeros(2)
        if not others:
            return 0
        for other in others:
            p += other.pos - self.pos
        self.vel_tmp += p / len(others) * ratio
        return p / len(others) * ratio
    
    def calculate(self, others):
        self.ruleSeparate(others, 0.6)
        self.ruleAlignment(others, 0.4)
        self.ruleCohesion(others, 0.5)
    
    def update(self) -> bool:
        self.cnt += 1
        self.vel += self.vel_tmp
        v = np.linalg.norm(self.vel)
        if v > self.VEL:
            self.vel = self.vel / v * self.VEL
        elif v < self.VEL / 2:
            self.vel = self.vel / v * self.VEL / 2
        
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
        self.agents_ptr = set(map(id, self.agents))
    
    def calculate(self):
        for agent in self.agents:
            agent.calculate([other for other in self.agents if agent != other])
    
    def update(self):
        self.agents = [agent for agent in self.agents if agent.update()]
    
    def simulation(self):
        self.calculate()
        self.update()
    
    def positions(self):
        x, y = list(), list()
        for agent in self.agents:
            x.append(agent.pos[0])
            y.append(agent.pos[1])
        return np.array(x), np.array(y)

if __name__ == "__main__":
    from matplotlib import pyplot as plt
    from matplotlib import animation

    boids = Boids(AGENT = 150)
    for i in range(150):
        boids.agents.append(AgentInverse())

    fig, ax = plt.subplots(figsize = (6, 6))
    arrowprops = {
        "shrink": 0,
        "width": 1,
        "headwidth": 8,
        "headlength": 10,
        "facecolor": 'gray',
        "edgecolor": 'gray'
    }
    def plot(data):
        print(survival)
        plt.cla()
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)
        boids.simulation()
        ax.plot(*boids.positions(), "o", ms = 5, c = "k")
        for agent in boids.agents:
            arrowprops["facecolor"] = agent.color
            arrowprops["edgecolor"] = agent.color
            ax.annotate(agent.name, xy = agent.pos + agent.vel, xytext = agent.pos, arrowprops = arrowprops)
    anim = animation.FuncAnimation(fig, plot, interval = 100)
    plt.show()