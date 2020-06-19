import random

from think import DisplayVisual, Task


class PVTTask(Task):
    '''Psychomotor Vigilance Task'''

    def __init__(self, env, instructions=None):
        super().__init__()
        self.display = env.display
        self.keyboard = env.keyboard
        self.instructions = instructions
        self.visual = None

    def run(self, time=60):
        self.stimulus = None

        def handle_key(key):
            if key == ' ':
                self.display.clear()
                self.visual = None

        self.keyboard.add_type_fn(handle_key)

        if self.instructions:
            self.display.add(10, 10, 100, 100, 'instructions',
                             self.instructions)
            self.wait(10.0)

        self.display.clear()
        self.display.add(10, 100, 40, 20, 'button', 'Acknowledge')

        while self.time() < time:
            self.wait(random.randint(2.0, 10.0))
            self.visual = DisplayVisual(50, 50, 20, 20, 'target',
                                        random.choice(['X', 'O']))
            self.visual.set('color', random.choice(['red', 'black']))
            self.display.add_visual(self.visual)
