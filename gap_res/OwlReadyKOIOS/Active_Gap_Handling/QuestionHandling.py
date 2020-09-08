from owlready2 import *
from ontoConstants import *
from ontoUtilities import *

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
    print(results)
    # Check if there is a role type which matches the role provided
    for result in results:
        # If the name of the role type matches the role provided, add the item to which it's connected to the list
        # of potential candidates
        if result.name == itemRole:
            roles = getInstancesConnectedViaProperty(result, OF_ITEM_ROLE_TYPE_EDGE)
            # REMOVE THIS
            potentialCandidates.extend(roles)
            # Iterate through all roles received back
            # TODO: ACTUALLY GET THE ITEM TO RESPOND WITH
            #for role in roles:
            #    items = getInstancesConnectedViaProperty(role, ASSUMED_BY_EDGE)
            #    potentialCandidates.extend(items)

    # If a name was provided, try to narrow down based on name to get accurate answer


    # If no name is provided, then the list of role type matches
    if itemName == "":
        validCandidates = potentialCandidates
    return validCandidates
