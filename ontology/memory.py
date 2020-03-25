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

    def add_knowledge(self, ace_output, ace):
        '''If we ever want to add other knowledge, we need to change this'''
        self.ontology.add_instruction_knowledge(ace_output)

    def _ontology_recall(self, name, get):
        self.think('recall {}'.format(name))
        self.log('recalling {}'.format(name))
        results = set([Rule(s) if ' => ' in s else Fact(s)
                       for s in get()])
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
