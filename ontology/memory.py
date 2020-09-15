import re

from think import Chunk, Memory

from .ontology import Ontology


class Fact(Chunk):

    def __init__(self, string):
        super().__init__(string=string)
        self.pred = string[:string.find('(')]
        self.objs = string[string.find('(')+1:string.find(')')].split(',')

    def obj(self, i):
        return self.objs[i]

    def __str__(self):
        return self.pred + '(' + ','.join(self.objs) + ')'


class Rule(Chunk):

    def __init__(self, string):
        super().__init__(string=string)
        parts = string.split(' => ')
        self.conditions = [Fact(x)
                           for x in re.findall(r'\w+\([\w,_-]*\)', parts[0])]
        self.actions = [Fact(x)
                        for x in re.findall(r'\w+\([\w,_-]*\)', parts[1])]

    def __str__(self):
        return (', '.join([str(x) for x in self.conditions]) +
                ' => ' +
                ', '.join([str(x) for x in self.actions]))


class OntologyMemory(Memory):

    DEFAULT_DURATION = .200

    def __init__(self, agent, decay=None):
        super().__init__(agent, decay=decay)
        self.ontology = Ontology().load()

    def add_instruction_knowledge(self, ace_output):
        self.ontology.add_instruction_knowledge(ace_output)

    # DS 2020-09-15 - added **kwargs to allow for passing arguments in to the get function
    # used for recall_ground_rules_similar_to_condition
    def _ontology_recall(self, name, get, *args):
        self.think('recall {}'.format(name))
        self.log('recalling {}'.format(name))
        results = set([Rule(s) if ' => ' in s else Fact(s)
                       for s in get(*args)])
        self.wait(OntologyMemory.DEFAULT_DURATION)
        self.log('recalled {}'.format(name))
        return results

    def recall_facts(self):
        return self._ontology_recall('facts', self.ontology.get_instruction_facts)

    def recall_reasoner_facts(self):
        return self._ontology_recall('reasoner facts', self.ontology.get_instruction_reasoner_facts)

    def recall_ground_rules(self):
        return self._ontology_recall('ground rules', self.ontology.get_instruction_ground_rules)

    def recall_rules(self):
        return self._ontology_recall('rules', self.ontology.get_instruction_rules)

    #DS 2020-09-15 - adding this in to get only a set of rules that have relevant information in the condition
    # Having a for loop doing regex work may well be cognitively incorrect - should this be changed to be in teh
    # SPARQL query?  Doing regex in SPARQL seems like it might load down the endpoint. TODO: ****
    def recall_ground_rules_with_condition_containing(self, conditionSegment):
        groundRulesContainingInCondition = []
        groundRules = self._ontology_recall('ground rules with "' + conditionSegment + '" in condition',
                              self.ontology.get_instruction_ground_rules_with_condition_containing, conditionSegment)
        # Iterate through all of the rules that came back containing conditionSegment and check that it's in the
        # condition and not in the consequence
        for rule in groundRules:
            # check to find the condition segment followed (at some point) by =>
            searchPattern = re.escape(conditionSegment) + '.+\=\>'
            segmentInCondition = re.search(searchPattern,str(rule))
            # if found, this is one of those we want
            if segmentInCondition is not None:
                groundRulesContainingInCondition.append(rule)
        return groundRulesContainingInCondition
