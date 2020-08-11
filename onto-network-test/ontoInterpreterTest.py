import socket
import subprocess
import time
import requests
import networkx
import re
# from SPARQLWrapper import SPARQLWrapper, JSON
from ontoConstants import *

interpreterFile = 'interpreterTest.txt'

taskCount = 0
itemCount = 0
agentCount = 0
itemRoleCount = 0
affordanceCount = 0
locationCount = 0
colorCount = 0
shapeCount = 0
typeCount = 0
itemDescriptionCount = 0
situationDescriptionCount = 0
transitionDescriptionCount = 0
actionCount = 0

earlierSituationFirstItemNumber = 0
currentSituationFirstItemNumber = 0

# Making an assumption that the number of situations will be the number of actions plus one.
# With this, we can set up each situation in advance, minus the necessary changes.

maxSituations = 0

instanceSignifier = ':Instance'
PREFIX = 'PREFIX : <http://www.uagent.com/ontology#>\nPREFIX opla: <http://ontologydesignpatterns.org/opla#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n'
situationItemsDict = {}
experimentItemsDict = {}

multiSituationDict = {}

affordanceDict = {"button": "clickable", "letter": "visible"}


# CONCERNS: Co-referencing nodes after they've been created etc. will be a real pain.  Trying to figure that out.
# The dict seems like a good idea, but for items with roles/names, what should be the key?  The name? The role?
# What if you have multiple items with the same name?  Same role?
# For now using the name if there is one - if not, using the role
# There would have to be consistency between this and the interpreter on what's used as the reference item
# Generalization is really going downhill with all this CV stuff
# hasProperty, appearsOn, press - all don't really map to ontology

# Proposed interpreter changes:
# a creation line (task(), item(), agent()) prior to first use in an isPartOf, etc.
# role,name format in items, at the very least

# Don't really like having to have a dict set up for affordances - maybe some way to encode them
# or find them automatically?

# Will need to figure out how to deal with isPartOf if not a task

# Maybe make a network representation of all this and then convert the network to RDF?

# "Action" on the ontology only appears to have a subject and a verb - no object?

def readInput():
    rdfLines = ""
    # Open up the interpreter output
    inputFile = open(interpreterFile, 'r')
    inputLines = inputFile.readlines()

    # Parse through the input and see how many actions there should be (thus how many situations)
    countSituations(inputLines)

    rdfLines = rdfLines + startSituationDescription()
    # Iterate through each line
    for line in inputLines:
        line = line.strip()
        rdfLines = rdfLines + processInterpreterOutputLine(line)
    # Close up the last situation description
    rdfLines = rdfLines + endSituationDescription()
    print(rdfLines)
    # Send em
    subprocess.call(['./s-update', '--service=http://localhost:3030/uagent/update',
                    '{} INSERT DATA  {{ {} }}'.format(PREFIX, rdfLines)])


def countSituations(inputLines):
    global maxSituations

    for line in inputLines:
        if "action" in line.split('(')[0]:
            maxSituations = maxSituations + 1

    # Add the initial situation as well
    maxSituations = maxSituations + 1


def processInterpreterOutputLine(inputLine):
    inputSplit = inputLine.split('(', 1)
    inputType = inputSplit[0]
    if "action" not in inputType:
        inputContents = inputSplit[1]
        inputContents = inputContents.split(')')[0]
    else:
        inputContents = inputLine

    # handle task
    if inputType == 'task':
        rdfLines = processTask(inputContents)

    # handle item
    if inputType == 'item':
        rdfLines = processItem(inputContents)

    # handle agent
    if inputType == 'agent':
        rdfLines = processAgent(inputContents)

    # handle isPartOf
    if inputType == 'isPartOf':
        rdfLines = processIsPartOf(inputContents)

    if inputType == 'action':
        rdfLines = processAction(inputContents)

    return rdfLines


