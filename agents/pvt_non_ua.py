from tasks.pvt import PVTAgent, PVTTask
from think import Environment, World

if __name__ == '__main__':

    # env = Environment()
    env = Environment(window=(500, 500))
    task = PVTTask(env)
    agent = PVTAgent(env)
    World(task, agent).run(60)
