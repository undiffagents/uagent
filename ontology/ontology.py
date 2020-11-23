import json
import os
import re
import socket
import subprocess
import time

class Ontology:

    instructionGraph = ':instructionGraph'
    dlGraph = ':dlGraph'
    koiosGraph = ':koiosGraph'
    thinkGraph = ':thinkGraph'
    
    predQueryMappings = {'ruleString':'asString','name':'name','arity':'arity','step':'reasoningStep','string':'asString','predicateType':'isa','termType':'isa','termString':'asString','term2Type':'isa','term2String':'asString','functionTermType':'isa','functionTermString':'asString','functionName':'name'} 
    
    PREFIX = 'PREFIX : <http://www.uagent.com/ontology#>\nPREFIX opla: <http://ontologydesignpatterns.org/opla#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n'

    def __init__(self,stopOldServer=False,loadFile=False):
        
        if not stopOldServer and self.isRunning(): self.initialized = True ; return
        
        self.initialized = False
        
        if stopOldServer: self.stopOldServer()
             
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:            
            while s.connect_ex(('localhost', 3030)) == 0: 
                print('Waiting for ontology server socket to become free...')
                
        print("Starting ontology server...")
        subprocess.Popen(['java', '-jar', 'lib/fuseki/fuseki-server.jar', '--update','--quiet'])
        
        if loadFile: self.load(filename=loadFile)
                
    def stopOldServer(self):
        print('Removing any old ontology servers...')
        if pid := self.isRunning():
            os.kill(pid, 9) 
            
    def isRunning(self):
        for l in ((subprocess.Popen(['ps','-A'], stdout=subprocess.PIPE)).communicate()[0]).splitlines():
            if 'java' in str(l):
                return int(l.split(None, 1)[0])
        return False

    def load(self,filename='uagent.owl'):
        
        if self.initialized: return self
        
        print('Waiting for ontology server...')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            while subprocess.call(['lib/fuseki/s-update','--service=http://localhost:3030/uagent/update', ''],stdout=subprocess.PIPE,stderr=subprocess.PIPE) != 0: 
                pass        
        
        print('Loading ontology...')
        path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))
        subprocess.call(['lib/fuseki/s-update','--service=http://localhost:3030/uagent/update', "LOAD <file://{}>".format(path)])
        
        self.initialized = True
    
    def add_instruction_knowledge(self,ace,factsExpression,nestedExpressions,facts,rules,reasonerFacts,groundRules):
        
        # add ACE
        instructionString = ' '.join(['[] a :Instruction ; :asString "{}" .'.format(x) for x in ace.splitlines()])
        
        # add DRS
        instructionString = instructionString + factsExpression.tripleString()
        
        for nestedExpression in nestedExpressions.expressions():
            instructionString = instructionString + nestedExpression.tripleString()         
        
        dlString = ''
        
        # add rules
        for fact in facts:
            instructionString = instructionString + '[] a :Instruction ; :asRule [ a :Fact ; :inReasoningStep 0 ; :hasHeadPredicate ['+fact.tripleString()+'] ; :asString "'+str(fact)+'" ] .'
            dlString = dlString + fact.dlTripleString()
            
        for rule in rules:
            instructionString = instructionString + '[] a :Instruction ; :asRule [ :asString "' +rule.toRule()+ '" ; a :Rule ; :inReasoningStep 0 ; :hasHeadPredicate ['+rule.head.pred.tripleString()+'] '+''.join(['; :hasBodyPredicate [{}] '.format(x.tripleString()) for x in rule.body.preds])+']. '
            
        for order,fact in reasonerFacts:
            instructionString = instructionString + '[] a :Instruction ; :asRule [ a :Fact ; :inReasoningStep '+str(order)+' ; :hasHeadPredicate ['+fact.tripleString()+'] ; :asString "'+str(fact)+'" ] .'
            dlString = dlString + fact.dlTripleString()
            
        for order,rule in groundRules:
            instructionString = instructionString + '[] a :Instruction ; :asRule [ :asString "' +rule.toRule()+ '" ; a :Rule ; :inReasoningStep '+str(order)+' ; :hasHeadPredicate ['+rule.head.pred.tripleString()+'] '+''.join(['; :hasBodyPredicate [{}] '.format(x.tripleString()) for x in rule.body.preds])+']. '
        
        self.add_to_instructions_graph(instructionString)
        self.add_to_dl_graph(dlString)

    def add(self,data):
        subprocess.call(['lib/fuseki/s-update', '--service=http://localhost:3030/uagent/update','{} INSERT DATA  {{ {} }}'.format(self.PREFIX,data)])
        
    def add_to_instructions_graph(self,data):
        self.add('graph {} {{ {} }}'.format(self.instructionGraph,data))
    
    def add_to_dl_graph(self,data):
        self.add('graph {} {{ {} }}'.format(self.dlGraph,data))    
    
    def add_to_koios_graph(self,data):
        self.add('graph {} {{ {} }}'.format(self.koiosGraph,data))
        
    def add_to_think_graph(self,data):
        self.add('graph {} {{ {} }}'.format(self.thinkGraph,data))    

    def query(self,query):
        return json.loads(str(subprocess.run(['lib/fuseki/s-query','--service','http://localhost:3030/uagent/query',query],stdout=subprocess.PIPE).stdout.decode('utf-8')))

    def query_select_in_one_graph(self,selectors,expression,graph):
        result = self.query('{} SELECT {} WHERE {{ {{ {} }} union {{ graph {} {{ {} }} }} }}'.format(self.PREFIX,' '.join(selectors),expression,graph,expression))
        return set(answer[selector]['value'] for selector in result['head']['vars'] for answer in result['results']['bindings'])
    
    def factQueryExpression(self):
        return '''[] a :Instruction ; :asRule [ :inReasoningStep ?step ; a :Fact ; :hasHeadPredicate ?pred ; :asString ?ruleString ] . 
                 ?pred a ?predicateType ; :hasName ?name ; :hasArity ?arity ; :asString ?string . 
                 optional {?pred :hasArity 1 ; :hasTerm [ a ?termType ; :asString ?termString ] . } . 
                 optional {?pred :hasTerm [ a ?termType ; :asString ?termString ] ; :hasTerm [ a ?term2Type ; :asString ?term2String ; :hasName ?functionName ; :hasTerm [a ?functionTermType ; :asString ?functionTermString]] . filter(?termType != ?term2Type)} 
                 optional {?pred :hasArity 2 ; :hasTerm ?term1 ; :hasTerm ?term2 . ?term1 a ?termType ; :asString ?termString . ?term2 a ?term2Type ; :asString ?term2String . filter(?term1 != ?term2) } .} '''
    
    def headQueryExpression(self):
        return '''[] a :Instruction ; :asRule ?rule .
                 ?rule :inReasoningStep ?step ; a :Rule ; :hasHeadPredicate ?pred ; :asString ?ruleString . 
                 ?pred a ?predicateType ; :hasName ?name ; :hasArity ?arity ; :asString ?string . 
                 optional {?pred :hasArity 1 ; :hasTerm [ a ?termType ; :asString ?termString ] . } . 
                 optional {?pred :hasTerm [ a ?termType ; :asString ?termString ] ; :hasTerm [ a ?term2Type ; :asString ?term2String ; :hasName ?functionName ; :hasTerm [a ?functionTermType ; :asString ?functionTermString]] . filter(?termType != ?term2Type)} 
                 optional {?pred :hasArity 2 ; :hasTerm ?term1 ; :hasTerm ?term2 . ?term1 a ?termType ; :asString ?termString . ?term2 a ?term2Type ; :asString ?term2String . filter(?term1 != ?term2) } .} '''
    
    def bodyQueryExpression(self,head):
        return '[] :hasHeadPredicate [ :asString "'+head+ '''" ] ; :inReasoningStep ?step ; a :Rule ; :hasBodyPredicate ?pred . 
                 ?pred a ?predicateType ; :hasName ?name ; :hasArity ?arity ; :asString ?string . 
                 optional {?pred :hasArity 1 ; :hasTerm [ a ?termType ; :asString ?termString ] . } . 
                 optional {?pred :hasTerm [ a ?termType ; :asString ?termString ] ; :hasTerm [ a ?term2Type ; :asString ?term2String ; :hasName ?functionName ; :hasTerm [a ?functionTermType ; :asString ?functionTermString]] . filter(?termType != ?term2Type)} 
                 optional {?pred :hasArity 2 ; :hasTerm ?term1 ; :hasTerm ?term2 . ?term1 a ?termType ; :asString ?termString . ?term2 a ?term2Type ; :asString ?term2String . filter(?term1 != ?term2) } .} '''     
    
    def get_instruction_ground_rules(self):
        expression = '{graph :instructionGraph { ' + self.headQueryExpression()  + 'filter(?step != 0) }'  
        result = self.query('{} SELECT DISTINCT {} WHERE {{ graph {} {{ {} }} }}'.format(self.PREFIX,' '.join(['?{}'.format(str(x)) for x in self.predQueryMappings.keys()]),self.instructionGraph,expression))
        
        rules = self.mapFlatPredQueryResultIntoNestedDictionary(self.readQueryResultIntoPredicateDictionary(result),fact=False)
                
        for rule in rules:
            result = self.query('{} SELECT DISTINCT {} WHERE {{ graph {} {{ {} }} }}'.format(self.PREFIX,' '.join(['?{}'.format(str(x)) for x in self.predQueryMappings.keys()]),self.instructionGraph,'{ graph :instructionGraph { ' + self.bodyQueryExpression(rule['head'][0]['asString'])  + 'filter(?step != 0) }' ))
            rule['body'] = self.mapFlatPredQueryResultIntoNestedDictionary(self.readQueryResultIntoPredicateDictionary(result),fact=False,head=False)
        
        return rules
    
    def get_instruction_rules(self):
        expression = '{graph :instructionGraph { ' + self.headQueryExpression()  + 'filter(?step = 0) }'  
        result = self.query('{} SELECT DISTINCT {} WHERE {{ graph {} {{ {} }} }}'.format(self.PREFIX,' '.join(['?{}'.format(str(x)) for x in self.predQueryMappings.keys()]),self.instructionGraph,expression))
        
        rules = self.mapFlatPredQueryResultIntoNestedDictionary(self.readQueryResultIntoPredicateDictionary(result),fact=False)
                
        for rule in rules:
            result = self.query('{} SELECT DISTINCT {} WHERE {{ graph {} {{ {} }} }}'.format(self.PREFIX,' '.join(['?{}'.format(str(x)) for x in self.predQueryMappings.keys()]),self.instructionGraph,'{ graph :instructionGraph { ' + self.bodyQueryExpression(rule['head'][0]['asString'])  + 'filter(?step = 0) }' ))
            rule['body'] = self.mapFlatPredQueryResultIntoNestedDictionary(self.readQueryResultIntoPredicateDictionary(result),fact=False,head=False)
        
        return rules
    
    def get_instruction_facts(self):
        expression = '{graph :instructionGraph { ' + self.factQueryExpression()  + 'filter(?step = 0) }' 
        
        result = self.query('{} SELECT DISTINCT {} WHERE {{ {{ graph {} {{ {} }} }}  }}'.format(self.PREFIX,' '.join(['?{}'.format(str(x)) for x in self.predQueryMappings.keys()]),self.instructionGraph,expression))
        
        return self.mapFlatPredQueryResultIntoNestedDictionary(self.readQueryResultIntoPredicateDictionary(result))
    
    def get_instruction_reasoner_facts(self):                                            
        expression = '{graph :instructionGraph { ' + self.factQueryExpression()  + 'filter(?step != 0) }'  
        
        result = self.query('{} SELECT DISTINCT {} WHERE {{ {{ graph {} {{ {} }} }}  }}'.format(self.PREFIX,' '.join(['?{}'.format(str(x)) for x in self.predQueryMappings.keys()]),self.instructionGraph,expression))
        
        return self.mapFlatPredQueryResultIntoNestedDictionary(self.readQueryResultIntoPredicateDictionary(result))    
    
    def mapFlatPredQueryResultIntoNestedDictionary(self,result,fact=True,head=True):        
        if head:
            preds = []
            for pred in result:
                if len(pred) == 8:
                    preds.append({'isa':'Fact' if fact else 'Rule',self.predQueryMappings['ruleString']:pred['ruleString'],self.predQueryMappings['step']:pred['step'],'head':[{self.predQueryMappings['string']:pred['string'],self.predQueryMappings['name']:pred['name'],self.predQueryMappings['arity']:pred['arity'],'isa':pred['predicateType'],'term':[{self.predQueryMappings['termString']:pred['termString'],self.predQueryMappings['termType']:pred['termType']}]}]})
                elif len(pred) == 10 and re.match(".*?\((.*?)\,.*",pred['string']).groups()[0] == pred['termString']:
                    preds.append({'isa':'Fact' if fact else 'Rule',self.predQueryMappings['ruleString']:pred['ruleString'],self.predQueryMappings['step']:pred['step'],'head':[{self.predQueryMappings['string']:pred['string'],self.predQueryMappings['name']:pred['name'],self.predQueryMappings['arity']:pred['arity'],'isa':pred['predicateType'],'term':[{self.predQueryMappings['termString']:pred['termString'],self.predQueryMappings['termType']:pred['termType']},{self.predQueryMappings['term2String']:pred['term2String'],self.predQueryMappings['term2Type']:pred['term2Type']}]}]})                            
                elif len(pred) == 13:
                    preds.append({'isa':'Fact' if fact else 'Rule',self.predQueryMappings['ruleString']:pred['ruleString'],self.predQueryMappings['step']:pred['step'],'head' if head else 'body':[{self.predQueryMappings['string']:pred['string'],self.predQueryMappings['name']:pred['name'],self.predQueryMappings['arity']:pred['arity'],'isa':pred['predicateType'],'term':[{self.predQueryMappings['termString']:pred['termString'],self.predQueryMappings['termType']:pred['termType']},{self.predQueryMappings['term2String']:pred['term2String'],self.predQueryMappings['functionName']:pred['functionName'],self.predQueryMappings['term2Type']:pred['term2Type'],'term':[{self.predQueryMappings['functionTermString']:pred['functionTermString'],self.predQueryMappings['functionTermType']:pred['functionTermType']}]}]}]})                             
        else:
            preds = []
            for pred in result:
                if len(pred) == 7:
                    preds.append({self.predQueryMappings['string']:pred['string'],self.predQueryMappings['name']:pred['name'],self.predQueryMappings['arity']:pred['arity'],'isa':pred['predicateType'],'term':[{self.predQueryMappings['termString']:pred['termString'],self.predQueryMappings['termType']:pred['termType']}]})
                elif len(pred) == 9 and re.match(".*?\((.*?)\,.*",pred['string']).groups()[0] == pred['termString']:
                    preds.append({self.predQueryMappings['string']:pred['string'],self.predQueryMappings['name']:pred['name'],self.predQueryMappings['arity']:pred['arity'],'isa':pred['predicateType'],'term':[{self.predQueryMappings['termString']:pred['termString'],self.predQueryMappings['termType']:pred['termType']},{self.predQueryMappings['term2String']:pred['term2String'],self.predQueryMappings['term2Type']:pred['term2Type']}]})                            
                elif len(pred) == 12:
                    preds.append({self.predQueryMappings['string']:pred['string'],self.predQueryMappings['name']:pred['name'],self.predQueryMappings['arity']:pred['arity'],'isa':pred['predicateType'],'term':[{self.predQueryMappings['termString']:pred['termString'],self.predQueryMappings['termType']:pred['termType']},{self.predQueryMappings['term2String']:pred['term2String'],self.predQueryMappings['functionName']:pred['functionName'],self.predQueryMappings['term2Type']:pred['term2Type'],'term':[{self.predQueryMappings['functionTermString']:pred['functionTermString'],self.predQueryMappings['functionTermType']:pred['functionTermType']}]}]})                                      
        
        return preds
        
    def readQueryResultIntoPredicateDictionary(self,result):
        
        predicates = []
        
        for answer in result['results']['bindings']:
            newDict = {}            
            for key in self.predQueryMappings:                
                if key not in answer:
                    continue
                elif answer[key]['type'] == 'uri':
                    newDict[key] = answer[key]['value'].split('#')[1]
                elif answer[key]['type'] == 'literal' and 'datatype' in answer[key]:
                    type = answer[key]['datatype'].split('#')[1]
                    if type == 'integer':
                        newDict[key] = int(answer[key]['value'])
                    else: raise
                else: 
                    newDict[key] = answer[key]['value']
            predicates.append(newDict)
                
        return predicates

    def query_count_in_one_graph(self,expression,graph):
        result = self.query('{} SELECT (COUNT(*) AS ?count) WHERE {{ {{ {} }} union {{ graph {} {{ {} }} }} }} GROUP BY ?count'.format(self.PREFIX,expression,graph,expression))['results']['bindings']
        return int(result[0]['count']['value']) if len(result) == 1 else 0

    def query_count_predicate_in_one_graph(self,predicate,graph):
        return self.query_count_in_one_graph(' ?subject {} ?object'.format(predicate),graph)

    def query_count_subject_in_one_graph(self,subject,graph):
        return self.query_count_in_one_graph('{} ?predicate ?object'.format(subject),graph)

    def query_count_object_in_one_graph(self,object,graph):
        return self.query_count_in_one_graph('?subject ?predicate {}'.format(object),graph)

    def query_count_subject_predicate_in_one_graph(self,subject,predicate,graph):
        return self.query_count_in_one_graph('{} {} ?object'.format(subject,predicate),graph)

    def query_count_subject_object_in_one_graph(self,subject,object,graph):
        return self.query_count_in_one_graph('{} ?predicate {}'.format(subject,object),graph)

    def query_count_predicate_object_in_one_graph(self,predicate,object,graph):
        return self.query_count_in_one_graph('?subject {} {}'.format(predicate,object),graph)

    def query_select_object_with_predicate_in_one_graph(self,predicate,graph):
        return self.query_select_in_one_graph(['?object'],'?subject {} ?object'.format(predicate),graph)
    
    def query_select_subject_with_predicate_in_one_graph(self,predicate,graph):
        return self.query_select_in_one_graph(['?subject'],'?subject {} ?object'.format(predicate),graph)

    def get_DRS_Strings(self):
        return self.query_select_in_one_graph(['?object'],'?subject :asDRSString ?object',self.instructionGraph)
    
    def countDRSStrings(self):
        return self.query_count_predicate_in_one_graph(':asDRSString',self.instructionGraph)

    def get_ACE_Strings(self):
        return self.query_select_in_one_graph(['?object'],'[] a :Instruction ; :asString ?object',self.instructionGraph)
    
    def countACEStrings(self):
        return self.query_count_subject_predicate_in_one_graph('[] a :Instruction ; ',':asString',self.instructionGraph)

if __name__ == "__main__":
    print("Starting ontology server...")
    Ontology().load()
    