def processTask(inputContents):
    global taskCount
    rdfLines = ""
    taskName = inputContents

    # assemble task creation rdf line
    taskCreator = instanceSignifier + TASK_NODE + str(taskCount)
    # increase task Count
    taskCount = taskCount + 1

    experimentItemsDict.update({taskName: taskCreator})
    rdfCreationLine = taskCreator + " " + TYPE_EDGE + " :" + TASK_NODE + " ."
    rdfNamingLine = taskCreator + " " + HAS_NAME_EDGE + " \"" + taskName + "\" ."

    rdfLines = rdfLines + rdfCreationLine + rdfNamingLine
    return rdfLines


def processItem(inputContents):
    global itemCount
    global affordanceCount
    global itemRoleCount
    rdfLines = ""
    itemRole = ""
    itemName = ""
    # if no comma in the contents, no name, just role.
    # If comma, first entry is role, second is name
    if ',' not in inputContents:
        itemRole = inputContents
    else:
        itemRole = inputContents.split(',')[0]
        itemName = inputContents.split(',')[1]

    # assemble item creation rdf line
    itemCreator = instanceSignifier + ITEM_NODE + str(itemCount)
    # increase item count
    itemCount = itemCount + 1

    if itemName != "":
        situationItemsDict.update({itemName: itemCreator})

    # Item creation
    itemCreationLine = itemCreator + " " + TYPE_EDGE + " :" + ITEM_NODE + " ."
    rdfLines = rdfLines + itemCreationLine
    if itemName != "":
        itemNamingLine = itemCreator + " " + HAS_ITEM_NAME_EDGE + " \"" + itemName + "\" ."
        rdfLines = rdfLines + itemNamingLine

    # Affordance creation if appropriate (in affordance dict)
    if affordanceDict.get(itemRole) is not None:
        # If the affordance doesn't already exist, create it.
        if situationItemsDict.get(affordanceDict.get(itemRole)) is None:
            affordanceCreator = instanceSignifier + AFFORDANCE_NODE + str(affordanceCount)
            affordanceCount = affordanceCount + 1
            # generate RDF lines
            affordanceCreationLine = affordanceCreator + " " + TYPE_EDGE + " :" + AFFORDANCE_NODE + " ."
            # TODO **** very unsure about the way to "ofType" things, right now using a string.
            affordanceTypingLine = affordanceCreator + " " + OF_TYPE_EDGE + " \"" + affordanceDict.get(
                itemRole) + "\" ."
            # Add to created things dictionary for the affordance of the role
            situationItemsDict.update({affordanceDict.get(itemRole): affordanceCreator})
            # Add to RDF output
            rdfLines = rdfLines + affordanceCreationLine + affordanceTypingLine
        # Connect item to affordance.
        itemAffordsLine = itemCreator + " " + AFFORDS_EDGE + " " + situationItemsDict.get(
            affordanceDict.get(itemRole)) + " ."
        rdfLines = rdfLines + itemAffordsLine

    # Role creation if role not already existing
    if situationItemsDict.get(itemRole) is None:
        roleCreator = instanceSignifier + ITEM_ROLE_NODE + str(itemRoleCount)
        itemRoleCount = itemRoleCount + 1

        # generate RDF lines
        roleCreationLine = roleCreator + " " + TYPE_EDGE + " :" + ITEM_ROLE_NODE + " ."
        roleTypingLine = roleCreator + " " + OF_TYPE_EDGE + " \"" + itemRole + "\" ."
        # Add to created things dictionary for the role
        situationItemsDict.update({itemRole: roleCreator})
        # Add to rdf output
        rdfLines = rdfLines + roleCreationLine + roleTypingLine
    else:
        roleCreator = situationItemsDict.get(itemRole)
    # Connect item to role
    itemHasRoleLine = roleCreator + " " + ASSUMED_BY_EDGE + " " + itemCreator + " ."

    rdfLines = rdfLines + itemHasRoleLine

    return rdfLines


def processAgent(inputContents):
    return ""


