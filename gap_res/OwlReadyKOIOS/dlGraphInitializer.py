# from SPARQLWrapper import SPARQLWrapper, JSON
from ontoConstants import *
from owlready2 import *
import sys

sys.path.append('/mnt/t/Projects/uagent-new/ontology')
sys.path.append('/mnt/t/Projects/uagent-new/lib')

from ontology import Ontology

interpreterFile = 'gap_res/OwlReadyKOIOS/interpreterTest.txt'
#interpreterFile = 'interpreterTest.txt'

currentExperiment = None
currentTask = None
currentSituation = None
previousSituation = None
transitionToCurrentSituation = None

# Making an assumption that the number of situations will be the number of actions plus one.
# With this, we can set up each situation in advance, minus the necessary changes.

instanceSignifier = ':Instance'
PREFIX = 'PREFIX : <http://www.uagent.com/ontology#>\nPREFIX opla: <http://ontologydesignpatterns.org/opla#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n'
situationItemsDict = {}
experimentItemsDict = {}

situationItems = [instanceSignifier + ITEM_NODE, instanceSignifier + ITEM_ROLE_NODE,
                  instanceSignifier + AFFORDANCE_NODE, instanceSignifier + ITEM_DESCRIPTION_NODE]

multiSituationDict = {}
situationItemsInRDF = []

situationRDFLines = []
totalRDFLines = []

sitLevelInputLines = []

affordanceDict = {"button": "clickable", "letter": "visible"}

onto = get_ontology("http://localhost:3030/uagent").load()

ontology = Ontology()

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

def initializeOntology():
    # TESTING ONTOLOGY CLASS
    # THIS DIRECTORY CHANGE IS MESSY AND LOCAL TO MY MACHINE BUT IT GETS IT WORKING
    # THIS SUCCESSFULLY PRINTS THE DRS STRINGS
    os.chdir('/mnt/t/Projects/uagent-new')
    rdfLines = ""
    # Open up the interpreter output
    # inputFile = open(interpreterFile, 'r')
    # inputLines = inputFile.readlines()
    # Set up the ISR-MATB Experiment
    beginExperiment()

    # Iterate through each line
    #for line in inputLines:
    #    line = line.strip()
    #    processInterpreterOutputLine(line)
        # rdfLines = rdfLines + processInterpreterOutputLine(line)
    # Close up the last situation description
    # rdfLines = rdfLines + endSituationDescription()
    # print(ontology.getAllTypedDRSInstructions())
    individuals = ontology.getDLGraphIndividuals()
    print(individuals)
    for individual in individuals:
        dlGraphClasses = ontology.getDLGraphClassesForIndividual(individual)
        #print(ontology.getDRSArgsForComponentName(individual))
        DRSTypesForIndividual = list(ontology.getDRSArgsForComponentName(individual).keys())
        #print("INDIV", DRSTypesForIndividual)
        for dlGraphClass in dlGraphClasses:
            # print(ontology.getDRSArgsForComponentName(dlGraphClass))
            DRSTypesForClass = list(ontology.getDRSArgsForComponentName(dlGraphClass).keys())
            #print("CLASS", DRSTypesForClass)
        DRSTypes = set(DRSTypesForClass + DRSTypesForIndividual)
        print(individual, dlGraphClass, DRSTypes)
        processDLGraphItem(individual, dlGraphClass, DRSTypes.pop())
        DRSTypesForClass.clear()
        DRSTypesForIndividual.clear()
        dlGraphClass = None

    roles = ontology.getDLGraphRoles()
    print(roles)
    for role in roles:
        print(ontology.getDLGraphTriplesForRole(role))

    endSituationDescription()
    separator = ' .'
    # Add final " ." after joining all the others
    rdfLines = separator.join(totalRDFLines) + " ."
    print(rdfLines)
    # Send em
    onto.save(file="gap_res/OwlReadyKOIOS/owlready-uagent.owl")

    # BUBBLEGUM AND DUCT-TAPE HACK TO GET THIS WORKING WITH MULTIPLE SUBGRAPHS (thanks owlready) ********
    # read the owl file
    owl_file = open("gap_res/OwlReadyKOIOS/owlready-uagent.owl", "r+")
    owl_file_content = ""
    for line in owl_file:
        stripped_line = line.strip()
        fixed_line = stripped_line
        # Remove the subgraph silliness that occurs
        if " <http://www.uagent.com/ontology#instructionGraph>" in fixed_line:
            fixed_line = fixed_line.replace(" <http://www.uagent.com/ontology#instructionGraph>", "http://www.uagent.com/ontology#instructionGraph")
        if "> <http://www.uagent.com/ontology#dlGraph" in fixed_line:
            fixed_line = fixed_line.replace("> <http://www.uagent.com/ontology#dlGraph", "")
        if "> <http://www.uagent.com/ontology#" in fixed_line:
            fixed_line = fixed_line.replace("> <http://www.uagent.com/ontology#", "")
        owl_file_content += fixed_line + "\n"
    print(owl_file_content)
    write_file = open("gap_res/OwlReadyKOIOS/owlready-uagent.owl", "w+")
    write_file.write(owl_file_content)
    owl_file.close()

    # onto.save(file="owlready-uagent.owl")
    filename = 'owlready-uagent.owl'
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    subprocess.call(['lib/fuseki/s-update', '--service=http://localhost:3030/uagent-initialized/update', "LOAD <file://{}>".format(path)])
    # ['./s-update', '--service=http://localhost:3030/uagent-initialized/update', "LOAD <file://{}>".format(path)])


