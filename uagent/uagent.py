import math
import random
import re

from interpreter import Interpreter
from ontology import OntologyMemory
from think import (Agent, Audition, Chunk, Language, Memory, Motor, Query,
                   Vision)

DEFAULT_REWARD = 20
DEFAULT_EGS = .1  # .5
DEFAULT_ALPHA = .2


class InstructionStep:

    def __init__(self, agent, rule):
        self.agent = agent
        self.memory = agent.memory
        self.process = agent.process

        self.rule = rule
        self.chunk = Chunk(isa='step', rule=self.rule)
        self.memory.add(self.chunk)

        self.utility_recall = DEFAULT_REWARD
        self.utility_execute = 0

        self.last_time = None
        self.last_time_was_recall = None

    #Use basic utility function to determine if an instruction step should be recalled from memory then executed, or simply executed
    def execute(self, context):
        self.last_time = self.agent.time()
        c_recall = math.exp(self.utility_recall / math.sqrt(2 * DEFAULT_EGS))
        c_execute = math.exp(self.utility_execute / math.sqrt(2 * DEFAULT_EGS))
        pr_recall = c_recall / (c_recall + c_execute)
        if random.random() < pr_recall:
            print('***** RECALL')
            self.memory.recall(isa='step', rule=self.rule)
            self.process(self.rule, context)
            self.last_time_was_recall = True
        else:
            print('***** EXECUTE')
            self.process(self.rule, context)
            self.last_time_was_recall = False

    #update utility values with time-based reward
    def give_reward(self, time, reward):
        if self.last_time is not None:
            reward -= (time - self.last_time)
            print(f'reward: {reward}')
            if self.last_time_was_recall:
                self.utility_recall += DEFAULT_ALPHA * \
                    (reward - self.utility_recall)
                if self.utility_execute < self.utility_recall:
                    self.utility_execute += DEFAULT_ALPHA * \
                        (self.utility_recall - self.utility_execute)
            else:
                self.utility_execute += DEFAULT_ALPHA * \
                    (reward - self.utility_execute)
        self.last_time = None
        self.last_time_was_recall = None
        print(f'u_recall: {self.utility_recall}')
        print(f'u_execute: {self.utility_execute}')


class Handler:

    def __init__(self, agent):
        self.agent = agent

    def _has(self, name):
        return hasattr(self, name)

    def _get(self, name):
        return getattr(self, name, None)

    def _arg(self, chunk, i):
        return chunk['ofItem'][i]['asString']


class ConditionHandler(Handler):

    def appear(self, cond, context):
        ''' appear(<isa>,on(screen)) '''

        isa = self._arg(cond, 0)

        # vision.find is non-blocking: it checks and returns immediately
        visual = self.agent.vision.find(isa=isa, seen=False)

        # vision.wait_for is blocking: it waits for the item to appear
        # visual = self.agent.vision.wait_for(isa=isa, seen=False)

        if visual:
            context.set('visual', visual)
            visobj = self.agent.vision.encode(visual)
            context.set(isa, visobj)
            return True
        else:
            return False


class ActionHandler(Handler):

    def press(self, action, context):
        ''' press(subject,<key>) '''

        key = self._arg(action, 1)

        if key == 'space_bar':
            key = ' '

        self.agent.motor.type(key)

    # def press(self, action, context):
    #     isa = self._arg(action, 0)
    #     visual = self.agent.vision.find(isa=isa)
    #     if visual:
    #         self.agent.motor.point_and_click(visual)

    # def click(self, action, context):
    #     visual = context.get('visual')
    #     self.agent.motor.point_and_click(visual)


class UndifferentiatedAgent(Agent):

    def __init__(self, env, output=True):
        super().__init__(output=output)

        self.memory = Memory(self)
        self.memory.latency_factor = 5.0

        self.ontology_memory = OntologyMemory(self)

        self.vision = Vision(self, env.display)
        self.audition = Audition(self, env.speakers)
        self.motor = Motor(self, self.vision, env)

        self.interpreter = Interpreter(self.ontology_memory)

        self.language = Language(self)
        self.language.add_interpreter(lambda words:
                                      self.interpreter.interpret_ace(' '.join(words)))

        self.condition_handler = ConditionHandler(self)
        self.action_handler = ActionHandler(self)

        # #Not used at the moment.
        # self.item_role_list = ['target','stimulus','distractor','responseButton','infoButton']
        # #"ItemRole" in the Ontology.

        # #For future implementations (trying to use other labs' instructions)
        # self.agent_synonym_list = ['subject','participant','you']

    def is_action(self, rule):
        for action in rule.actions:
            if self.action_handler._has(action['name']):
                return True
        return False

    def check_condition(self, cond, context):
        handler = self.condition_handler._get(cond['name'])
        if handler:
            self.think('check condition "{}"'.format(cond))
            return handler(cond, context)
        else:
            return True

    def execute_action(self, action, context):
        handler = self.action_handler._get(action['name'])
        if handler:
            self.think('execute action "{}"'.format(action))
            handler(action, context)

    def process_rule(self, rule, context):
        if self.is_action(rule):
            self.think('process rule "{}"'.format(rule))
            for cond in rule.conditions:
                if not self.check_condition(cond, context):
                    return False
            for action in rule.actions:
                self.execute_action(action, context)
            return True

    def run(self, time=60):

        instr_visual = self.vision.wait_for(isa='text')
        instructions = self.vision.encode(instr_visual)
        self.language.interpret(instructions)

        steps = []
        for rule in self.ontology_memory.recall_ground_rules():
            step = InstructionStep(self, rule)
            steps.append(step)

        def give_reward():
            for step in steps:
                step.give_reward(self.time(), DEFAULT_REWARD)

        self.motor.keyboard.add_type_fn(lambda key: give_reward())

        #Repeatedly loops through the instruction steps.
        # execute()
            # uses utility functions to determine if the rule is first recalled from memory, or simply executed.
            # In either case, the rule is then passed to process() and procedes as in the previous version.
            # CK->DARIO: I think it'd be a good idea to change the name of this (execute()) function to 'determine_action', 'utility_action' or something similar -- seems more in line with what the function is doing.
        while self.time() < time:
            context = Chunk()
            for rule in self.memory.recall_ground_rules():
                self.process_rule(rule, context)
