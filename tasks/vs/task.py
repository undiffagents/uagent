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

        self.display.add(50, 200, 40, 20, 'button', 'Acknowledge')

        self.wait(1.0)
        start_trial()

        while self.time() < time:
            self.wait(random.randint(5.0, 8.0))
            start_trial()