def beginExperiment():
    global currentExperiment
    with onto:
        newExperiment = onto[EXPERIMENT_NODE]()
        currentExperiment = newExperiment


def processDLGraphItem(individualName, className, DRSType):
    if DRSType == 'object':
        if className == 'task':
            DLGraphProcessTask(individualName)
        else:
            print("process item")
            DLGraphProcessItem(individualName, className)


    if DRSType == 'property':
        # Create a property
        pass

def DLGraphProcessTask(taskName):
    global currentTask
    global currentSituation
    global previousSituation
    global sitLevelInputLines

    # TODO: **** Should each task  start fresh with a new situation Description?
    # For now, doing that - clearing all prior information and starting anew
    endSituationDescription()
    currentSituation = None
    previousSituation = None
    situationItemsInRDF.clear()
    situationItemsDict.clear()
    situationRDFLines.clear()
    sitLevelInputLines.clear()
    startSituationDescription()

    # Create new task
    with onto:
        newTask = onto[TASK_NODE]()
        onto[HAS_NAME_EDGE][newTask].append(taskName)
        # newTask = [TASK_NODE]
        # Attach this task to the experiment if exists
        if currentExperiment is not None:
            onto[HAS_TASK_EDGE][currentExperiment].append(newTask)
        # If there is a prior experiment, that previous experiment informs this new one
        if currentTask is not None:
            onto[INFORMS_EDGE][currentTask].append(newTask)
    currentTask = newTask

    experimentItemsDict.update({taskName: newTask})

