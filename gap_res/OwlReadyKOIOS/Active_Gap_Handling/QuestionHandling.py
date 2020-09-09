from owlready2 import *
from ontoConstants import *
from Active_Gap_Handling.ontoUtilities import *

def itemExistenceQuestion(onto, inputContents):
    itemRole = ""
    itemName = ""
    # if no comma in the contents, no name, just role.
    # If comma, first entry is role, second is name
    if ',' not in inputContents:
        itemRole = inputContents
    else:
        itemRole = inputContents.split(',')[0]
        itemName = inputContents.split(',')[1]

    potentialCandidates = []
    validCandidates = []

    # Get list of role type
    results = onto.search(is_a = onto[ITEM_ROLE_TYPE_NODE])
    # Check if there is a role type which matches the role provided
    for result in results:
        # If the name of the role type matches the role provided, add the item to which it's connected to the list
        # of potential candidates
        if result.name == itemRole:
            roles = getInstancesConnectedViaProperty(onto, result, OF_ITEM_ROLE_TYPE_EDGE)
            # REMOVE THIS
            #potentialCandidates.extend(roles)
            # Iterate through all roles received back
            # TODO: ACTUALLY GET THE ITEM TO RESPOND WITH
            for role in roles:
                items = getInstancesConnectedViaProperty(onto, role, ASSUMED_BY_EDGE)
                potentialCandidates.extend(items)

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
