import re

from interpreter import Interpreter
from ontology import OntologyMemory
from think import (Agent, Audition, Chunk, Language, Memory, Motor, Query,
                   Vision)


class Handler:

    def _has(self, name):
        return hasattr(self, name)

    def _get(self, name):
        return getattr(self, name, None)

    def _term(self, chunk, i):
        return chunk['term'][i]['asString']


class ConditionHandler(Handler):

    def appear(self, agent, cond, context):
        isa = self._term(cond, 0)
        # visual = self.vision.find(isa=isa, seen=False)
        visual = agent.vision.search_for(Query(isa=isa, seen=False), None)
        if visual:
            context.set('visual', visual)
            visobj = agent.vision.encode(visual)
            context.set(isa, visobj)
            return True
        else:
            return False


class ActionHandler(Handler):

    def press(self, agent, action, context):
        isa = self._term(action, 0)
        visual = agent.vision.find(isa=isa)
        if visual:
            agent.motor.point_and_click(visual)

    def click(self, agent, action, context):
        visual = context.get('visual')
        agent.motor.point_and_click(visual)


class UndifferentiatedAgent(Agent):

    def __init__(self, env, output=True):
        super().__init__(output=output)

        self.memory = OntologyMemory(self)
        self.vision = Vision(self, env.display)
        self.audition = Audition(self, env.speakers)
        self.motor = Motor(self, self.vision, env)

        self.interpreter = Interpreter(self.memory)

        self.language = Language(self)
        self.language.add_interpreter(lambda words:
                                      self.interpreter.interpret_ace(' '.join(words)))

        self.condition_handler = ConditionHandler()
        self.action_handler = ActionHandler()

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
            return handler(self, cond, context)
        else:
            return True

    def execute_action(self, action, context):
        handler = self.action_handler._get(action['name'])
        if handler:
            self.think('execute action "{}"'.format(action))
            handler(self, action, context)

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

        while self.time() < time:
            context = Chunk()
            for rule in self.memory.recall_ground_rules():
                print()
                for cond in rule.conditions:
                    print(cond)
                self.process_rule(rule, context)