def DLGraphProcessItem(itemName, itemRole):
    # Create new item and item role
    with onto:
        newItem = onto[ITEM_NODE]()
        # If the item is named, add its name
        if itemName != "":
            onto[HAS_ITEM_NAME_EDGE][newItem].append(itemName)
            # Append to situation item tracker
            situationItemsDict.update({itemName: newItem})
        # Create the item role
        newItemRole = onto[ITEM_ROLE_NODE]()
        # Create the item role type
        newItemRoleType = onto[ITEM_ROLE_TYPE_NODE](itemRole)
        # Connect the item role type to the item role
        onto[OF_ITEM_ROLE_TYPE_EDGE][newItemRole].append(newItemRoleType)
        # Connect the role to the item
        onto[ASSUMED_BY_EDGE][newItemRole].append(newItem)
        # Append to situation item tracker - I THINK THIS IS RIGHT TODO ****
        situationItemsDict.update({itemRole: newItemRole})
        # If there is an affordance for this role, then create an affordance and link it to the item
        if affordanceDict.get(itemRole) is not None:
            newAffordance = onto[AFFORDANCE_NODE]()
            newAffordanceType = onto[AFFORDANCE_TYPE_NODE](affordanceDict.get(itemRole))
            onto[HAS_AFFORDANCE_TYPE_EDGE][newAffordance].append(newAffordanceType)
            onto[AFFORDS_EDGE][newItem].append(newAffordance)
            # Append to situation item tracker
            situationItemsDict.update({affordanceDict.get(itemRole): newAffordance})
        # Create Item Description with all of its offshoots
        newItemDescription = onto[ITEM_DESCRIPTION_NODE]()
        # TODO: **** Add values to these somehow?
        newItemLocation = onto[ITEM_LOCATION_NODE]()
        newItemColor = onto[ITEM_COLOR_NODE]()
        newItemShape = onto[ITEM_SHAPE_NODE]()
        newItemType = onto[ITEM_TYPE_NODE]()
        onto[REFERS_TO_ITEM_LOCATION_EDGE][newItemDescription].append(newItemLocation)
        onto[REFERS_TO_ITEM_COLOR_EDGE][newItemDescription].append(newItemColor)
        onto[REFERS_TO_ITEM_SHAPE_EDGE][newItemDescription].append(newItemShape)
        onto[REFERS_TO_ITEM_TYPE_EDGE][newItemDescription].append(newItemType)
        onto[OF_ITEM_EDGE][newItemDescription].append(newItem)

        # Attach item to Task
        # if currentTask is not None:
        #  currentTask.providesRole.append(newItemRole)
        print(list(newItem.get_properties()))
        print(list(newItem.get_inverse_properties()))

    # Add the tags that have to do with the situation to a tracker




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
        # rdfLines = processTask(inputContents)
        # processTask(inputContents)
        owlReadyProcessTask(inputContents)
        addDescriptionInstruction(inputLine)

    # handle item
    if inputType == 'item':
        if inputLine not in sitLevelInputLines:
            sitLevelInputLines.append(inputLine)
        # rdfLines = processItem(inputContents)
        # processItem(inputContents)
        owlReadyProcessItem(inputContents)
        addDescriptionInstruction(inputLine)

    # handle agent
    if inputType == 'agent':
        # rdfLines = processAgent(inputContents)
        owlReadyProcessAgent(inputContents)
        addDescriptionInstruction(inputLine)
        pass

    # handle isPartOf
    if inputType == 'isPartOf':
        if inputLine not in sitLevelInputLines:
            sitLevelInputLines.append(inputLine)
        # rdfLines = processIsPartOf(inputContents)
        # processIsPartOf(inputContents)
        owlReadyProcessIsPartOf(inputContents)
        addDescriptionInstruction(inputLine)

    if inputType == 'action':
        # rdfLines = processAction(inputContents)
        # processAction(inputContents)
        owlReadyProcessAction(inputContents)
        addActionInstruction(inputLine)

    # return rdfLines


def addActionInstruction(inputLine):
    with onto:
        # Create description instruction
        newInstruction = onto[ACTION_INSTRUCTION_NODE]()
        # Add the input line from the reasoner (I think this is right TODO ****)
        onto[AS_REASONER_FACT_STRING_EDGE][newInstruction].append(inputLine)
        # Connect instruction to situation
        onto[PRESCRIBES_EDGE][newInstruction].append(transitionToCurrentSituation)
        # Connect instruction to task
        onto[HAS_INSTRUCTION_EDGE][currentTask].append(newInstruction)


def addDescriptionInstruction(inputLine):
    with onto:
        # Create description instruction
        newInstruction = onto[DESCRIPTION_INSTRUCTION_NODE]()
        # Add the input line from the reasoner (I think this is right TODO ****)
        onto[AS_REASONER_FACT_STRING_EDGE][newInstruction].append(inputLine)
        # Connect instruction to situation
        onto[CONTRIBUTES_TO_EDGE][newInstruction].append(currentSituation)
        # Connect instruction to task
        onto[HAS_INSTRUCTION_EDGE][currentTask].append(newInstruction)


def owlReadyProcessTask(inputContents):
    global currentTask
    global currentSituation
    global previousSituation
    global sitLevelInputLines
    taskName = inputContents

    # TODO: **** Should each task  start fresh with a new situation Description?
    # For now, doing that - clearing all prior information and starting anew
    endSituationDescription()
    currentSituation = None
    previousSituation = None
    situationItemsInRDF.clear()
    situationItemsDict.clear()
    situationRDFLines.clear()
    sitLevelInputLines.clear()
    startSituationDescription()

    # Create new task
    with onto:
        newTask = onto[TASK_NODE]()
        onto[HAS_NAME_EDGE][newTask].append(taskName)
        # newTask = [TASK_NODE]
        # Attach this task to the experiment if exists
        if currentExperiment is not None:
            onto[HAS_TASK_EDGE][currentExperiment].append(newTask)
        # If there is a prior experiment, that previous experiment informs this new one
        if currentTask is not None:
            onto[INFORMS_EDGE][currentTask].append(newTask)
    currentTask = newTask

    experimentItemsDict.update({taskName: newTask})


