from owlready2 import *
from ontoConstants import *
from Active_Gap_Handling.ontoUtilities import *
from ControlPanel import *

def itemQuestion(onto, inputContents):
    itemRole = ""
    itemName = ""
    response = ""

    # if no comma in the contents, no name, just role.
    # If comma, first entry is role, second is name
    if ',' not in inputContents:
        itemRole = inputContents
    else:
        itemRole = inputContents.split(',')[0]
        itemName = inputContents.split(',')[1]

    # If the role slot has a question mark in it, the user is querying for the roles of items with the provided name
    if '?' in itemRole:
        response = itemRoleTypeQuestion(onto, itemName)

        if response == None or response == '' or response == []:
            if CONTROL_IDENTIFY_LEXICAL == True:
                print("Potential lexical gap identified: The ontology could not return information regarding item "
                         + inputContents)
        else:
            print("One or more items with name " + itemName + " exist - their roles are : " + str(response))

    # If the name slot has a question mark in it, the user is querying for the names of items with the provided role
    elif '?' in itemName:
        response = itemNameQuestion(onto, itemRole)

        if response == None or response == '' or response == []:
            if CONTROL_IDENTIFY_LEXICAL == True:
                print("Potential lexical gap identified: The ontology could not return information regarding item "
                         + inputContents)
        else:
            print("One or more items with role " + itemRole + " exist - their names are : " + str(response))

    # If neither slot has a question mark in it, the user is querying for the existence of items with the provided name
    # and/or role
    else:
        response = itemExistenceQuestion(onto, itemRole, itemName)

        if response == None or response == '' or response == []:
            if CONTROL_IDENTIFY_LEXICAL == True:
                print("Potential lexical gap identified: The ontology could not return information regarding item "
                         + inputContents)
        else:
            print("One or more items with this role/name exist - they are : " + str(response))

# TODO: What about searching JUST by name, not by role or role + name
# If no item name provided, default to ""
def itemExistenceQuestion(onto, itemRole, itemName=""):
    validCandidates = []

    # Get the list of items which have the role type itemRole
    potentialCandidates = getItemsOfRoleType(onto, itemRole)

    # If a name was provided, try to narrow down based on name to get accurate answer
    if itemName != "":
        # Get the name of each potential candidate and validate it against the requested item's name.
        for candidate in potentialCandidates:
            # Returns a list but we SHOULD be able to just pop the first item out of the list.
            # TODO: Presumably an item can't have multiple names?
            candidateNameList = getInstancesConnectedViaProperty(onto, candidate, HAS_ITEM_NAME_EDGE)
            # Get the candidate's name
            if len(candidateNameList) > 0:
                candidateName = candidateNameList[0]
            else:
                candidateName = ""
            # Compare candidate name to requested name
            if candidateName == itemName:
                validCandidates.append(candidate)


    # If no name is provided, then the list of role type matches
    else:
        validCandidates = potentialCandidates
    return validCandidates

def itemRoleTypeQuestion(onto, itemName):
    rolesOfItemsWithName = []

    itemsWithSelectedName = getItemsWithName(onto, itemName)

    # Get the role of each item and add it to the list
    for itemTuple in itemsWithSelectedName:
        item = itemTuple[0]
        name = itemTuple[1]
        # Just as confirmation that no incorrectly named items slip through the cracks
        if name == itemName:
            itemRole = getRoleOfItem(onto, item)
            # Append role of item to item list
            rolesOfItemsWithName.append((item, itemRole))
    # Return list of items with their role
    return rolesOfItemsWithName

def itemNameQuestion(onto, itemRole):
    namesOfItemsWithRole = []

    # Get the list of items which have the role type itemRole
    itemsWithSelectedRole =  getItemsOfRoleType(onto, itemRole)

    # Get the name of each item and add it to the list
    for item in itemsWithSelectedRole:
        itemName = getNameOfItem(onto, item)
        # Append name of item to item list
        namesOfItemsWithRole.append((item, itemName))
    # Return list of items with their name
    return namesOfItemsWithRole
