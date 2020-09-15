import re

from interpreter import Interpreter
from ontology import OntologyMemory
from think import (Agent, Audition, Chunk, Language, Memory, Motor, Query,
                   Vision)


class UndifferentiatedAgent(Agent):

    def __init__(self, env, output=True):
        super().__init__(output=output)

        self.memory = OntologyMemory(self)
        self.vision = Vision(self, env.display)
        self.audition = Audition(self, env.speakers)
        self.motor = Motor(self, self.vision, env)

        self.interpreter = Interpreter(self.memory)

        self.language = Language(self)
        self.language.add_interpreter(lambda words:
                                      self.interpreter.interpret_ace(' '.join(words)))

        #CONTROLLED VOCABULARY TERMS:
        #CK 2020-06-03: Rough implementation of controlled vocabulary. 
        #Chose to put definitions here, as multiple functions already relate to actions, and I expect that to get more complicated in the future.
        #First version only includes terms THINK is already set up to use.

        #Actions that execute_action() can handle.
        # DS 2020-09-15 - Modifying this to be the list of actions that the agent is aware of how to do.
        # This is pre-determined, as opposed to the task-level actions list, which is built dynamically
        self.agent_action_list = ['press','click','remember']
        #'press' and 'remember' aren't in the Ontology.
        # "Action" CV in Ontology: 'click', 'read', 'retrieve', 'search', 'listen-for', 'watch-for'

        # DS 2020-09-15 - Adding a list of task-specific agent actions which will be built on the fly by reading rules
        # which have actions which are performed by the subject.  This allows for gap detection on if the agent is
        # requested to do something which it does not know how to do.
        self.task_action_list = []

        # DS 2020-09-15 - adding a list of desired predicates in case "action" isn't the only one
        self.action_predicate_list = ['action']

        #Conditions that check_condition() can handle.
        # DS 09-15-2020: modified "appearsOn" to "appear"
        self.condition_list = ['appear','visible']
        #'appearsOn' isn't in the Ontology.
        # "Affordance" CV in the Ontology: 'clickable', 'searchable', 'retrievable', 'findable', 'audible', 'visible'

        #Not used at the moment.
        self.item_role_list = ['target','stimulus','distractor','responseButton','infoButton']
        #"ItemRole" in the Ontology.

        #For future implementations (trying to use other labs' instructions)
        self.agent_synonym_list = ['subject','participant','you']

    # subject(subject), screen(screen), letter(target),
    # hasProperty(present,positive), hasProperty(target,correct),
    # appearsOn(target,screen), button(present)
    # =>
    # press(subject,present)

    # button(absent), hasProperty(absent,negative),
    # letter(distractor), screen(screen),
    # appearsOn(distractor,screen), letter(distractor),
    # hasProperty(distractor,incorrect), subject(subject)
    # =>
    # press(subject,absent)

    #CK 2020-06-03: Updated for CV terms. Function output unaltered for 'press' (the only action it looked for, previously)
    # DS 2020-09-15: Modifying for new format - check if pred = "action" and then grab the first object (the verb)
    def is_action(self, rule):
        for action in rule.actions:
            if action.pred in self.action_predicate_list:
                for potential_action in self.agent_action_list:
                    # grab the verb from the action (the first object)
                    if action.obj(0) == potential_action:
                        return True
        return False

    def is_action_old(self, rule):
        for action in rule.actions:
            for potential_action in self.agent_action_list:
                if action.pred == potential_action:
                    return True
        return False

    #CK 2020-06-03: Updated for CV terms. Function output unaltered for 'appearsOn' (the only thing it looked for, previously). Treats 'visible' as identical to 'appearsOn' at the moment.
    # DS 2020-09-15: Modifying to work on the "action(x,y,z) format
    def check_condition(self, cond, context):
        for potential_predicate in self.action_predicate_list:
            #as more conditions are added, their cases must be coded in here.
            if cond.pred == potential_predicate:
                # Check the verb and see if it's "appear"
                if cond.obj(0) == 'appear':
                    self.think('check condition "{}"'.format(cond))
                    isa = cond.obj(1)
                    visual = self.vision.find(isa=isa, seen=False)
                    if visual:
                        print('----- Found {}'.format(isa))
                        context.set('visual', visual)
                        visobj = self.vision.encode(visual)
                        context.set(isa, visobj)
                    else:
                        return False
        return True

    #CK 2020-06-03: Updated for CV terms. Function output unaltered for 'appearsOn' (the only thing it looked for, previously). Treats 'visible' as identical to 'appearsOn' at the moment.
    def check_condition_old(self, cond, context):
        for potential_condition in self.condition_list:
            #as more conditions are added, their cases must be coded in here.
            if cond.pred == potential_condition:
                # if cond.pred == 'appearsOn' or cond.pred == 'visible':
                #     self.think('check condition "{}"'.format(cond))
                #     isa = cond.obj(0)
                #     # visual = self.vision.find(isa=isa)
                #     visual = self.vision.search_for(Query(isa=isa), None)
                #     if visual:
                #         print('----- Found visual')
                #         context.set('visual', visual)
                #         visobj = self.vision.encode(visual)
                #         context.set(isa, visobj)
                #     else:
                #         return False
                if cond.pred == 'appearsOn':
                    self.think('check condition "{}"'.format(cond))
                    isa = cond.obj(0)
                    visual = self.vision.find(isa=isa, seen=False)
                    if visual:
                        print('----- Found {}'.format(isa))
                        context.set('visual', visual)
                        visobj = self.vision.encode(visual)
                        context.set(isa, visobj)
                    else:
                        return False
        return True

    #CK 2020-06-03: Updated for CV terms. Function output unaltered for action subject 'subject' (the only identifier it looked for, previously), and for actions 'press', 'click', and 'remember'.
    def execute_action(self, action, context):
        for potential_syn in self.agent_synonym_list:
            if action.obj(1) == potential_syn:
                self.think('execute action "{}"'.format(action))

                if action.obj(0) == 'press':
                    # visual = self.vision.find(isa=action.obj(1))
                    # if visual:
                    #     self.motor.point_and_click(visual)
                    key = action.obj(2)
                    if key == 'space_bar':
                        key = ' '
                    self.motor.type(key)

                if action.obj(0) == 'click':
                    visual = context.get('visual')
                    self.motor.point_and_click(visual)

                elif action.pred == 'remember':
                    pass

    #CK 2020-06-03: Updated for CV terms. Function output unaltered for action subject 'subject' (the only identifier it looked for, previously), and for actions 'press', 'click', and 'remember'.
    def execute_action_old(self, action, context):
        for potential_syn in self.agent_synonym_list:
            if action.obj(0) == potential_syn:
                self.think('execute action "{}"'.format(action))

                if action.pred == 'press':
                    # visual = self.vision.find(isa=action.obj(1))
                    # if visual:
                    #     self.motor.point_and_click(visual)
                    key = action.obj(1)
                    if key == 'space_bar':
                        key = ' '
                    self.motor.type(key)

                if action.pred == 'click':
                    visual = context.get('visual')
                    self.motor.point_and_click(visual)

                elif action.pred == 'remember':
                    pass

    # DS 2020-09-15: Adding this to dynamically construct the list of actions which the agent must perform in the
    # task.
    def constructTaskActionList(self, rule):
        # Check the actions of the rule
        for action in rule.actions:
            # Check that this is a valid "action(x,y,z)" format
            if action.pred in self.action_predicate_list and len(action.objs) == 3:
                # Get the action's verb/performer/target.
                # Verb is something like "appear", "press", etc.
                # Performer is like "subject", "letter", etc.
                # Target would be "space_bar", "screen", etc.
                # Action format = action(verb,performer,target)

                actionVerb = action.obj(0)
                actionPerformer = action.obj(1)
                actionTarget = action.obj(2)
                # Check if the agent is the one supposed to be performing this action.
                if actionPerformer in self.agent_synonym_list:
                    # If the action not already in the list, add this action to the list of task-specific actions.
                    if actionVerb not in self.task_action_list:
                        self.task_action_list.append(actionVerb)

    # DS 2020-09-15: Simple gap identification - if there are actions in the task action list which the uagent doesn't
    # have knowledge of, then a gap arises.
    def checkForGapWRTActions(self):
        gapFound = False
        for task_action in self.task_action_list:
            if task_action not in self.agent_action_list:
                print("GAP DETECTED: Action " + task_action + " required by the task which the agent does not know.")
                gapFound = True
        return gapFound

    def process(self, rule, context):
        if self.is_action(rule):
            self.think('process rule "{}"'.format(rule))
            for cond in rule.conditions:
                if not self.check_condition(cond, context):
                    return False
            for action in rule.actions:
                self.execute_action(action, context)
            return True


    def run(self, time=60):

        instr_visual = self.vision.wait_for(isa='text')
        instructions = self.vision.encode(instr_visual)
        self.language.interpret(instructions)

        # DS 2020-09-15 - adding this so that the task-level actions are constructed before the task starts.
        # Probably not cognitively correct TODO ****
        for rule in self.memory.recall_ground_rules():
            self.constructTaskActionList(rule)

        gapPresent = self.checkForGapWRTActions()

        while self.time() < time:
            context = Chunk()

            # Currently hardcoding the letter check - there will probably be a way to dynamically decide what to wait on
            # Wait for a letter to appear in vision, otherwise do nothing.
            stimulus_appears = self.vision.wait_for(isa='letter')
            if stimulus_appears is not None:
                for rule in self.memory.recall_ground_rules():
                    #self.constructTaskActionList(rule)
                    #print("TASK ACTIONS " + str(self.task_action_list))
                    self.process(rule, context)
