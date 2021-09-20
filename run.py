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

    #script control flags
    do_outlog = 1 # 0 prints to console, 1 records to /data/logs
    simulateRules = 0 #1 for testing, 0 for use interpreter
    stopOldServer = 1 #1 to re-initialize Ontology every run

    # Default Settings
    # runtime = 300
    runtime = 30
    # task_name = 'vs'
    task_name = 'pvt'
    agent_name = 'uagent'
    window_name = 'none'

    owlFile = 'uagent.owl'

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
        elif args[0] == '--runtime' and len(args) > 1:
            runtime = args[1]
            args = args[2:]
        elif args[0] == '--log' and len(args) > 1:
            do_outlog = args[1]
            args = args[2:]
        else:
            print('Unknown arguments: {}'.format(args))
            print(
                'Possible arguments: [--task {pvt,vs}] [--agent {uagent,pvt,vs}] [--window {none,window,<host>}]')
            sys.exit(1)


    # create window (if needed)
    if window_name == 'window':
        window = Window(size=(300, 300), title='Task Window')
    elif window_name == 'none':
        window = None
    else:
        window = ClientWindow(host=window_name)

    # create environment
    env = Environment(window=window)

    #'tasks/pvt/ace.txt'
    # curInst = 'tasks/pvt/ace.txt'
    # typoInst = 'tasks/pvt/gaptests/typo.txt'
    curInst = 'tasks/pvt/gaptests/pacebar.txt'
    # create task
    if task_name == 'pvt':
        task = (PVTTask(env, load_text(curInst))
                if agent_name == 'uagent' else
                PVTTask(env))
    elif task_name == 'vs':
        task = (VSTask(env, load_text('tasks/vs/ace.txt'))
                if agent_name == 'uagent' else
                VSTask(env))
    else:
        print('Unknown task argument: {}'.format(task_name))
        sys.exit(1)

    # 0 = console output, 1 = record log (saves to /data/logs/)
    if do_outlog:
        output = get_think_logger(name='think',
            logfilename=''.join(['data/logs/', task_name, "_", datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), '.txt']), uselogfile=True)
    else:
        output = True

# def get_think_logger(name='think',
#                      logfilename='outfile.txt',
#                      uselogfile=False,
#                      formats='%(time)12.3f      %(source)-18s      %(message)s',
#                      level=logging.DEBUG):

    # create agent
    # def __init__(self, env, output=True,stopOldServer=False,owlFile='uagent.owl'):
    if agent_name == 'uagent':
        # agent = UndifferentiatedAgent(env,output=output,stopOldServer=stopOldServer,owlFile=owlFile)
        agent = UndifferentiatedAgent(env,output=output,stopOldServer=stopOldServer,owlFile=owlFile,simulateRules=simulateRules)
    elif agent_name == 'pvt':
        agent = PVTAgent(env,output=output)
    elif agent_name == 'vs':
        agent = VSAgent(env,output=output)
    else:
        print('Unknown agent argument: {}'.format(agent_name))
        sys.exit(1)

    # run simulation
    print(''.join(['\nSTARTING SIMULATION. \nTASK: ', task_name, '\nAGENT: ', agent_name, '\nRUNTIME: ', str(runtime),'\n'] ),end='\n')

    world = World(task, agent)
    # world.run(runtime, real_time=(window is not None))
    world.run(runtime)

    print(''.join(['\nSIMULATION COMPLETE.\n']),end='\n')
