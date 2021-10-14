from interpreter import Interpreter
from ontology import OntologyMemory
from think import (Agent, Audition, Chunk, Language, Memory, Motor, Query,
                   Vision)


SYNONYMS = [
    ('number', 'digit'),
    ('press', 'click'),
    ('target', 'letter'),
]

SYNONYM_DICT = {}
for (x, y) in SYNONYMS:
    SYNONYM_DICT[x] = y
    SYNONYM_DICT[y] = x


class Handler:

    def __init__(self, agent):
        self.agent = agent
        self.knowledge = agent.knowledge

    def _find_synonym(self, word):
        if word in SYNONYM_DICT:
            synonym_chunk = self.knowledge.recall(isa='synonym', word=word)
            if synonym_chunk:
                synonym = synonym_chunk.get('synonym')
                self.log(
                    f"[did not understand '{word}', trying synonym '{synonym}']")
                return synonym
        return None

    def _get(self, name, find_synonyms=True):
        handler = getattr(self, name, None)
        if handler is None and find_synonyms:
            synonym = self._find_synonym(name)
            if synonym:
                handler = getattr(self, synonym, None)
        return handler

    def _has(self, name, find_synonyms=True):
        return self._get(name, find_synonyms=find_synonyms) is not None

    def _arg(self, chunk, i):
        return chunk['ofItem'][i]['asString']


class ConditionHandler(Handler):

    def appear(self, cond, context):
        ''' appear(<isa>,on(screen)) '''

        isa = self._arg(cond, 0)

        # vision.find is non-blocking: it checks and returns immediately
        visual = self.agent.vision.find(isa=isa, seen=False)

        # vision.wait_for is blocking: it waits for the item to appear
        # visual = self.agent.vision.wait_for(isa=isa, seen=False)

        if visual:
            context.set('visual', visual)
            visobj = self.agent.vision.encode(visual)
            context.set(isa, visobj)
            return True
        else:
            return False

    def find(self, cond, context):
        if context.get('search-state'):
            return True
        else:
            return False

    def fail(self, cond, context):
        if context.get('search-state'):
            return False
        else:
            return True

#HOW TO HAND FIND / FAIL VISUAL SEARCH? AS CONDITIONS?


# Necessary Think CV/functions

# Search (visual attention: looking for a letter to appear on the screen)
# Click/Press (manual: press a button/clickable object)
# appearsOn - needs to inform the agent that something has appeared and where?
# visible - recognize something that is/can be on the screen
# clickable - recognize something that can be pressed manually
# subject/agent/you/participant - self-awareness to know that an instruction involves an agent action
# target/stimulus - recognize something as the goal/trigger in a task
# button - recognize the button that needs pressed (may be subsumed/superclassed by clickable)


#could also be called foreknowledge or world knowledge, whatever
# class MetaHandler(Handler):
    # subject/agent/you/participant - self-awareness to know that an instruction involves an agent action


#CONTROLLLED VOCABULARY
# class PerceptionHandler(Handler):

    # def visible(self, action, context):

    # target/stimulus - recognize something as the goal/trigger in a task


#I want this to represent the 'Interface' behaviors -- actions which the UA takes to do something in the Environment
class ActionHandler(Handler):

    #HOW TO HANDLE SYNONYMS? DICTIONARY OF TERMS THAT ALL POINT TO THE SAME FUNCTION? [E.G. PRESS, CLICK, ETC]
    #Related: parts of speech etc., e.g. clickable - recognize something that can be pressed manually
    # button - recognize the button that needs pressed (may be subsumed/superclassed by clickable)
    def press(self, action, context):
        ''' press(subject,<key>) '''

        key = self._arg(action, 1)

        if key == 'space_bar':
            key = ' '

        if key == 'r_key':
            key = 'r'
        if key == 'w_key':
            key = 'w'

        self.agent.motor.type(key)

    # def press(self, action, context):
    #     isa = self._arg(action, 0)
    #     visual = self.agent.vision.find(isa=isa)
    #     if visual:
    #         self.agent.motor.point_and_click(visual)

    def click(self, action, context):
        visual = context.get('visual')
        self.agent.motor.point_and_click(visual)

    # Search (visual attention: looking for a letter to appear on the screen)
    # def search(self, action, context):
    #     BLAH

    # appearsOn - needs to inform the agent that something has appeared and where?

