# from SPARQLWrapper import SPARQLWrapper, JSON
#from ontoConstants import *
#from owlready2 import *
import re

dlGraphFile = 'dlGraphForInitialization.txt'
ontologySignature = 'http://www.uagent.com/ontology#'
owlSignature = 'http://www.w3.org/2002/07/owl#'

itemBlocksInGraph = []
graphChunks = {}

IS_A = "isa"
PREDS = "preds"


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
        currentObject = getObjectValue(itemBlock)
        #  Get the list of supertypes associated with the object
        processedObjectTypeList = getObjectTypeList(itemBlock)
        # Get the list of predicates (action/target pairs) associated with the object
        processedPredicateList = getPredicateList(itemBlock)

        # Construct a "chunk" for the object, declaring its supertypes and predicates (affordances?)
        graphChunks.update({currentObject: {IS_A: processedObjectTypeList, PREDS: processedPredicateList}})


def getObjectValue(itemBlock: str):
    # Track the current object (left side of the "a")
    currentObject = itemBlock.split('> a')[0]
    # Strip out the HTTP etc. signature
    currentObject = stripHTML(currentObject)

    return currentObject


def getObjectTypeList(itemBlock: str):
    objectsAndPredicates = itemBlock.split('> a')[1]

    # Track the "parent-types" (right side of a, left before first semicolon, separated by commas)
    objectTypeString = objectsAndPredicates.split(';', 1)[0].strip()
    objectTypes = objectTypeString.split(',')
    processedObjectTypeList = []
    for objectType in objectTypes:
        # Process each object type individually
        objectType = objectType.strip()
        # Strip out the HTTP etc. signature
        objectType = stripHTML(objectType)
        # Strip out anything after the closing angle bracket of the signature
        if '>' in objectType:
            objectType = objectType.split('>')[0].strip()
        # Add processed object type to list of types for this object.
        processedObjectTypeList.append(objectType)

    return processedObjectTypeList


def getPredicateList(itemBlock):
    processedPredicateList = []
    # Track the relationships (after first semicolon, separated by semicolons - predicate then target)
    if ';' in itemBlock:
        objectsAndPredicates = itemBlock.split('> a')[1]
        # Get all of the predicates in one string (basically dump the object and types)
        predicateString = objectsAndPredicates.split(';', 1)[1].strip()
        # Split up all of the predicates into their individual groups
        predicateList = predicateString.split(';')
        # Process each predicate individually
        for predicate in predicateList:
            predicate = predicate.strip()
            # Split the predicate into the "action" and the target
            predicateAction = predicate.split(' ')[0]
            predicateTarget = predicate.split(' ')[1]
            # Strip out the HTTP etc. signature of the action
            predicateAction = stripHTML(predicateAction)
            # Strip out anything after the closing angle bracket of the action signature
            if '>' in predicateAction:
                predicateAction = predicateAction.split('>')[0].strip()
            # Strip out the HTTP etc. signature of the target
            predicateTarget = stripHTML(predicateTarget)
            # Strip out anything after the closing angle bracket of the target signature
            if '>' in predicateTarget:
                predicateTarget = predicateTarget.split('>')[0].strip()

            processedPredicateList.append((predicateAction, predicateTarget))

    return processedPredicateList


def stripHTML(itemToStrip):
    # Strip out the HTTP etc. signature
    if ontologySignature in itemToStrip:
        itemToStrip = itemToStrip.split(ontologySignature)[1].strip()
    elif owlSignature in itemToStrip:
        itemToStrip = itemToStrip.split(owlSignature)[1].strip()

    return itemToStrip


getItemBlocksInGraph()
parseItemBlocks()
print(itemBlocksInGraph)
print(graphChunks)