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
    # TODO: Should there be a .strip () here?
    if ',' not in inputContents:
        itemRole = inputContents
    else:
        itemRole = inputContents.split(',')[0]
        itemName = inputContents.split(',')[1]

    # If the role slot has a question mark in it, the user is querying for the roles of items with the provided name
    if '?' in itemRole:
        response = itemRoleTypeQuestion(onto, itemName)

    # If the name slot has a question mark in it, the user is querying for the names of items with the provided role
    elif '?' in itemName:
        response = itemNameQuestion(onto, itemRole)

    # If neither slot has a question mark in it, the user is querying for the existence of items with the provided name
    # and/or role
    else:
        # If no item name is provided, just search for existence of items with the name:
        if itemName == "":
            response = itemExistenceQuestion(onto, itemRole)

        # If no item role is provided, just search for the existence of items with name
        if itemRole == "":
            response = itemExistenceQuestion(onto, itemRole, itemName)

        # If both item role and item name are provided, search for the existence of item with this role and name
        if itemRole != "" and itemName != "":
            response = itemExistenceQuestion(onto, itemRole, itemName)

        # Error-proofing in case someone enters item() or item(,)
        if itemRole == "" and itemName == "":
            response = ""

    # Output the results of the query
    outputItemQuestionResults(response, inputContents, itemRole, itemName)


# TODO: What about searching JUST by name, not by role or role + name
# If no item name provided, default to ""
def itemExistenceQuestion(onto, itemRole, itemName=""):
    validCandidates = []

    # If an item role is provided, search by role and validate each item's name if a name was provided
    if itemRole != "":
        # Get the list of items which have the role type itemRole
        potentialCandidates = getItemsOfRoleType(onto, itemRole)

        # If a name was provided, try to narrow down based on name to get accurate answer
        if itemName != "":
            # Get the name of each potential candidate and validate it against the requested item's name.
            for candidate in potentialCandidates:
                candidateName = getNameOfItem(onto, candidate)
                # Compare candidate name to requested name
                if candidateName == itemName:
                    validCandidates.append(candidate)

        # If no name is provided, then the list of role type matches
        else:
            validCandidates = potentialCandidates

    # If no item role is provided, then search to find all items with the given name - no role validation, naturally
    else:
        validCandidates = getItemsWithName(onto, itemName)

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



def outputItemQuestionResults(response, inputContents, itemRole, itemName):
    if response == None or response == '' or response == []:
        if CONTROL_IDENTIFY_LEXICAL == True:
            print("Potential lexical gap identified: The ontology could not return information regarding item("
                  + inputContents + ")")
    else:
        if itemRole == "":
            print("One or more items with name " + itemName + " exist - they are : " + str(response))

        if itemName == "":
            print("One or more items with role " + itemRole + " exist - they are : " + str(response))

        if '?' in itemRole:
            print("One or more items with name " + itemName + " exist - their roles are : " + str(response))

        if '?' in itemName:
            print("One or more items with role " + itemRole + " exist - their names are : " + str(response))

        if itemRole != "" and itemName != "" and '?' not in itemRole and '?' not in itemName:
            print("One or more items with role " + itemRole + " and name " + itemName + " exist - they are : "
                  + str(response))