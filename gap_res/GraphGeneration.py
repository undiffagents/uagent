import networkx
from Constants import *


# Create Graph
def generateItemGraph(graphNumber):
    itemGraph = networkx.MultiDiGraph()
    itemGraph.add_node(CONST_ITEM_NODE + str(graphNumber), value='')
    itemGraph.add_node(CONST_ITEM_NAME_NODE + str(graphNumber), value='')
    itemGraph.add_node(CONST_ITEM_AFFORDANCE_NODE + str(graphNumber), value='')
    itemGraph.add_node(CONST_ITEM_DESCRIPTION_NODE + str(graphNumber), value='')
    itemGraph.add_node(CONST_ITEM_ROLE_NODE + str(graphNumber), value='')

    itemGraph.add_edge(CONST_ITEM_NODE + str(graphNumber), CONST_ITEM_NAME_NODE + str(graphNumber),
                       value=CONST_ITEM_HAS_NAME_EDGE)
    itemGraph.add_edge(CONST_ITEM_NODE + str(graphNumber), CONST_ITEM_AFFORDANCE_NODE + str(graphNumber),
                       value=CONST_ITEM_HAS_AFFORDANCE_EDGE)
    itemGraph.add_edge(CONST_ITEM_NODE + str(graphNumber), CONST_ITEM_DESCRIPTION_NODE + str(graphNumber),
                       value=CONST_ITEM_HAS_DESCRIPTION_EDGE)
    itemGraph.add_edge(CONST_ITEM_NODE + str(graphNumber), CONST_ITEM_ROLE_NODE + str(graphNumber),
                       value=CONST_ITEM_HAS_ROLE_EDGE)

    return itemGraph


def generatePropGraph(graphNumber):
    propGraph = networkx.MultiDiGraph()
    propGraph.add_node(CONST_PROP_NODE + str(graphNumber), value='')
    propGraph.add_node(CONST_PROP_ADJECTIVE_NODE + str(graphNumber), value='')
    propGraph.add_node(CONST_PROP_SEC_OBJECT_NODE + str(graphNumber), value='')
    propGraph.add_node(CONST_PROP_TERT_OBJECT_NODE + str(graphNumber), value='')
    propGraph.add_node(CONST_PROP_DEG_NODE + str(graphNumber), value='')
    propGraph.add_node(CONST_PROP_COMP_TARGET_NODE + str(graphNumber), value='')

    propGraph.add_edge(CONST_PROP_NODE + str(graphNumber), CONST_PROP_ADJECTIVE_NODE + str(graphNumber),
                       value=CONST_PROP_HAS_ADJECTIVE_EDGE)
    propGraph.add_edge(CONST_PROP_NODE + str(graphNumber), CONST_PROP_SEC_OBJECT_NODE + str(graphNumber),
                       value=CONST_PROP_HAS_SEC_OBJECT_EDGE)
    propGraph.add_edge(CONST_PROP_NODE + str(graphNumber), CONST_PROP_TERT_OBJECT_NODE + str(graphNumber),
                       value=CONST_PROP_HAS_TERT_OBJECT_EDGE)
    propGraph.add_edge(CONST_PROP_NODE + str(graphNumber), CONST_PROP_DEG_NODE + str(graphNumber),
                       value=CONST_PROP_HAS_DEG_EDGE)
    propGraph.add_edge(CONST_PROP_NODE + str(graphNumber), CONST_PROP_COMP_TARGET_NODE + str(graphNumber),
                       value=CONST_PROP_HAS_COMP_TARGET_EDGE)

    return propGraph


def generateActionGraph(graphNumber):
    actionGraph = networkx.MultiDiGraph()
    actionGraph.add_node(CONST_ACTION_NODE + str(graphNumber), value='')
    actionGraph.add_node(CONST_ACTION_VERB_NODE + str(graphNumber), value='')

    actionGraph.add_edge(CONST_ACTION_NODE + str(graphNumber), CONST_ACTION_VERB_NODE + str(graphNumber),
                         value=CONST_ACTION_HAS_VERB_EDGE)

    return actionGraph


def generateModPPGraph(graphNumber):
    modPPGraph = networkx.MultiDiGraph()
    modPPGraph.add_node(CONST_MODPP_NODE + str(graphNumber), value='')
    modPPGraph.add_node(CONST_MODPP_PREP_NODE + str(graphNumber), value='')

    modPPGraph.add_edge(CONST_MODPP_NODE + str(graphNumber), CONST_MODPP_PREP_NODE + str(graphNumber),
                        value=CONST_MODPP_HAS_PREP_EDGE)

    return modPPGraph


