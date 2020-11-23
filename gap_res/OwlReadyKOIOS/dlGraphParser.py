# from SPARQLWrapper import SPARQLWrapper, JSON
#from ontoConstants import *
#from owlready2 import *
import re

dlGraphFile = 'dlGraphForInitialization.txt'
ontologySignature = 'http://www.uagent.com/ontology#'
owlSignature = 'http://www.w3.org/2002/07/owl#'

itemBlocksInGraph = []


def getItemBlocksInGraph():
    inputFile = open(dlGraphFile, 'r')
    inputLines = inputFile.readlines()
    currentItemBlock = ''
    # Go through lines in the dlGraph
    for line in inputLines:
        # strip unneeded whitespace from beginning and end of string
        line = line.strip()
        # Add the current line to the current item block
        currentItemBlock = currentItemBlock + " " + line
        # If the line ends with a period, then it's the end of that item block - end the block
        if line.endswith('.'):
            # Append this item block to the list of item blocks
            itemBlocksInGraph.append(currentItemBlock)
            # Reset the item block
            currentItemBlock = ''

    pass

def parseItemBlocks():
    # Strip out the URL portions of the XML segments
    for itemBlock in itemBlocksInGraph:
        # Track the current object (left side of the "a")
        beforeA = itemBlock.split('> a')[0]
        afterA = itemBlock.split('> a')[1]
        currentObject = beforeA.split(ontologySignature)[1]
        # Track the "parent-types" (right side of a, left before first semicolon, separated by commas)
        # Track the relationships (after first semicolon, separated by semicolons - predicate then target)

getItemBlocksInGraph()
parseItemBlocks()
print(itemBlocksInGraph)