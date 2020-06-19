from think import Agent, Eyes, Motor, Query, Vision


class VSAgent(Agent):

    def __init__(self, env):
        """Initializes the agent"""
        super().__init__(output=True)
        self.vision = Vision(self, env.display, eyes=Eyes(self))
        self.motor = Motor(self, self.vision, env)

    def run(self, time):
        while self.time() < time:
            self.vision.wait_for(isa='letter', seen=False)
            visual = self.vision.search_for(
                Query(isa='letter', color='red', region='vs'), 'X')
            if visual:
                # self.log('target present')
                self.motor.type('w')
                self.wait(1.0)
            else:
                # self.log('target absent')
                self.motor.type('r')
                self.wait(1.0)
