import os
import re
import subprocess
from operator import attrgetter

class Class:
    '''Corresponds to both a Descrioption logic Class and a prolog predicate arity /1'''
    def __init__(self,letter,name,inst):
        self.letter = letter
        self.name = self.name(name)
        self.inst = self.term(inst)
        
    def term(self,term):
        if m:= re.match("string\((.*)\)",term):
            return "'" + m.groups()[0] + "'"
        if m:= re.match("named\((.*)\)",term): 
            return m.groups()[0]
        return term 
    
    def name(self,name):
        return name
        
    def __str__(self):
        return self.name + "(" + self.inst + ")"
    
    def __repr__(self):
        return self.name + "(" + self.inst + ")"    

class Role:
    '''Corresponds to both a Descrioption logic Role and a prolog predicate arity /2'''
    def __init__(self,letter,name,subj,obj):
        self.letter = letter
        self.name = self.name(name)
        self.subj = self.term(subj)
        self.obj = self.term(obj)
        
    def term(self,term):
        if m:= re.match("string\((.*)\)",term):
            return "'" + m.groups()[0] + "'"
        if m:= re.match("named\((.*)\)",term): 
            return m.groups()[0]
        return term 
    
    def name(self,name):
        return name
        
    def __str__(self):
        return self.name + "(" + self.subj + "," + self.obj + ")"
    
    def __repr__(self):
        return self.name + "(" + self.subj + "," + self.obj + ")"

class Predicate:
    '''Corresponds to a prolog predicate arity > 2'''
    
    def __init__(self,letter,name,*terms):
        self.letter = letter
        self.name = self.name(name)
        self.terms = [self.term(x) for x in terms]
        
    def term(self,term):
        if m:= re.match("string\((.*)\)",term):
            return "'" + m.groups()[0] + "'"
        if m:= re.match("named\((.*)\)",term): 
            return m.groups()[0]
        return term 
    
    def name(self,name):
        return name
        
    def __str__(self):
        return self.name + "(" + ",".join(self.terms) + ")"
    
    def __repr__(self):
        return self.name + "(" + ",".join(self.terms) + ")"  
    
class Object:
    '''DRS object'''
    def __init__(self,indent,letter,name,quant,stuff1,stuff2,stuff3):
        self.letter = letter
        self.name = name
        self.quant = quant
        
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name

class ObjectList:
    '''List of DRS objects'''
    
    def __init__(self):
        self.objs = []
        self.var = {}
        
    def reset(self):
        self.objs = []
        self.var = {}
        
    def append(self,obj):
        o = Object(*obj)
        self.objs.append(o)
                       
        if o.letter not in self.var: 
            self.var[o.letter] = o.name
    
    def incName(self,name):
        split = [i for i in re.split(r'([A-Za-z]+)', name) if i]
        if len(split) == 1:
            return name + str(1)
        return ''.join(split[:-1]) + str(int(split[-1])+1)
        
    def remove(self,obj):
        self.objs.remove(obj)
        del self.var[obj.letter]
        for obj in self.objs:
            if obj.letter not in self.var:
                self.var[obj.letter] = obj.name
    
    def __str__(self):        
        return "[" + ",".join([str(x) for x in self.objs]) + "]"
    
    def __repr__(self):
        return "[" + ",".join([str(x) for x in self.objs]) + "]"
    
class Property:
    '''DRS property.'''
    def __init__(self,indent,letter,name,type):
        self.letter = letter
        self.name = name
        self.type = type
        
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name   

class PropertyList:
    '''List of DRS properties'''
    
    def __init__(self):
        self.props = []
        self.var = {}
        
    def append(self,prop):
        p = Property(*prop)
        self.props.append(p)
        if not p.letter in self.var: self.var[p.letter] = p.name
        
    
    def __str__(self):        
        return "[" + ",".join([str(x) for x in self.props]) + "]"
    
    def __repr__(self):
        return "[" + ",".join([str(x) for x in self.props]) + "]"        

class Relation:
    '''DRS relation'''
    def __init__(self,indent,letter,name,to):
        self.letter = letter
        self.name = name
        self.to = to
        
    def __str__(self):
        return self.name + "(" + self.to + ")"
    
    def __repr__(self):
        return self.name + "(" + self.to + ")"
    