# If the subject searches the target and the target appears on the screen then the subject presses the n:space_bar.
# If the subject searches the target and the distractor appears on the screen then the subject presses the n:q_key.

    def search(self, action, context):
        target = self._arg(action, 1)
        if target == 'target':
            print("TARGET!")
        else:
            print("BOO!")
            target = "target"

        self.agent.vision.wait_for(isa='letter', seen=False)
        visual = self.agent.vision.search_for(
            Query(isa='letter', color='red', region='vs'), target)
        context.set('search-visual', visual)

        if visual:
            context.set('search-state', True)
        else:
            context.set('search-state', False)

        # if visual:
        #     # self.log('target present')
        #     self.agent.motor.type('w')
        #     self.agent.wait(1.0)
        # else:
        #     # self.log('target absent')
        #     self.agent.motor.type('r')
        #     self.agent.wait(1.0)

    #STOLEN FROM VISION.PY
    # def search_for(self, query, target):
    #     if query is None:
    #         query = Query()
    #     query = query.eq('seen', False)
    #     visual = self.find(query)
    #     obj = self.encode(visual) if visual else None
    #     while visual and target and obj != target:
    #         visual = self.find(query)
    #         obj = self.encode(visual) if visual else None
    #     if obj and obj == target:
    #         return visual
    #     else:
    #         return None

        # #Not used at the moment.
        # self.item_role_list = ['target','stimulus','distractor','responseButton','infoButton']
        # #"ItemRole" in the Ontology.

        # #For future implementations (trying to use other labs' instructions)
        # self.agent_synonym_list = ['subject','participant','you']


class UndifferentiatedAgent(Agent):

    def __init__(self, env, output=True, stopOldServer=False, owlFile='uagent.owl', simulateRules=False):
        super().__init__(output=output)

        #basic pass-ins for now for speed of testing
        self.memory = OntologyMemory(
            self, stopOldServer=stopOldServer, owlFile=owlFile)

        # create ACT-R-like knowledge memory for synonyms
        self.knowledge = Memory(self, Memory.OPTIMIZED_DECAY)
        self.knowledge.decay_rate = .5
        self.knowledge.activation_noise = .5
        self.knowledge.retrieval_threshold = -1.8
        self.knowledge.latency_factor = .450
        for word, synonym in SYNONYM_DICT.items():
            chunk = Chunk(isa='synonym', word=word, synonym=synonym)
            self.knowledge.store(chunk, boost=10000)

        self.vision = Vision(self, env.display)
        self.audition = Audition(self, env.speakers)
        self.motor = Motor(self, self.vision, env)

        self.interpreter = Interpreter(self.memory)

        self.language = Language(self)
        self.language.add_interpreter(lambda words:
                                      self.interpreter.interpret_ace(' '.join(words)))

        self.condition_handler = ConditionHandler(self)
        self.action_handler = ActionHandler(self)

        #for testing updated Ground Rules focusing on CV
        self.simulateRules = simulateRules

    def is_action(self, rule):
        for action in rule.actions:
            if self.action_handler._has(action['name']):
                return True
        return False

    def check_condition(self, cond, context):
        handler = self.condition_handler._get(cond['name'])
        if handler:
            self.think('check condition "{}"'.format(cond))
            return handler(cond, context)
        else:
            return True

    def execute_action(self, action, context):
        handler = self.action_handler._get(action['name'])
        if handler:
            self.think('execute action "{}"'.format(action))
            handler(action, context)

    def process_rule(self, rule, context):
        self.think('processing rule "{}"'.format(rule))
        if self.is_action(rule):
            self.think('processing: rule is an action, check conditions')
            for cond in rule.conditions:
                if not self.check_condition(cond, context):
                    self.think('processed rule: conditions not met')
                    return False
            self.think('processing: condition(s) met, execute action(s)')
            for action in rule.actions:
                self.execute_action(action, context)
            return True
        else:
            self.think('processed rule: not an action')

    def run(self, time=60):

        instr_visual = self.vision.wait_for(isa='text')
        instructions = self.vision.encode(instr_visual)
        self.language.interpret(instructions)

        self.interpreter.printLogfile(self.memory.ontology)

        while self.time() < time:
            context = Chunk()
            for rule in self.memory.recall_ground_rules():
                self.process_rule(rule, context)

    # VS-AGENT
    # def run(self, time):
    #     while self.time() < time:
    #         self.vision.wait_for(isa='letter', seen=False)
    #         visual = self.vision.search_for(
    #             Query(isa='letter', color='red', region='vs'), 'X')
    #         if visual:
    #             # self.log('target present')
    #             self.motor.type('w')
    #             self.wait(1.0)
    #         else:
    #             # self.log('target absent')
    #             self.motor.type('r')
    #             self.wait(1.0)
    #
    # PVT-AGENT
    # def run(self, time=60):
    #     while self.time() < time:
    #         visual = self.vision.wait_for(
    #             isa='letter', region='pvt', seen=False)
    #         self.vision.start_encode(visual)
    #         self.motor.type(' ')
    #         self.vision.get_encoded()
    #
