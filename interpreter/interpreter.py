import os
import re
import subprocess
import sys

sys.path.insert(1, os.getcwd()+'/ontology')
from ontology import Ontology

class Term:

    def __init__(self,name,*args):
        self.name = self.makeName(name)
        self.args = [self.makeName(arg) for arg in args]

    def isInt(self,s):
        try: 
            s = int(s)
            return s
        except ValueError:
            return False

    def isFloat(self,s):
        try: 
            s = float(s)
            return s
        except ValueError:
            return False    

    def makeName(self,arg):
        if i := self.isInt(arg):
            return i
        if f := self.isFloat(arg):
            return f
        if m := re.match("string\((.*)\)",arg):
            return "'" + m.groups()[0] + "'"
        if m := re.match("named\((.*)\)",arg): 
            return m.groups()[0]
        return arg   

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class Variable(Term):

    def __init__(self,name,*args):
        if not re.match("^([A-Z][0-9]*)$",name):
            raise Exception("Not a DRS variable")
        super().__init(name,*args)

class Constant(Term):

    def __init__(self,name,*args):
        if re.match("^([A-Z][0-9]*)$",name):
            raise Exception("Not a DRS constant")
        super().__init__(name,*args)

class Function(Term):

    def __init__(self,name,*args):
        super().__init__(name,*args)

    def __str__(self):
        return self.name + "(" + (",".join(self.terms) if len(terms) > 1 else self.terms[0]) + ")"

    def __repr__(self):
        return self.name + "(" + (",".join(self.terms) if len(terms) > 1 else self.terms[0]) + ")"

class Predicate:
    '''Corresponds to a prolog predicate arity > 2'''

    def __init__(self,name,*args):
        self.name = self.makeName(name)
        self.args = [self.makeName(x) for x in args]

    def isInt(self,s):
        try: 
            s = int(s)
            return s
        except ValueError:
            return False

    def isFloat(self,s):
        try: 
            s = float(s)
            return s
        except ValueError:
            return False

    def makeName(self,arg):
        if i := self.isInt(arg):
            return i
        if f := self.isFloat(arg):
            return f
        if m := re.match("string\((.*)\)",arg):
            return "'" + m.groups()[0] + "'"
        if m := re.match("named\((.*)\)",arg): 
            return m.groups()[0]
        return arg  

    def letter(self):
        return self.letter

    def name(self):
        return self.name

    def indent(self):
        return self.indent 

    def arg(self,i):
        return self.args[i]

    def args(self):
        return self.args

    def __str__(self):
        return self.name + "(" + (",".join(self.args) if len(self.args) > 1 else self.args[0]) + ")"

    def __repr__(self):
        return self.name + "(" + (",".join(self.args) if len(self.args) > 1 else self.args[0]) + ")"

class PredicateList:
    '''List of DRS predicates'''

    def __init__(self):
        self.preds = []

    def append(self,pred):
        if not isinstance(pred,Predicate): 
            raise Exception("Must append Predicates to PredicateList")
        self.preds.append(pred)

    def remove(self,pred):
        if not isinstance(pred,Predicate): 
            raise Exception("Must remove Predicates from PredicateList")
        self.preds.remove(pred)

    def removeAt(self,i):      
        self.preds.pop(i)    

    def predicates(self):
        return self.preds

    def predicate(self,i):
        return self.preds[i]
    
    def __len__(self):
        return len(self.preds)    

    def __str__(self):        
        return "[" + ",".join([str(x) for x in self.preds]) + "]"

    def __repr__(self):
        return "[" + ",".join([str(x) for x in self.preds]) + "]"

class Class(Predicate):
    '''Corresponds to both a Descrioption logic Class and a prolog predicate arity /1 read from DRS'''
    def __init__(self,indent,letter,name,inst,num1,num2):
        super().__init__(name,inst,num1,num2)
        self.indent = self.makeName(indent)
        self.letter = self.makeName(letter)      

    def __str__(self):
        return self.name + "(" + self.args[0] + ")"

    def __repr__(self):
        return self.name + "(" + self.args[0] + ")"

