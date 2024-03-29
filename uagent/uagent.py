import re

from interpreter import Interpreter
from ontology import OntologyMemory
from think import (Agent, Audition, Chunk, Language, Memory, Motor, Query,
                   Vision)


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

    def click(self, action, context):
        visual = context.get('visual')
        self.agent.motor.point_and_click(visual)


class UndifferentiatedAgent(Agent):

    def __init__(self, env, output=True,stopOldServer=False,owlFile='uagent.owl'):
        super().__init__(output=output)

        #basic pass-ins for now for speed of testing
        self.memory = OntologyMemory(self,stopOldServer=stopOldServer,owlFile=owlFile)
        self.vision = Vision(self, env.display)
        self.audition = Audition(self, env.speakers)
        self.motor = Motor(self, self.vision, env)

        self.interpreter = Interpreter(self.memory)

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

        while self.time() < time:
            context = Chunk()
            for rule in self.memory.recall_ground_rules():
                self.process_rule(rule, context)
