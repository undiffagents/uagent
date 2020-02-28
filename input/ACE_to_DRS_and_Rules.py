import re,os,subprocess
from Dapylog import *

def lowercase(s):
    return s[:1].lower() + s[1:] if s else ''

def parseVarLine(line):
    return ((line.split('[')[1]).split(']')[0]).split(',')

def parseObjectLine(line):
    line=(line.split('(')[1]).split(',')
    return [line[0],line[1]]

def lookupObject(letter,objs):
    for pair in objs:
        if pair[0] == letter: return pair[1].lower()
    return False

def falseNegCheck(name):
    for pair in objs:
        if pair[1] == name: return pair[1].lower()
    return False    

def isFact(term):
    for fact in facts:
        fact = fact.split('(')[0]
        if fact == term: return True
    return False

def lookupTerm(letter,objs,namedFacts,antecedent,head,body,unGround):    
    a = ''
    term = lookupObject(letter,objs)
    if not term: return term
    for obj in objs:
        if obj[1] == term: 
            a = obj[1]
            break
    if a in namedFacts:
        a = namedFacts[term]
    newatom = '{}({})'.format(a,obj[0])
    if a == '': newatom = '{}({})'.format(obj[1],obj[0])        
    if antecedent: body.append(newatom)
    else: head.append(newatom)
    unGround.append(newatom)
    return obj[0]

def subObject(letter,string,objs,unnamedFacts,namedFacts):
    for pair in objs:
        if pair[0] == letter: unnamedFacts.remove(pair[1]) ; namedFacts[string] = pair[1] ; pair[1] = string ; return True
    return False

def lookupProperty(letter,props):
    for pair in props:
        if pair[0] == letter: return pair[1]
    raise

def parsePropertyLine(line):
    line=(line.split('(')[1]).split(',')
    return(line[0],line[1])

def isVar(st):
    if len(st) == 1: return False
    return len(st) > 2

def parsePredicateLine(line,props,objs,unnamedFacts,namedFacts,antecedent,consequent,rules,datalog,head,body,unGround):
    line=(line.split('(',1)[1]).split(',')[1:]
    line[2]=line[2].split(')')[0]
    if isVar(line[1]): line[-2]=(line[-2].split('(')[1]).split(')')[0]
    if isVar(line[1]) and line[0] == 'be':
        b = line[1]
        a = lookupObject(line[2],objs)
        if not a:
            a = falseNegCheck(line[1])
            b = lookupProperty(line[2])
            return 'hasProperty({},{})'.format(a,b)
        else:
            subObject(line[2],lowercase(b),objs,unnamedFacts,namedFacts)
            return '{}({})'.format(a,b)
    elif line[0] == 'be': 
        b = lookupObject(line[2],objs)
        a = lookupObject(line[1],objs)   
        if not b: 
            return 'hasProperty({},{})'.format(lookupTerm(line[1],objs,namedFacts,antecedent,head,body,unGround),lookupProperty(line[2],props))
        else:
            rules.append('{}({}) => {}({})'.format(a,line[1],b,line[1]))
            datalog.append('{}({})->{}({})'.format(a,line[1],b,line[1]))
            body = [] ; head= []
            return
    elif not antecedent and not consequent:
        a = lookupObject(line[1],objs)
        b = lookupObject(line[2],objs)
        return '{}({},{})'.format(line[0],a,b)
    else:
        a = lookupTerm(line[1],objs,namedFacts,antecedent,head,body,unGround)
        b = lookupTerm(line[2],objs,namedFacts,antecedent,head,body,unGround)     
        return '{}({},{})'.format(line[0],a,b)

def flipSide(antecedent,consequent,preds,facts):
    if not antecedent and not consequent: addAllFacts(preds,facts) ; antecedent = True
    elif antecedent: consequent = True ; antecedent = False
    else: antecedent = True ; consequent = False
    return antecedent,consequent

def addAllFacts(preds,facts):
    for pred in preds:
        facts.append(pred)

def extractVars(atom):
    return ((atom.split('(')[1]).split(')')[0]).split(',')

def determineVars(lists):
    vrs = []
    for atom in lists:
        vrs.extend(extractVars(atom))
    return set(vrs)


def checkVars(atom,head,body):
    vrsBody = determineVars(body)
    vrsHead = determineVars(head)
    while not vrsHead.issubset(vrsBody):
        
        for atom in head:
            b = set(extractVars(atom))
            if b.issubset(vrsBody):
                print()
            else:
                head.remove(atom)
                body.append(atom)
        
        vrsBody = determineVars(body)
        vrsHead = determineVars(head)   

