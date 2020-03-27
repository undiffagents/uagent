import os
import re
import subprocess


def lowercase(s):
    return s[:1].lower() + s[1:] if s else ''


def parseVarLine(line):
    return ((line.split('[')[1]).split(']')[0]).split(',')


def parseObjectLine(line):
    line = (line.split('(')[1]).split(',')
    return [line[0], line[1]]


def lookupObject(letter, objs):
    for pair in objs:
        if pair[0] == letter:
            return pair[1].lower()
    return False


def falseNegCheck(name, objs):
    for pair in objs:
        if pair[1] == name:
            return pair[1].lower()
    return False


def isFact(term):
    for fact in facts:
        fact = fact.split('(')[0]
        if fact == term:
            return True
    return False


def lookupTerm(letter, objs, namedFacts, antecedent, head, body, unGround):
    a = ''
    term = lookupObject(letter, objs)
    if not term:
        return term
    for obj in objs:
        if obj[1] == term:
            a = obj[1]
            break
    if a in namedFacts:
        a = namedFacts[term]
    newatom = '{}({})'.format(a, obj[0])
    if a == '':
        newatom = '{}({})'.format(obj[1], obj[0])
    if antecedent:
        body.append(newatom)
    else:
        head.append(newatom)
    unGround.append(newatom)
    return obj[0]


def subObject(letter, string, objs, unnamedFacts, namedFacts):
    for pair in objs:
        if pair[0] == letter:
            unnamedFacts.remove(pair[1])
            namedFacts[string] = pair[1]
            pair[1] = string
            return True
    return False


def lookupProperty(letter, props):
    for pair in props:
        if pair[0] == letter:
            return pair[1]
    raise


def parsePropertyLine(line):
    line = (line.split('(')[1]).split(',')
    return(line[0], line[1])


def isVar(st):
    return not st.isupper()


def parsePredicateLine(line, props, objs, unnamedFacts, namedFacts, antecedent, consequent, rules, prolog, head, body, unGround):
    line = (line.split('(', 1)[1]).split(',')[1:]
    line[2] = line[2].split(')')[0]
    if isVar(line[1]):
        line[-2] = (line[-2].split('(')[1]).split(')')[0]
    if isVar(line[1]) and line[0] == 'be':
        b = line[1]
        a = lookupObject(line[2], objs)
        if not a:
            a = falseNegCheck(line[1], objs)
            b = lookupProperty(line[2], props)
            return 'hasProperty({},{})'.format(a, b)
        else:
            subObject(line[2], lowercase(b), objs, unnamedFacts, namedFacts)
            return '{}({})'.format(a.lower(), b)
    elif line[0] == 'be':
        b = lookupObject(line[2], objs)
        a = lookupObject(line[1], objs)
        if not b:
            return 'hasProperty({},{})'.format(lookupTerm(line[1], objs, namedFacts, antecedent, head, body, unGround), lookupProperty(line[2], props))
        else:
            rules.append('{}({}) => {}({})'.format(a, line[1], b, line[1]))
            prolog.append([atom, body])
            body = []
            head = []
            return
    elif not antecedent and not consequent:
        a = lookupObject(line[1], objs)
        b = lookupObject(line[2], objs)
        return '{}({},{})'.format(line[0], a, b)
    else:
        a = lookupTerm(line[1], objs, namedFacts,
                       antecedent, head, body, unGround)
        b = lookupTerm(line[2], objs, namedFacts,
                       antecedent, head, body, unGround)
        return '{}({},{})'.format(line[0], a, b)


def flipSide(antecedent, consequent, preds, facts):
    if not antecedent and not consequent:
        addAllFacts(preds, facts)
        antecedent = True
    elif antecedent:
        consequent = True
        antecedent = False
    else:
        antecedent = True
        consequent = False
    return antecedent, consequent


def addAllFacts(preds, facts):
    for pred in preds:
        facts.append(pred)


def extractVars(atom):
    return ((atom.split('(')[1]).split(')')[0]).split(',')


def determineVars(lists):
    vrs = []
    for atom in lists:
        vrs.extend(extractVars(atom))
    return set(vrs)


def checkVars(atom, head, body):
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


def strip_xml(xml_string):
    new_string = ''
    started = False
    for line in xml_string.splitlines():
        if "</drspp>" in line:
            break
        elif "<drspp>" in line:
            line = line.split(">")[1]
            started = True
        elif '&gt;' in line:
            line = line.replace("&gt;", ">")
        if started:
            new_string += line + '\n'
    return new_string


