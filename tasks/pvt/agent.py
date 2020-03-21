from think import Agent, Audition, Hands, Typing, Vision, Visual


class PVTAgent(Agent):

    def __init__(self, machine):
        """Initializes the agent"""
        super().__init__(output=True)
        self.vision = Vision(self, machine.display)
        self.typing = Typing(self, machine.keyboard, Hands(self))

    def run(self, time=60):
        while self.time() < time:
            visual = self.vision.wait_for(seen=False)
            self.vision.start_encode(visual)
            self.typing.type('j')
            self.vision.get_encoded()
