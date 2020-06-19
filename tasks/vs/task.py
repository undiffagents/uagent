import random

from think import DisplayVisual, Task


class VSTask(Task):
    '''Visual Search Task'''

    def __init__(self, env, instructions=None):
        super().__init__()
        self.display = env.display
        self.keyboard = env.keyboard
        self.instructions = instructions
        self.stimuli = []

    def run(self, time=60):

        def create_visual(color, obj):
            visual = DisplayVisual(random.randint(30, 250), random.randint(30, 210),
                                   20, 20, 'letter', obj)
            visual.set('region', 'vs')
            visual.set('color', color)
            return visual

        def start_trial():
            end_trial()
            if random.random() < .80:
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
            if key == 'w' or key == 'r':
                end_trial()

        self.keyboard.add_type_fn(handle_key)

        if self.instructions:
            self.display.add(30, 30, 200, 200, 'text', self.instructions)
            self.wait(10.0)
            self.display.clear()

        self.display.add(20, 20, 260, 260, 'rectangle', '')
        self.display.add(50, 240, 61, 30, 'button', 'Present')
        self.display.add(110, 240, 30, 30, 'button', 'w')
        self.display.add(160, 240, 61, 30, 'button', 'Absent')
        self.display.add(220, 240, 30, 30, 'button', 'r')

        self.wait(1.0)
        start_trial()

        while self.time() < time:
            self.wait(random.randint(5.0, 8.0))
            start_trial()