def owlReadyProcessItem(inputContents):
    itemRole = ""
    itemName = ""
    # if no comma in the contents, no name, just role.
    # If comma, first entry is role, second is name
    if ',' not in inputContents:
        itemRole = inputContents
    else:
        itemRole = inputContents.split(',')[0]
        itemName = inputContents.split(',')[1]

    # Create new item and item role
    with onto:
        newItem = onto[ITEM_NODE]()
        # If the item is named, add its name
        if itemName != "":
            onto[HAS_ITEM_NAME_EDGE][newItem].append(itemName)
            # Append to situation item tracker
            situationItemsDict.update({itemName: newItem})
        # Create the item role
        newItemRole = onto[ITEM_ROLE_NODE]()
        # Create the item role type
        newItemRoleType = onto[ITEM_ROLE_TYPE_NODE](itemRole)
        # Connect the item role type to the item role
        onto[OF_ITEM_ROLE_TYPE_EDGE][newItemRole].append(newItemRoleType)
        # Connect the role to the item
        onto[ASSUMED_BY_EDGE][newItemRole].append(newItem)
        # Append to situation item tracker - I THINK THIS IS RIGHT TODO ****
        situationItemsDict.update({itemRole: newItemRole})
        # If there is an affordance for this role, then create an affordance and link it to the item
        if affordanceDict.get(itemRole) is not None:
            newAffordance = onto[AFFORDANCE_NODE]()
            newAffordanceType = onto[AFFORDANCE_TYPE_NODE](affordanceDict.get(itemRole))
            onto[HAS_AFFORDANCE_TYPE_EDGE][newAffordance].append(newAffordanceType)
            onto[AFFORDS_EDGE][newItem].append(newAffordance)
            # Append to situation item tracker
            situationItemsDict.update({affordanceDict.get(itemRole): newAffordance})
        # Create Item Description with all of its offshoots
        newItemDescription = onto[ITEM_DESCRIPTION_NODE]()
        # TODO: **** Add values to these somehow?
        newItemLocation = onto[ITEM_LOCATION_NODE]()
        newItemColor = onto[ITEM_COLOR_NODE]()
        newItemShape = onto[ITEM_SHAPE_NODE]()
        newItemType = onto[ITEM_TYPE_NODE]()
        onto[REFERS_TO_ITEM_LOCATION_EDGE][newItemDescription].append(newItemLocation)
        onto[REFERS_TO_ITEM_COLOR_EDGE][newItemDescription].append(newItemColor)
        onto[REFERS_TO_ITEM_SHAPE_EDGE][newItemDescription].append(newItemShape)
        onto[REFERS_TO_ITEM_TYPE_EDGE][newItemDescription].append(newItemType)
        onto[OF_ITEM_EDGE][newItemDescription].append(newItem)

        # Attach item to Task
        # if currentTask is not None:
        #  currentTask.providesRole.append(newItemRole)
        print(list(newItem.get_properties()))
        print(list(newItem.get_inverse_properties()))

    # Add the tags that have to do with the situation to a tracker


def owlReadyProcessAgent(inputContents):
    # return ""
    pass


def owlReadyProcessIsPartOf(inputContents):
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
    superIsA = superelement.is_a[0].name
    subIsA = subelement.is_a[0].name
    if ITEM_NODE in subIsA and TASK_NODE == superIsA:
        if ITEM_NODE == subIsA:
            # Make sure to use the ItemRole, not the Item
            # Get the list of incoming properties to the item
            for inverseProp in subelement.get_inverse_properties():
                source, value = inverseProp
                # Check if one of the incoming properties has the value "ofItem"
                if ASSUMED_BY_EDGE in value.name:
                    # If so, the source is the item role we want
                    subelement = source
            # If we've received an item role, then connect it to the current task
        if subelement is not None:
            onto[PROVIDES_ROLE_EDGE][superelement].append(subelement)


