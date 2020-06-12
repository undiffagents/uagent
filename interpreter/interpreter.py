import os
import re
import subprocess


class Class:
    '''Corresponds to both a Descrioption logic Class and a prolog predicate arity /1'''
    def __init__(self,letter,name,inst):
        self.letter = letter
        self.name = self.name(name)
        self.inst = self.term(inst)
        
    def term(self,term):
        m = re.match("string\((.*)\)",term)
        if m: return "'" + m.groups()[0] + "'"
        m = re.match("named\((.*)\)",term)
        if m: return m.groups()[0]        
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
        m = re.match("string\((.*)\)",term)
        if m: return "'" + m.groups()[0] + "'"
        m = re.match("named\((.*)\)",term)
        if m: return m.groups()[0] 
        return term 
    
    def name(self,name):
        return name
        
    def __str__(self):
        return self.name + "(" + self.subj + "," + self.obj + ")"
    
    def __repr__(self):
        return self.name + "(" + self.subj + "," + self.obj + ")"
        
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
        if not o.letter in self.var: self.var[o.letter] = o.name
    
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

class Body:
    '''Body of a prolog rule. append and remove maintain a list of terms for verification.'''
    def __init__(self):
        self.body = []
        self.var = set()
        
    def append(self,pred):
        if not (isinstance(pred,Class) or isinstance(pred,Role)): raise
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

def appendToDRSFile(drsline):
    '''Self explanatory'''    
    open("interpreter/DRS.txt","a").write(drsline + '\n')

def groundExpressions(predicates,objects,properties,fact=True):
    '''performs a "grounding" on DRS objects so that the proper terms
    are uniformly substituted in accordance with the semantics to
    obtain Classes and Roles for use in a logic or rules-based program'''
    
    sameThings = []
    
    for i in range(len(predicates)):
        predicates[i] = groundPredicate(predicates[i],objects,properties)
        if predicates[i].name == 'sameThings': sameThings.append(predicates[i])    
        
    if fact: classes = set([y.name for y in list(filter(lambda x: isinstance(x,Class),predicates))])    
    
    sameNames = []
    for same in sameThings:
        for pred in predicates:
            if pred.name == 'sameThings': continue
            if isinstance(pred,Class):
                if pred.inst == same.obj and pred.inst != same.subj:
                    classes.add(pred.inst)
                    sameNames.append(Class(pred.letter,pred.name,same.subj))
                elif pred.inst == same.subj and pred.inst != same.obj:
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
        for obj in objects.objs:
            if obj.name in classes: continue
            else: 
                predicates.append(Class(obj.letter,obj.name,obj.name))
            classes.add(obj.name)
    else:
        for obj in objects.objs: 
            predicates.append(Class(obj.letter,obj.name,obj.letter)) 
    
    predicates = predicates + sameNames   
        
    return predicates

def groundPredicate(pred,objects,properties):
    '''"Grounds" one DRS predicate'''
    
    subjectVar = re.match("([A-Z][0-9]*)",pred.subj)
    objectVar  = re.match("([A-Z][0-9]*)",pred.obj)
    
    subjectVar = None if not subjectVar else subjectVar.groups()[0]    
    objectVar = None if not objectVar else objectVar.groups()[0]
    if subjectVar and objectVar:
        for var in objects.var:           
            if var == subjectVar:
                pred.subj = objects.var[var]
                subjectVar = None
            if var == objectVar:
                pred.obj = objects.var[var]
                objectVar = None
            if subjectVar == None and objectVar == None:
                if pred.name == 'be': return Class(pred.letter,pred.obj,pred.subj)
                else: return pred
        for var in properties.var:
            if var == objectVar:
                return Role(pred.letter,"hasProperty",pred.subj,properties.var[var])
        return pred
    elif objectVar:   
        for var in objects.var:
            if var == objectVar:
                objects.var[pred.subj] = objects.var[var]
                objects.var[var] = pred.subj
                return Class(pred.letter,objects.var[pred.subj],objects.var[var])
        for var in properties.var:
            if var == objectVar:
                return Role(pred.letter,"hasProperty",pred.subj,properties.var[var])
        return pred
    elif subjectVar: 
        for var in objects.var:
            if var == subjectVar:
                return Role(pred.letter,"sameThings",objects.var[pred.subj],pred.obj)
        for var in properties.var:
            if var == objectVar:
                return Role(pred.letter,"hasProperty",pred.subj,properties.var[var])   
    
    raise Exception("Undefined Semantics",pred)

