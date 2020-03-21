import json
import os
import socket
import subprocess


class Ontology:

    PREFIX = 'PREFIX : <http://www.uagent.com/ontology#>\nPREFIX opla: <http://ontologydesignpatterns.org/opla#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n'

    def __init__(self, filename='uagent.owl'):
        self._load(filename)

    def _load(self, filename):
        print('Waiting for ontology server...')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            while s.connect_ex(('localhost', 3030)) > 0:
                pass
        print('Loading ontology...')
        path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), filename)
        subprocess.call(['lib/fuseki/s-update',
                         '--service=http://localhost:3030/uagent/update', "LOAD <file://"+path+">"])
        return self

    def add(self, input_string, as_type):
        inputs = (':initialInstruction rdf:type :Instruction . :initialInstruction {} "{}" .'.format(
            as_type, input_string))
        subprocess.call(['lib/fuseki/s-update', '--service=http://localhost:3030/uagent/update',
                         '{} INSERT DATA  {{ {} }}'.format(self.PREFIX, inputs)])

    def add_file(self, path, as_type):
        with open(path, 'r') as f:
            self.add('\\n'.join(f.read().splitlines()), as_type)

    def add_inputs(self, ace_output, ace_file, drs_file):
        print("Adding inputs to ontology...")
        facts, rules, ground_rules, new_facts = ace_output
        for fact in facts:
            self.add(fact, ':asFactString')
        for rule in rules:
            self.add(rule, ':asRuleString')
        for ground_rule in ground_rules:
            self.add(ground_rule, ':asGroundRuleString')
        for new_fact in new_facts:
            self.add(new_fact, ':asReasonerFactString')
        self.add_file(ace_file, ':asACEString')
        self.add_file(drs_file, ':asDRSString')
        return facts, rules, ground_rules, new_facts

    def query(self, query):
        results = subprocess.run(['lib/fuseki/s-query', '--service', 'http://localhost:3030/uagent/query',
                                  '{} SELECT ?object WHERE {{ {} }}'.format(self.PREFIX, query)],
                                 stdout=subprocess.PIPE).stdout.decode('utf-8')
        bindings = json.loads(str(results))['results']['bindings']
        return set([x['object']['value'] for x in bindings])

    def get(self, as_type):
        return self.query(':initialInstruction {} ?object .'.format(as_type))

    def get_rules(self):
        return self.get(':asRuleString')

    def get_ground_rules(self):
        return self.get(':asGroundRuleString')

    def get_facts(self):
        return self.get(':asFactString')

    def get_reasoner_facts(self):
        return self.get(':asReasonerFactString')
