import random

from think import DisplayVisual, Task

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


class VSTask(Task):
    '''Psychomotor Vigilance Task'''

    def __init__(self, env, instructions=None):
        super().__init__()
        self.display = env.display
        self.keyboard = env.keyboard
        self.instructions = instructions
        self.stimuli = []

    def run(self, time=60):

        def create_visual(color, obj):
            visual = DisplayVisual(random.randint(20, 280), random.randint(20, 280),
                                   20, 20, 'text', obj)
            visual.set('kind', 'stimulus')
            visual.set('color', color)
            return visual

        def start_trial():
            end_trial()
            if random.random() < .8:
                self.stimuli.append(create_visual('red', 'X'))
            for _ in range(10):
                self.stimuli.append(create_visual('blue', 'X'))
                self.stimuli.append(create_visual('red', 'O'))
            random.shuffle(self.stimuli)
            self.display.add_visuals(self.stimuli)

        def end_trial():
            if self.stimuli:
                self.display.remove_visuals(self.stimuli)
                self.stimuli = []

        def handle_key(key):
            print('------ Key pressed: {}'.format(key))
            end_trial()

        self.keyboard.add_type_fn(handle_key)

        if self.instructions:
            self.display.add(10, 10, 100, 100, 'instructions',
                             self.instructions)
            self.wait(10.0)

        self.display.clear()
        self.display.add(50, 200, 40, 20, 'button', 'Acknowledge')

        self.wait(1.0)
        start_trial()

        while self.time() < time:
            self.wait(random.randint(5.0, 8.0))
            start_trial()