class Role(Predicate):
    '''Corresponds to both a Descrioption logic Role and a prolog predicate arity /2 read from DRS'''
    def __init__(self,indent,letter,name,subj,obj,num1,num2):
        super().__init__(name,subj,obj,num1,num2)
        self.indent = self.makeName(indent)
        self.letter = self.makeName(letter)        

    def __str__(self):
        return self.name + "(" + self.args[0] + "," + self.args[1] + ")"

    def __repr__(self):
        return self.name + "(" + self.args[0] + "," + self.args[1] + ")"

class Object(Constant):
    '''DRS object'''
    def __init__(self,indent,letter,name,quant,stuff1,stuff2,stuff3,num1,num2):
        super().__init__(name,quant,stuff1,stuff2,stuff3,num1,num2)
        self.indent = self.makeName(indent)
        self.letter = self.makeName(letter)
    
    def __str__(self):
        return "'" + self.name + "':" + self.letter

    def __repr__(self):
        return "'" + self.name + "':" + self.letter   

class ObjectList:
    '''List of DRS objects'''

    def __init__(self):
        self.objs = []
        self.var = {}

    def reset(self):
        self.objs = []
        self.var = {}

    def append(self,obj):
        if not isinstance(obj,Object): 
            raise Exception("Must append Objects to ObjectList")
        self.objs.append(obj)

        if obj.letter not in self.var: 
            self.var[obj.letter] = obj.name

    def remove(self,obj):
        if not isinstance(obj,Object): 
            raise Exception("Can only remove Objects from ObjectList")        
        self.objs.remove(obj)
        del self.var[obj.letter]
        for obj in self.objs:
            if obj.letter not in self.var:
                self.var[obj.letter] = obj.name

    def removeAt(self,i):      
        self.objs.pop(i)  

    def objects(self):
        return self.objs

    def object(self,i):
        return self.objs[i]   

    def nameDictionary(self):
        return self.var

    def __len__(self):
        return len(self.objs)
    
    def __str__(self):        
        return "[" + ",".join([str(x) for x in self.objs]) + "]"

    def __repr__(self):
        return "[" + ",".join([str(x) for x in self.objs]) + "]"

class Property(Constant):
    '''DRS property.'''
    def __init__(self,indent,letter,name,type,num1,num2):
        super().__init__(name,type,num1,num2)
        self.indent = self.makeName(indent)
        self.letter = self.makeName(letter)

class PropertyList:
    '''List of DRS properties'''

    def __init__(self):
        self.props = []
        self.var = {}

    def append(self,prop):
        if not isinstance(prop,Property): 
            raise Exception("Must append Properties to PropertyList")
        self.props.append(prop)
        if not prop.letter in self.var: 
            self.var[prop.letter] = prop.name

    def remove(self,prop):
        if not isinstance(prop,Property): 
            raise Exception("Must remove Properties from PropertyList")
        self.props.remove(prop)
        del self.var[prop.letter]
        for prop in self.props:
            if prop.letter not in self.var:
                self.var[prop.letter] = prop.name

    def removeAt(self,i):      
        self.props.pop(i)    

    def properties(self):
        return self.props

    def property(self,i):
        return self.props[i]

    def nameDictionary(self):
        return self.var
    
    def __len__(self):
        return len(self.props)    

    def __str__(self):        
        return "[" + ",".join([str(x) for x in self.props]) + "]"

    def __repr__(self):
        return "[" + ",".join([str(x) for x in self.props]) + "]"

class Relation(Predicate):
    '''DRS relation'''
    def __init__(self,name,to,num1,num2):
        super().__init__(name,to,num1,num2)
        self.indent = self.makeName(indent)
        self.letter = self.makeName(letter)       

    def __str__(self):
        return self.name + "(" + self.args[0] + ")"

    def __repr__(self):
        return self.name + "(" + self.args[0] + ")"

class RelationList:
    '''List of DRS relations'''

    def __init__(self):
        self.rels = []

    def append(self,rel):
        if not isinstance(rel,Relation): 
            raise Exception("Must append Relations to RelationList")
        self.rels.append(rel)

    def remove(self,rel):
        if not isinstance(rel,Relation): 
            raise Exception("Must remove Relations from RelationList")
        self.rels.remove(rel)    

    def removeAt(self,i):      
        self.preps.pop(i)

    def relations(self):
        return self.rels

    def relation(self,i):
        return self.rels[i]   

    def __len__(self):
        return len(self.rels)
    
    def __str__(self):        
        return "[" + ",".join([str(x) for x in self.rels]) + "]"

    def __repr__(self):
        return "[" + ",".join([str(x) for x in self.rels]) + "]"