def owlReadyProcessAction(inputContents):
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

    # Initializing here to nothing so that if it doesn't get populated, things don't break
    actionRefersToRDFLine = ""
    # rdfLines = ""

    with onto:
        newAction = onto[ACTION_NODE]()
        # Assign the action type
        newActionType = onto[ACTION_TYPE_NODE](actionVerb)
        onto[OF_ACTION_TYPE_EDGE][newAction].append(newActionType)
        # Attach action to the item that triggered it
        if situationItemsDict.get(actionSubject) is None:
            print("Uh oh - it looks like an error occurred trying to process the action.  The term " + actionSubject + \
                  " was not found.  For debugging purposes, this happened in processAction - line 240.")
        else:
            # TODO **** I really need to figure out the dict thing - right now since the dict returns a role, just
            # subbing out the term "role" for "item" if it appears.
            actionTarget = situationItemsDict.get(actionSubject)
            actionTargetType = actionTarget.is_a[0].name
            if actionTargetType == ITEM_ROLE_NODE:
                # actionRefersToItem = re.sub("ItemRole", "Item", actionRefersToItem)
                actionTarget = actionTarget.assumedBy
            # TODO **** Is it correct to always grab the first?  What if there are multiple?
            onto[REFERS_TO_ITEM_SHAPE_EDGE][newAction].append(actionTarget[0])

        # Close up the pre-action situation description
        # rdfLines = rdfLines + endSituationDescription()
        endSituationDescription()

        # Next step is to create a new situation description.  Unsure exactly what carries over from one to the next but
        # for now just cloning the previous situation description and adding whatever the action consequence is.
        # TODO **** Figure out situation descriptions in more detail
        # rdfLines = rdfLines + startSituationDescription()
        startSituationDescription()

        # Create Transition Description and connect situation descriptions to it
        # rdfLines = rdfLines + createTransitionDescription()
        newTransition = createTransitionDescription()

        # Set action up to trigger transition
        onto[TRIGGERS_EDGE][newAction].append(newTransition)

    # Connect action to transition description (have to use current transition count - 1 because it was incremented
    # when the transition was created)
    # actionTriggersTransitionLine = actionCreator + " " + TRIGGERS_EDGE + " " + transitionCreator
    # rdfLines = rdfLines + actionTriggersTransitionLine
    # totalRDFLines.append(actionTriggersTransitionLine)

    # SOMEWHERE IN HERE WE SHOULD POPULATE THE NEW SITUATION - FOR NOW IT'S JUST BEING DONE BY DOUBLING UP THE
    # ITEMS ETC.
    # TODO *****

    # Handle the consequence
    # TODO **** THIS IS PROBABLY NOT THE IDEAL ROUTE
    # rdfLines = rdfLines + processInterpreterOutputLine(consequence)
    processInterpreterOutputLine(consequence)

    # return rdfLines


def createTransitionDescription():

    global transitionToCurrentSituation
    # rdfLines = ""

    # Create a transition and increment the number of transitions
    with onto:
        newTransition = onto[TRANSITION_DESCRIPTION_NODE]()
        if currentSituation is not None and previousSituation is not None:
            onto[HAS_PRE_SITUATION_DESCRIPTION_EDGE][newTransition].append(previousSituation)
            onto[HAS_POST_SITUATION_DESCRIPTION_EDGE][newTransition].append(currentSituation)

    transitionToCurrentSituation = newTransition
    return newTransition


