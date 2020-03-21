import re

from interpreter import Interpreter
from ontology import Ontology
from think import (Agent, Audition, Aural, Chunk, Hands, Item, Language,
                   Memory, Mousing, Query, Typing, Vision)


class UndifferentiatedAgent(Agent):

    def __init__(self, machine, output=True):
        super().__init__(output=output)

        self.vision = Vision(self, machine.display)
        self.audition = Audition(self)
        self.hands = Hands(self)
        self.mousing = Mousing(self, machine.mouse, self.vision, self.hands)
        self.typing = Typing(self, machine.keyboard, self.hands)

        self.ontology = Ontology().load()
        self.interpreter = Interpreter(self.ontology)

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
        for fact in rule.rhs:
            if fact.pred == 'press':
                return True
        return False

    # def _execute_condition(self, cond, context):
    #     if cond.predicate == 'appearsIn':
    #         visual = self._deep_find(cond.subject)
    #         if visual:
    #             context.set('visual', visual)
    #             visobj = self.vision.encode(visual)
    #             context.set(cond.subject, visobj)
    #             return True
    #     return False

    # def _execute_action(self, action, context):
    #     if action.subject == 'Subject':
    #         print('**************  ' + action.predicate)

    #         if action.predicate == 'click':
    #             visual = context.get('visual')
    #             self.mouse.point_and_click(visual)

    #         elif action.predicate == 'remember':
    #             pass

    # def execute(self, chunk, context):
    #     if chunk.isa == 'rule':

    #         cond = self.memory.recall(isa='condition', last=chunk.id)
    #         while cond:
    #             if not self._execute_condition(cond, context):
    #                 return False
    #             cond = self.memory.recall(isa='condition', last=cond.id)

    #         act = self.memory.recall(isa='action', last=chunk.id)
    #         while act:
    #             self._execute_action(act, context)
    #             act = self.memory.recall(isa='action', last=act.id)

    #         return True

    def run(self, time=60):

        instr_visual = self.vision.wait_for(isa='instructions')
        instructions = self.vision.encode(instr_visual)
        self.language.interpret(instructions)

        while self.time() < time:
            for rule in self.ontology.get_ground_rules():
                if self.is_action(rule):
                    print(rule)
                self.wait(1.0)
