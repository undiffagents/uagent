import os
import re
import subprocess

class Class:
    
    def __init__(self,letter,name,inst):
        self.letter = letter
        self.name = self.name(name)
        self.inst = self.term(inst)
        
    def term(self,term):
        m = re.match("named\((.*)\)",term)
        if m:
            return m.groups()[0]
        return term 
    
    def name(self,name):
        return name
        
    def __str__(self):
        return self.name + "(" + self.inst + ")"
    
    def __repr__(self):
        return self.name + "(" + self.inst + ")"    

class Role:
    
    def __init__(self,letter,name,subj,obj):
        self.letter = letter
        self.name = self.name(name)
        self.subj = self.term(subj)
        self.obj = self.term(obj)
        
    def term(self,term):
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
    
    def __init__(self,letter,name,quant,stuff1,stuff2,stuff3):
        self.letter = letter
        self.name = name
        self.quant = quant
        
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name

class ObjectList:
    
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
    
    def __init__(self,letter,name,type):
        self.letter = letter
        self.name = name
        self.type = type
        
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name   

class PropertyList:
    
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
    program = sorted(prolog+facts, key=lambda x: x[0])
    open(prologfile, "w").write('{}\n:- open("{}",write, Stream),open("{}",write, Stream2),\n{}close(Stream),close(Stream2),halt.\n'.format(''.join(['{}.\n'.format('{} :- {}'.format(thing[0], ",".join(thing[1])) if isinstance(thing, list) else thing) for thing in program]), factFile, groundFile, ''.join(['forall(({}),({})),\n'.format(thing[0]+","+",".join(thing[1]), '{}write(Stream2," => "),write(Stream2,{}),write(Stream2,"\\n"),write(Stream,{}),write(Stream,"\\n")'.format(''.join(['write(Stream2,{}),{}'.format(stuff, 'write(Stream2,","),' if not stuff == thing[1][-1] else "") for stuff in thing[1]]), thing[0], thing[0])) for thing in prolog])))

def runProlog(facts, prolog, prologfile):

    factFile = "interpreter/reasonerFacts.txt"
    groundFile = "interpreter/groundRules.txt"

    writePrologFile(facts, prolog, prologfile, factFile, groundFile)

    subprocess.call(['swipl', prologfile])

    reasonerFacts = open(factFile, "r").read().splitlines()
    groundRules = open(groundFile, "r").read().splitlines()

    #os.remove(factFile)
    #os.remove(groundFile)

    return reasonerFacts, groundRules

def strip_xml(xml_string):
    drsLines = []
    drs = False
    for line in xml_string.splitlines():
        if "</drspp>" in line:
            break
        elif "<drspp>" in line:
            line = line.split(">")[1]
            drs = True
        if drs: drsLines.append(line.replace("&gt;", ">"))
    return drsLines

