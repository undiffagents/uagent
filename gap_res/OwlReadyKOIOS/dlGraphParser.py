# from SPARQLWrapper import SPARQLWrapper, JSON
#from ontoConstants import *
#from owlready2 import *
import re
import networkx as nx

dlGraphFile = 'dlGraphForInitialization.txt'
ontologySignature = 'http://www.uagent.com/ontology#'
owlSignature = 'http://www.w3.org/2002/07/owl#'

itemBlocksInGraph = []
graphChunks = {}
classList = []
instanceList = []
instanceParents = []
classChildren = []

testGraph = nx.MultiDiGraph()

IS_A = "isa"
PREDS = "preds"
CLASS_TYPE = "Class"

# If it's a NamedIndividual, it's an instantiation; if it's a class and not a namedindividual, it's not.
# OR if it's both, then there's a class and this is an an instantiation of that class at once ?????
# IGNORE NAMEDINDIVIDUAL - IT'S AN INSTANCE IF IT HAS A UAGENT REFERENCE (button/task) IN ITS THING
# WHAT ABOUT #active THEN?  IT ONLY HAS NAMEDINDIVIDUAL
# If it's an "ObjectProperty" it's an "action" edge?
# How to figure out relationships between classes? i.e. subject -> button passes through spacebar.
# Maybe track relationships between namedindividuals and that means the classes have a relationship?
# Would be nice to have a "structure" of acceptable relationships between classes.

# Iterate through all classes and construct those
# Then initialize namedIndividuals as is appropriate - ARE THE NAMED INDIVIDUALS INSTANCES THOUGH?  OR NOT NECESSARILY
# Then connect the individuals

# The class side of the graph could be the "expected structure" and the instance side of the graph could be the
# "actual structure" - maybe those could be compared?

def constructClasses():
    # Iterate through graphChunks and grab each "class" and create a node out of that.
    for chunkKey, chunkValue in graphChunks.items():
        objectName = chunkKey
        # print(chunkKey, chunkValue)
        print(objectName)
        # Get the supertypes of the object
        superTypes = chunkValue.get(IS_A)
        # If one of the supertypes is "Class" then we want to create a class-level node for this.
        if CLASS_TYPE in superTypes:
            # REMOVE THE + CLASS_TYPE, THAT'S JUST FOR DEBUGGING?  UNLESS IT WOULD BE USEFUL TO KEEP
            testGraph.add_node(objectName + '_' + CLASS_TYPE, nodeType=CLASS_TYPE, parentClass='Object')
            # Add to list of classes
            classList.append(objectName)

def connectClasses():
    # Iterate through the classes and find what predicate relationships they have with items.  If those items aren't
    # classes, then need to find the parent class and connect it to that.
    for classObject in classList:
        # Get the chunk values for the object in question
        objectChunk = graphChunks.get(classObject)
        # Get the predicates out of that chunk
        objectPreds = objectChunk.get(PREDS)
        # Iterate through the predicates
        for action, target in objectPreds:
            # Check if the target is a class object or not
            if target in classList:
                # Connect the object and the target via the action.
                print(classObject, target, action)
                testGraph.add_edge(str(classObject) + '_' + CLASS_TYPE,
                                   str(target) + '_' + CLASS_TYPE, predicate=str(action))
            # If the target is not a class object, then we need to get its parent class and connect the current
            # class object to the parent class.
            else:
                # Get the chunk about the target
                targetChunk = graphChunks.get(target)
                # Retrieve the supertypes from the target chunk
                targetClasses = targetChunk.get(IS_A)
                # Compare the target chunk supertypes to the list of classes
                parentClassesFound = [foundClass for foundClass in classList if foundClass in targetClasses]
                # If a parent class is found
                if len(parentClassesFound) > 0:
                    # ASSUME ONLY ONE PARENT CLASS PER INDIVIDUAL
                    parentClass = parentClassesFound[0]
                    testGraph.add_edge(str(classObject) + '_' + CLASS_TYPE,
                                       str(parentClass) + '_' + CLASS_TYPE, predicate=str(action))

def constructInstances():
    # Iterate through graphChunks and grab each "class" and create a node out of that.
    for chunkKey, chunkValue in graphChunks.items():
        objectName = chunkKey
        # Get the supertypes of the object
        superTypes = chunkValue.get(IS_A)
        # Check if any of the classes are in the list of types for this object
        parentClassesFound = [foundClass for foundClass in classList if foundClass in superTypes]
        if len(parentClassesFound) > 0:
            # ASSUMING ONLY ONE PARENT CLASS PER INDIVIDUAL
            parentClass = parentClassesFound[0]
            # TODO: Need to somehow inherit the properties/links of the parent class?
            testGraph.add_node(objectName, nodeType='Instance', parentClass=parentClass+'_'+CLASS_TYPE)
            # Add to list of classes
            instanceList.append(objectName)
            # Track parent of instance
            instanceParents.append((objectName, parentClass))
            classChildren.append((parentClass, objectName))

# This gives affordances pretty nicely I guess?  Maybe - unless there's a difference between afforded actions and
# "used" actions
def connectInstances():
    # Need to find a way to get the parent classes of the instance (easy) and then connect the instance to any instances
    # of classes which the parent class is connected to (hard)
    for currentInstance in instanceList:
        # Get the chunk values for the instance in question
        instanceChunk = graphChunks.get(currentInstance)
        # Get the predicates out of that chunk
        instancePreds = instanceChunk.get(PREDS)
        # Iterate through the predicates - connect the predicates declared on the instance to the targets which are
        # instances
        for action, target in instancePreds:
            # Check if the target is a class object or not
            testGraph.add_edge(str(currentInstance), str(target), predicate=str(action))
        # TODO: OTHER STEPS WHICH NEED DONE:
        # Get the parent of the currentInstance and see if there are any connections which the parent class has
        # which can be mirrored?  Also check if there are any connections to classes and connect to the child instances?
        # OR MAYBE NOT - THIS COULD BE A GAP.  F.E.: Button has "beIn PVT" but space_bar does not.
        # SO THIS COULD BE SOMETHING FOR DETECTION.
        # Just because a class has/allows for a connection doesn't mean it HAS to be true.
        # Specifically, what if there are multiple instances of a class; how do you know which to connect to?
        # Not necessarily all of them.

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
constructClasses()
constructInstances()
connectClasses()
connectInstances()
nx.write_graphml_lxml(testGraph, "testGraph.graphml")

print(itemBlocksInGraph)
print(graphChunks)
