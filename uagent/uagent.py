import re

from interpreter import Interpreter
from ontology import Ontology
from think import (Agent, Audition, Aural, Chunk, Hands, Item, Language,
                   Memory, Mousing, Query, Typing, Vision)


class UndifferentiatedAgent(Agent):

    def __init__(self, machine, output=True):
        """Initializes the agent"""
        super().__init__(output=True)
        self.vision = Vision(self, machine.display)
        self.audition = Audition(self)
        self.hands = Hands(self)
        self.mousing = Mousing(self, machine.mouse, self.vision, self.hands)
        self.typing = Typing(self, machine.keyboard, self.hands)

        self.ontology = Ontology().load()
        self.interpreter = Interpreter(self.ontology)

        self.language = Language(self)
        self.language.add_interpreter(
            lambda ace: self.interpreter.interpret_ace(ace))

        # self.instruction = Instruction(
        #     self, self.memory, self.audition, self.language)
        # self.instruction.add_executor(self.execute)

    # def _interpret_predicate(self, text, isa='fact', last=None):
    #     chunk = None
    #     (pred, args) = text.replace(')', '').split('(')
    #     args = args.split(',')
    #     if len(args) == 1:
    #         chunk = Chunk(isa=isa, predicate='isa',
    #                       subject=args[0], object=pred)
    #     elif len(args) == 2:
    #         chunk = Chunk(isa=isa, predicate=pred,
    #                       subject=args[0], object=args[1])
    #     if chunk:
    #         if last:
    #             chunk.set('last', last.id)
    #         self.memory.store(chunk)
    #     return chunk

    # def _interpret_rule(self, text):
    #     lhs, rhs = text.split('=>')
    #     pred_pat = re.compile(r'[A-Za-z_-]+\([A-Za-z_,-]*\)')

    #     rule = Chunk(isa='rule')
    #     self.memory.store(rule)

    #     last = rule
    #     for t in pred_pat.findall(lhs):
    #         chunk = self._interpret_predicate(t, isa='condition', last=last)
    #         last = chunk

    #     last = rule
    #     for t in pred_pat.findall(rhs):
    #         chunk = self._interpret_predicate(t, isa='action', last=last)
    #         last = chunk

    #     return rule

    # def _interpret_drs(self, text):
    #     text = text.replace(' ', '')
    #     if text.find('=>') >= 0:
    #         return self._interpret_rule(text)
    #     else:
    #         return self._interpret_predicate(text)

    # def interpret(self, words):
    #     return self._interpret_drs(''.join(words))

    # def _deep_find(self, isa):
    #     visual = self.vision.find(isa=isa, seen=False)
    #     if visual:
    #         return visual
    #     else:
    #         part_of = self.memory.recall(predicate='isPartOf', object=isa)
    #         if part_of:
    #             return self._deep_find(part_of.subject)
    #         else:
    #             return None

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

    def has_action(self, rule):
        for fact in rule.rhs:
            if fact.pred == 'press':
                return True
        return False

    def run(self, time=60):

        instr_visual = self.vision.wait_for(isa='instructions')
        instructions = self.vision.encode(instr_visual)
        self.language.interpret(instructions)

        while self.time() < time:
            for rule in self.ontology.get_ground_rules():
                if self.has_action(rule):
                    print(rule)
                self.wait(1.0)
