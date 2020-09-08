from owlready2 import *

# NEEDS DEBUGGING
def getInstancesConnectedViaProperty(currentInstance, property):
    validProperties = []
    instancesConnected = []
    properties = currentInstance.get_properties()
    inverseProperties = currentInstance.get_inverse_properties()
    allProperties = list(properties) + list(inverseProperties)
    # Iterate through the selected instance's properties
    for prop in allProperties:
        # Get the value of the  property element
        for propValue in prop:
            # Make sure to look at the edge on the property to make sure we have the right property
            if type(propValue) == ObjectPropertyClass or isinstance(type(propValue), ObjectPropertyClass):
                # If one is found which matches the desired property
                if propValue.name == property:
                    # Then add the property to the list of valid properties
                        validProperties.append(prop)

    # Iterate through all valid properties and append the target node to the list of instances connected
    for property in validProperties:
        # Get the value of the property element
        for propertyValue in property:
            # Make sure to look at the node in the property and not the edge
            if isinstance(type(propertyValue), ThingClass):
                # Append the node at the end of the property to the list
                instancesConnected.append(propertyValue)
    return instancesConnected