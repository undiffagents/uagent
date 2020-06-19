from think import Agent, Eyes, Motor, Vision


class PVTAgent(Agent):

    def __init__(self, env):
        """Initializes the agent"""
        super().__init__(output=True)
        self.vision = Vision(self, env.display, eyes=Eyes(self))
        self.motor = Motor(self, self.vision, env)

    def run(self, time=60):
        while self.time() < time:
            visual = self.vision.wait_for(
                isa='letter', region='pvt', seen=False)
            self.vision.start_encode(visual)
            self.motor.type(' ')
            self.vision.get_encoded()
