from uagent import UndifferentiatedAgent
from think import Machine, World, get_think_logger
from tasks.pvt import PVTTask
from tasks.vs import VSTask
from datetime import datetime


def load_text(path):
    with open(path, 'r') as f:
        return f.read()

#CK 4/16 - updated to allow for both PVT and VS task definitions

def run_pvt():
    instructions = load_text('tasks/pvt/ace.txt')
    machine = Machine()
    task = PVTTask(machine, instructions)
    agent = UndifferentiatedAgent(machine)
    World(task, agent).run(30)


def run_vs():
    instructions = load_text('tasks/vs/ace.txt')
    machine = Machine()
    task = VSTask(machine, instructions)
    agent = UndifferentiatedAgent(machine)
    World(task, agent).run(30)


if __name__ == '__main__':
    do_outlog = 1
    taskID = 2 # = PVT, 2 = VS
    taskText = ["","PVT","VS"]

    if do_outlog:
        #log now indicates taskText, and time started
        thinklog = get_think_logger(logfilename=''.join(['data/logs/',taskText[taskID],"_",datetime.now().strftime("%Y-%M-%d_%H-%M-%S"),'.txt']), uselogfile=True)


    #refactor later; easy testing for now
    if taskID == 1:
        run_pvt()
    elif taskID == 2:
        run_vs()
