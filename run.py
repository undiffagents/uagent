import os
import sys
from datetime import datetime

from tasks.pvt import PVTAgent, PVTTask
from tasks.vs import VSAgent, VSTask
from think import ClientWindow, Environment, Window, World, get_think_logger
from uagent import UndifferentiatedAgent


def load_text(path):
    with open(path, 'r') as f:
        return f.read()


if __name__ == '__main__':

    # set defaults
    task_name = 'pvt'
    agent_name = 'uagent'
    window_name = 'none'

    # read arguments from command line
    args = sys.argv[1:]
    while args:
        if args[0] == '--agent' and len(args) > 1:
            agent_name = args[1]
            args = args[2:]
        elif args[0] == '--task' and len(args) > 1:
            task_name = args[1]
            args = args[2:]
        elif args[0] == '--window' and len(args) > 1:
            window_name = args[1]
            args = args[2:]
        else:
            print('Unknown arguments: {}'.format(args))
            print(
                'Possible arguments: [--task {pvt,vs}] [--agent {uagent,pvt,vs}] [--window {none,socket,window}>]')
            sys.exit(1)

    # create environment
    if window_name == 'window':
        env = Environment(window=Window())
    elif window_name == 'socket':
        env = Environment(window=ClientWindow())
    elif window_name == 'none':
        env = Environment()
    else:
        print('Unknown window argument: {}'.format(window_name))
        sys.exit(1)

    # create task
    if task_name == 'pvt':
        task = (PVTTask(env, load_text('tasks/pvt/ace.txt'))
                if agent_name == 'uagent' else
                PVTTask(env))
    elif task_name == 'vs':
        task = (VSTask(env, load_text('tasks/vs/ace.txt'))
                if agent_name == 'uagent' else
                VSTask(env))
    else:
        print('Unknown task argument: {}'.format(task_name))
        sys.exit(1)

    # create agent
    if agent_name == 'uagent':
        agent = UndifferentiatedAgent(env)
    elif agent_name == 'pvt':
        agent = PVTAgent(env)
    elif agent_name == 'vs':
        agent = VSAgent(env)
    else:
        print('Unknown agent argument: {}'.format(agent_name))
        sys.exit(1)

    # 0 = don't log (console output), 1 = log (saves to /data/logs/)
    do_outlog = 1
    if do_outlog:
        #log now indicates taskText, and time started
        thinklog = get_think_logger(logfilename=''.join(
            ['data/logs/', task_name, "_", datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), '.txt']), uselogfile=True)

    # run simulation
    World(task, agent).run(30)
