from uagent import UndifferentiatedAgent
from think import Machine, World
from tasks.pvt import PVTTask


def load_text(path):
    with open(path, 'r') as f:
        return f.read()


def run_pvt():
    instructions = load_text('tasks/pvt/ace.txt')
    machine = Machine()
    task = PVTTask(machine, instructions)
    agent = UndifferentiatedAgent(machine)
    World(task, agent).run(30)


if __name__ == '__main__':
    run_pvt()
