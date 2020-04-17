from think import Agent, Motor, Vision


class VSAgent(Agent):

    def __init__(self, machine):
        """Initializes the agent"""
        super().__init__(output=True)
        self.vision = Vision(self, machine.display)
        self.motor = Motor(self, self.vision, machine)

    def run(self, time=60):
        while self.time() < time:
            visual = self.vision.wait_for(seen=False)
            #def search_for(self, query, target):
            self.vision.search_for(visual,,'X') #how does query work?
            

            self.motor.type('j')
            self.vision.get_encoded()