def addGlobalValuesToPredicateList(l,globalObjects,globalProperties):
    '''Extend local variables in implications with the global variables from the DRS'''
    
    # properties are global
    l[2].var.update(globalProperties.var)
    # objects are local    
    keys = [k for k in l[1].var]
    for k in keys:
        if l[1].var[k] in globalObjects.var.values():
            l[1].var.pop(k)
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

def groundImplications(implications,globalObjects,globalProperties):
    '''performs a "grounding" on each DRS object in an implication'''
    
    newImps = []
    for head,body in implications:    
        head = set(groundExpressions(*addGlobalValuesToPredicateList(head,globalObjects,globalProperties),False))        
        newBody = Body()
        for pred in groundExpressions(*addGlobalValuesToPredicateList(body,globalObjects,globalProperties),False):
            newBody.append(pred)
        for pred in set(filter(lambda x: isinstance(x,Class),head)):
            if re.match("[A-Z][0-9]*",pred.inst) and pred.inst not in newBody.var:
                newBody.append(pred)
                head.remove(pred)
        for pred in set(filter(lambda x: isinstance(x,Role),head)):
            if re.match("[A-Z][0-9]*",pred.subj) and pred.subj not in newBody.var and pred.subj in globalObjects.var: 
                newBody.append(Class(pred.subj,globalObjects.var[globalObjects.var[pred.subj]] if globalObjects.var[pred.subj] in globalObjects.var else globalObjects.var[pred.subj],pred.subj))
            if (re.match("[A-Z][0-9]*",pred.obj) and pred.obj not in newBody.var): 
                newBody.append(Class(pred.obj,globalObjects.var[globalObjects.var[pred.obj]] if globalObjects.var[pred.obj] in globalObjects.var else globalObjects.var[pred.obj],pred.obj))
        for pred in set(filter(lambda x: isinstance(x,Class),newBody.body)):
            if pred.inst in globalObjects.var: newBody.append(Class(pred.inst,globalObjects.var[pred.inst],pred.inst))
        for pred in set(filter(lambda x: isinstance(x,Role),newBody.body)):
            if pred.subj in globalObjects.var:
                newBody.append(Class(pred.subj,globalObjects.var[globalObjects.var[pred.subj]] if globalObjects.var[pred.subj] in globalObjects.var else globalObjects.var[pred.subj],pred.subj))
            if pred.obj in globalObjects.var:
                newBody.append(Class(pred.obj,globalObjects.var[globalObjects.var[pred.obj]] if globalObjects.var[pred.obj] in globalObjects.var else globalObjects.var[pred.obj],pred.obj))
        for atom in head:
            newImps.append(Implication(removeDuplicates(newBody),atom))
    return newImps

