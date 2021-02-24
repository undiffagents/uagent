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

        #CONTROLLED VOCABULARY TERMS:

        #ACTIONS that execute_action() can handle.
        self.action_list = ['press', 'click', 'remember']
        #'press' and 'remember' aren't in the Ontology.
        # "Action" CV in Ontology: 'click', 'read', 'retrieve', 'search', 'listen-for', 'watch-for'

        #CONDITIONS that check_condition() can handle.
        self.condition_list = ['appearsOn', 'visible']
        #'appearsOn' isn't in the Ontology.
        # "Affordance" CV in the Ontology: 'clickable', 'searchable', 'retrievable', 'findable', 'audible', 'visible'

        #Not used at the moment.
        self.item_role_list = ['target', 'stimulus',
                               'distractor', 'responseButton', 'infoButton']
        #"ItemRole" in the Ontology.

        #AGENT NAMES
        self.agent_synonym_list = ['subject', 'participant', 'you']

    def is_action(self, rule):
        for action in rule.actions:
            for potential_action in self.action_list:
                if action.pred == potential_action:
                    return True
        return False

    def check_condition(self, cond, context):
        for potential_condition in self.condition_list:
            #as more conditions are added, their cases must be coded in here.
            if cond.pred == potential_condition:
                if cond.pred == 'appearsOn':
                    self.think('check condition "{}"'.format(cond))
                    isa = cond.obj(0)
                    visual = self.vision.find(isa=isa, seen=False)
                    # visual = self.vision.wait_for(isa=isa, seen=False)
                    if visual:
                        print('----- Found {}'.format(isa))
                        context.set('visual', visual)
                        visobj = self.vision.encode(visual)
                        context.set(isa, visobj)
                    else:
                        return False
        return True

    def execute_action(self, action, context):
        for potential_syn in self.agent_synonym_list:
            if action.obj(0) == potential_syn:
                self.think('execute action "{}"'.format(action))

                if action.pred == 'press':
                    # visual = self.vision.find(isa=action.obj(1))
                    # if visual:
                    #     self.motor.point_and_click(visual)
                    key = action.obj(1)
                    if key == 'space_bar':
                        key = ' '
                    self.motor.type(key)

                if action.pred == 'click':
                    visual = context.get('visual')
                    self.motor.point_and_click(visual)

                elif action.pred == 'remember':
                    pass

    #1) check if the rule is an action relevant to the UA
    #2) if so, check if all conditions are met
    #3) if so, execute the action
    def process(self, rule, context):
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
            for step in steps:
                step.execute(context)