class Preposition(Function):
    '''DRS relation'''
    def __init__(self,indent,letter,name,to,num1,num2):
        super().__init__(name,to,num1,num2) 
        self.indent = self.makeName(indent)
        self.letter = self.makeName(letter)

    def __str__(self):
        return self.name + "(" + self.args[0] + ")"

    def __repr__(self):
        return self.name + "(" + self.args[0] + ")"

class PrepositionList:
    '''List of DRS prepositions'''

    def __init__(self):
        self.preps = []

    def append(self,prep):
        if not isinstance(prep,Preposition): 
            raise Exception("Must append Prepositions to PrepositionList")
        self.preps.append(prep)

    def remove(self,prep):
        if not isinstance(prep,Preposition): 
            raise Exception("Can only remove Prepositions from PrepositionList")        
        self.preps.remove(prep)

    def removeAt(self,i):      
        self.preps.pop(i)    

    def prepositions(self):
        return self.preps

    def preposition(self,i):
        return self.preps[i]
    
    def __len__(self):
        return len(self.preps)    

    def __str__(self):        
        return "[" + ",".join([str(x) for x in self.preps]) + "]"

    def __repr__(self):
        return "[" + ",".join([str(x) for x in self.preps]) + "]"

class Expression:
    '''One DRS expression, composed of DRS components'''

    def __init__(self):
        self.predicates = PredicateList()
        self.relations = RelationList()
        self.prepositions = PrepositionList()
        self.objects = ObjectList()
        self.properties = PropertyList()
        self.empty = True

    def getAllParts(self):
        return self.predicates,self.relations,self.prepositions,self.objects,self.properties

    def append(self,thing):
        if isinstance(thing,Predicate):
            self.predicates.append(thing)
            self.empty = False
        elif isinstance(thing,Relation):
            self.relations.append(thing)
            self.empty = False
        elif isinstance(thing,Preposition):
            self.prepositions.append(thing)
            self.empty = False
        elif isinstance(thing,Object):
            self.objects.append(thing)
            self.empty = False
        elif isinstance(thing,Property):
            self.properties.append(thing)
            self.empty = False
        else:
            raise Exception("Can only append Predicate,Relation,Preposition,Object,or Property")

    def remove(self,thing):
        if isinstance(thing,Predicate):
            self.predicates.remove(thing)
            self.empty = all([len(x) == 0 for x in [self.predicates,self.relations,self.prepositions,self.objects,self.properties]])
        elif isinstance(thing,Relation):
            self.relations.remove(thing)
            self.empty = all([len(x) == 0 for x in [self.predicates,self.relations,self.prepositions,self.objects,self.properties]])
        elif isinstance(thing,Preposition):
            self.prepositions.remove(thing)
            self.empty = all([len(x) == 0 for x in [self.predicates,self.relations,self.prepositions,self.objects,self.properties]])
        elif isinstance(thing,Object):
            self.objects.remove(thing)
            self.empty = all([len(x) == 0 for x in [self.predicates,self.relations,self.prepositions,self.objects,self.properties]])
        elif isinstance(properties,Property):
            self.properties.remove(thing)
            self.empty = all([len(x) == 0 for x in [self.predicates,self.relations,self.prepositions,self.objects,self.properties]])
        else:
            raise Exception("Can only remove Predicate,Relation,Preposition,Object,or Property")

    def removePredicateAt(self,i):
        self.predicates.removeAt(i)

    def removeRelationAt(self,i):
        self.predicates.removeAt(i)

    def removePrepositionAt(self,i):
        self.predicates.removeAt(i)

    def removeObjectAt(self,i):
        self.predicates.removeAt(i)

    def removePropertyAt(self,i):
        self.predicates.removeAt(i)

    def predicates(self):
        self.predicates.predicates()

    def predicate(self,i):
        self.predicates.predicate(i)

    def relations(self):
        self.relations.relations()

    def relation(self,i):
        self.relations.relation(i)

    def prepositions(self):
        self.prepositions.prepositions()

    def preposition(self,i):
        self.prepositions.preposition(i)

    def objects(self):
        self.objects.objects()

    def object(self,i):
        self.objects.object(i)
    
    def properties(self):
        self.properties.properties()

    def property(self,i):
        self.properties.property(i)
        
    def __str__(self):        
        return "predicates [" + ",".join([str(x) for x in self.predicates.predicates()]) + "]\nrelations [" + ",".join([str(x) for x in self.relations.relations()]) + "]\nprepositions [" + ",".join([str(x) for x in self.prepositions.prepositions()]) + "]\nobjects [" + ",".join([str(x) for x in self.objects.objects()]) + "]\nproperties [" + ",".join([str(x) for x in self.properties.properties()]) + "]"

    def __repr__(self):
        return "predicates [" + ",".join([str(x) for x in self.predicates.predicates()]) + "]\nrelations [" + ",".join([str(x) for x in self.relations.relations()]) + "]\nprepositions [" + ",".join([str(x) for x in self.prepositions.prepositions()]) + "]\nobjects [" + ",".join([str(x) for x in self.objects.objects()]) + "]\nproperties [" + ",".join([str(x) for x in self.properties.properties()]) + "]"
    