def writePrologFile(facts, prolog, prologfile, factFile, groundFile):
    program = sorted(prolog+facts, key=lambda x: x[0])

    open(prologfile, "w").write('{}\n:- open("{}",write, Stream),open("{}",write, Stream2),\n{}close(Stream),close(Stream2),halt.\n'.format(''.join(['{}.\n'.format('{} :- {}'.format(thing[0], ",".join(thing[1])) if isinstance(thing, list) else thing) for thing in program]), factFile, groundFile, ''.join(['forall(({}),({})),\n'.format(
        thing[0]+","+",".join(thing[1]), '{}write(Stream2," => "),write(Stream2,{}),write(Stream2,"\\n"),write(Stream,{}),write(Stream,"\\n")'.format(''.join(['write(Stream2,{}),{}'.format(stuff, 'write(Stream2,","),' if not stuff == thing[1][-1] else "") for stuff in thing[1]]), thing[0], thing[0])) for thing in prolog])))


def runProlog(facts, prolog, prologfile):

    factFile = "reasonerFacts.txt"
    groundFile = "groundRules.txt"

    writePrologFile(facts, prolog, prologfile, factFile, groundFile)

    subprocess.call(['swipl', prologfile, '-cdrspp'])

    reasonerFacts = open(factFile, "r").read().splitlines()
    groundRules = open(groundFile, "r").read().splitlines()

    os.remove(factFile)
    os.remove(groundFile)

    return reasonerFacts, groundRules


def interpret_ace(text):
    print("Interpreting ACE...")

    process = subprocess.Popen(['lib/ape/ape.exe', '-cdrspp'],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    process.stdin.write(text.encode('utf-8'))
    ace_drs = process.communicate()[0].decode('utf-8')
    process.stdin.close()

    ace_drs = strip_xml(ace_drs)
    print(ace_drs)

    varlist = []
    unGround = []
    objs = []
    preds = []
    props = []

    facts = []
    rules = []
    prolog = []
    body = []
    head = []

    antecedent = False
    consequent = False
    unnamedFacts = []
    namedFacts = {}

    for line in ace_drs.splitlines():
        if not ' ' in line:
            if 'object'in line:
                objs.append(parseObjectLine(line))
                unnamedFacts.append(objs[-1][1])
            elif 'named' in line or 'string' in line:
                preds.append(parsePredicateLine(line, props, objs, unnamedFacts, namedFacts,
                                                antecedent, consequent, rules, prolog, head, body, unGround))
            elif 'property' in line:
                props.append(parsePropertyLine(line))

    for fact in unnamedFacts:
        preds.append('{}({})'.format(fact, fact))

    for line in ace_drs.splitlines():
        if '[' in line:
            varlist.extend(parseVarLine(line))
            if ' ' in line:
                antecedent, consequent = flipSide(
                    antecedent, consequent, preds, facts)
                if antecedent:
                    if len(body) > 0 and len(head) > 0:
                        body = list(set(body))
                        head = list(set(head))
                        for a in body:
                            if a in head:
                                head.remove(a)
                        rules.append('{} => {}'.format(
                            ','.join(body), ','.join(head)))
                        for atom in head:
                            prolog.append([atom, body])
                    body = []
                    head = []
        elif ' object' in line:
            objs.append(parseObjectLine(line))
        elif ' property' in line:
            props.append(parsePropertyLine(line))
        elif 'predicate' in line and not ('named' in line or 'string' in line):
            if not antecedent and not consequent:
                preds.append(parsePredicateLine(line, props, objs, unnamedFacts, namedFacts,
                                                antecedent, consequent, rules, prolog, head, body, unGround))
            elif antecedent:
                body.append(parsePredicateLine(line, props, objs, unnamedFacts, namedFacts,
                                               antecedent, consequent, rules, prolog, head, body, unGround))
            elif len(body) == 0 and len(head) == 0:
                a = parsePredicateLine(line, props, objs, unnamedFacts, namedFacts,
                                       antecedent, consequent, rules, prolog, head, body, unGround)
                if len(head) > 0:
                    body = head
                    head = []
                    head.append(a)
            elif len(body) > 0:
                a = parsePredicateLine(line, props, objs, unnamedFacts, namedFacts,
                                       antecedent, consequent, rules, prolog, head, body, unGround)
                checkVars(a, head, body)
                head.append(a)

    if len(body) > 0 and len(head) > 0:
        for a in body:
            if a in head:
                head.remove(a)
        rules.append('{} => {}'.format(','.join(body), ','.join(head)))
        for atom in head:
            prolog.append([atom, body])

    print("Reasoning...")
    prologfile = "interpreter/prolog.pl"
    reasonerFacts, groundRules = runProlog(facts, prolog, prologfile)
    os.remove(prologfile)

    return set(facts), set(rules), set(groundRules), set(reasonerFacts)


class Interpreter:

    def __init__(self, memory):
        self.memory = memory

    def interpret_ace(self,ace):
        '''Interprets ACE text and adds the resulting knowledge to memory'''
        self.memory.add_instruction_knowledge(interpret_ace(ace))