def startSituationDescription():
    # If not 0, then from 0 to current - earlier condition, from current to max - current condition

    global currentSituation


    # Create a situation and DO NOT increment the number of situations - the increment will happen
    # at the end of the situation
    with onto:
        newSituation = onto[SITUATION_DESCRIPTION_NODE]()
        currentSituation = newSituation

        # Situations now refer to ItemDescriptions instead of directly to Items
        for createdNameOrRole in situationItemsDict:
            createdItemRoleOrAffordance = situationItemsDict.get(createdNameOrRole)
            createdIRAType = createdItemRoleOrAffordance.is_a[0].name
            if createdIRAType == AFFORDANCE_NODE:
                # Do nothing - we don't want to connect an affordance to the situation
                pass
            # If we have an item, just get the itemDescription it's connected to
            elif createdIRAType == ITEM_NODE:
                # Get the list of incoming properties to the item
                for inverseProp in createdItemRoleOrAffordance.get_inverse_properties():
                    source, value = inverseProp
                    # Check if one of the incoming properties has the value "ofItem"
                    if OF_ITEM_EDGE in value.name:
                        # If so, the source is the item description we want
                        relevantItemDescription = source
                # If we've received an item description, then connect it to the current situation as an earlierCondition
                if relevantItemDescription is not None:
                    onto[HAS_EARLIER_CONDITION_EDGE][newSituation].append(relevantItemDescription)
            # If we have an itemRole, grab the itemDescription of the item which the role is assumed by
            elif createdIRAType == ITEM_ROLE_NODE:
                # TODO **** Again, is grabbing the first one the best move?
                relevantItemDescription = None
                # Get the item which the role is assumed by
                relevantItem = createdItemRoleOrAffordance.assumedBy[0]
                # Get the list of incoming properties to the item
                for inverseProp in relevantItem.get_inverse_properties():
                    source, value = inverseProp
                    # Check if one of the incoming properties has the value "ofItem"
                    if OF_ITEM_EDGE in value.name:
                        # If so, the source is the item description we want
                        relevantItemDescription = source
                # If we've received an item description, then connect it to the current situation as an earlierCondition
                if relevantItemDescription is not None:
                    onto[HAS_EARLIER_CONDITION_EDGE][newSituation].append(relevantItemDescription)
            else:
                print("WARNING: Unexpected type in situationItemsDict.  Process can continue, but may crash later.")

    # Clear the previous situation's situation dictionary

    situationItemsInRDF.clear()
    situationItemsDict.clear()
    situationRDFLines.clear()

    for line in sitLevelInputLines:
        processInterpreterOutputLine(line)


def endSituationDescription():
    # If not 0, then from 0 to current - earlier condition, from current to max - current condition
    global previousSituation

    # Move situation RDF lines over into total RDF lines - anything happening in here will be experiment-level
    # or part of a new situation I THINK?
    # TODO *****

    # Create a situation

    if currentSituation is not None:
        with onto:
            # We use the current situation, as we are closing the current situation
            for createdNameOrRole in situationItemsDict:
                createdItemRoleOrAffordance = situationItemsDict.get(createdNameOrRole)
                createdIRAType = createdItemRoleOrAffordance.is_a[0].name
                if createdIRAType == AFFORDANCE_NODE:
                    # Do nothing - we don't want to connect an affordance to the situation
                    pass
                # If we have an item, just get the itemDescription it's connected to
                elif createdIRAType == ITEM_NODE:
                    # Get the list of incoming properties to the item
                    for inverseProp in createdItemRoleOrAffordance.get_inverse_properties():
                        source, value = inverseProp
                        # Check if one of the incoming properties has the value "ofItem"
                        if OF_ITEM_EDGE in value.name:
                            # If so, the source is the item description we want
                            relevantItemDescription = source
                    # If we've received an item description, then connect it to the current situation as an earlierCondition
                    if relevantItemDescription is not None:
                        onto[HAS_CURRENT_CONDITION_EDGE][currentSituation].append(relevantItemDescription)
                # If we have an itemRole, grab the itemDescription of the item which the role is assumed by
                elif createdIRAType == ITEM_ROLE_NODE:
                    # TODO **** Again, is grabbing the first one the best move?
                    relevantItemDescription = None
                    # Get the item which the role is assumed by
                    relevantItem = createdItemRoleOrAffordance.assumedBy[0]
                    # Get the list of incoming properties to the item
                    for inverseProp in relevantItem.get_inverse_properties():
                        source, value = inverseProp
                        # Check if one of the incoming properties has the value "ofItem"
                        if OF_ITEM_EDGE in value.name:
                            # If so, the source is the item description we want
                            relevantItemDescription = source
                    # If we've received an item description, then connect it to the current situation
                    # as an earlierCondition
                    if relevantItemDescription is not None:
                        onto[HAS_CURRENT_CONDITION_EDGE][currentSituation].append(relevantItemDescription)
                else:
                    print("WARNING: Unexpected type in situationItemsDict.  Process can continue, but may crash later.")

        # Add the current situation's items to the multi-situation backup dict and
        # NEED TO MAKE SURE ONLY TO CLEAR SITUATION ITEMS; there's definitely a problem with storing
        # the task etc. in here.
        multiSituationDict.update({currentSituation: situationItemsDict.copy()})

        # Make sure to store the current situation as being the previous situation so that transitions can occur easily
        previousSituation = currentSituation


initializeOntology()
