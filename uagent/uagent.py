import re

from interpreter import Interpreter
from ontology import OntologyMemory
from think import (Agent, Audition, Aural, Chunk, Hands, Item, Language,
                   Memory, Mousing, Query, Typing, Vision)


class UndifferentiatedAgent(Agent):

    def __init__(self, machine, output=True):
        super().__init__(output=output)

        self.memory = OntologyMemory(self)
        self.vision = Vision(self, machine.display)
        self.audition = Audition(self)
        self.hands = Hands(self)
        self.mousing = Mousing(self, machine.mouse, self.vision, self.hands)
        self.typing = Typing(self, machine.keyboard, self.hands)

        self.interpreter = Interpreter(self.memory)

        self.language = Language(self)
        self.language.add_interpreter(self.interpreter.interpret_ace)

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

    def is_action(self, rule):
        for action in rule.actions:
            if action.pred == 'press':
                return True
        return False

    def execute_condition(self, cond, context):
        print(cond.pred)
        if cond.pred == 'appearsOn':
            isa = cond.obj(0)
            visual = self.vision.find(isa=isa)
            if visual:
                context.set('visual', visual)
                visobj = self.vision.encode(visual)
                context.set(isa, visobj)
            else:
                return False
        return True

    def execute_action(self, action, context):
        if action.obj(0) == 'subject':
            print('**************  ' + action.obj(1))

            if action.pred == 'press':
                visual = self.vision.find(isa=action.obj(1))
                self.mouse.point_and_click(visual)

            if action.pred == 'click':
                visual = context.get('visual')
                self.mouse.point_and_click(visual)

            elif action.pred == 'remember':
                pass

    def execute(self, rule, context):
        if self.is_action(rule):
            for cond in rule.conditions:
                if not self.execute_condition(cond, context):
                    return False
            for action in rule.actions:
                self.execute_action(action, context)
            return True

    def run(self, time=60):

        instr_visual = self.vision.wait_for(isa='instructions')
        instructions = self.vision.encode(instr_visual)
        self.language.interpret(instructions)

        while self.time() < time:
            context = Chunk()
            for rule in self.memory.recall_ground_rules():
                self.execute(rule, context)
                self.wait(1.0)
