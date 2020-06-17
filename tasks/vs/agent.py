from think import Agent, Motor, Vision


class VSAgent(Agent):

    def __init__(self, env):
        """Initializes the agent"""
        super().__init__(output=True)
        self.vision = Vision(self, env.display)
        self.motor = Motor(self, self.vision, env)

    def run(self, time=60):
        while self.time() < time:
            visual = self.vision.wait_for(seen=False)
            #def search_for(self, query, target):
            self.vision.search_for(visual,'isa','target') #how does query work?
            self.motor.type('j')
            self.vision.get_encoded()
