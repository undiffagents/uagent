from think import Agent, Motor, Vision


class PVTAgent(Agent):

    def __init__(self, machine):
        """Initializes the agent"""
        super().__init__(output=True)
        self.vision = Vision(self, machine.display)
        self.motor = Motor(self, self.vision, machine)

    def run(self, time=60):
        while self.time() < time:
            visual = self.vision.wait_for(seen=False)
            self.vision.start_encode(visual)
            self.motor.type('j')
            self.vision.get_encoded()