class NestedExpression:
    
    def __init__(self):
        self.typeIDCharacter = None
        self.first = None
        self.second = None        
    
    def setTypeIDCharacter(self,idchar):
        if not (isinstance(idchar,str) and len(idchar)==1): 
            raise Exception("Must use Characters")          
        self.typeIDCharacter = idchar
        
    def setFirstExpression(self,first):
        if not (isinstance(first,NestedExpression) or isinstance(first,Expression)): 
            raise Exception("Must use NestedExpressions or Expressions")        
        self.first = first
    
    def setSecondExpression(self,second):
        if not (isinstance(second,NestedExpression) or isinstance(second,Expression)): 
            raise Exception("Must use NestedExpressions or Expressions")        
        self.second = second  
        
    def firstExpression(self):
        return self.first
    
    def secondExpression(self):
        return self.second
    
    def typeCharacter(self):
        return self.typeIDCharacter
    
    def __str__(self):        
        return "type = " + str(self.typeIDCharacter) + "\n\nfirst expression:\n\n" + str(self.first) + "\n\nsecond expression:\n\n" + str(self.second)

    def __repr__(self):
        return "type = " + str(self.typeIDCharacter) + "\n\nfirst expression:\n\n" + str(self.first) + "\n\nsecond expression:\n\n" + str(self.second)    

class NestedExpressionList:
    '''List of nested DRS expressions'''

    def __init__(self):
        self.exps = []

    def append(self,exp):
        if not isinstance(exp,NestedExpression): 
            raise Exception("Must append NestedExpressions to NestedExpressionList")
        self.exps.append(exp)

    def remove(self,exp):
        if not isinstance(exp,NestedExpression): 
            raise Exception("Must remove NestedExpressions from NestedExpressionList")
        self.exps.remove(exp)

    def removeAt(self,i):      
        self.exps.pop(i)    

    def expressions(self):
        return self.exps

    def expression(self,i):
        return self.exps[i]

    def __len__(self):
        return len(self.exps)
    
    def __str__(self):        
        return "[" + "\n\n,".join([str(x) for x in self.exps]) + "]"

    def __repr__(self):
        return "[" + "\n\n,".join([str(x) for x in self.exps]) + "]"
    
class Body:
    '''Body of a prolog rule. append and remove maintain a list of terms for verification.'''
    def __init__(self):
        self.body = []
        self.var = set()

    def append(self,pred):
        if not (isinstance(pred,Class) or isinstance(pred,Role) or isinstance(pred,Predicate)): raise
        self.body.append(pred)
        if isinstance(pred,Class) and not pred.args[0] in self.var: self.var.add(pred.args[0])
        if isinstance(pred,Role) and not pred.args[0] in self.var: self.var.add(pred.args[0])
        if isinstance(pred,Role) and not pred.args[1] in self.var: self.var.add(pred.args[1])

    def remove(self,pred):
        oldVars = set()
        if isinstance(pred,Class): oldVars.add(pred.args[0])
        if isinstance(pred,Role): oldVars.add(pred.args[0]) ; oldVars.add(pred.args[1])
        self.body.remove(pred)
        for pred in self.body:
            if isinstance(pred,Class) and pred.args[0] in oldVars:
                oldVars.remove(pred.args[0])
                if len(oldVars) == 0: return
            if isinstance(pred,Role) and pred.args[0] in oldVars:
                oldVars.remove(pred.args[0])
                if len(oldVars) == 0: return                
            elif isinstance(pred,Role) and pred.args[1] in oldVars:
                oldVars.remove(pred.args[1])
                if len(oldVars) == 0: return
        for var in oldVars:
            self.var.remove(var)

    def __str__(self):        
        return ",".join([str(x) for x in self.body])

    def __repr__(self):
        return ",".join([str(x) for x in self.body])

