from owlready2 import *

def getInstancesConnectedViaProperty(onto, currentInstance, property):
    validProperties = []
    validInverseProperties = []
    instancesConnected = []
    properties = currentInstance.get_properties()
    inverseProperties = currentInstance.get_inverse_properties()
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