class Body:
    '''Body of a prolog rule. append and remove maintain a list of terms for verification.'''
    def __init__(self):
        self.body = []
        self.var = set()
        
    def append(self,pred):
        if not (isinstance(pred,Class) or isinstance(pred,Role) or isinstance(pred,Predicate)): raise
        self.body.append(pred)
        if isinstance(pred,Class) and not pred.inst in self.var: self.var.add(pred.inst)
        if isinstance(pred,Role) and not pred.subj in self.var: self.var.add(pred.subj)
        if isinstance(pred,Role) and not pred.obj in self.var: self.var.add(pred.obj)
    
    def remove(self,pred):
        oldVars = set()
        if isinstance(pred,Class): oldVars.add(pred.inst)
        if isinstance(pred,Role): oldVars.add(pred.subj) ; oldVars.add(pred.obj)
        self.body.remove(pred)
        for pred in self.body:
            if isinstance(pred,Class) and pred.inst in oldVars:
                oldVars.remove(pred.inst)
                if len(oldVars) == 0: return
            if isinstance(pred,Role) and pred.subj in oldVars:
                oldVars.remove(pred.subj)
                if len(oldVars) == 0: return                
            elif isinstance(pred,Role) and pred.obj in oldVars:
                oldVars.remove(pred.obj)
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