def stripXML(new,tmpFile):
    newFile = open(new,"w")
    started=False
    for line in tmpFile:
        if "</drspp>" in line:
            break
        elif "<drspp>" in line:
            line = line.split(">")[1]
            started=True
        elif '&gt;' in line:
            line=line.replace("&gt;",">")
        if started: newFile.write(line)
    newFile.close()
    os.remove(tmpFile)

def readACEFile(filename,drsName):
    print("Reading ACE file to make DRS and Rules")    

    aceFile = filename
    tmp = "tmp_DRS.txt"
    drsFile = drsName
    
    subprocess.call(['input/APE/ape.exe', '-file', aceFile,'-cdrspp'],stdout=open(tmp,"w"))

    stripXML(drsFile,tmp)
    
    varlist = []
    unGround = []
    objs = []
    preds = []
    props = []
    
    facts = []
    rules = []
    datalog = []
    body = []
    head = []
    
    drsfile = open(drsFile,"r")
    antecedent = False
    consequent = False
    unnamedFacts = []
    namedFacts = {}
    
    for line in drsfile:
        if not ' ' in line:
            if 'object'in line:
                objs.append(parseObjectLine(line))
                unnamedFacts.append(objs[-1][1])
            elif 'named' in line or 'string' in line:
                preds.append(parsePredicateLine(line,props,objs,unnamedFacts,namedFacts,antecedent,consequent,rules,datalog,head,body,unGround))
            elif 'property' in line:
                props.append(parsePropertyLine(line))
    
    drsfile.seek(0)
    
    for fact in unnamedFacts:
        preds.append('{}({})'.format(fact,fact))
    
    for line in drsfile:
        if '[' in line:
            varlist.extend(parseVarLine(line))
            if ' ' in line: 
                antecedent,consequent = flipSide(antecedent,consequent,preds,facts)
                if antecedent: 
                    if len(body) > 0 and len(head) > 0: 
                        body = list(set(body)) ; head= list(set(head))
                        for a in body:
                            if a in head: head.remove(a)
                        rules.append('{} => {}'.format(','.join(body),','.join(head))) 
                        for atom in head:
                            datalog.append('{}->{}'.format('^'.join(body),atom))
                    body = [] ; head= []
        elif ' object' in line:
            objs.append(parseObjectLine(line)) 
        elif ' property' in line:
            props.append(parsePropertyLine(line))
        elif 'predicate' in line and not ('named' in line or 'string' in line):
            if not antecedent and not consequent: preds.append(parsePredicateLine(line,props,objs,unnamedFacts,namedFacts,antecedent,consequent,rules,datalog,head,body,unGround))
            elif antecedent: 
                body.append(parsePredicateLine(line,props,objs,unnamedFacts,namedFacts,antecedent,consequent,rules,datalog,head,body,unGround))
            elif len(body) == 0 and len(head) == 0:  
                a = parsePredicateLine(line,props,objs,unnamedFacts,namedFacts,antecedent,consequent,rules,datalog,head,body,unGround)
                if len(head) > 0: 
                    body = head
                    head = []
                    head.append(a)
            elif len(body) > 0:
                a = parsePredicateLine(line,props,objs,unnamedFacts,namedFacts,antecedent,consequent,rules,datalog,head,body,unGround)
                checkVars(a,head,body)
                head.append(a)
    
    if len(body) > 0 and len(head) > 0: 
        rules.append('{} => {}'.format(','.join(body),','.join(head)))
        for atom in head:
            datalog.append('{}->{}'.format('^'.join(body),atom))
    
    drsfile.close()
    
    rulesfile = open("input/Rules.txt","w")
    datalogfile = open("input/datalog.dl","w")
    
    rulesfile.write("Facts:\n")
    datalogfile.write("%facts\n")

    for fact in facts:
        rulesfile.write('{}\n'.format(fact))
        datalogfile.write('{}\n'.format(fact))
    
    rulesfile.write('\nRules:\n')
    datalogfile.write("\n%rules\n")
    
    for rule in rules:
        rulesfile.write('{}\n'.format(rule))
    for rule in datalog:
        datalogfile.write('{}\n'.format(rule))
    
    rulesfile.close()

    datalogfile.close()
    
    reasoner = Dapylog(menu=False)
    newFacts = reasoner.getNewFacts()

    return  set(facts),set(rules),set(newFacts)