class Implication:
    '''Prolog Rule'''
    def __init__(self,body,head):
        self.head = head
        self.body = body

    def toRule(self):
        return ",".join([str(x) for x in self.body.body]) + " => " + str(self.head)

    def __str__(self):        
        return str(self.head) + ":-" + ",".join([str(x) for x in self.body.body])

    def __repr__(self):
        return str(self.head) + ":-" + ",".join([str(x) for x in self.body.body])

class Disjunction:
    '''Or'''
    def __init__(self,a,b):
        self.first = a
        self.second = b

    def toRule(self):
        return str(self.first) + " v " + str(self.second)

    def __str__(self):        
        return str(self.first) + ";" + str(self.second)

    def __repr__(self):
        return str(self.first) + ";" + str(self.second)

def checkDictsForKey(key,*dicts):
    for d in dicts:
        if key in d:
            return d[key] if d[key] not in d else d[d[key]]
    return key

def writePrologFile(facts, prolog, prologfile, factFile, groundFile):
    '''writes a prolog file that executes a logic program built from 
    the instructions that will produce all facts it enatils in one 
    file and all solved rules it used to obtain enatilments facts in another'''    
    program = sorted(prolog+facts, key=lambda x: x[0])
    open(prologfile, "w").write('{}\n:- open("{}",write, Stream),open("{}",write, Stream2),\n{}close(Stream),close(Stream2),halt.\n'.format(''.join(['{}\n'.format('{} :- {}.'.format(thing[0], ",".join(thing[1])) if isinstance(thing, list) else "{}.".format(thing)) for thing in program]), factFile, groundFile, ''.join(['forall(({}),({})),\n'.format(thing[0]+","+",".join(thing[1]), '{}write(Stream2," => "),writeq(Stream2,{}),writeln(Stream2,""),writeq(Stream,{}),writeln(Stream,"")'.format(''.join(['writeq(Stream2,{}),{}'.format(stuff, 'write(Stream2,","),' if not stuff == thing[1][-1] else "") for stuff in thing[1]]), thing[0], thing[0])) for thing in prolog])))

def runProlog(facts, prolog, prologfile,makeLogFiles):
    '''runs the prolog file and reads and discards its output files
    returns the lines from the files it discards'''

    factFile = "interpreter/reasonerFacts.txt"
    groundFile = "interpreter/groundRules.txt"

    writePrologFile(facts, prolog, prologfile, factFile, groundFile)

    subprocess.call(['swipl', prologfile])

    reasonerFacts = open(factFile, "r").read().splitlines()
    groundRules = open(groundFile, "r").read().splitlines()

    if not makeLogFiles: os.remove(factFile)
    if not makeLogFiles: os.remove(groundFile)

    return reasonerFacts, groundRules

