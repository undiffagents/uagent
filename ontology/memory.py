import re

from think import Chunk, Memory

from .ontology import Ontology


class Fact(Chunk):

    def __init__(self, dictionary):        
        super().__init__(**dictionary)
        self.conditions = self.slots['preCondition']
        self.actions = self.slots['postCondition']

    def __str__(self):
        return self.slots['asString']


class Rule(Chunk):

    def __init__(self, dictionary):
        super().__init__(**dictionary)
        self.conditions = self.slots['preCondition']
        self.actions = self.slots['postCondition']

    def __str__(self):
        return self.slots['asString']


class OntologyMemory(Memory):

    DEFAULT_DURATION = .200

    def __init__(self, agent, decay=None):
        super().__init__(agent, decay=decay)
        self.ontology = Ontology(stopOldServer=True,owlFile='uagent.owl')

    def add_instruction_knowledge(self, ace_output):
        self.ontology.add_instruction_knowledge(*ace_output[:-1])

    def _ontology_recall(self, name, get):
        self.think('recall {}'.format(name))
        self.log('recalling {}'.format(name))
        results = set([Rule(s) if s['isa'] == 'Rule' else Fact(s) for s in get()])
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