class ItemGraph(object):
    # Constructor
    def __init__(self, graphNumber):
        self.graphNumber = graphNumber
        if graphNumber is not None:
            self.graph = generateItemGraph(self.graphNumber)
        else:
            self.graph = None

    # Generic append method based on whatever target is passed in
    def __append(self, target, newValue):
        currentValue = self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY]
        if currentValue == '':
            updatedValue = newValue
        else:
            updatedValue = currentValue + '|' + newValue
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = updatedValue

    # Generic replace method based on whatever target is passed in
    def __replace(self, target, newValue):
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = newValue

    # Append/replace methods for each node value in Item Graph
    def appendItemValue(self, newValue):
        self.__append(CONST_ITEM_NODE, newValue)

    def replaceItemValue(self, newValue):
        self.__replace(CONST_ITEM_NODE, newValue)

    def appendItemName(self, newName):
        self.__append(CONST_ITEM_NAME_NODE, newName)

    def replaceItemName(self, newName):
        self.__replace(CONST_ITEM_NAME_NODE, newName)

    def appendItemAffordance(self, newAffordance):
        self.__append(CONST_ITEM_AFFORDANCE_NODE, newAffordance)

    def replaceItemAffordance(self, newAffordance):
        self.__replace(CONST_ITEM_AFFORDANCE_NODE, newAffordance)

    def appendItemDescription(self, newDescription):
        self.__append(CONST_ITEM_DESCRIPTION_NODE, newDescription)

    def replaceItemDescription(self, newDescription):
        self.__replace(CONST_ITEM_DESCRIPTION_NODE, newDescription)

    def appendItemRole(self, newRole):
        self.__append(CONST_ITEM_ROLE_NODE, newRole)

    def replaceItemRole(self, newRole):
        self.__replace(CONST_ITEM_ROLE_NODE, newRole)

    # Method to find a node containing a given value
    def FindItemWithValue(self, valueToFind):
        if self.graph is not None:
            # iterate through all graph nodes
            for node, values in self.graph.nodes.data():
                # print(node, values)
                # If the current Node's value = the value passed in
                if values[CONST_NODE_VALUE_KEY] == valueToFind:
                    return node
        return None

    # Methods to add different types of edges between nodes
    def addGroupMembershipEdges(self, groupNode, memberNode):
        self.graph.add_edge(memberNode, groupNode, value=CONST_IS_MEMBER_EDGE)
        self.graph.add_edge(groupNode, memberNode, value=CONST_HAS_MEMBER_EDGE)

    def addNodeEquivalencyEdges(self, firstNode, secondNode):
        self.graph.add_edge(firstNode, secondNode, value=CONST_IS_EQUIVALENT_EDGE)
        self.graph.add_edge(secondNode, firstNode, value=CONST_IS_EQUIVALENT_EDGE)

    def addCompositionEdges(self, composedNode, partOfNode):
        self.graph.add_edge(composedNode, partOfNode, value=CONST_HAS_A_EDGE)
        self.graph.add_edge(partOfNode, composedNode, value=CONST_IS_PART_OF_EDGE)

    def addPropertyEdge(self, objectNode, propertyNode):
        self.graph.add_edge(objectNode, propertyNode, value=CONST_IS_EDGE)

    # Methods to add different types of edges between nodes
    def addActionPerformerEdges(self, performerNode, actionNode):
        self.graph.add_edge(performerNode, actionNode, value=CONST_PERFORMS_EDGE)
        self.graph.add_edge(actionNode, performerNode, value=CONST_IS_PERFORMED_EDGE)

    def addActionTargetEdges(self, actionNode, targetNode):
        self.graph.add_edge(actionNode, targetNode, value=CONST_HAS_TARGET_EDGE)
        self.graph.add_edge(targetNode, actionNode, value=CONST_IS_TARGET_EDGE)

    def addModifierVerbEdges(self, modifierNode, verbNode):
        self.graph.add_edge(modifierNode, verbNode, value=CONST_MODIFIES_VERB_EDGE)
        self.graph.add_edge(verbNode, modifierNode, value=CONST_IS_MODIFIED_EDGE)

    def addModifierObjectEdges(self, modifierNode, objectNode):
        self.graph.add_edge(modifierNode, objectNode, value=CONST_MODIFIES_OBJECT_EDGE)
        self.graph.add_edge(objectNode, modifierNode, value=CONST_IS_MODIFIED_EDGE)

    def addConditionalTriggerEdges(self, ifNodeValue, thenNodeValue):
        ifNode = self.FindItemWithValue(ifNodeValue)
        thenNode = self.FindItemWithValue(thenNodeValue)
        # We only want to trigger actions, not statement
        if ifNode is not None and thenNode is not None:
            if CONST_ACTION_NODE in thenNode:
                self.graph.add_edge(ifNode, thenNode, value=CONST_TRIGGERS_EDGE)
                self.graph.add_edge(thenNode, ifNode, value=CONST_TRIGGERED_BY_EDGE)

    # Methods to replace values of specific nodes
    def ReplaceItemAffordanceAtSpecificNode(self, nodeToAddAffordance, newAffordance):
        node = self.FindItemWithValue(nodeToAddAffordance)
        if node is not None:
            edgesFromNode = self.graph.edges(node, data=True)
            for startNode, endNode, edgeValues in edgesFromNode:
                # If an edge has the value ItemHasName, then we want to modify the end node
                if edgeValues[CONST_NODE_VALUE_KEY] == CONST_ITEM_HAS_AFFORDANCE_EDGE:
                    # Update graph with name
                    self.graph.nodes(data=True)[endNode][CONST_NODE_VALUE_KEY] = newAffordance
                    return True
        else:
            print("No node with direct object reference as value found")
            return False

    # Methods to replace values of specific nodes
    def AppendItemAffordanceAtSpecificNode(self, nodeToAddAffordance, newAffordance):
        node = self.FindItemWithValue(nodeToAddAffordance)
        if node is not None:
            edgesFromNode = self.graph.edges(node, data=True)
            for startNode, endNode, edgeValues in edgesFromNode:
                # If an edge has the value ItemHasName, then we want to modify the end node
                if edgeValues[CONST_NODE_VALUE_KEY] == CONST_ITEM_HAS_AFFORDANCE_EDGE:
                    # Update graph with name
                    currentValue = self.graph.nodes(data=True)[endNode][CONST_NODE_VALUE_KEY]
                    if currentValue == '':
                        updatedValue = newAffordance
                    else:
                        updatedValue = currentValue + '|' + newAffordance
                    self.graph.nodes(data=True)[endNode][CONST_NODE_VALUE_KEY] = updatedValue
                    return True
        else:
            print("No node with direct object reference as value found")
            return False

    # Methods to replace values of specific nodes
    def AppendValueAtSpecificNode(self, nodeToAddValue, newValue):
        # Update graph with name
        currentValue = self.graph.nodes(data=True)[nodeToAddValue][CONST_NODE_VALUE_KEY]
        if currentValue == '':
            updatedValue = newValue
        else:
            updatedValue = currentValue + '|' + newValue
        self.graph.nodes(data=True)[nodeToAddValue][CONST_NODE_VALUE_KEY] = updatedValue
        return True

    def ReplaceItemNameAtSpecificNode(self, nodeToAddName, newName):
        # Find Node
        node = self.FindItemWithValue(nodeToAddName)
        if node is not None:
            # Get list of edges from the node
            edgesFromNode = self.graph.edges(node, data=True)
            for startNode, endNode, edgeValues in edgesFromNode:
                # If an edge has the value ItemHasName, then we want to modify the end node
                if edgeValues[CONST_NODE_VALUE_KEY] == CONST_ITEM_HAS_NAME_EDGE:
                    # Update graph with name
                    self.graph.nodes(data=True)[endNode][CONST_NODE_VALUE_KEY] = newName
                    return True
        else:
            print("No node with direct object reference as value found")
            return False


