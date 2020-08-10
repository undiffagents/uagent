import socket
import subprocess
import time
import requests
import networkx
#from SPARQLWrapper import SPARQLWrapper, JSON
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
actionCount = 0

instanceSignifier = ':Instance'
PREFIX = 'PREFIX : <http://www.uagent.com/ontology#>\nPREFIX opla: <http://ontologydesignpatterns.org/opla#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n'
createdItemsDict = {}

affordanceDict = {"button": "clickable", "letter": "visible"}

# CONCERNS: Co-referencing nodes after they've been created etc. will be a real pain.  Trying to figure that out.
# The dict seems like a good idea, but for items with roles/names, what should be the key?  The name? The role?
# What if you have multiple items with the same name?  Same role?
# For now using the name if there is one - if not, using the role
# There would have to be consistency between this and the interpreter on what's used as the reference item
# Generalization is really going downhill with all this CV stuff

# Proposed interpreter changes:
# a creation line (task(), item(), agent()) prior to first use in an isPartOf, etc.
# role,name format in items, at the very least

# Don't really like having to have a dict set up for affordances - maybe some way to encode them
# or find them automatically?

# Will need to figure out how to deal with isPartOf if not a task

def updateOnto():
    # Read my file of ontology test additions
    totalString = ''
    file1 = open('ontoTestAddition.txt', 'r')
    Lines = file1.readlines()
    # Get them ready to send up
    for line in Lines:
        line = line.strip()
        totalString += line + " ."
    totalString = totalString[:-1]
    print(totalString)

    # Send em
    subprocess.call(['./s-update', '--service=http://localhost:3030/uagent/update',
                     '{} INSERT DATA  {{ {} }}'.format(PREFIX, totalString)])


def readInput():
    rdfLines = ""
    # Open up the interpreter output
    inputFile = open(interpreterFile, 'r')
    inputLines = inputFile.readlines()
    # Iterate through each line
    for line in inputLines:
        line = line.strip()
        rdfLines = rdfLines + processInterpreterOutputLine(line)
    print(rdfLines)
    # Send em
    subprocess.call(['./s-update', '--service=http://localhost:3030/uagent/update',
                     '{} INSERT DATA  {{ {} }}'.format(PREFIX, rdfLines)])


def processInterpreterOutputLine(inputLine):
    inputSplit = inputLine.split('(', 1)
    inputType = inputSplit[0]
    inputContents = inputSplit[1]
    inputContents = inputContents.split(')')[0]

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

    return rdfLines


def processTask(inputContents):
    global taskCount
    rdfLines = ""
    taskName = inputContents

    # assemble task creation rdf line
    taskCreator = instanceSignifier + TASK_NODE + str(taskCount)
    # increase task Count
    taskCount = taskCount + 1

    createdItemsDict.update({taskName: taskCreator})
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
        createdItemsDict.update({itemName: itemCreator})

    # Item creation
    itemCreationLine = itemCreator + " " + TYPE_EDGE + " :" + ITEM_NODE + " ."
    rdfLines = rdfLines + itemCreationLine
    if itemName != "":
        itemNamingLine = itemCreator + " " + HAS_ITEM_NAME_EDGE + " \"" + itemName + "\" ."
        rdfLines = rdfLines + itemNamingLine

    # Affordance creation if appropriate (in affordance dict)
    if affordanceDict.get(itemRole) is not None:
        # If the affordance doesn't already exist, create it.
        if createdItemsDict.get(affordanceDict.get(itemRole)) is None:
            affordanceCreator = instanceSignifier + AFFORDANCE_NODE + str(affordanceCount)
            affordanceCount = affordanceCount + 1
            # generate RDF lines
            affordanceCreationLine = affordanceCreator + " " + TYPE_EDGE + " :" + AFFORDANCE_NODE + " ."
            # TODO **** very unsure about the way to "ofType" things, right now using a string.
            affordanceTypingLine = affordanceCreator + " " + OF_TYPE_EDGE + " \"" + affordanceDict.get(itemRole) + "\" ."
            # Add to created things dictionary for the affordance of the role
            createdItemsDict.update({affordanceDict.get(itemRole): affordanceCreator})
            # Add to RDF output
            rdfLines = rdfLines + affordanceCreationLine + affordanceTypingLine
        # Connect item to affordance.
        itemAffordsLine = itemCreator + " " + AFFORDS_EDGE + " " + createdItemsDict.get(affordanceDict.get(itemRole)) + " ."
        rdfLines = rdfLines + itemAffordsLine

    # Role creation if role not already existing
    if createdItemsDict.get(itemRole) is None:
        roleCreator = instanceSignifier + ITEM_ROLE_NODE + str(itemRoleCount)
        itemRoleCount = itemRoleCount + 1

        # generate RDF lines
        roleCreationLine = roleCreator + " " + TYPE_EDGE + " :" + ITEM_ROLE_NODE + " ."
        roleTypingLine = roleCreator + " " + OF_TYPE_EDGE + " \"" + itemRole + "\" ."
        # Add to created things dictionary for the role
        createdItemsDict.update({itemRole: roleCreator})
        # Add to rdf output
        rdfLines = rdfLines + roleCreationLine + roleTypingLine
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

    subelement = createdItemsDict.get(subelementIdentifier)
    superelement = createdItemsDict.get(superelementIdentifier)

    # Handle the isPartOf(item,task) scenario
    if "Item" in subelement and "Task" in superelement:
        taskProvidesRoleLine = superelement + " " + PROVIDES_ROLE_EDGE + " " + subelement + " ."
        rdfLines = rdfLines + taskProvidesRoleLine

    return rdfLines


readInput()