def interpret_ace(ace,makeFiles = False):
    '''interpret the ACE to obtain facts,rules,as well as new reasoner facts and rules'''
    
    drs = getDRSFromACE(ace)   
    if makeFiles and os.path.isfile("interpreter/DRS.txt"): os.remove("interpreter/DRS.txt")
    
    predicates = []
    objects = ObjectList()    
    properties = PropertyList()
    impObjects = ObjectList()    
    impProperties = PropertyList()    
    impRoles = []
    implications = []
        
    head = []
    body = [] 
    twice = False
    
    # these match all possible DRS lines as defined by the current semantics
    xmlBeforeDRSPattern = re.compile("^\s*(?:<.*>)?$")
    variablesPattern = re.compile("\s*<drspp>\s*\[([A-Z][0-9]*(?:,[A-Z][0-9]*)*)\].*")
    objectPattern = re.compile("()object\(([A-Z][0-9]*),(.+),(.+),(.+),(.+),(.+)\)-(\d+)/(\d+)\s*")
    predicatePattern = re.compile("()predicate\(([A-Z][0-9]*),(.+),(.+),(.+)\)-(\d+)/(\d+)\s*")
    propertyPattern = re.compile("()property\(([A-Z][0-9]*),(.+),(.+)\)-(\d+)/(\d+)\s*") 
    doneReadingPattern = re.compile("^\s*</drspp>.*") 
    
    # implications have the same stuff, they are just indented (\s+)
    implicationVariablesPattern = re.compile("(\s+)\[([A-Z][0-9]*(?:,[A-Z][0-9]*)*)\].*")
    implicationSignPattern = re.compile("(\s+)(=&gt;)\s*")
    implicationObjectPattern = re.compile("(\s+)object\(([A-Z][0-9]*),(.+),(.+),(.+),(.+),(.+)\)-(\d+)/(\d+)\s*")
    implicationPredicatePattern = re.compile("(\s+)predicate\(([A-Z][0-9]*),(.+),(.+),(.+)\)-(\d+)/(\d+)\s*")
    implicationPropertyPattern = re.compile("(\s+)property\(([A-Z][0-9]*),(.+),(.+)\)-(\d+)/(\d+)\s*")     
    
    for line in drs:
        
        if re.match(doneReadingPattern,line):
            break
        if re.match(xmlBeforeDRSPattern,line):
            continue       
        m = re.match(variablesPattern,line)
        if m:
            if makeFiles: appendToDRSFile('['+m.groups()[0]+']')
            continue
        if re.match(implicationVariablesPattern,line):
            if makeFiles: appendToDRSFile(line)
            if len(body) == 0: continue
            elif twice:
                implications.append(((impRoles,impObjects,impProperties),body))
                impObjects = ObjectList()    
                impProperties = PropertyList()    
                impRoles = []                
                body = []
                twice = False
            else: twice = True 
            continue
        m = re.match(implicationSignPattern,line)
        if re.match(implicationSignPattern,line):
            if makeFiles: appendToDRSFile(m.groups()[0]+'=>')
            body = (impRoles,impObjects,impProperties)
            impObjects = ObjectList()    
            impProperties = PropertyList()    
            impRoles = []
            continue
        ma = re.match(objectPattern,line)
        if ma: 
            if makeFiles: appendToDRSFile(line)
            objects.append(ma.groups()[:-2])
            continue
        ma = re.match(predicatePattern,line)
        if ma: 
            if makeFiles: appendToDRSFile(line)
            predicates.append(Role(*ma.groups()[1:-2]))
            continue
        ma = re.match(propertyPattern,line)
        if ma: 
            if makeFiles: appendToDRSFile(line)
            properties.append(ma.groups()[:-2])
            continue
        ma = re.match(implicationObjectPattern,line)
        if ma: 
            if makeFiles: appendToDRSFile(line)
            impObjects.append(ma.groups()[:-2])
            continue
        ma = re.match(implicationPredicatePattern,line)
        if ma: 
            if makeFiles: appendToDRSFile(line)
            impRoles.append(Role(*ma.groups()[1:-2]))
            continue
        ma = re.match(implicationPropertyPattern,line)
        if ma: 
            if makeFiles: appendToDRSFile(line)
            impProperties.append(ma.groups()[:-2])
            continue
        raise Exception("Undefined DRS Expression",line)
    
    if len(body) != 0: implications.append([(impRoles,impObjects,impProperties),body])
    
    facts = groundExpressions(predicates,objects,properties)
    
    implications = groundImplications(implications,objects,properties)    
    
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
    interpret_ace(open("interpreter/ace.txt","r").read(),True)