def getDRSFromACE(ace):
    print("Interpreting ACE...")
    
    process = subprocess.Popen(['lib/ape/ape.exe', '-cdrspp'],stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    process.stdin.write(ace.encode('utf-8'))
    drs = strip_xml(process.communicate()[0].decode('utf-8'))
    process.stdin.close()  # possibly unnecessary when function returns? not great at subprocess
    
    return drs

def makeDRSFile(drs):
    open("interpreter/DRS.txt","w").write("\n".join(drs))

def groundExpressions(predicates,objects,properties,fact=True):
    for i in range(len(predicates)):
        predicates[i] = groundPred(predicates[i],objects,properties)
    if fact:
        classes = set([y.name for y in list(filter(lambda x: isinstance(x,Class),predicates))])
        for obj in objects.objs:
            if obj.name in classes: continue
            else: 
                predicates.append(Class(obj.letter,obj.name,obj.name))
            classes.add(obj.name)
    else:
        for obj in objects.objs: 
            predicates.append(Class(obj.letter,obj.name,obj.letter)) 
            
    return predicates

def groundPred(pred,objects,properties):
    m = re.match("([A-Z]+[0-9]*)",pred.subj)
    m = None if not m else m.groups()[0]
    n  = re.match("([A-Z]+[0-9]*)",pred.obj)
    n = None if not n else n.groups()[0]
    if m and n:        
        for var in objects.var:           
            if var == m:
                if objects.var[var] in objects.var and objects.var[objects.var[var]] not in objects.var:
                    pred.subj = objects.var[objects.var[var]]
                else:
                    pred.subj = objects.var[var]
                m = None
            if var == n:
                if objects.var[var] in objects.var and objects.var[objects.var[var]] not in objects.var:
                    pred.obj = objects.var[objects.var[var]]
                else:
                    pred.obj = objects.var[var]
                n = None
            if m == None and n == None: return pred
        for var in properties.var:
            if var == n:
                pred = Role(pred.letter,"hasProperty",pred.subj,properties.var[var])
    elif n:
        for var in objects.var:
            if var == n:
                newName = objects.var[var] if objects.var[var] not in objects.var else objects.var[objects.var[var]]
                objects.var[newName] = pred.subj
                return Class(pred.letter,newName,pred.subj)
        for var in properties.var:
            if var == n:
                return Role(pred.letter,"hasProperty",pred.subj,properties.var[var])
    elif m: raise
    return pred

def addGlobalValuesToPredicateList(l,globalObjects,globalProperties):
    l[2].props.extend(globalProperties.props)
    l[2].var.update(globalProperties.var)
    keys = [k for k in l[1].var]
    for k in keys:
        if l[1].var[k] in globalObjects.var.values():
            l[1].var = l[1].var.pop(k)
    return l

def removeDuplicates(body):
    noDups = []
    for atom in body.body:
        unique = True
        for atom2 in noDups:
            if str(atom) == str(atom2): unique = False ; break
        if unique: noDups.append(atom)
    body.body = noDups
    return body

def groundImplications(implications,globalObjects,globalProperties):
    newImps = []
    for head,body in implications:
        head = set(groundExpressions(*addGlobalValuesToPredicateList(head,globalObjects,globalProperties),False))        
        newBody = Body()
        for pred in groundExpressions(*addGlobalValuesToPredicateList(body,globalObjects,globalProperties),False):
            newBody.append(pred)
        for pred in set(filter(lambda x: isinstance(x,Class),head)):
            if re.match("[A-Z]+[0-9]*",pred.inst) and pred.inst not in newBody.var:
                newBody.append(pred)
                head.remove(pred)
        for pred in set(filter(lambda x: isinstance(x,Role),head)):
            if (re.match("[A-Z]+[0-9]*",pred.subj) and pred.subj not in newBody.var):
                if pred.subj in globalObjects.var:
                    newBody.append(Class(pred.subj,globalObjects.var[pred.subj],pred.subj))
            if (re.match("[A-Z]+[0-9]*",pred.obj) and pred.obj not in newBody.var):
                newBody.append(Class(pred.obj,globalObjects.var[pred.obj],pred.obj))
        for pred in set(filter(lambda x: isinstance(x,Class),newBody.body)):
            if pred.inst in globalObjects.var:
                newBody.append(Class(pred.inst,globalObjects.var[pred.inst],pred.inst))
        for pred in set(filter(lambda x: isinstance(x,Role),newBody.body)):
            if pred.subj in globalObjects.var:
                newBody.append(Class(pred.subj,globalObjects.var[pred.subj],pred.subj))
            if pred.obj in globalObjects.var:
                newBody.append(Class(pred.obj,globalObjects.var[pred.obj],pred.obj))
        for atom in head:
            newImps.append(Implication(removeDuplicates(newBody),atom))
        
    return newImps

def interpret_ace(ace):
    
    drs = getDRSFromACE(ace)    
    print('\n'.join(drs))
    #makeDRSFile(drs)
    
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
        
    varsPat = re.compile("\[([A-Z0-9\,]+)\].*")   
    objPat = re.compile("object\(([A-Z0-9]+),(.+),(.+),(.+),(.+),(.+)\)-(\d+)/(\d+)\s*")
    predPat = re.compile("predicate\(([A-Z0-9]+),(.+),(.+),([A-Z0-9]+)\)-(\d+)/(\d+)\s*")
    propPat = re.compile("property\(([A-Z0-9]+),(.+),(.+)\)-(\d+)/(\d+)\s*")
    impVarsPat = re.compile("\s+\[([A-Z0-9\,]+)\].*")
    impSignPat = re.compile("\s+(=>)\s*")
    impObjPat = re.compile("\s+object\(([A-Z0-9]+),(.+),(.+),(.+),(.+),(.+)\)-(\d+)/(\d+)\s*")
    impPredPat = re.compile("\s+predicate\(([A-Z0-9]+),(.+),(.+),([A-Z0-9]+)\)-(\d+)/(\d+)\s*")
    impPropPat = re.compile("\s+property\(([A-Z0-9]+),(.+),(.+)\)-(\d+)/(\d+)\s*")     
    
    
    for line in drs:
        if re.match(varsPat,line):
            continue
        elif re.match(impVarsPat,line):
            if len(body) == 0: 
                continue
            elif twice:
                implications.append(((impRoles,impObjects,impProperties),body))
                impObjects = ObjectList()    
                impProperties = PropertyList()    
                impRoles = []                
                body = []
                twice = False
            else:
                twice = True                
        elif re.match(impSignPat,line):
            body = (impRoles,impObjects,impProperties)
            impObjects = ObjectList()    
            impProperties = PropertyList()    
            impRoles = []
        else:
            ma = re.match(objPat,line)
            if ma: objects.append(ma.groups()[:-2])
            else: 
                ma = re.match(predPat,line)
                if ma: predicates.append(Role(*ma.groups()[:-2]))
                else:
                    ma = re.match(propPat,line)
                    if ma: properties.append(ma.groups()[:-2])
                    else: 
                        ma = re.match(impObjPat,line)
                        if ma: impObjects.append(ma.groups()[:-2])
                        else: 
                            ma = re.match(impPredPat,line)
                            if ma: impRoles.append(Role(*ma.groups()[:-2]))
                            else:
                                ma = re.match(impPropPat,line)
                                if ma: impProperties.append(ma.groups()[:-2])
                                else: raise
    
    if len(body) != 0: implications.append([(impRoles,impObjects,impProperties),body])
    
    facts = groundExpressions(predicates,objects,properties)
    
    implications = groundImplications(implications,objects,properties)    
    
    print("Reasoning...")
    prologfile = "interpreter/prolog.pl"
    reasonerFacts, groundRules = runProlog([str(fact) for fact in facts], [[str(imp.head),[str(b) for b in imp.body.body]] for imp in implications], prologfile)
    #os.remove(prologfile)

    return set(facts), set([imp.toRule() for imp in implications]), set(groundRules), set(reasonerFacts)

class Interpreter:

    def __init__(self, memory):
        self.memory = memory

    def interpret_ace(self,ace):
        '''Interprets ACE text and adds the resulting knowledge to memory'''
        self.memory.add_instruction_knowledge(interpret_ace(ace))

if __name__ == "__main__":
    interpret_ace(open("interpreter/ace.txt","r").read())