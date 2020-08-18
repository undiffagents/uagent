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

    def run(self, time=30):

        def start_trial():
            end_trial()
            self.stimulus = DisplayVisual(140, 130, 20, 20, 'letter',
                                          random.choice(['X', 'O']))
            self.stimulus.set('region', 'pvt')
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
            visual = DisplayVisual(50, 50, 200, 200, 'text', self.instructions)
            visual.set('multiline', True)
            self.display.add_visual(visual)
            self.wait(10.0)
            self.display.clear()

        self.display.add(20, 20, 260, 260, 'rectangle', '')
        self.display.add(80, 240, 101, 30, 'button', 'Acknowledge')
        self.display.add(180, 240, 40, 30, 'button', 'sb')

        self.wait(1.0)
        start_trial()

        while self.time() < time:
            self.wait(random.randint(2.0, 5.0))
            start_trial()