class PropertyGraph(object):
    # Constructor
    def __init__(self, graphNumber):
        self.graphNumber = graphNumber
        if graphNumber is not None:
            self.graph = generatePropGraph(self.graphNumber)
        else:
            self.graph = None

    # Generic append method based on whatever target is passed in
    def __append(self, target, newValue):
        currentValue = self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY]
        if currentValue == '':
            updatedValue = newValue
        else:
            updatedValue = currentValue + '|' + newValue
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = updatedValue

    # Generic replace method based on whatever target is passed in
    def __replace(self, target, newValue):
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = newValue

    # Append/replace methods for each node value in Property Graph
    def appendPropValue(self, newValue):
        self.__append(CONST_PROP_NODE, newValue)

    def replacePropValue(self, newValue):
        self.__replace(CONST_PROP_NODE, newValue)

    def appendPropAdj(self, newAdjective):
        self.__append(CONST_PROP_ADJECTIVE_NODE, newAdjective)

    def replacePropAdj(self, newAdjective):
        self.__replace(CONST_PROP_ADJECTIVE_NODE, newAdjective)

    def appendPropSecObj(self, newSecondaryObject):
        self.__append(CONST_PROP_SEC_OBJECT_NODE, newSecondaryObject)

    def replacePropSecObj(self, newSecondaryObject):
        self.__replace(CONST_PROP_SEC_OBJECT_NODE, newSecondaryObject)

    def appendPropTertObj(self, newTertiaryObject):
        self.__append(CONST_PROP_TERT_OBJECT_NODE, newTertiaryObject)

    def replacePropTertObj(self, newTertiaryObject):
        self.__replace(CONST_PROP_TERT_OBJECT_NODE, newTertiaryObject)

    def appendPropDegree(self, newDegree):
        self.__append(CONST_PROP_DEG_NODE, newDegree)

    def replacePropDegree(self, newDegree):
        self.__replace(CONST_PROP_DEG_NODE, newDegree)

    def appendPropCompTarget(self, newCompTarget):
        self.__append(CONST_PROP_COMP_TARGET_NODE, newCompTarget)

    def replacePropCompTarget(self, newCompTarget):
        self.__replace(CONST_PROP_COMP_TARGET_NODE, newCompTarget)

    # Method to find a node containing a given value
    def FindPropertyWithValue(self, valueToFind):
        if self.graph is not None:
            # iterate through all graph nodes
            for node, values in self.graph.nodes.data():
                # If the current Node's value = the value passed in
                if values[CONST_NODE_VALUE_KEY] == valueToFind:
                    return node
        return None