def runProlog(facts, prolog, prologfile,makeFiles):
    '''runs the prolog file and reads and discards its output files
    returns the lines from the files it discards'''
    
    factFile = "interpreter/reasonerFacts.txt"
    groundFile = "interpreter/groundRules.txt"

    writePrologFile(facts, prolog, prologfile, factFile, groundFile)

    subprocess.call(['swipl', prologfile])

    reasonerFacts = open(factFile, "r").read().splitlines()
    groundRules = open(groundFile, "r").read().splitlines()

    if not makeFiles: os.remove(factFile)
    if not makeFiles: os.remove(groundFile)

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
    variablesPattern = re.compile("\s*<drspp>\s*\[([A-Z][0-9]*(?:,[A-Z][0-9]*)*)?\]\s*")
    objectPattern = re.compile("()object\(([A-Z][0-9]*),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    unaryPredicatePattern = re.compile("()predicate\(([A-Z][0-9]*),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    binaryPredicatePattern = re.compile("()predicate\(([A-Z][0-9]*),([^,]+),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    propertyPattern = re.compile("()property\(([A-Z][0-9]*),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    expressionPattern = re.compile("^(\s+)[^\s]+.*")   
    doneReadingPattern = re.compile("^\s*</drspp>.*")
    prepositionPattern = re.compile("^()modifier_pp\(([A-Z][0-9]*),([^,]+),([A-Z][0-9]*)\)\s*")
    relationPattern = re.compile("^()relation\(([A-Z][0-9]*),([^,]+),([A-Z][0-9]*)\)\s*")
    
    # expressions have the same stuff as the facts, they are just indented (\s+)
    expressionVariablesPattern = re.compile("(\s+)\[([A-Z][0-9]*(?:,[A-Z][0-9]*)*)?\]\s*")
    implicationSignPattern = re.compile("(\s+)(=&gt;)\s*")
    disjunctionSignPattern = re.compile("(\s+v)\s*")
    expressionObjectPattern = re.compile("(\s+)object\(([A-Z][0-9]*),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    expressionUnaryPredicatePattern = re.compile("(\s+)predicate\(([A-Z][0-9]*),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    expressionBinaryPredicatePattern = re.compile("(\s+)predicate\(([A-Z][0-9]*),([^,]+),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    expressionPropertyPattern = re.compile("(\s+)property\(([A-Z][0-9]*),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    expressionPrepositionPattern = re.compile("^(\s+)modifier_pp\(([A-Z][0-9]*),([^,]+),([A-Z][0-9]*)\)\s*")
    expressionRelationPattern = re.compile("^(\s+)relation\(([A-Z][0-9]*),([^,]+),([A-Z][0-9]*)\)\s*")
    
    return {'xmlBeforeDRS':xmlBeforeDRSPattern,'variables':variablesPattern,'object':objectPattern,'unaryPredicate':unaryPredicatePattern,
            'binaryPredicate':binaryPredicatePattern,'property':propertyPattern,'expression':expressionPattern,'doneReading':doneReadingPattern,
            'preposition':prepositionPattern,'expressionVariables':expressionVariablesPattern,'implicationSign':implicationSignPattern,
            'disjunctionSign':disjunctionSignPattern,'expressionObject':expressionObjectPattern,'expressionUnaryPredicate':expressionUnaryPredicatePattern,
            'expressionBinaryPredicate':expressionBinaryPredicatePattern,'expressionProperty':expressionPropertyPattern,'expressionPreposition':expressionPrepositionPattern,
            'relation':relationPattern,'expressionRelation':expressionRelationPattern}
def appendToDRSFile(drsline):
    '''Self explanatory'''    
    open("interpreter/DRS.txt","a").write(drsline + '\n')

def groundExpressions(predicates,objects,properties,fact=True):
    '''performs a "grounding" on DRS objects so that the proper terms
    are uniformly substituted in accordance with the semantics to
    obtain Classes and Roles for use in a logic or rules-based program'''
    
    sameThings = []
    
    # ground all the predicates from DRS
    for i in range(len(predicates)):
        if isinstance(predicates[i],Predicate): 
            newTerms = []
            for term in predicates[i].terms:
                if fact and term in objects.var and term in objects.var.values():
                    newTerms.append(term)
                elif fact and term in objects.var:
                    newTerms.append(objects.var[term])
                elif term in properties.var:
                    newTerms.append(properties.var[term])
                else:
                    newTerms.append(term)
            predicates[i].terms = newTerms
            continue
        if isinstance(predicates[i],Role):
            predicates[i] = groundDRSPredicate(predicates[i],objects if fact else ObjectList(),properties)
        if predicates[i].name == 'equal': sameThings.append(predicates[i])
        elif predicates[i].name == 'be':
            objects.var[predicates[i].subj] = objects.var[predicates[i].obj]
            del objects.var[predicates[i].obj]
            predicates[i] = Class(predicates[i].letter,objects.var[predicates[i].subj],predicates[i].subj)
    
    # figure out all the class and instance names
    if fact: 
        cs = list(filter(lambda x: isinstance(x,Class),predicates))
        classes = set([y.name for y in cs] + [y.inst for y in cs])    
    
    # add predicates for anything that is a name for something else
    sameNames = []
    for same in sameThings:
        
        # if it is an ininstantiated class, make this an instance of that class (since there won't be one)
        if same.subj in objects.var.values() and same.subj not in classes:
            predicates.append(Class(same.letter,same.obj,same.subj))
            classes.add(same.subj)
        elif same.obj in objects.var.values() and same.obj not in classes: 
            predicates.append(Class(same.letter,same.obj,same.subj))
            classes.add(same.obj)
        
        # make the same facts about the thing as its equal
        for pred in predicates:            
            if pred.name == 'equal': continue
            if isinstance(pred,Class):
                if pred.inst == same.obj and pred.inst != same.subj:
                    classes.add(pred.inst)
                    sameNames.append(Class(pred.letter,pred.name,same.subj))
                elif pred.inst == same.subj and pred.inst != same.obj and not (pred.inst in objects.var and same.obj in objects.var and objects.var[same.obj] in objects.var):
                    classes.add(pred.inst)
                    sameNames.append(Class(pred.letter,pred.name,same.obj))
            elif isinstance(pred,Role): 
                if pred.obj == same.obj and pred.obj != same.subj:
                    sameNames.append(Role(pred.letter,pred.name,pred.subj,same.subj))
                elif pred.obj == same.subj and pred.obj != same.obj:
                    sameNames.append(Role(pred.letter,pred.name,pred.subj,same.obj))    
                if pred.subj == same.obj and pred.subj != same.subj:
                    sameNames.append(Role(pred.letter,pred.name,same.subj,pred.obj))
                elif pred.subj == same.subj and pred.subj != same.obj:
                    sameNames.append(Role(pred.letter,pred.name,same.obj,pred.obj))
                 
    if fact:
        # add facts for objects that have no named instance
        for obj in objects.objs:
            if obj.name in classes: continue
            else: 
                if objects.var[obj.letter] in objects.var:
                    predicates.append(Class(obj.letter,objects.var[objects.var[obj.letter]],objects.var[obj.letter]))
                else:
                    predicates.append(Class(obj.letter,obj.name,obj.name))
                if obj.letter in properties.var:
                    predicates.append(Role(obj.letter,"hasProperty",obj.name,properties.var[obj.letter]))
            classes.add(obj.name)
    else:
        # add variable Classes for objects that have no named instance, renaming if a global instance
        for obj in objects.objs:
            if obj.letter in objects.var:
                predicates.append(Class(obj.letter,objects.var[obj.name] if obj.name in objects.var else obj.name,obj.letter)) 
    
    predicates = predicates + sameNames
    
    return predicates

def groundDRSPredicate(pred,objects,properties):
    '''"Grounds" one DRS predicate'''
    
    subjectVar = re.match("^([A-Z][0-9]*)$",pred.subj)
    objectVar  = re.match("^([A-Z][0-9]*)$",pred.obj)
    
    subjectVar = None if not subjectVar else subjectVar.groups()[0]    
    objectVar = None if not objectVar else objectVar.groups()[0]
    
    # both terms are variables
    if subjectVar and objectVar:
        for var in objects.var:
            
            if var == subjectVar:
                pred.subj = objects.var[var]
                subjectVar = None
            elif var == objectVar:
                pred.obj = objects.var[var]
                objectVar = None
                
            if pred.name == 'be' and objectVar == None and len(objects.var) == 1:
                objects.var[pred.subj] = pred.obj
                if var in objects.var:
                    del objects.var[var]
                return Class(pred.letter,pred.obj,pred.subj) 
            elif pred.name == 'be' and subjectVar == None and len(objects.var) == 1:
                objects.var[pred.obj] = pred.subj
                if var in objects.var:
                    del objects.var[var]
                return Class(pred.letter,pred.obj,pred.subj)      
            elif subjectVar == None and objectVar == None and pred.name == 'be':
                if objects.var[var] in objects.var:
                    return Class(pred.letter,objects.var[objects.var[var]],checkDictsForKey(var,objects.var))
                elif pred.obj in objects.var:
                    return Class(pred.letter,objects.var[objects.var[var]],objects.var[var])                
                elif objects.var[var] == pred.subj:
                    objects.var[var] = pred.obj
                else:
                    objects.var[var] = pred.subj
                objects.var[pred.subj] = pred.obj
                return Class(pred.letter,pred.obj,pred.subj)
            elif subjectVar == None and objectVar == None:
                return pred
                     
        for var in properties.var:
            if var == objectVar:
                return Role(pred.letter,"hasProperty",pred.subj,properties.var[var])
        
        return pred
    # object is a variable
    elif objectVar:   
        for var in objects.var:
            if var == objectVar and pred.name == 'be' and re.match("^\'.*\'$",pred.subj):                
                return Role(pred.letter,"equal",objects.var[pred.obj],pred.subj)            
            elif var == objectVar and pred.name == 'be':
                objects.var[pred.subj] = objects.var[var]
                objects.var[var] = pred.subj
                #print(Class(pred.letter,objects.var[pred.subj],objects.var[var]))
                return Class(pred.letter,objects.var[pred.subj],objects.var[var])                          
            elif var == objectVar:
                return Role(pred.letter,pred.name,pred.subj,objects.var[var])                  
        for var in properties.var:
            if var == objectVar:
                return Role(pred.letter,"hasProperty",pred.subj,properties.var[var])
        if pred.name == 'be' and re.match("^\'.*\'$",pred.subj):
            return Role(pred.letter,"equal",pred.subj,pred.obj) 
        else:
            return pred
    # subject is a variable
    elif subjectVar:        
        for var in objects.var:
            if var == subjectVar and pred.name == 'be' and re.match("^\'.*\'$",pred.obj):
                return Role(pred.letter,"equal",objects.var[pred.subj],pred.obj)             
            elif var == subjectVar and pred.name == 'be':
                objects.var[pred.subj] = objects.var[var]
                objects.var[var] = pred.subj
                return Class(pred.letter,objects.var[pred.subj],objects.var[var])                          
            elif var == objectVar:
                return Role(pred.letter,pred.name,pred.subj,objects.var[var])  
        for var in properties.var:
            if var == objectVar:
                return Role(pred.letter,"hasProperty",pred.subj,properties.var[var])   
        if pred.name == 'be' and re.match("^\'.*\'$",pred.obj):
            return Role(pred.letter,"equal",pred.subj,pred.obj) 
        else:
            return pred
    
    # shouldn't ground a fact
    raise Exception("Undefined Semantics",pred)

def addGlobalValuesToPredicateList(l,globalObjects,globalProperties):
    '''Extend local variables in implications with the global variables from the DRS'''
    
    # properties are global
    l[2].var.update(globalProperties.var)
        
    gloInst = [(k,globalObjects.var[k]) for k in filter(lambda x: not re.match("[A-Z][0-9]*",x),globalObjects.var)]
    loc = [(k,l[1].var[k]) for k in l[1].var]
        
     # objects are local (named instances may require renaming, so the names are added)
    for k in gloInst + loc:
        l[1].var[k[0]] = k[1]
    
    return l

def removeDuplicates(body):
    '''Self explanatory'''
    
    noDups = []
    for atom in body.body:
        unique = True
        for atom2 in noDups:
            if str(atom) == str(atom2): unique = False ; break
        if unique: noDups.append(atom)
    body.body = noDups
    return body

def groundImplication(body,head,globalObjects,globalProperties):
    '''performs a "grounding" on each DRS object in an implication'''
    
    newImps = [] 
    
    # ground the head and body
    if head[0] == "i":
        head = groundImplication(head[1],head[2],globalObjects,globalProperties)
    else:
        head = set(groundExpressions(*addGlobalValuesToPredicateList(head,globalObjects,globalProperties),False))
    
    newBody = Body()    
    if body[0] == "i":
        imps = groundImplication(body[1],body[2],globalObjects,globalProperties)
        for imp in imps:
            newBody.append(imp.head)
            for pred in imp.body.body:
                newBody.append(pred)
    else:
        for pred in set(groundExpressions(*addGlobalValuesToPredicateList(body,globalObjects,globalProperties),False)):
            newBody.append(pred)                     
        
    # if a Class or Role in the head has a variable that isn't in the body, it should be moved to the body (language quirk)
    for pred in set(filter(lambda x: isinstance(x,Class),head)):
        if re.match("[A-Z][0-9]*",pred.inst) and pred.inst not in newBody.var:
            newBody.append(pred)
            head.remove(pred)
    for pred in set(filter(lambda x: isinstance(x,Role),head)):
        if re.match("[A-Z][0-9]*",pred.subj) and pred.subj not in newBody.var and pred.subj in globalObjects.var:
            newBody.append(Class(pred.subj,checkDictsForKey(pred.subj,globalObjects.var),pred.subj))
        if (re.match("[A-Z][0-9]*",pred.obj) and pred.obj not in newBody.var):
            newBody.append(Class(pred.obj,checkDictsForKey(pred.obj,globalObjects.var),pred.obj))
    
    # if a Class or Role in the body has a variable that is a DRS global variable, make a class with that variable in the body
    for pred in set(filter(lambda x: isinstance(x,Class),newBody.body)):
        if pred.inst in globalObjects.var:
            newBody.append(Class(pred.inst,checkDictsForKey(pred.inst,globalObjects.var),pred.inst))
    for pred in set(filter(lambda x: isinstance(x,Role),newBody.body)):
        if pred.subj in globalObjects.var:
            newBody.append(Class(pred.subj,checkDictsForKey(pred.subj,globalObjects.var),pred.subj))
        if pred.obj in globalObjects.var:
            newBody.append(Class(pred.obj,checkDictsForKey(pred.obj,globalObjects.var),pred.obj))
    
    # make an implication from each head with the same body
    for atom in head:
        newImps.append(Implication(removeDuplicates(newBody),atom))
    
    return newImps

def readExpression(space,drs,i,regexPatterns,makeFiles):
    
    objects = ObjectList()    
    properties = PropertyList()    
    predicates = []
    relations = []
    
    t = ''
    
    antecedent = None
    notTwice = True
    
    k = 0
    
    for j in range(i,len(drs)): 
        line = drs[max(k,j)]
        if k >= j: k += 1
        if re.match(regexPatterns['doneReading'],line) or re.match(regexPatterns['object'],line) or re.match(regexPatterns['unaryPredicate'],line) or re.match(regexPatterns['binaryPredicate'],line) or re.match(regexPatterns['property'],line) or re.match(regexPatterns['preposition'],line) or re.match(regexPatterns['relation'],line):
            return j,t,[t,antecedent,(predicates,objects,properties)]
        if m := re.match(regexPatterns['expressionVariables'],line):
            if len(m.groups()[0]) > space:
                k,t,ex = readExpression(len(m.groups()[0]),drs,j+1,regexPatterns,makeFiles)               
                if antecedent:
                    return k,t,[t,antecedent,ex]
                else:
                    antecedent = ex
            elif antecedent and notTwice:
                if makeFiles: appendToDRSFile(line)
                notTwice = False
            elif antecedent:
                return j,t,[t,antecedent,(collapseRelationsIntoPredicates(predicates,relations,objects),objects,properties)]            
        elif m := re.match(regexPatterns['implicationSign'],line):
            if makeFiles: appendToDRSFile(m.groups()[0]+'=>')
            t = 'i'
            if not antecedent:
                antecedent = (collapseRelationsIntoPredicates(predicates,relations,objects),objects,properties)
                objects = ObjectList()    
                properties = PropertyList()    
                predicates = []
                relations = []
        elif m:= re.match(regexPatterns['disjunctionSign'],line):
            if makeFiles: appendToDRSFile(m.groups()[0])
            t = 'd'
            antecedent = (collapseRelationsIntoPredicates(predicates,relations,objects),objects,properties)
            objects = ObjectList()    
            properties = PropertyList()    
            predicates = [] 
            relations = []
        elif m := re.match(regexPatterns['expressionObject'],line): 
            if makeFiles: appendToDRSFile(line)
            objects.append(m.groups()[:-2])
        elif m:= re.match(regexPatterns['expressionUnaryPredicate'],line): 
            if makeFiles: appendToDRSFile(line)
            predicates.append(Class(*m.groups()[1:-2]))        
        elif m:= re.match(regexPatterns['expressionBinaryPredicate'],line): 
            if makeFiles: appendToDRSFile(line)
            predicates.append(Role(*m.groups()[1:-2]))
        elif m := re.match(regexPatterns['expressionProperty'],line): 
            if makeFiles: appendToDRSFile(line)
            properties.append(m.groups()[:-2])
        elif m := re.match(regexPatterns['expressionRelation'],line):
            for ob in objects.objs:
                if ob.letter == m.groups()[1]:
                    predicates.append(Role(m.groups()[1],ob.name+m.groups()[2].capitalize(),m.groups()[1],m.groups()[3]))
        elif m := re.match(regexPatterns['expressionPreposition'],line):
            for pred in predicates:
                if isinstance(pred,Class) and pred.letter == m.groups()[1]:
                    if pred.name == 'be': pred.name = 'is'
                    predicates.remove(pred)
                    predicates.append(Role(pred.letter,pred.name+m.groups()[2][0].capitalize()+m.groups()[2][1:],pred.inst,m.groups()[3]))
                    break
                elif isinstance(pred,Role) and pred.letter == m.groups()[1]:                    
                    if pred.obj in properties.var:
                        newName = ('is' if pred.name == 'be' else pred.name)+properties.var[pred.obj][0].capitalize()+ properties.var[pred.obj][1:]+m.groups()[2][0].capitalize()+m.groups()[2][1:]
                        predicates.append(Role(pred.letter,newName,pred.subj,m.groups()[3]))
                    else:
                        newName = ('is' if pred.name == 'be' else pred.name)+m.groups()[2][0].capitalize()+m.groups()[2][1:]
                        predicates.append(Predicate(pred.letter,newName,pred.subj,pred.obj,m.groups()[3]))
                        predicates.remove(pred)
                    break       
        else:
            # there are things we can add, depending on the requirements
            # just need to define the behavior to fix this exception
            raise Exception("Undefined Interpretation for DRS Expression",line)        

def splitter(data, pred):
    yes, no = [], []
    for d in data:
        (yes if pred(d,data) else no).append(d)
    return [yes] if 0 == len(no) else [yes] + splitter(no,pred)

def collapseRelationsIntoPredicates(predicates,relations,objects): 
    
    relations = sorted(relations, key=attrgetter('name','to'))
    
    relations = splitter(relations,(lambda x,y: x.name == y[0].name))
    
    newPreds = [] 
    
    for relType in relations:
        for rel in relType:
            for pred in predicates:
                if isinstance(pred,Class) and pred.inst == rel.letter:
                    raise Exception("Undefined Interpretation for DRS Expression",line)
                elif isinstance(pred,Role):
                    if pred.subj == rel.letter:
                        if pred.name == 'be': pred.name = 'is'
                        predicates.remove(pred)
                        newPreds.append(Role(pred.letter,pred.name+rel.name[0].capitalize()+rel.name[1:],rel.to,pred.obj))             
                    if pred.obj == rel.letter:
                        if pred.name == 'be': pred.name = 'is'
                        predicates.remove(pred)
                        newPreds.append(Role(pred.letter,pred.name+rel.name[0].capitalize()+rel.name[1:],pred.subj,rel.to))
                        
    return predicates + newPreds
    
def interpret_ace(ace,makeFiles = False):
    '''interpret the ACE to obtain facts,rules,as well as new reasoner facts and rules'''
    
    drs = getDRSFromACE(ace)   
    if makeFiles and os.path.isfile("interpreter/DRS.txt"): os.remove("interpreter/DRS.txt")
    
    initEmpties()
    
    expressions = []
    predicates = []
    objects = ObjectList()    
    properties = PropertyList()
    relations = []
    
    # TODO - fix relation, do adverbs, more connectives
    regexPatterns = compileRegexes()
    #print("\n".join(drs))
    j = 0
    for i in range(len(drs)):        
        line = drs[max(i,j)]
        if j >= i: j += 1
        if re.match(regexPatterns['doneReading'],line): 
            break
        elif m := re.match(regexPatterns['xmlBeforeDRS'],line): 
            continue
        elif m := re.match(regexPatterns['variables'],line):
            if makeFiles: appendToDRSFile('['+('' if not m.groups()[0] else m.groups()[0])+']')
        elif m := re.match(regexPatterns['object'],line): 
            if makeFiles: appendToDRSFile(line)
            objects.append(m.groups()[:-2])
        elif m := re.match(regexPatterns['unaryPredicate'],line): 
            if makeFiles: appendToDRSFile(line)
            predicates.append(Class(*m.groups()[1:-2]))        
        elif m := re.match(regexPatterns['binaryPredicate'],line): 
            if makeFiles: appendToDRSFile(line)
            predicates.append(Role(*m.groups()[1:-2]))
        elif m := re.match(regexPatterns['property'],line): 
            if makeFiles: appendToDRSFile(line)
            properties.append(m.groups()[:-2])
        elif m := re.match(regexPatterns['expression'],line):
            j,t,ex = readExpression(len(m.groups()[0]),drs,max(i,j),regexPatterns,makeFiles)
            expressions.append(ex)
        elif m := re.match(regexPatterns['relation'],line):
            for ob in objects.objs:
                if ob.letter == m.groups()[1]:
                    predicates.append(Role(m.groups()[1],ob.name+m.groups()[2].capitalize(),m.groups()[1],m.groups()[3]))
        elif m := re.match(regexPatterns['preposition'],line):
            for pred in predicates:
                if isinstance(pred,Class) and pred.letter == m.groups()[1]:
                    if pred.name == 'be': pred.name = 'is'
                    predicates.remove(pred)
                    predicates.append(Role(pred.letter,pred.name+m.groups()[2][0].capitalize()+m.groups()[2][1:],pred.inst,m.groups()[3]))
                    break
                elif isinstance(pred,Role) and pred.letter == m.groups()[1]:                    
                    if pred.obj in properties.var:
                        newName = ('is' if pred.name == 'be' else pred.name)+properties.var[pred.obj][0].capitalize()+ properties.var[pred.obj][1:]+m.groups()[2][0].capitalize()+m.groups()[2][1:]
                        predicates.append(Role(pred.letter,newName,pred.subj,m.groups()[3]))
                    else:
                        newName = ('is' if pred.name == 'be' else pred.name)+m.groups()[2][0].capitalize()+m.groups()[2][1:]
                        predicates.append(Predicate(pred.letter,newName,pred.subj,pred.obj,m.groups()[3]))
                        predicates.remove(pred)
                    break
        else:
            # there are things we can add, depending on the requirements
            # just need to define the behavior to fix this exception
            raise Exception("Undefined Interpretation for DRS Expression",line)
    
    predicates = collapseRelationsIntoPredicates(predicates,relations,objects)
    
    facts = groundExpressions(predicates,objects,properties)
    
    implications = [x for y in [groundImplication(y,z,objects,properties) for (x,y,z) in filter(lambda x: x[0] == 'i',expressions)] for x in y]
    
    print("Reasoning...")
    prologfile = "interpreter/prolog.pl"
    reasonerFacts, groundRules = runProlog([str(fact) for fact in facts], [[str(imp.head),[str(b) for b in imp.body.body]] for imp in implications], prologfile,makeFiles)
    if not makeFiles: os.remove(prologfile)

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
    
    interpret_ace(open("interpreter/ace.txt","r").read(),True)