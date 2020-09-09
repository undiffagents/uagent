from owlready2 import *
from ontoConstants import *

# Get a list of individuals connected to the selected instance via some specific property
def getInstancesConnectedViaProperty(onto, currentInstance, property):
    validInverseProperties = []
    instancesConnected = []
    properties = list(currentInstance.get_properties())
    inverseProperties = list(currentInstance.get_inverse_properties())
    if (properties + inverseProperties) == 0:
        print("Potential context gap: It appears that " + str(currentInstance) + " has no properties attached to it!")
    # Iterate through the selected instance's properties
    # TODO: Confirm that this works with multiple targets which all have the same edge type
    # I THINK this should work - gets the target at the end of the property.
    if len(onto[property][currentInstance]) > 0:
        instancesConnected.extend(onto[property][currentInstance])
    # for prop in properties:
        # No need to check if this is a property - unlike inverse properties, this only gives a list of the edges
        #if prop.name == property:
            #test = onto[property][currentInstance]
            #print(test)
            #validProperties.append(prop)

    # Iterate through the selected instance's inverse properties (don't think there's as neat a way as for props)
    for invProp in inverseProperties:
        # Get the value of the property tuple elements
        subject = invProp[0]
        propEdge = invProp[1]
        # If the property is one which matches the desired property
        if propEdge.name == property:
            # Then add the subject to the list of connected instances
                instancesConnected.append(subject)

    # Iterate through all valid inverse properties and append the target node to the list of instances connected
    for property in validInverseProperties:
        # Get the value of the property element
        for propertyValue in property:
            # Make sure to look at the node in the property and not the edge
            if isinstance(type(propertyValue), ThingClass):
                # Append the node at the end of the property to the list
                instancesConnected.append(propertyValue)
    return instancesConnected


# Get the list of items which have assume a role of type itemRole
def getItemsOfRoleType(onto, itemRole):
    itemsAssumingSelectedRoleType = []

    # Get list of role type
    results = onto.search(type=onto[ITEM_ROLE_TYPE_NODE])
    # Check if there is a role type which matches the role provided
    for result in results:
        # If the name of the role type matches the role provided, add the item to which it's connected to the list
        # of potential candidates
        if result.name == itemRole:
            roles = getInstancesConnectedViaProperty(onto, result, OF_ITEM_ROLE_TYPE_EDGE)
            # Iterate through all roles received back
            for role in roles:
                items = getInstancesConnectedViaProperty(onto, role, ASSUMED_BY_EDGE)
                itemsAssumingSelectedRoleType.extend(items)

    return itemsAssumingSelectedRoleType


# Get the list of items which have the selected name
def getItemsWithName(onto, itemName):
    itemsWithSelectedName = []

    # Get list of Item individuals
    results = onto.search(type=onto[ITEM_NODE])
    # Check each Item to see if its name matches the expected name
    for result in results:
        # Make sure this is an instance and not a class
        foundName = getNameOfItem(onto, result)
        if foundName == itemName:
            # Append name of item to item list if matches
            itemsWithSelectedName.append((result, foundName))
    # Return the list of items with the given name
    return itemsWithSelectedName


# Get the name of an item
def getNameOfItem(onto, item):
    # Returns a list but we SHOULD be able to just pop the first item out of the list.
    # TODO: Presumably an item can't have multiple names?
    itemNameList = getInstancesConnectedViaProperty(onto, item, HAS_ITEM_NAME_EDGE)
    # Get the candidate's name
    if len(itemNameList) > 0:
        itemName = itemNameList[0]
    else:
        itemName = ""
    # Return the name of the item
    return itemName


# Get the role of an item
def getRoleOfItem(onto, item):
    # Presumably should only have one role assigned to it?  To check
    # TODO: Can an item have more than one role?
    itemRoleList = getInstancesConnectedViaProperty(onto, item, ASSUMED_BY_EDGE)
    # Get the role of the item
    if len(itemRoleList) > 0:
        itemRole = itemRoleList[0]
    else:
        itemRole = None
    # Now get the name of the item's role
    if itemRole is not None:
        itemRoleTypeList = getInstancesConnectedViaProperty(onto, itemRole, OF_ITEM_ROLE_TYPE_EDGE)
        # Presumably only one roleType per role
        # TODO: Can a role have more than one role type?
        if len(itemRoleTypeList) > 0:
            itemRoleType = itemRoleTypeList[0]
        else:
            itemRoleType = ""
    else:
        itemRoleType = ""
    return itemRoleType