def getDRSFromACE(ace):
    '''Runs APE on the ACE file and returns the lines of the DRS it created'''    
    print("Interpreting ACE...")

    process = subprocess.Popen(['lib/ape/ape.exe', '-cdrspp'],stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    process.stdin.write(ace.encode('utf-8'))
    drs = process.communicate()[0].decode('utf-8').splitlines()
    process.stdin.close()  # possibly unnecessary when function returns? not great at subprocess

    return drs

def initEmpties():

    ObjectList.empty = ObjectList()
    PropertyList.empty = PropertyList()

def compileRegexes():

    # these match all possible DRS lines as defined by the current semantics
    xmlBeforeDRSPattern = re.compile("^\s*(?:<.*>)?$")
    variablesPattern = re.compile("^\s*<drspp>\s*\[([A-Z][0-9]*(?:,[A-Z][0-9]*)*)?\]\s*")
    objectPattern = re.compile("^()object\(([A-Z][0-9]*),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    unaryPredicatePattern = re.compile("^()predicate\(([A-Z][0-9]*),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    binaryPredicatePattern = re.compile("^()predicate\(([A-Z][0-9]*),([^,]+),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    propertyPattern = re.compile("^()property\(([A-Z][0-9]*),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    expressionPattern = re.compile("^(\s+)[^\s]+.*")   
    doneReadingPattern = re.compile("^\s*</drspp>.*")
    prepositionPattern = re.compile("^()modifier_pp\(([A-Z][0-9]*),([^,]+),([A-Z][0-9]*)\)-(\d+)/(\d+)\s*")
    relationPattern = re.compile("^()relation\(([A-Z][0-9]*),([^,]+),([A-Z][0-9]*)\)-(\d+)/(\d+)\s*")

    # expressions have the same stuff as the facts, they are just indented (\s+)
    expressionVariablesPattern = re.compile("^(\s+)\[([A-Z][0-9]*(?:,[A-Z][0-9]*)*)?\]\s*")
    expressionAnonymousPattern = re.compile("^(\s+)\[\]\s*")
    implicationSignPattern = re.compile("^(\s+)(=&gt;)\s*")
    disjunctionSignPattern = re.compile("^(\s+v)\s*")
    expressionObjectPattern = re.compile("^(\s+)object\(([A-Z][0-9]*),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    expressionUnaryPredicatePattern = re.compile("^(\s+)predicate\(([A-Z][0-9]*),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    expressionBinaryPredicatePattern = re.compile("^(\s+)predicate\(([A-Z][0-9]*),([^,]+),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    expressionPropertyPattern = re.compile("^(\s+)property\(([A-Z][0-9]*),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    expressionPrepositionPattern = re.compile("^(\s+)modifier_pp\(([A-Z][0-9]*),([^,]+),([A-Z][0-9]*)\)-(\d+)/(\d+)\s*")
    expressionRelationPattern = re.compile("^(\s+)relation\(([A-Z][0-9]*),([^,]+),([A-Z][0-9]*)\)-(\d+)/(\d+)\s*")
    expressionDonePattern = re.compile("^[^\s]+.*")   

    return {'xmlBeforeDRS':xmlBeforeDRSPattern,'variables':variablesPattern,'object':objectPattern,'unaryPredicate':unaryPredicatePattern,
            'binaryPredicate':binaryPredicatePattern,'property':propertyPattern,'expression':expressionPattern,'doneReading':doneReadingPattern,
            'preposition':prepositionPattern,'expressionVariables':expressionVariablesPattern,'implicationSign':implicationSignPattern,
            'disjunctionSign':disjunctionSignPattern,'expressionObject':expressionObjectPattern,'expressionUnaryPredicate':expressionUnaryPredicatePattern,
            'expressionBinaryPredicate':expressionBinaryPredicatePattern,'expressionProperty':expressionPropertyPattern,'expressionPreposition':expressionPrepositionPattern,
            'relation':relationPattern,'expressionRelation':expressionRelationPattern,'expressionDone':expressionDonePattern,'expressionAnonymous':expressionAnonymousPattern}

def appendToDRSFile(drsline):
    '''Self explanatory'''    
    open("interpreter/DRS.txt","a").write(drsline + '\n')

def readExpression(drs,globalLineIndex,regexPatterns,makeLogFiles):

    nestedExpression = NestedExpression()
    currentExpression = Expression()

    thisExpressionLocalLineIndex = 0

    for currentReadingIndex in range(globalLineIndex,len(drs)):
        
        # manage the indexes for nested expressions
        if thisExpressionLocalLineIndex >= currentReadingIndex: thisExpressionLocalLineIndex += 1
        currentReadingIndex = max(thisExpressionLocalLineIndex,currentReadingIndex)
        line = drs[currentReadingIndex]
        
        # check if expression is over
        if re.match(regexPatterns['doneReading'],line):
            if not currentExpression.empty and nestedExpression.firstExpression():
                nestedExpression.setSecondExpression(currentExpression)
                return currentReadingIndex-1,nestedExpression   
            elif not currentExpression.empty and not nestedExpression.typeCharacter():
                nestedExpression.setFirstExpression(currentExpression)
                return currentReadingIndex-1,currentExpression             
            else: 
                raise Exception("BAD")
        if re.match(regexPatterns['expressionDone'],line):
            nestedExpression.setSecondExpression(currentExpression)
            return currentReadingIndex-1,nestedExpression

        # is there another expression in the expresion?
                
        # anonymous expression
        if m := re.match(regexPatterns['expressionAnonymous'],line):
            
            if makeLogFiles: appendToDRSFile(line)
            
            # add to second
            if not currentExpression.empty and nestedExpression.firstExpression():
                nestedExpression.setSecondExpression(currentExpression)
                return currentReadingIndex-1,nestedExpression
            # add to first
            elif not currentExpression.empty:
                nestedExpression.setFirstExpression(currentExpression)
                currentExpression = Expression()
            # nested, skip this one
            else: continue
        
        # flat expression
        elif m := re.match(regexPatterns['expressionVariables'],line):
            if makeLogFiles: appendToDRSFile(line)
            
            # add to second
            if not currentExpression.empty and nestedExpression.firstExpression():
                nestedExpression.setSecondExpression(currentExpression)
                return currentReadingIndex-1,nestedExpression
            # add to first
            elif not currentExpression.empty:
                nestedExpression.setFirstExpression(currentExpression)
                currentExpression = Expression()
            # nested, skip this one
            else: continue

        # expression type identifiers
        elif m := re.match(regexPatterns['implicationSign'],line):
            if makeLogFiles: appendToDRSFile(m.groups()[0]+'=>')
            
            # is it the big => ?
            if nestedExpression.typeCharacter() and len(m.groups()[0]) == 3:
                nestedExpression.setSecondExpression(currentExpression)
                newExpression = NestedExpression()
                newExpression.setFirstExpression(nestedExpression)
                nestedExpression = newExpression
                newExpression = None
                currentExpression = Expression()
            # nested =>
            elif nestedExpression.typeCharacter():
                currentReadingIndex += 1
                if makeLogFiles: appendToDRSFile(drs[currentReadingIndex])
                thisExpressionLocalLineIndex,expression = readExpression(drs,currentReadingIndex+1,regexPatterns,makeLogFiles)
                newExpression = NestedExpression()
                newExpression.setFirstExpression(currentExpression)
                newExpression.setSecondExpression(expression)
                newExpression.setTypeIDCharacter('i')
                nestedExpression.setSecondExpression(newExpression)
                return thisExpressionLocalLineIndex,nestedExpression           
            
            nestedExpression.setTypeIDCharacter('i')
                
        elif m := re.match(regexPatterns['disjunctionSign'],line):
            if makeLogFiles: appendToDRSFile(m.groups()[0])
            
            # v is always nested
            if nestedExpression.typeCharacter():
                currentReadingIndex += 1
                if makeLogFiles: appendToDRSFile(drs[currentReadingIndex])
                thisExpressionLocalLineIndex,expression = readExpression(drs,currentReadingIndex+1,regexPatterns,makeLogFiles)
                newExpression = NestedExpression()
                newExpression.setFirstExpression(currentExpression)
                newExpression.setSecondExpression(expression)
                newExpression.setTypeIDCharacter('d')
                nestedExpression.setSecondExpression(newExpression)
                return thisExpressionLocalLineIndex,nestedExpression
            else:
                nestedExpression.setTypeIDCharacter('d')

        # normal components
        elif m := re.match(regexPatterns['expressionObject'],line): 
            if makeLogFiles: appendToDRSFile(line)
            currentExpression.append(Object(*m.groups()))
        elif m:= re.match(regexPatterns['expressionUnaryPredicate'],line): 
            if makeLogFiles: appendToDRSFile(line)
            currentExpression.append(Class(*m.groups()))        
        elif m:= re.match(regexPatterns['expressionBinaryPredicate'],line): 
            if makeLogFiles: appendToDRSFile(line)
            currentExpression.append(Role(*m.groups()))
        elif m := re.match(regexPatterns['expressionProperty'],line): 
            if makeLogFiles: appendToDRSFile(line)
            currentExpression.append(Property(*m.groups()))
        elif m := re.match(regexPatterns['expressionRelation'],line):
            if makeLogFiles: appendToDRSFile(line)
            currentExpression.append(Relation(*m.groups()))
        elif m := re.match(regexPatterns['expressionPreposition'],line):
            if makeLogFiles: appendToDRSFile(line)
            currentExpression.append(Preposition(*m.groups()))  
        else:
            # there are things we can add, depending on the requirements
            # just need to define the behavior to fix this exception
            raise Exception("Undefined Interpretation for DRS Expression",line)        

def interpret_ace(ace,makeLogFiles = False):
    '''interpret the ACE to obtain facts,rules,as well as new reasoner facts and rules'''
    
    # get DRS
    drs = getDRSFromACE(ace)   
    if makeLogFiles and os.path.isfile("interpreter/DRS.txt"): os.remove("interpreter/DRS.txt")

    # get ready to read
    initEmpties()
    regexPatterns = compileRegexes()

    mainExpression = Expression()
    nestedExpressions = NestedExpressionList()

    thisExpressionLocalLineIndex = 0

    for currentReadingIndex in range(len(drs)):
        
        # manage the indexes for nested expressions
        if thisExpressionLocalLineIndex >= currentReadingIndex: thisExpressionLocalLineIndex += 1
        currentReadingIndex = max(thisExpressionLocalLineIndex,currentReadingIndex)
        line = drs[currentReadingIndex]
        
        #check if the DRS is over or hasn't started yet
        if re.match(regexPatterns['doneReading'],line): break
        elif m := re.match(regexPatterns['xmlBeforeDRS'],line): continue

        # read DRS components
        elif m := re.match(regexPatterns['variables'],line):
            if makeLogFiles: appendToDRSFile('['+('' if not m.groups()[0] else m.groups()[0])+']')

        # if there's an expression starting, read those components separately
        elif m := re.match(regexPatterns['expression'],line):
            if makeLogFiles: appendToDRSFile(line)
            thisExpressionLocalLineIndex,expression = readExpression(drs,currentReadingIndex+1,regexPatterns,makeLogFiles)#[:-1]
            nestedExpressions.append(expression)

        # more components
        elif m := re.match(regexPatterns['object'],line): 
            if makeLogFiles: appendToDRSFile(line)
            mainExpression.append(Object(*m.groups()))
        elif m := re.match(regexPatterns['unaryPredicate'],line):
            if makeLogFiles: appendToDRSFile(line)
            mainExpression.append(Class(*m.groups()))        
        elif m := re.match(regexPatterns['binaryPredicate'],line):
            if makeLogFiles: appendToDRSFile(line)
            mainExpression.append(Role(*m.groups()))
        elif m := re.match(regexPatterns['property'],line):
            if makeLogFiles: appendToDRSFile(line)
            mainExpression.append(Property(*m.groups()))
        elif m := re.match(regexPatterns['relation'],line):
            if makeLogFiles: appendToDRSFile(line)
            mainExpression.append(Relation(*m.groups()))
        elif m := re.match(regexPatterns['preposition'],line):
            if makeLogFiles: appendToDRSFile(line)
            mainExpression.append(Preposition(*m.groups()))
        else:
            # there are things we can add, depending on the requirements
            # just need to define the behavior to fix this exception
            raise Exception("Undefined Interpretation for DRS Expression",line)
    
    print(nestedExpressions)
    
    facts = groundExpressions(predicates,objects,properties)

    implications = [x for y in [groundImplication(y,z,objects,properties) for (x,y,z) in filter(lambda x: x[0] == 'i',expressions)] for x in y]

    print("Reasoning...")
    prologfile = "interpreter/prolog.pl"
    reasonerFacts, groundRules = runProlog([str(fact) for fact in facts], [[str(imp.head),[str(b) for b in imp.body.body]] for imp in implications], prologfile,makeLogFiles)
    if not makeLogFiles: os.remove(prologfile)

    return set(facts), set([imp.toRule() for imp in implications]), set(groundRules), set(reasonerFacts)

class Interpreter:

    def __init__(self, memory):
        self.memory = memory

    def interpret_ace(self,ace):
        '''Interprets ACE text and adds the resulting knowledge to memory'''
        self.memory.add_instruction_knowledge(interpret_ace(ace))

if __name__ == "__main__":

    if os.path.isfile("interpreter/reasonerFacts.txt"): os.remove("interpreter/reasonerFacts.txt")
    if os.path.isfile("interpreter/groundRules.txt"): os.remove("interpreter/groundRules.txt")
    if os.path.isfile("interpreter/DRS.txt"): os.remove("interpreter/DRS.txt")
    if os.path.isfile("interpreter/prolog.pl"): os.remove("interpreter/prolog.pl")

    ontology = Ontology(stopOldServer=True).load(os.getcwd()+'/ontology/uagent.owl')

    ontology.add_instruction_knowledge(interpret_ace(open("interpreter/ace.txt","r").read(),makeLogFiles=True))