import random

from think import Task

ACE_INSTRUCTIONS = \
'''Psychomotor-Vigilance is a task X1.
Acknowledge is a button X2.
X1 has a box X3 and a target X4.
X1 has a box X3.
X1 has a target X4.
X4 is a letter X5.
If X4 appears in X3 then a subject X6 clicks X2 and X6 remembers X5.
If X1 is active then X4 appears in X3.'''


# DRS_INSTRUCTIONS = [
#     'task(Psychomotor-Vigilance)',
#     'button(Acknowledge)',
#     'box(Box)',
#     'target(Target)',
#     'letter(Letter)',
#     'subject(Subject)',
#     'isPartOf(Box,Psychomotor-Vigilance)',
#     'isPartOf(Target,Psychomotor-Vigilance)',
#     'isPartOf(Letter,Target)',
#     # 'hasProperty(Psychomotor-Vigilance,active)=>appearsIn(Target,Box)',
#     'appearsIn(Target,Box)=>click(Subject,Acknowledge),remember(Subject,Letter)',
#     'done(Psychomotor-Vigilance)'
# ]


class PVTTask(Task):
    """Psychomotor Vigilance Task"""

    def __init__(self, machine, instructions=ACE_INSTRUCTIONS):
        super().__init__()
        self.display = machine.display
        self.keyboard = machine.keyboard
        self.instructions = instructions

    def run(self, time=60):

        def handle_key(key):
            self.display.clear()
            self.record('response')

        self.keyboard.add_type_fn(handle_key)

        self.display.add(10, 10, 100, 100, 'instructions', self.instructions)
        self.wait(10.0)

        while self.time() < time:
            self.wait(random.randint(2.0, 10.0))
            self.display.add(50, 50, 20, 20, 'Letter', 'A')
            self.record('stimulus')
