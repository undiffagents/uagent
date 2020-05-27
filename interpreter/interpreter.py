import os
import re
import subprocess

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
    new_string = []
    started = False
    for line in xml_string.splitlines():
        if "</drspp>" in line:
            break
        elif "<drspp>" in line:
            line = line.split(">")[1]
            started = True
        #elif '&gt;' in line: line = line.replace("&gt;", ">")
        if started:
            line = line.replace("&gt;", ">")
            new_string.append(line)
    return new_string

def getDRSFromACE(ace):
    print("Interpreting ACE...")
    
    process = subprocess.Popen(['lib/ape/ape.exe', '-cdrspp'],stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    process.stdin.write(ace.encode('utf-8'))
    drs = strip_xml(process.communicate()[0].decode('utf-8'))
    process.stdin.close()  # possibly unnecessary when function returns? not great at subprocess
    
    return drs

def makeDRSFile(drs):
    open("interpreter/DRS.txt","w").write("\n".join(drs))

def interpret_ace(ace):
    
    drs = getDRSFromACE(ace)    
    print(drs)
    makeDRSFile(drs)
    
    '''REWRITING PARSER HERE'''
    
    print("Reasoning...")
    prologfile = "interpreter/prolog.pl"
    reasonerFacts, groundRules = runProlog(facts, prolog, prologfile)
    #os.remove(prologfile)

    return set(facts), set(rules), set(groundRules), set(reasonerFacts)


class Interpreter:

    def __init__(self, memory):
        self.memory = memory

    def interpret_ace(self,ace):
        '''Interprets ACE text and adds the resulting knowledge to memory'''
        self.memory.add_instruction_knowledge(interpret_ace(ace))
