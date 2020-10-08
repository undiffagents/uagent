import re

from interpreter import Interpreter
from ontology import OntologyMemory
from think import (Agent, Audition, Chunk, Language, Memory, Motor, Query,
                   Vision)


class InstructionStep:

    def __init__(self, agent, rule):
        self.agent = agent
        self.memory = agent.memory
        self.process = agent.process
        self.rule = rule
        self.chunk = Chunk(isa='step', rule=self.rule)
        self.memory.add(self.chunk)
        self.utility = 0

    def execute(self, context):

        if self.utility <= 0:
            self.memory.recall(isa='step', rule=self.rule)

        self.process(self.rule, context)

        reward = 1  # needs improvement later
        alpha = .2
        self.utility += alpha * (reward - self.utility)


class UndifferentiatedAgent(Agent):

    def __init__(self, env, output=True):
        super().__init__(output=output)

        self.memory = Memory(self)
        self.ontology_memory = OntologyMemory(self)

        self.vision = Vision(self, env.display)
        self.audition = Audition(self, env.speakers)
        self.motor = Motor(self, self.vision, env)

        self.interpreter = Interpreter(self.ontology_memory)

        self.language = Language(self)
        self.language.add_interpreter(lambda words:
                                      self.interpreter.interpret_ace(' '.join(words)))

        #CONTROLLED VOCABULARY TERMS:
        #CK 2020-06-03: Rough implementation of controlled vocabulary.
        #Chose to put definitions here, as multiple functions already relate to actions, and I expect that to get more complicated in the future.
        #First version only includes terms THINK is already set up to use.

        #Actions that execute_action() can handle.
        self.action_list = ['press', 'click', 'remember']
        #'press' and 'remember' aren't in the Ontology.
        # "Action" CV in Ontology: 'click', 'read', 'retrieve', 'search', 'listen-for', 'watch-for'

        #Conditions that check_condition() can handle.
        self.condition_list = ['appearsOn', 'visible']
        #'appearsOn' isn't in the Ontology.
        # "Affordance" CV in the Ontology: 'clickable', 'searchable', 'retrievable', 'findable', 'audible', 'visible'

        #Not used at the moment.
        self.item_role_list = ['target', 'stimulus',
                               'distractor', 'responseButton', 'infoButton']
        #"ItemRole" in the Ontology.

        #For future implementations (trying to use other labs' instructions)
        self.agent_synonym_list = ['subject', 'participant', 'you']

    # subject(subject), screen(screen), letter(target),
    # hasProperty(present,positive), hasProperty(target,correct),
    # appearsOn(target,screen), button(present)
    # =>
    # press(subject,present)

    # button(absent), hasProperty(absent,negative),
    # letter(distractor), screen(screen),
    # appearsOn(distractor,screen), letter(distractor),
    # hasProperty(distractor,incorrect), subject(subject)
    # =>
    # press(subject,absent)

    #CK 2020-06-03: Updated for CV terms. Function output unaltered for 'press' (the only action it looked for, previously)
    def is_action(self, rule):
        for action in rule.actions:
            for potential_action in self.action_list:
                if action.pred == potential_action:
                    return True
        return False

    #CK 2020-06-03: Updated for CV terms. Function output unaltered for 'appearsOn' (the only thing it looked for, previously). Treats 'visible' as identical to 'appearsOn' at the moment.
    def check_condition(self, cond, context):
        for potential_condition in self.condition_list:
            #as more conditions are added, their cases must be coded in here.
            if cond.pred == potential_condition:
                # if cond.pred == 'appearsOn' or cond.pred == 'visible':
                #     self.think('check condition "{}"'.format(cond))
                #     isa = cond.obj(0)
                #     # visual = self.vision.find(isa=isa)
                #     visual = self.vision.search_for(Query(isa=isa), None)
                #     if visual:
                #         print('----- Found visual')
                #         context.set('visual', visual)
                #         visobj = self.vision.encode(visual)
                #         context.set(isa, visobj)
                #     else:
                #         return False
                if cond.pred == 'appearsOn':
                    self.think('check condition "{}"'.format(cond))
                    isa = cond.obj(0)
                    # visual = self.vision.find(isa=isa, seen=False)
                    visual = self.vision.wait_for(isa=isa, seen=False)
                    if visual:
                        print('----- Found {}'.format(isa))
                        context.set('visual', visual)
                        visobj = self.vision.encode(visual)
                        context.set(isa, visobj)
                    else:
                        return False
        return True

    #CK 2020-06-03: Updated for CV terms. Function output unaltered for action subject 'subject' (the only identifier it looked for, previously), and for actions 'press', 'click', and 'remember'.
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

        # while self.time() < time:
        #     context = Chunk()
        #     for rule in self.ontology_memory.recall_ground_rules():
        #         self.process(rule, context)

        steps = []
        for rule in self.ontology_memory.recall_ground_rules():
            step = InstructionStep(self, rule)
            steps.append(step)
            print(rule)

        while self.time() < time:
            context = Chunk()
            for step in steps:
                step.execute(context)