def processIsPartOf(inputContents):
    rdfLines = ""
    subelementIdentifier = inputContents.split(',')[0]
    superelementIdentifier = inputContents.split(',')[1]

    subelement = situationItemsDict.get(subelementIdentifier)
    superelement = situationItemsDict.get(superelementIdentifier)
    if subelement is None:
        subelement = experimentItemsDict.get(subelementIdentifier)
    if superelement is None:
        superelement = experimentItemsDict.get(superelementIdentifier)

    if subelement is None or superelement is None:
        print("There was a problem with processing IsPartOf(" + inputContents + ").  Line 212 for debug.")

    # Handle the isPartOf(item,task) scenario
    if "Item" in subelement and "Task" in superelement:
        if "Role" not in subelement:
            subelement = re.sub("Item", "ItemRole", subelement)
        taskProvidesRoleLine = superelement + " " + PROVIDES_ROLE_EDGE + " " + subelement + " ."
        rdfLines = rdfLines + taskProvidesRoleLine

    return rdfLines


def processAction(inputContents):
    global actionCount

    # Messy string manipulation to get the action contents out of the total string
    actionContents = inputContents.split(" => ")[0]
    actionContents = actionContents.split('(')[1]
    actionContents = actionContents.split(')')[0]
    actionVerb = actionContents.split(',')[0]
    actionSubject = actionContents.split(',')[1]
    if len(actionContents.split(',')) > 2:
        actionObject = actionContents.split(',')[2]
    consequence = inputContents.split(" => ")[1]
    consequence = consequence.split(')')[0]
    consequenceType = consequence.split('(')[0]
    consequenceContents = consequence.split('(')[1]

    rdfLines = ""

    # Set up the action linking to the pre-action situation description item before flushing situation items
    actionCreator = instanceSignifier + ACTION_NODE + str(actionCount)
    # Increment the number of actions that exist
    actionCount = actionCount + 1

    # Create action node of type Action
    actionCreationLine = actionCreator + " " + TYPE_EDGE + " :" + ACTION_NODE + " ."
    rdfLines = rdfLines + actionCreationLine

    # Make RDF line to instantiate action wrt. the item that triggered it
    if situationItemsDict.get(actionSubject) is None:
        print("Uh oh - it looks like an error occurred trying to process the action.  The term " + actionSubject + \
              " was not found.  For debugging purposes, this happened in processAction - line 240.")
    else:
        # TODO **** I really need to figure out the dict thing - right now since the dict returns a role, just
        # subbing out the term "role" for "item" if it appears.
        actionRefersToItem = situationItemsDict.get(actionSubject)
        if "Role" in actionRefersToItem:
            actionRefersToItem = re.sub("ItemRole", "Item", actionRefersToItem)
        actionRefersToRDFLine = actionCreator + " " + REFERS_TO_EDGE + " " + actionRefersToItem + " ."
        rdfLines = rdfLines + actionRefersToRDFLine

    # Add type of action
    actionTypeRDFLine = actionCreator + " " + OF_TYPE_EDGE + " \"" + actionVerb + "\" ."
    rdfLines = rdfLines + actionTypeRDFLine

    # Close up the pre-action situation description
    rdfLines = rdfLines + endSituationDescription()

    # Next step is to create a new situation description.  Unsure exactly what carries over from one to the next but
    # for now just cloning the previous situation description and adding whatever the action consequence is.
    # TODO **** Figure out situation descriptions in more detail
    rdfLines = rdfLines + startSituationDescription()

    # Create Transition Description and connect situation descriptions to it
    rdfLines = rdfLines + createTransitionDescription()

    # Connect action to transition description (have to use current transition count - 1 because it was incremented
    # when the transition was created)
    transitionCreator = instanceSignifier + TRANSITION_DESCRIPTION_NODE + str(transitionDescriptionCount - 1)
    actionTriggersTransitionLine = actionCreator + " " + TRIGGERS_EDGE + " " + transitionCreator + " ."
    rdfLines = rdfLines + actionTriggersTransitionLine

    # SOMEWHERE IN HERE WE SHOULD POPULATE THE NEW SITUATION - FOR NOW IT'S JUST BEING DONE BY DOUBLING UP THE
    # ITEMS ETC.
    # TODO *****

    # Handle the consequence
    # TODO **** THIS IS PROBABLY NOT THE IDEAL ROUTE
    rdfLines = rdfLines + processInterpreterOutputLine(consequence)

    return rdfLines


