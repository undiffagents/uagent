import json
import os
import re
import socket
import subprocess
import time

class Ontology:

    '''External functions and queries to use (commented)'''
    
    def get_instruction_ground_rules(self):
        '''
        input:  self
        return: [ dict ]
        
        Creates a dictionary that represents the ontology information about solutions to instruction conditionals used to make the reasoner facts 
        '''
        
        expression = self.headQueryExpression()  + 'filter(?step != 0)'  
        result = self.query('{} SELECT DISTINCT {} WHERE {{ graph {} {{ {} }} }}'.format(self.prefixes,' '.join(['?{}'.format(str(x)) for x in self.predQueryMappings.keys()]),self.instructionGraph,expression))
        
        rules = self.mapFlatPredQueryResultIntoNestedDictionary(self.readQueryResultIntoPredicateDictionary(result),fact=False)
                
        for rule in rules:
            result = self.query('{} SELECT DISTINCT {} WHERE {{ graph {} {{ {} }} }}'.format(self.prefixes,' '.join(['?{}'.format(str(x)) for x in self.predQueryMappings.keys()]),self.instructionGraph,self.bodyQueryExpression(rule['postCondition'][0]['asString'])  + 'filter(?step != 0)' ))
            rule['preCondition'] = self.mapFlatPredQueryResultIntoNestedDictionary(self.readQueryResultIntoPredicateDictionary(result),fact=False,head=False)
        
        return rules
    
    def get_instruction_rules(self):
        '''
        input:  self
        return: [ dict ]
        
        Creates a list of dictionaries that represent the ontology information about the unsolved conditionals (they could have solutions as well) 
        '''
        
        expression = self.headQueryExpression()  + 'filter(?step = 0)'  
        result = self.query('{} SELECT DISTINCT {} WHERE {{ graph {} {{ {} }} }}'.format(self.prefixes,' '.join(['?{}'.format(str(x)) for x in self.predQueryMappings.keys()]),self.instructionGraph,expression))
        
        rules = self.mapFlatPredQueryResultIntoNestedDictionary(self.readQueryResultIntoPredicateDictionary(result),fact=False)
                
        for rule in rules:
            result = self.query('{} SELECT DISTINCT {} WHERE {{ graph {} {{ {} }} }}'.format(self.prefixes,' '.join(['?{}'.format(str(x)) for x in self.predQueryMappings.keys()]),self.instructionGraph,self.bodyQueryExpression(rule['postCondition'][0]['asString'])  + 'filter(?step = 0)' ))
            rule['preCondition'] = self.mapFlatPredQueryResultIntoNestedDictionary(self.readQueryResultIntoPredicateDictionary(result),fact=False,head=False)
        
        return rules
    
    def get_instruction_facts(self):
        '''
        input:  self
        return: [ dict ]
        
        Creates a list of dictionaries that represent the ontology information about the facts known in the instructions
        ''' 
        
        expression = self.factQueryExpression()  + 'filter(?step = 0)' 
        result = self.query('{} SELECT DISTINCT {} WHERE {{ {{ graph {} {{ {} }} }}  }}'.format(self.prefixes,' '.join(['?{}'.format(str(x)) for x in self.predQueryMappings.keys()]),self.instructionGraph,expression))
        
        return self.mapFlatPredQueryResultIntoNestedDictionary(self.readQueryResultIntoPredicateDictionary(result))
    
    def get_instruction_reasoner_facts(self):   
        '''
        input:  self
        return: [ dict ]
        
        Creates a list of dictionaries that represent the ontology information about the facts learned from reasoning about the instructions 
        ''' 
        
        expression = self.factQueryExpression()  + 'filter(?step != 0)'  
        
        result = self.query('{} SELECT DISTINCT {} WHERE {{ {{ graph {} {{ {} }} }}  }}'.format(self.prefixes,' '.join(['?{}'.format(str(x)) for x in self.predQueryMappings.keys()]),self.instructionGraph,expression))
        
        return self.mapFlatPredQueryResultIntoNestedDictionary(self.readQueryResultIntoPredicateDictionary(result))    

    def get_DRS_Strings(self):
        '''
        input:  self
        return: [ str ]
        
        Gets a list of the DRS strings in the ontology  
        ''' 
        
        return self.select_in_one_graph(['?object'],'?subject :asDRSString ?object',self.instructionGraph)
    
    def get_DRS_Fact_Strings(self):
        '''
        input:  self
        return: [ str ]
        
        Gets a list of the DRS strings in the ontology that do not occur in a conditional  
        ''' 
        
        return self.select_in_one_graph(['?object'],'?subject :asDRSString ?object NOT EXISTS { [:drsType :conditional ; :asDRSString ?object]} NOT EXISTS { [:drsType :conditional] ?predicate ?subject}',self.instructionGraph)  
    
    def get_DRS_PreCondition_Part_Strings(self):
        '''
        input:  self
        return: [ str ]
        
        Gets a list of all of the DRS strings in the ontology that are in the first part of a conditional (not sorted)
        ''' 
        
        return self.select_in_one_graph(['?object'],'[:drsType :conditional] :hasPreSituationDescripton [:asDRSString ?object]',self.instructionGraph)   
    
    def get_DRS_PostCondition_Part_Strings(self):
        '''
        input:  self
        return: [ str ]
        
        Gets a list of the DRS strings in the ontology that are in the first second of a conditional (not sorted)
        ''' 
        
        return self.select_in_one_graph(['?object'],'[:drsType :conditional] :hasPostSituationDescripton [:asDRSString ?object]',self.instructionGraph)       
    
    def get_DRS_Conditional_Part_Strings(self):
        '''
        input:  self
        return: [ str ]
        
        Gets a list of the DRS strings in the ontology that are in a conditional (not sorted)
        ''' 
        
        return self.get_DRS_PreCondition_Part_Strings().union(self.get_DRS_PostCondition_Part_Strings()) 
    
    def get_DRS_Conditional_Strings(self):
        '''
        input:  self
        return: [ str ]
        
        Gets a list of the DRS conditional strings in the ontology
        ''' 
        
        return self.select_in_one_graph(['?object'],'[:drsType :conditional ; :asDRSString ?object]',self.instructionGraph)    
    
    def countDRSStrings(self):
        '''
        input:  self
        return: int
        
        Counts the DRS strings in the ontology
        ''' 
        
        return self.count_predicate_in_one_graph(':asDRSString',self.instructionGraph)

    def get_ACE_Strings(self):
        '''
        input:  self
        return: [ str ]
        
        Gets a list of all DRS strings in the ontology. Will return conditionals as well as the parts of the conditionals.
        ''' 
        
        return self.select_in_one_graph(['?object'],'[] a :Instruction ; :asString ?object',self.instructionGraph)
    
    def countACEStrings(self):
        '''
        input:  self
        return: int
        
        Counts the ACE strings in the ontology
        ''' 
        
        return self.count_subject_predicate_in_one_graph('[] a :Instruction ; ',':asString',self.instructionGraph)
    
    def getAllTypedDRSInstructions(self):
        '''
        input:  self
        return: {str:[dict],...}
        
        Builds a dictionary that lists each DRS component in the ontology by type.
        ''' 
        
        results = self.query('{} SELECT DISTINCT ?type ?string ?args WHERE {{ graph {} {{ [ :drsType ?type ; :hasName ?string ; :drsArgs ?args ] }} }}'.format(self.prefixes,self.instructionGraph))
        
        answer = {}
        
        for result in results['results']['bindings']:
            if result['type']['type'] == 'uri':
                ansType = result['type']['value'].split('#')[1]
                if ansType not in answer:
                    answer[ansType] = []
                args = json.loads(result['args']['value'])
                args['name'] = result['string']['value']
                answer[ansType].append(args)
            else: raise Exception("Query should only return URIs")
            
        return answer      
    
    def getDRSArgsForComponentType(self,type,name=None):
        '''
        input:  self
                name : str
                type : str
        return: [ dict ] if name != None else {str:[dict],...}
        
        Gets a list of the DRS strings in the ontology that are have the supplied name and optional name
        ''' 
        
        if name:
            results = self.query('{} SELECT DISTINCT ?args WHERE {{ graph {} {{ [:hasName "{}" ; :drsArgs ?args ; :drsType :{}] }} }}'.format(self.prefixes,self.instructionGraph,name,type))
            
            answer = []
            
            for arg in results['results']['bindings']:
                args = json.loads(arg['args']['value'])
                args['name'] = name
                answer.append(args)
                
            return answer
        
        else:
        
            results = self.query('{} SELECT DISTINCT ?string ?args WHERE {{ graph {} {{ [ :drsType :{} ; :hasName ?string  ; :drsArgs ?args ] }} }}'.format(self.prefixes,self.instructionGraph,type))
                
            return [dict(json.loads(result['args']['value']),**{'name':result['string']['value']}) for result in results['results']['bindings']]
    
    def getDRSArgsForComponentName(self,name,type=None):
        '''
        input:  self
                name : str
                type : str
        return: [ dict ] if type != None else {str:[dict],...}
        
        Gets a list of the DRS strings in the ontology that are have the supplied name and optional type
        ''' 
        
        if type:
            results = self.query('{} SELECT DISTINCT ?args WHERE {{ graph {} {{ [:hasName "{}" ; :drsArgs ?args ; :drsType :{}] }} }}'.format(self.prefixes,self.instructionGraph,name,type))
            
            answer = []
            
            for arg in results['results']['bindings']:
                args = json.loads(arg['args']['value'])
                args['name'] = name
                answer.append(args)
                
            return answer
        
        else:
            results = self.query('{} SELECT DISTINCT ?type ?args WHERE {{ graph {} {{ [ :drsType ?type ; :hasName "{}"  ; :drsArgs ?args ] }} }}'.format(self.prefixes,self.instructionGraph,name))
                
            answer = {}
        
            for result in results['results']['bindings']:
                if result['type']['type'] == 'uri':
                    ansType = result['type']['value'].split('#')[1]
                    if ansType not in answer:
                        answer[ansType] = []
                    args = json.loads(result['args']['value'])
                    args['name'] = name
                    answer[ansType].append(args)
                else: raise Exception("Query should only return URIs")
                
            return answer  
        
    def getDLGraphClasses(self):
        '''
        input:  self
        return: [ str ]
        
        Gets a list of classes in the dl graph
        '''         
        return [result['type']['value'].split('#')[1] for result in self.query('{} SELECT DISTINCT ?type WHERE {{ graph {} {{ ?type a owl:Class }} }}'.format(self.prefixes,self.dlGraph))['results']['bindings']]
    
    def getDLGraphIndividuals(self):
        '''
        input:  self
        return: [ str ]
        
        Gets a list of individuals in the dl graph
        '''         
        return [result['type']['value'].split('#')[1] for result in self.query('{} SELECT DISTINCT ?type WHERE {{ graph {} {{ ?type a owl:NamedIndividual }} }}'.format(self.prefixes,self.dlGraph))['results']['bindings']]  
    
    def getDLGraphRoles(self):
        '''
        input:  self
        return: [ str ]
        
        Gets a list of roles in the dl graph
        '''         
        return [result['type']['value'].split('#')[1] for result in self.query('{} SELECT DISTINCT ?type WHERE {{ graph {} {{ ?type a owl:ObjectProperty }} }}'.format(self.prefixes,self.dlGraph))['results']['bindings']]    
    
    def getDLGraphTriples(self):
        '''
        input:  self
        return: [ (str,str,str) ]
        
        Gets a list of triples that connect any instruction individual to another with a role in the dl graph
        '''   
        return [(result['individual1']['value'].split('#')[1],result['role']['value'].split('#')[1],result['individual2']['value'].split('#')[1]) for result in  self.query('{} SELECT DISTINCT ?individual1 ?role ?individual2 WHERE {{ graph {} {{ ?role a owl:ObjectProperty . ?individual1 a owl:NamedIndividual ; ?role ?individual2 . ?individual2 a owl:NamedIndividual .}} }}'.format(self.prefixes,self.dlGraph))['results']['bindings']]

    def getDLGraphClassesForIndividual(self,individual):
        '''
        input:  self
        return: [ str ]
        
        Gets a list of classes that an individual is in
        '''         
        return [result['type']['value'].split('#')[1] for result in self.query('{} SELECT DISTINCT ?type WHERE {{ graph {} {{ ?type a owl:Class . :{} a ?type ; a owl:NamedIndividual }} }}'.format(self.prefixes,self.dlGraph,individual))['results']['bindings']]
    
    def getDLGraphIndividualsForClass(self,cl):
        '''
        input:  self
        return: [ str ]
        
        Gets a list of classes that an individual is in
        '''       
        return [result['type']['value'].split('#')[1] for result in self.query('{} SELECT DISTINCT ?type WHERE {{ graph {} {{ :{} a owl:Class . ?type a :{} ; a owl:NamedIndividual }} }}'.format(self.prefixes,self.dlGraph,cl,cl))['results']['bindings']]    
    
    def getDLGraphIndividualsForRole(self,role):
        '''
        input:  self
        return: [ str ]
        
        Gets a list of classes that an individual is in
        '''       
        return [(result['one']['value'].split('#')[1],result['two']['value'].split('#')[1]) for result in self.query('{} SELECT DISTINCT ?one ?two WHERE {{ graph {} {{ :{} a owl:ObjectProperty . ?one :{} ?two ; a owl:NamedIndividual . ?two a owl:NamedIndividual }} }}'.format(self.prefixes,self.dlGraph,cl,cl))['results']['bindings']]    

    
    def getDLGraphTriplesForIndivdual(self,individual):
        '''
        input:  self
        return: [ (str,str,str) ]
        
        Gets a list of triples that connect an instruction individual to another with a role in the dl graph
        '''   
        query1 = {(individual,result['role']['value'].split('#')[1],result['individual2']['value'].split('#')[1]) for result in self.query('{} SELECT DISTINCT ?role ?individual2 WHERE {{ graph {} {{ ?role a owl:ObjectProperty . :{} a owl:NamedIndividual ; ?role ?individual2 . ?individual2 a owl:NamedIndividual .}} }}'.format(self.prefixes,self.dlGraph,individual))['results']['bindings']}
        query2 = {(result['individual2']['value'].split('#')[1],result['role']['value'].split('#')[1],individual) for result in self.query('{} SELECT DISTINCT ?role ?individual2 WHERE {{ graph {} {{ ?role a owl:ObjectProperty . :{} a owl:NamedIndividual . ?individual2 a owl:NamedIndividual ; ?role :{} .}} }}'.format(self.prefixes,self.dlGraph,individual,individual))['results']['bindings']}
        
        return query1.union(query2)
    
    def getDLGraphTriplesForRole(self,role):
        '''
        input:  self
        return: [ (str,str,str) ]
        
        Gets a list of triples that connect an instruction individual to another with a role in the dl graph
        '''   
        return {(result['individual1']['value'].split('#')[1],role,result['individual2']['value'].split('#')[1]) for result in self.query('{} SELECT DISTINCT ?individual1 ?individual2 WHERE {{ graph {} {{ :{} a owl:ObjectProperty . ?individual1 a owl:NamedIndividual ; :{} ?individual2 . ?individual2 a owl:NamedIndividual .}} }}'.format(self.prefixes,self.dlGraph,role,role))['results']['bindings']} 
    
    '''Class and internal functions (comments ommited unless requested)'''
    
    instructionGraph = ':instructionGraph'
    dlGraph = ':dlGraph'
    koiosGraph = ':koiosGraph'
    thinkGraph = ':thinkGraph'    
    predQueryMappings = {'ruleString':'asString','name':'name','arity':'arity','step':'reasoningStep','string':'asString','predicateType':'isa','termType':'isa','termString':'asString','term2Type':'isa','term2String':'asString','functionTermType':'isa','functionTermString':'asString','functionName':'name'} 
    prefixes = 'PREFIX : <http://www.uagent.com/ontology#>\nPREFIX opla: <http://ontologydesignpatterns.org/opla#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n'
    
    def __init__(self,stopOldServer=False,owlFile=False):
        
        if not stopOldServer and self.isRunning(): self.initialized = True ; return
        
        self.initialized = False
        
        if stopOldServer: self.stopOldServer()
             
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:            
            while s.connect_ex(('localhost', 3030)) == 0: 
                print('Waiting for ontology server socket to become free...')
                
        print("Starting ontology server...")
        subprocess.Popen(['java', '-jar', 'lib/fuseki/fuseki-server.jar', '--update','--quiet'])
        
        if owlFile: self.load(filename=owlFile)
                
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
    
    def add_instruction_knowledge(self,ace,drs,factsExpression,nestedExpressions,facts,rules,reasonerFacts,groundRules):
        
        # add ACE
        instructionString = ' '.join(['[] a :Instruction ; :asString "{}" .'.format(x.replace('"','\\\"')) for x in ace.splitlines()])
        
        # add DRS
        instructionString = instructionString + ' . '.join(factsExpression.tripleString()) + ' . '
        
        for nestedExpression in nestedExpressions.expressions():
            instructionString = instructionString + nestedExpression.tripleString()         
        
        dlString = ''
        
        # add rules
        for fact in facts:
            instructionString = instructionString + '[] a :Instruction ; :asRule [ a :Fact ; :inReasoningStep 0 ; :hasHeadPredicate ['+fact.tripleString()+'] ; :asString "'+str(fact)+'" ] . '
            dlString = dlString + fact.dlTripleString() + '\n'
            
        for rule in rules:
            instructionString = instructionString + '[] a :Instruction ; :asRule [ :asString "' +rule.toRule()+ '" ; a :Rule ; :inReasoningStep 0 ; :hasHeadPredicate ['+rule.head.pred.tripleString()+'] '+''.join(['; :hasBodyPredicate [{}] '.format(x.tripleString()) for x in rule.body.preds])+']. '
            
        for order,fact in reasonerFacts:
            instructionString = instructionString + '[] a :Instruction ; :asRule [ a :Fact ; :inReasoningStep '+str(order)+' ; :hasHeadPredicate ['+fact.tripleString()+'] ; :asString "'+str(fact)+'" ] . '
            dlString = dlString + fact.dlTripleString() + '\n'
            
        for order,rule in groundRules:
            instructionString = instructionString + '[] a :Instruction ; :asRule [ :asString "' +rule.toRule()+ '" ; a :Rule ; :inReasoningStep '+str(order)+' ; :hasHeadPredicate ['+rule.head.pred.tripleString()+'] '+''.join(['; :hasBodyPredicate [{}] '.format(x.tripleString()) for x in rule.body.preds])+']. '
        
        self.add_to_instructions_graph(instructionString)            
        self.add_to_dl_graph(dlString)
        
    def add(self,data):
        subprocess.call(['lib/fuseki/s-update', '--service=http://localhost:3030/uagent/update','{} INSERT DATA  {{ {} }}'.format(self.prefixes,data)])
        
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

    def select_in_one_graph(self,selectors,expression,graph):
        result = self.query('{} SELECT {} WHERE {{ {{ {} }} union {{ graph {} {{ {} }} }} }}'.format(self.prefixes,' '.join(selectors),expression,graph,expression))
        return set(answer[selector]['value'] for selector in result['head']['vars'] for answer in result['results']['bindings'])
    
    def factQueryExpression(self):
        return '''[] a :Instruction ; :asRule [ :inReasoningStep ?step ; a :Fact ; :hasHeadPredicate ?pred ; :asString ?ruleString ] . 
                 ?pred a ?predicateType ; :hasName ?name ; :hasArity ?arity ; :asString ?string . 
                 optional {?pred :hasArity 1 ; :hasTerm [ a ?termType ; :asString ?termString ] . } . 
                 optional {?pred :hasTerm [ a ?termType ; :asString ?termString ] ; :hasTerm [ a ?term2Type ; :asString ?term2String ; :hasName ?functionName ; :hasTerm [a ?functionTermType ; :asString ?functionTermString]] . filter(?termType != ?term2Type)} 
                 optional {?pred :hasArity 2 ; :hasTerm ?term1 ; :hasTerm ?term2 . ?term1 a ?termType ; :asString ?termString . ?term2 a ?term2Type ; :asString ?term2String . filter(?term1 != ?term2) } .'''
    
    def headQueryExpression(self):
        return '''[] a :Instruction ; :asRule ?rule .
                 ?rule :inReasoningStep ?step ; a :Rule ; :hasHeadPredicate ?pred ; :asString ?ruleString . 
                 ?pred a ?predicateType ; :hasName ?name ; :hasArity ?arity ; :asString ?string . 
                 optional {?pred :hasArity 1 ; :hasTerm [ a ?termType ; :asString ?termString ] . } . 
                 optional {?pred :hasTerm [ a ?termType ; :asString ?termString ] ; :hasTerm [ a ?term2Type ; :asString ?term2String ; :hasName ?functionName ; :hasTerm [a ?functionTermType ; :asString ?functionTermString]] . filter(?termType != ?term2Type)} 
                 optional {?pred :hasArity 2 ; :hasTerm ?term1 ; :hasTerm ?term2 . ?term1 a ?termType ; :asString ?termString . ?term2 a ?term2Type ; :asString ?term2String . filter(?term1 != ?term2) } .'''
    
    def bodyQueryExpression(self,head):
        return '[] :hasHeadPredicate [ :asString "'+head+ '''" ] ; :inReasoningStep ?step ; a :Rule ; :hasBodyPredicate ?pred . 
                 ?pred a ?predicateType ; :hasName ?name ; :hasArity ?arity ; :asString ?string . 
                 optional {?pred :hasArity 1 ; :hasTerm [ a ?termType ; :asString ?termString ] . } . 
                 optional {?pred :hasTerm [ a ?termType ; :asString ?termString ] ; :hasTerm [ a ?term2Type ; :asString ?term2String ; :hasName ?functionName ; :hasTerm [a ?functionTermType ; :asString ?functionTermString]] . filter(?termType != ?term2Type)} 
                 optional {?pred :hasArity 2 ; :hasTerm ?term1 ; :hasTerm ?term2 . ?term1 a ?termType ; :asString ?termString . ?term2 a ?term2Type ; :asString ?term2String . filter(?term1 != ?term2) } .'''     
    
    def mapFlatPredQueryResultIntoNestedDictionary(self,result,fact=True,head=True):        
        if head:
            preds = []
            for pred in result:
                if len(pred) == 8:
                    preds.append({'isa':'Fact' if fact else 'Rule',self.predQueryMappings['ruleString']:pred['ruleString'],self.predQueryMappings['step']:pred['step'],'preCondition':[],'postCondition':[{self.predQueryMappings['string']:pred['string'],self.predQueryMappings['name']:pred['name'],self.predQueryMappings['arity']:pred['arity'],'isa':pred['predicateType'],'term':[{self.predQueryMappings['termString']:pred['termString'],self.predQueryMappings['termType']:pred['termType']}]}]})
                elif len(pred) == 10 and re.match(".*?\((.*?)\,.*",pred['string']).groups()[0] == pred['termString']:
                    preds.append({'isa':'Fact' if fact else 'Rule',self.predQueryMappings['ruleString']:pred['ruleString'],self.predQueryMappings['step']:pred['step'],'preCondition':[],'postCondition':[{self.predQueryMappings['string']:pred['string'],self.predQueryMappings['name']:pred['name'],self.predQueryMappings['arity']:pred['arity'],'isa':pred['predicateType'],'term':[{self.predQueryMappings['termString']:pred['termString'],self.predQueryMappings['termType']:pred['termType']},{self.predQueryMappings['term2String']:pred['term2String'],self.predQueryMappings['term2Type']:pred['term2Type']}]}]})                            
                elif len(pred) == 13:
                    preds.append({'isa':'Fact' if fact else 'Rule',self.predQueryMappings['ruleString']:pred['ruleString'],self.predQueryMappings['step']:pred['step'],'preCondition':[],'postCondition':[{self.predQueryMappings['string']:pred['string'],self.predQueryMappings['name']:pred['name'],self.predQueryMappings['arity']:pred['arity'],'isa':pred['predicateType'],'term':[{self.predQueryMappings['termString']:pred['termString'],self.predQueryMappings['termType']:pred['termType']},{self.predQueryMappings['term2String']:pred['term2String'],self.predQueryMappings['functionName']:pred['functionName'],self.predQueryMappings['term2Type']:pred['term2Type'],'term':[{self.predQueryMappings['functionTermString']:pred['functionTermString'],self.predQueryMappings['functionTermType']:pred['functionTermType']}]}]}]})                             
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
    
    def count_in_one_graph(self,expression,graph):
        result = self.query('{} SELECT (COUNT(*) AS ?count) WHERE {{ {{ {} }} union {{ graph {} {{ {} }} }} }} GROUP BY ?count'.format(self.prefixes,expression,graph,expression))['results']['bindings']
        return int(result[0]['count']['value']) if len(result) == 1 else 0

    def count_predicate_in_one_graph(self,predicate,graph):         
        return self.count_in_one_graph(' ?subject {} ?object'.format(predicate),graph)

    def count_subject_in_one_graph(self,subject,graph):
        return self.count_in_one_graph('{} ?predicate ?object'.format(subject),graph)

    def count_object_in_one_graph(self,object,graph):
        return self.count_in_one_graph('?subject ?predicate {}'.format(object),graph)

    def count_subject_predicate_in_one_graph(self,subject,predicate,graph):
        return self.count_in_one_graph('{} {} ?object'.format(subject,predicate),graph)

    def count_subject_object_in_one_graph(self,subject,object,graph):
        return self.count_in_one_graph('{} ?predicate {}'.format(subject,object),graph)

    def count_predicate_object_in_one_graph(self,predicate,object,graph):
        return self.count_in_one_graph('?subject {} {}'.format(predicate,object),graph)
    def select_object_with_predicate_in_one_graph(self,predicate,graph):
        return self.select_in_one_graph(['?object'],'?subject {} ?object'.format(predicate),graph)
    
    def select_subject_with_predicate_in_one_graph(self,predicate,graph):
        return self.select_in_one_graph(['?subject'],'?subject {} ?object'.format(predicate),graph)
    
if __name__ == "__main__":
    print("Starting ontology server...")
    Ontology().load()
    