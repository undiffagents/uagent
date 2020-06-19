from think import Agent, Motor, Query, Vision


class VSAgent(Agent):

    def __init__(self, env):
        """Initializes the agent"""
        super().__init__(output=True)
        self.vision = Vision(self, env.display)
        self.motor = Motor(self, self.vision, env)

    # def run(self, time):
    #     while self.time() < time:
    #         visual = self.vision.wait_for(
    #             isa='letter', color='red', region='vs', seen=False)
    #         obj = self.vision.encode(visual) if visual else None
    #         while visual and obj != 'X':
    #             visual = self.vision.find(
    #                 isa='letter', color='red', region='vs', seen=False)
    #             obj = self.vision.encode(visual) if visual else None
    #         if obj == 'X':
    #             # self.log('target present')
    #             self.motor.type('w')
    #             self.wait(1.0)
    #         else:
    #             # self.log('target absent')
    #             self.motor.type('r')
    #             self.wait(1.0)

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