class ActionGraph(object):
    # Constructor
    def __init__(self, graphNumber):
        self.graphNumber = graphNumber
        if graphNumber is not None:
            self.graph = generateActionGraph(self.graphNumber)
        else:
            self.graph = None

    # Generic append method based on whatever target is passed in
    def __append(self, target, newValue):
        currentValue = self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY]
        if currentValue == '':
            updatedValue = newValue
        else:
            updatedValue = currentValue + '|' + newValue
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = updatedValue

    # Generic replace method based on whatever target is passed in
    def __replace(self, target, newValue):
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = newValue

    # Append/replace methods for each node value in Property Graph
    def appendActionValue(self, newValue):
        self.__append(CONST_ACTION_NODE, newValue)

    def replaceActionValue(self, newValue):
        self.__replace(CONST_ACTION_NODE, newValue)

    def appendActionVerb(self, newVerb):
        self.__append(CONST_ACTION_VERB_NODE, newVerb)

    def replaceActionVerb(self, newVerb):
        self.__replace(CONST_ACTION_VERB_NODE, newVerb)

    # Method to find a node containing a given value
    def FindActionWithValue(self, valueToFind):
        if self.graph is not None:
            # iterate through all graph nodes
            for node, values in self.graph.nodes.data():
                # If the current Node's value = the value passed in
                if values[CONST_NODE_VALUE_KEY] == valueToFind:
                    return node
        return None


# Modifier_PP (adv will need a different graph)
class ModifierPPGraph(object):
    # Constructor
    def __init__(self, graphNumber):
        self.graphNumber = graphNumber
        if graphNumber is not None:
            self.graph = generateModPPGraph(self.graphNumber)
        else:
            self.graph = None

    # Generic append method based on whatever target is passed in
    def __append(self, target, newValue):
        currentValue = self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY]
        if currentValue == '':
            updatedValue = newValue
        else:
            updatedValue = currentValue + '|' + newValue
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = updatedValue

    # Generic replace method based on whatever target is passed in
    def __replace(self, target, newValue):
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = newValue

    # Append/replace methods for each node value in Property Graph
    def appendModPPValue(self, newValue):
        self.__append(CONST_MODPP_NODE, newValue)

    def replaceModPPValue(self, newValue):
        self.__replace(CONST_MODPP_NODE, newValue)

    def appendModPPPrep(self, newPreposition):
        self.__append(CONST_MODPP_PREP_NODE, newPreposition)

    def replaceModPPPrep(self, newPreposition):
        self.__replace(CONST_MODPP_PREP_NODE, newPreposition)

    # Method to find a node containing a given value
    def FindModWithValue(self, valueToFind):
        if self.graph is not None:
            # iterate through all graph nodes
            for node, values in self.graph.nodes.data():
                # If the current Node's value = the value passed in
                if values[CONST_NODE_VALUE_KEY] == valueToFind:
                    return node
        return None

