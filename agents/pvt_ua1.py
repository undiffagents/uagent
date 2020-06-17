# %% Main Task
# Undifferentiated Agent, v1
# Should be run with uagent/think-ua/ as the current working directory
#
# CK 2020-01-23
# Updated logging:
# 'do_outlog = True' (first line in main code), logging is sent to a textfile
# ('log#.txt', # = number of existing logs + 1) in the logs folder (logs/).
# 'do_outlog = False' defaults back to original script design (logs to console)

import glob
import importlib
import logging
import os

from tasks.pvt import PVTTask
from think import Environment, World, get_think_logger
from ua import UndifferentiatedAgent

if __name__ == "__main__":

    do_outlog = False

    def run_agent():
        env = Environment()
        task = PVTTask(env)
        agent = UndifferentiatedAgent(env)
        World(task, agent).run(60)

    if do_outlog:
        #should be robust across computers and OSes
        
        curlog = os.path.join('data','logs', 'log' +
                              str(1+len(glob.glob(os.path.join('data','logs', 'log*.txt')))) + '.txt')
        thinklog = get_think_logger(logfilename=curlog, uselogfile=True)

        run_agent()

        #shutdown and reset logging - faster to implement than updating/fixing handlers between executions.
        logging.shutdown()
        importlib.reload(logging)

    else:
        run_agent()


# %%
#comparison of instructions for ease of ref

#ORIGINAL:
#OWL_INSTRUCTIONS = [
#    'task(Psychomotor-Vigilance)',
#    'button(Acknowledge)',
#    'box(Box)',
#    'target(Target)',
#    'letter(Letter)',
#    'subject(Subject)',
#    'isPartOf(Box,Psychomotor-Vigilance)',
#    'isPartOf(Target,Psychomotor-Vigilance)',
#    'isPartOf(Letter,Target)',
#    # 'hasProperty(Psychomotor-Vigilance,active)=>appearsIn(Target,Box)',
#    'appearsIn(Target,Box)=>click(Subject,Acknowledge),remember(Subject,Letter)',
#    'done(Psychomotor-Vigilance)'
#]

#PROCESSED:
#task(Psychomotor-vigilance)
#button(Acknowledge)
#box(Box)
#target(Target)
#isPartOf(Acknowledge,Psychomotor-vigilance)
#isPartOf(Box,Psychomotor-vigilance)
#isPartOf(Target,Psychomotor-vigilance)
#target(X) => letter(X)
#appearsIn(Target,Box) => click(Subject,Acknowledge),remember(Subject,Target)
#hasProperty(Psychomotor-vigilance,Active) => appearsIn(Target,Box)
#done(Psychomotor-vigilance)
