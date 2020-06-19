import random

from think import DisplayVisual, Task


class PVTTask(Task):
    '''Psychomotor Vigilance Task'''

    def __init__(self, env, instructions=None):
        super().__init__()
        self.display = env.display
        self.keyboard = env.keyboard
        self.instructions = instructions
        self.stimulus = None

    def run(self, time=60):

        def start_trial():
            end_trial()
            self.stimulus = DisplayVisual(50, 50, 20, 20, 'text',
                                          random.choice(['X', 'O']))
            self.stimulus.set('kind', 'stimulus')
            self.stimulus.set('color', random.choice(['red', 'black']))
            self.display.add_visual(self.stimulus)

        def end_trial():
            if self.stimulus:
                self.display.remove_visual(self.stimulus)
                self.stimulus = None

        def handle_key(key):
            if key == ' ':
                end_trial()

        self.keyboard.add_type_fn(handle_key)

        if self.instructions:
            self.display.add(10, 10, 100, 100, 'instructions',
                             self.instructions)
            self.wait(10.0)

        self.display.add(10, 100, 40, 20, 'button', 'Acknowledge')

        self.wait(1.0)
        start_trial()

        while self.time() < time:
            self.wait(random.randint(2.0, 5.0))
            start_trial()