def createTransitionDescription():
    global transitionDescriptionCount

    rdfLines = ""

    # Create a transition and increment the number of transitions
    transitionCreator = instanceSignifier + TRANSITION_DESCRIPTION_NODE + str(transitionDescriptionCount)
    transitionDescriptionCount = transitionDescriptionCount + 1

    # Add RDF Line to create transition
    createTransitionLine = transitionCreator + " " + TYPE_EDGE + " :" + TRANSITION_DESCRIPTION_NODE + " ."
    rdfLines = rdfLines + createTransitionLine

    # Connect Transition Description to its pre/post-situations
    if situationDescriptionCount > 0:
        # Pre-situation = current situation count minus one
        transitionPreSituationLine = transitionCreator + " " + HAS_PRE_SITUATION_DESCRIPTION_EDGE + " :" + \
            SITUATION_DESCRIPTION_NODE + str(situationDescriptionCount - 1) + " ."
        # Post-situation = current situation count
        transitionPostSituationLine = transitionCreator + " " + HAS_POST_SITUATION_DESCRIPTION_EDGE + " :" + \
            SITUATION_DESCRIPTION_NODE + str(situationDescriptionCount) + " ."
        rdfLines = rdfLines + transitionPreSituationLine + transitionPostSituationLine

    return rdfLines


def startSituationDescription():
    # If not 0, then from 0 to current - earlier condition, from current to max - current condition

    global earlierSituationFirstItemNumber
    global currentSituationFirstItemNumber
    rdfLines = ""

    # The first item in the new situation will start at the current item count
    earlierSituationFirstItemNumber = currentSituationFirstItemNumber
    currentSituationFirstItemNumber = itemCount

    # Create a situation and DO NOT increment the number of situations - the increment will happen
    # at the end of the situation
    situationCreator = instanceSignifier + SITUATION_DESCRIPTION_NODE + str(situationDescriptionCount)

    # multiSituationDict.update({situationCreator: {}})

    # Make rdf line to create situation
    createSituationLine = situationCreator + " " + TYPE_EDGE + " :" + SITUATION_DESCRIPTION_NODE + " ."
    rdfLines = rdfLines + createSituationLine

    for i in range(earlierSituationFirstItemNumber, currentSituationFirstItemNumber):
        earlierConditionItem = instanceSignifier + ITEM_NODE + str(i)
        addEarlierConditionToSituationLine = situationCreator + " " + HAS_EARLIER_CONDITION_EDGE + \
                                             " " + earlierConditionItem + " ."
        rdfLines = rdfLines + addEarlierConditionToSituationLine
    return rdfLines


def endSituationDescription():
    # If not 0, then from 0 to current - earlier condition, from current to max - current condition
    global situationDescriptionCount

    rdfLines = ""

    # Create a situation
    situationCreator = instanceSignifier + SITUATION_DESCRIPTION_NODE + str(situationDescriptionCount)

    # Make rdf line to create situation
    # createSituationLine = situationCreator + " " + TYPE_EDGE + " :" + SITUATION_DESCRIPTION_NODE + " ."
    # rdfLines = rdfLines + createSituationLine

    for i in range(currentSituationFirstItemNumber, itemCount):
        currentConditionItem = instanceSignifier + ITEM_NODE + str(i)
        addCurrentConditionToSituationLine = situationCreator + " " + HAS_CURRENT_CONDITION_EDGE + \
                                             " " + currentConditionItem + " ."
        rdfLines = rdfLines + addCurrentConditionToSituationLine

    # Increment the number of situations at this point
    situationDescriptionCount = situationDescriptionCount + 1

    # Add the current situation's items to the multi-situation backup dict and
    # Clear the dictionary of current situation items since we're ending a situation
    # NEED TO MAKE SURE ONLY TO CLEAR SITUATION ITEMS; there's definitely a problem with storing the task etc. in here.
     multiSituationDict.update({situationCreator: situationItemsDict.copy()})
     situationItemsDict.clear()

    return rdfLines


readInput()
