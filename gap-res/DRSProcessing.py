from nltk.corpus import wordnet
import requests
import json

from GraphGeneration import *
from ConditionalHandling import *
from LineCategorization import *
from Constants import *
from ControlPanel import *


class predicateSwitcher(object):

    def __init__(self):
        self.graphNumber = 0
        self.DRSGraph = ItemGraph(None)

    # Method to call the appropriate function based on the argument passed in
    def callFunction(self, predicateType, predicateContents):
        # Get the name of the method
        methodName = 'predicate_' + str(predicateType)
        # Get the method itself
        method = getattr(self, methodName, lambda: "Unknown predicate")
        # Call the method and return its output
        method(predicateContents)
        return self.DRSGraph

    def updateDRSGraph(self, newDRSGraph):
        self.DRSGraph = newDRSGraph

    # For object() predicates SHOULD CHECK IF OBJECT WITH GIVEN NAME ALREADY EXISTS!!!  IF SO, FIGURE OUT WHAT ARE
    # THE CONDITIONS FOR THAT TO OCCUR
    def predicate_object(self, predicateContents):
        # Break up elements of object line into variables
        predicateComponents = predicateContents.split(',')
        objReferenceVariable = predicateComponents[0]
        objName = predicateComponents[1]
        # FOLLOWING ONES PROBABLY UNUSED BUT LEAVING COMMENTED OUT SO I HAVE ACCESS EASILY
        # objClass = predicateComponents[2]
        # objUnit = predicateComponents[3]
        # objOperator = predicateComponents[4]
        # objCount = predicateComponents[5].split(')')[0]
        if self.DRSGraph.FindItemWithValue(objReferenceVariable) is None:
            # Apply appropriate variables to ItemGraph
            objectGraph = ItemGraph(self.graphNumber)
            objectGraph.appendItemValue(objReferenceVariable)
            objectGraph.appendItemRole(objName)
            # Increase the graph number for auto-generation of names
            self.graphNumber = self.graphNumber + 1
            # If a main graph already exists, then add the new graph in to it
            if self.DRSGraph.graph is not None:
                self.DRSGraph.graph = networkx.algorithms.operators.binary.compose(self.DRSGraph.graph,
                                                                                   objectGraph.graph)
            # if no main graph exists, this is the main graph
            else:
                self.DRSGraph.graph = objectGraph.graph
            return True
        else:
            return False

    # For predicate() predicates
    # HOW TO HANDLE SENTENCE SUB-ORDINATION?
    def predicate_predicate(self, predicateContents):
        # Intransitive verbs: (predName, verb, subjectRef)
        # - The SubjectRef Verbed (the man laughed, the target appears)
        # Transitive verbs: (predName, verb, subjectRef, dirObjRef)
        # - The Subjectref Verbed the dirObjRef (the task A has a group of objects H,
        # the subject L remembers the letter I)
        # Ditransitive verbs: (predName, verb, subjRef, dirObjRef, indirObjRef)
        # - The SubjectRef verbed the DirObjRef to the indirObjRef (The professor (S) gave
        # the paper (D) to the student (I))
        # Break up the predicate
        predicateComponents = predicateContents.split(',')
        numberOfComponents = len(predicateComponents)
        # Always have first three components, so only special cases are transitive/ditransitive
        predReferenceVariable = predicateComponents[0]
        predVerb = predicateComponents[1]
        predSubjRef = predicateComponents[2]
        # Different cases (differing number of components)
        if numberOfComponents == 3:
            # intransitive
            predSubjRef = predSubjRef.split(')')[0]
        elif numberOfComponents == 4:
            # Transitive
            predDirObjRef = predicateComponents[3].split(')')[0]
        elif numberOfComponents == 5:
            # Ditransitive - NOT YET IMPLEMENTED
            # predIndirObjRef = predicateComponents[4].split(')')[0]
            pass
        else:
            # invalid
            raise ValueError('Too many components ?')
        # Hardcode be case for specific scenarios

        if predVerb == CONST_PRED_VERB_BE:
            # Check if naming or setting an equivalency
            if CONST_PRED_SUBJ_NAMED in predSubjRef:
                # If so call naming method
                self.DRSGraph = self.nameItem(predSubjRef, predDirObjRef, self.DRSGraph)
            # If not named(XYZ) but still has 4 components
            elif numberOfComponents == 4:
                # Get nodes for both subject and direct object
                subjRefNode = self.DRSGraph.FindItemWithValue(predSubjRef)
                dirObjRefNode = self.DRSGraph.FindItemWithValue(predDirObjRef)
                # If both are ITEM nodes in the graph, then the "Be" is setting an equivalency
                if subjRefNode is not None and dirObjRefNode is not None and CONST_ITEM_NODE in dirObjRefNode:
                    self.DRSGraph.addNodeEquivalencyEdges(subjRefNode, dirObjRefNode)
                # If the target node is a PROPERTY node, then the 'BE' is setting an "is" property relationship
                elif subjRefNode is not None and dirObjRefNode is not None and CONST_PROP_NODE in dirObjRefNode:
                    self.DRSGraph.addPropertyEdge(subjRefNode, dirObjRefNode)
            # HANDLE ANY OTHER CASES????

        # Hardcode "have" case for composition
        elif predVerb == CONST_PRED_VERB_HAVE:
            if numberOfComponents == 4:
                # Get nodes for both subject and direct object
                subjRefNode = self.DRSGraph.FindItemWithValue(predSubjRef)
                dirObjRefNode = self.DRSGraph.FindItemWithValue(predDirObjRef)
                # If both are nodes in the graph, then the "have" is setting a composition
                if subjRefNode is not None and dirObjRefNode is not None:
                    self.DRSGraph.addCompositionEdges(subjRefNode, dirObjRefNode)
        else:
            # Create Action Node
            self.DRSGraph.AppendItemAffordanceAtSpecificNode(predSubjRef, predVerb)
            actionGraph = ActionGraph(self.graphNumber)
            actionGraph.appendActionValue(predReferenceVariable)
            actionGraph.appendActionVerb(predVerb)
            # Increase the graph number for auto-generation of names
            self.graphNumber = self.graphNumber + 1
            # If a main graph already exists, then add the new graph in to it
            if self.DRSGraph.graph is not None:
                self.DRSGraph.graph = networkx.algorithms.operators.binary.compose(self.DRSGraph.graph,
                                                                                   actionGraph.graph)
            # if no main graph exists, this is the main graph
            else:
                self.DRSGraph.graph = actionGraph.graph

            # Get subject reference node
            subjRefNode = self.DRSGraph.FindItemWithValue(predSubjRef)
            actionNode = self.DRSGraph.FindItemWithValue(predReferenceVariable)

            # If just one subject "The target appears"
            if numberOfComponents == 3:
                self.DRSGraph.addActionPerformerEdges(subjRefNode, actionNode)
            # If subject and direct object (e.g. "The subject remembers the letter")
            # predSubjRef = "Subject", predDirObjRef = "letter"
            elif numberOfComponents == 4:
                dirObjRefNode = self.DRSGraph.FindItemWithValue(predDirObjRef)
                self.DRSGraph.addActionPerformerEdges(subjRefNode, actionNode)
                self.DRSGraph.addActionTargetEdges(actionNode, dirObjRefNode)

            # TODO TODO TODO TODO
            elif numberOfComponents == 5:
                pass

    # For has_part() predicates
    def predicate_has_part(self, predicateContents):
        # Get predicate items
        predicateComponents = predicateContents.split(',')
        predGroupRef = predicateComponents[0]
        predGroupMember = predicateComponents[1].split(')')[0]
        # Hardcode the new object as being a group
        predGroupDescription = CONST_PRED_GROUP_DESC
        # if Group reference doesn't exist
        groupNode = self.DRSGraph.FindItemWithValue(predGroupRef)
        memberNode = self.DRSGraph.FindItemWithValue(predGroupMember)
        if groupNode is None:
            # Then create that item
            # Apply appropriate variables to ItemGraph
            groupGraph = ItemGraph(self.graphNumber)
            groupGraph.appendItemValue(predGroupRef)
            groupGraph.appendItemRole(predGroupDescription)
            # Get the node for the group
            groupNode = groupGraph.FindItemWithValue(predGroupRef)
            # Increase the graph number for auto-name generation
            self.graphNumber = self.graphNumber + 1
            # Compose the new graph with the existing graph
            # (no scenario of no existing graph because can't start with has_part())
            self.DRSGraph.graph = networkx.algorithms.operators.binary.compose(self.DRSGraph.graph, groupGraph.graph)
        # Add membership edges
        self.DRSGraph.addGroupMembershipEdges(groupNode, memberNode)

    # HANDLE MODIFIERS - PREPOSITION
    # TODO TODO TODO TODO
    def predicate_modifier_pp(self, predicateContents):
        # Find action node of predicate
        # Get predicate items
        predicateComponents = predicateContents.split(',')
        modPPRefID = predicateComponents[0] + CONST_PRED_MOD_TAG
        modPPPrep = predicateComponents[1]
        modPPModifiedVerb = predicateComponents[0]
        modPPTargetObj = predicateComponents[2].split(')')[0]

        # Create Modifier Node
        modGraph = ModifierPPGraph(self.graphNumber)
        modGraph.appendModPPValue(modPPRefID)
        modGraph.appendModPPPrep(modPPPrep)

        # Increase the graph number for auto-generation of names
        self.graphNumber = self.graphNumber + 1

        # If a main graph already exists, then add the new graph in to it
        if self.DRSGraph.graph is not None:
            self.DRSGraph.graph = networkx.algorithms.operators.binary.compose(self.DRSGraph.graph, modGraph.graph)
        # if no main graph exists, this is the main graph
        else:
            self.DRSGraph.graph = modGraph.graph

        # Add verb and object modifier edges
        modNode = self.DRSGraph.FindItemWithValue(modPPRefID)
        verbNode = self.DRSGraph.FindItemWithValue(modPPModifiedVerb)
        objectNode = self.DRSGraph.FindItemWithValue(modPPTargetObj)
        self.DRSGraph.addModifierVerbEdges(modNode, verbNode)
        self.DRSGraph.addModifierObjectEdges(modNode, objectNode)

    # HANDLE MODIFIERS - ADVERB
    def predicate_modifier_adv(self, predicateContents):
        pass

    # HANDLE PROPERTIES
    # TODO: Handle 4/6 component properties
    # TODO: Handle degrees besides "pos"
    def predicate_property(self, predicateContents):
        # Break up the predicate
        predicateComponents = predicateContents.split(',')
        numberOfComponents = len(predicateComponents)
        # Always have first two components, others distributed based on number of components
        propRefId = predicateComponents[0]
        propAdjective = predicateComponents[1]
        # Different cases (differing number of components)
        if numberOfComponents == 3:
            # Only a primary object
            propDegree = predicateComponents[2].split(')')[0]
        elif numberOfComponents == 4:
            # Primary and secondary object
            propDegree = predicateComponents[2]
            # propSecObj = predicateComponents[3].split(')')[0]
        elif numberOfComponents == 6:
            # Primary, secondary, and tertiary objects
            # propSecObj = predicateComponents[2]
            propDegree = predicateComponents[3]
            # propCompTarget = predicateComponents[4]
            # propTertObj = predicateComponents[5].split(')')[0]
        else:
            # invalid
            raise ValueError('Too many components ?')

        existingNodeWithRefId = self.DRSGraph.FindItemWithValue(propRefId)
        if existingNodeWithRefId is None:
            # Apply appropriate variables to PropertyGraph (operating off same graph number
            # because the number in the name is irrelevant)
            propGraph = PropertyGraph(self.graphNumber)
            propGraph.appendPropValue(propRefId)
            propGraph.appendPropAdj(propAdjective)
            propGraph.appendPropDegree(propDegree)
            # Increase the graph number for auto-generation of names
            self.graphNumber = self.graphNumber + 1
            # If a main graph already exists, then add the new graph in to it
            if self.DRSGraph.graph is not None:
                self.DRSGraph.graph = networkx.algorithms.operators.binary.compose(self.DRSGraph.graph, propGraph.graph)
            # if no main graph exists, this is the main graph
            else:
                self.DRSGraph.graph = propGraph.graph
            return True
        else:
            outEdgesFromNode = self.DRSGraph.graph.out_edges(existingNodeWithRefId, data=True)
            adjectiveNode = None
            for startNode, endNode, edgeValues in outEdgesFromNode:
                # If an edge has the value ItemHasName, then we want to modify the end node
                if edgeValues[CONST_NODE_VALUE_KEY] == CONST_PROP_HAS_ADJECTIVE_EDGE:
                    # Update graph with name
                    adjectiveNode = endNode
            if adjectiveNode is not None:
                self.DRSGraph.AppendValueAtSpecificNode(adjectiveNode, propAdjective)
            else:
                print("Error - Encountered duplicate reference for property but did not find adjective "
                      "node to append to")
            return True

    # Method used to get the name out of a "named" predicate and associate said name with the appropriate object.
    def nameItem(self, predSubjRef, predDirObjRef, DRSGraph):
        # Get item name out of "named(XYZ)"
        itemName = predSubjRef[predSubjRef.find("(") + 1:predSubjRef.find(")")]
        # Replace the name
        DRSGraph.ReplaceItemNameAtSpecificNode(predDirObjRef, itemName)
        # Return graph
        return DRSGraph


# CURRENTLY OPERATING UNDER ASSUMPTION THAT questions ALWAYS end with the predicate as the final piece.
# This will 100% need revised (probably just check if
# the current line is the final question line and then process the complete question at that point).
class questionSwitcher(object):

    def __init__(self):
        self.graphNumber = 0
        self.DRSGraph = None
        self.nodesWithGivenProperty = []
        self.nodesWithGivenPropertyAntonym = []
        self.subjectNode = None
        self.objectNode = None
        self.itemCount = 0
        self.propertyCount = 0
        self.newToOldRefIDMapping = {}

    # Method to call the appropriate function based on the argument passed in
    def callFunction(self, predicateType, predicateContents, DRSGraph):
        # Get the name of the method
        methodName = 'question_' + str(predicateType)
        # Get the method itself
        method = getattr(self, methodName, lambda: "Unknown predicate")
        # Call the method and return its output
        self.DRSGraph = DRSGraph
        # print(predicateContents)
        method(predicateContents)

    def returnDRSGraph(self):
        return self.DRSGraph

    def question_object(self, predicateContents):
        # Get object information
        predicateComponents = predicateContents.split(',')
        objRefId = predicateComponents[0]
        objRole = predicateComponents[1]
        # objClass = predicateComponents[2]
        # objUnit = predicateComponents[3]
        # objOperator = predicateComponents[4]
        # objCount = predicateComponents[5].split(')')[0]
        # Get the item node in the original instruction which this SHOULD correspond to (via role)
        DRSEquivalentNode = self.findItemNodeWithRole(objRole)
        # print(DRSEquivalentNode)
        # Replace the reference ID (from APE Webclient) to the equivalent node's reference ID (from the graph)
        if self.DRSGraph.graph.has_node(DRSEquivalentNode):
            DRSNodeRefID = self.DRSGraph.graph.node[DRSEquivalentNode][CONST_NODE_VALUE_KEY]
            self.newToOldRefIDMapping.update({objRefId: DRSNodeRefID})
            # print("NEW TO OLD OBJECT REF ID MAPPING", objRefId, DRSNodeRefID)
        else:
            self.newToOldRefIDMapping.update({objRefId: None})
            # print("NEW TO OLD OBJECT REF ID NULL MAPPING", objRefId)
        # WILL NEED TO FIND A WAY TO HANDLE NAME AND ROLE TO GET MORE ACCURATE PICTURE?

    # HANDLE PROPERTIES
    # TODO: Handle 4/6 component properties
    # TODO: Handle degrees besides "pos"
    def question_property(self, predicateContents):
        # Break up the predicate
        predicateComponents = predicateContents.split(',')
        numberOfComponents = len(predicateComponents)
        # Always have first two components, others distributed based on number of components
        propRefId = predicateComponents[0]
        propAdjective = predicateComponents[1]
        # Different cases (differing number of components) - completely unused right now, but leaving commented out
        # in case of implementation
        if numberOfComponents == 3:
            # Only a primary object
            # propDegree = predicateComponents[2].split(')')[0]
            pass
        elif numberOfComponents == 4:
            # Primary and secondary object
            # propDegree = predicateComponents[2]
            # propSecObj = predicateComponents[3].split(')')[0]
            pass
        elif numberOfComponents == 6:
            # Primary, secondary, and tertiary objects
            # propSecObj = predicateComponents[2]
            # propDegree = predicateComponents[3]
            # propCompTarget = predicateComponents[4]
            # propTertObj = predicateComponents[5].split(')')[0]
            pass
        else:
            # invalid
            raise ValueError('Too many components ?')

        # INITIAL NYM TESTING - will need to extend to other predicates as well of course
        #TODO: Resolve occurs before identify here - that shouldn't be the case probably
        adjectiveNymList, antonymList = getNyms(propAdjective)
        if CONTROL_RESOLVE_LEXICAL == True:
            adjectiveNodes = self.ListOfNodesWithValueFromList(adjectiveNymList)
        else:
            adjectiveNodes = self.ListOfNodesWithValue(propAdjective)
        # We
        if CONTROL_IDENTIFY_NEGATION == True:
            if CONTROL_RESOLVE_LEXICAL == True:
                antonymNodes = self.ListOfNodesWithValueFromList(antonymList)
            else:
                antonymNodes = self.ListOfNodesWithValue(propAdjective)

        # print("ADJECTIVE NODES", adjectiveNodes)
        newNymCount = 0
        if CONTROL_IDENTIFY_LEXICAL == True:
            if len(adjectiveNodes) < 1:
                print("Lexical gap encountered - an adjective was introduced which is not currently in the system's "
                      "vocabulary.")
            if CONTROL_RESOLVE_LEXICAL == True:
                #TODO: Allow user to manually choose yes/no to resolve?
                #Should antonymNodes be counted here too?
                while len(adjectiveNodes) < 1 and len(antonymNodes) < 1 and newNymCount < 3:
                    # No nodes "active"
                    newAdjective = requestNewTermToNymCheck(propAdjective)
                    newNymCount = newNymCount + 1
                    adjectiveNymList, newAntonymList = getNyms(newAdjective)
                    antonymNodes = self.ListOfNodesWithValueFromList(newAntonymList)
                    adjectiveNodes = self.ListOfNodesWithValueFromList(adjectiveNymList)
                    if len(adjectiveNodes) > 0:
                        print("Lexical gap resolved - an adjective given was found in the knowledge base")

        if len(adjectiveNodes) > 0:
            for node in adjectiveNodes:
                # print("AdjectiveNode", node)
                # Add new term into adjective node in order to grow our vocabulary
                if propAdjective not in self.DRSGraph.graph.node[node][CONST_NODE_VALUE_KEY]:
                    self.DRSGraph.AppendValueAtSpecificNode(node, propAdjective)
                propertyNode = self.getPropertyNodeFromAdjective(node)
                self.nodesWithGivenProperty.append(propertyNode)
                # MAP FOUND PROPERTY NODE'S REF ID TO THE INCOMING REF ID
                if self.DRSGraph.graph.has_node(propertyNode):
                    DRSNodeRefID = self.DRSGraph.graph.node[propertyNode][CONST_NODE_VALUE_KEY]
                    self.newToOldRefIDMapping.update({propRefId: DRSNodeRefID})
                    # print("NEW TO OLD PROPERTY REF ID MAPPING", propRefId, DRSNodeRefID)
                else:
                    self.newToOldRefIDMapping.update({propRefId: None})
                    # print("NEW TO OLD PROPERTY REF ID NULL MAPPING", propRefId)

        if len(antonymNodes) > 0:
            if CONTROL_IDENTIFY_NEGATION == True:
                print("Negation gap identified - a node has been found that contains an antonym of one of the "
                      "provided adjectives")
                # propertyNodesWithAdjective = []
                if CONTROL_RESOLVE_NEGATION == True:
                    for node in antonymNodes:
                        # print("AntonymNode", node)
                        propertyNode = self.getPropertyNodeFromAdjective(node)
                        self.nodesWithGivenPropertyAntonym.append(propertyNode)
                        print("Negation gap resolved - an antonym has been found in the knowledge graph")
                        # MAP FOUND ANTONYM NODE'S REF ID TO THE INCOMING REF ID
                        if self.DRSGraph.graph.has_node(propertyNode):
                            DRSNodeRefID = self.DRSGraph.graph.node[propertyNode][CONST_NODE_VALUE_KEY]
                            self.newToOldRefIDMapping.update({propRefId: DRSNodeRefID})
                            # print("NEW TO OLD PROPERTY REF ID MAPPING", propRefId, DRSNodeRefID)
                        else:
                            self.newToOldRefIDMapping.update({propRefId: None})
                            # print("NEW TO OLD PROPERTY REF ID NULL MAPPING", propRefId)

        # ***********************************************************************************************************************************
        # If no adjective nodes are found, then we look for antonyms
        # Because of this, we are positive-biased, as if we find adjective nodes, we don't look for antonyms
        # May be a better approach to look for both and, if both are found, declare a conflict rather than assume
        # one way or the other?
        # Slower processing time though
        # ***********************************************************************************************************************************
        # else:
        # antonymNodes = self.ListOfNodesWithValueFromList(antonymList)
        # We don't want to grow the vocabulary here directly, so we skip the adding new terms
        # if (len(antonymNodes) > 0):
        #    propertyNodesWithAdjective = []
        #    for node in antonymNodes:
        #        print("AntonymNode", node)
        #        if(propAdjective not in self.DRSGraph.graph.node[node]['value']):
        #            self.DRSGraph.AppendValueAtSpecificNode(node, propAdjective)
        #        propertyNode = self.getPropertyNodeFromAdjective(node)
        #        #print("propertyNode", propertyNode)
        #        self.nodesWithGivenPropertyAntonym.append(propertyNode)

    # For predicate() predicates
    # HOW TO HANDLE SENTENCE SUB-ORDINATION?
    def question_predicate(self, predicateContents):
        # Intransitive verbs: (predName, verb, subjectRef)
        # - The SubjectRef Verbed (the man laughed, the target appears)
        # Transitive verbs: (predName, verb, subjectRef, dirObjRef)
        # - The Subjectref Verbed the dirObjRef (the task A has a group of objects H,
        # the subject L remembers the letter I)
        # Ditransitive verbs: (predName, verb, subjRef, dirObjRef, indirObjRef)
        # - The SubjectRef verbed the DirObjRef to the indirObjRef (The professor (S) gave
        # the paper (D) to the student (I))
        # Break up the predicate
        predicateComponents = predicateContents.split(',')
        numberOfComponents = len(predicateComponents)
        # Always have first three components, so only special cases are transitive/ditransitive
        # predReferenceVariable = predicateComponents[0]
        predVerb = predicateComponents[1]
        predSubjRef = predicateComponents[2]
        # Set dir/indir object references to none so we can check them for substitution
        predDirObjRef = None
        predIndirObjRef = None
        # Different cases (differing number of components)
        if numberOfComponents == 3:
            # intransitive
            predSubjRef = predSubjRef.split(')')[0]
        elif numberOfComponents == 4:
            # Transitive
            predDirObjRef = predicateComponents[3].split(')')[0]
        elif numberOfComponents == 5:
            # Ditransitive
            predIndirObjRef = predicateComponents[4].split(')')[0]
        else:
            # invalid
            raise ValueError('Too many components ?')
        # Hardcode be case for specific scenarios

        # Substitute in DRS equivalents for dereferenced ref IDs
        if predSubjRef in self.newToOldRefIDMapping:
            predSubjRef = self.newToOldRefIDMapping.get(predSubjRef)
            if predSubjRef is None:
                # TODO: Better define this error case
                if CONTROL_IDENTIFY_LEXICAL:
                    print("Lexical gap encountered - an item was introduced which is not currently in the system's "
                          "vocabulary.")
                return None
        if predDirObjRef is not None and predDirObjRef in self.newToOldRefIDMapping:
            predDirObjRef = self.newToOldRefIDMapping.get(predDirObjRef)
            if predDirObjRef is None:
                # TODO: Better define this error case
                if CONTROL_IDENTIFY_LEXICAL:
                    print("Lexical gap encountered - an item was introduced which is not currently in the system's "
                          "vocabulary.")
                    return None
        if predIndirObjRef is not None and predIndirObjRef in self.newToOldRefIDMapping:
            predIndirObjRef = self.newToOldRefIDMapping.get(predIndirObjRef)
            if predIndirObjRef is None:
                # TODO: Better define this error case
                if CONTROL_IDENTIFY_LEXICAL:
                    print("Lexical gap encountered - an item was introduced which is not currently in the system's "
                          "vocabulary.")
                    return None

        if predVerb == CONST_PRED_VERB_BE:
            # If the SUBJECT reference is a proper name
            # Check if we find a node containing said name
            if CONST_PRED_SUBJ_NAMED in predSubjRef:
                # Get item name out of "named(XYZ)"
                itemName = predSubjRef[predSubjRef.find("(") + 1:predSubjRef.find(")")]
                nodesWithGivenName = self.ListOfNodesWithValue(itemName)
                if len(nodesWithGivenName) > 0:
                    itemNodes = []
                    for nameNode in nodesWithGivenName:
                        # Need to get the actual item node, not the name node.
                        itemNode = self.findItemNodeConnectedToNameNode(nameNode)
                        itemNodes.append(itemNode)
                        # print("ITEM WITH NAME", itemName, ": ", itemNode)
                    # If only one item with that name, then we've found our subject node
                    if len(itemNodes) == 1:
                        self.subjectNode = itemNodes[0]
                    # Need to figure out a case if more than one item with the name
            # If the subject reference is another variable, not a proper name
            else:
                subjectRefVar = predSubjRef
                subjectNodes = self.ListOfNodesWithValue(subjectRefVar)
                if len(subjectNodes) > 0:
                    # print("SUBJECT NODES", subjectNodes)
                    self.subjectNode = subjectNodes[0]

            # Same as above for OBJECT reference
            if CONST_PRED_SUBJ_NAMED in predDirObjRef:
                # Get item name out of "named(XYZ)"
                itemName = predDirObjRef[predDirObjRef.find("(") + 1:predDirObjRef.find(")")]
                nodesWithGivenName = self.ListOfNodesWithValue(itemName)
                if len(nodesWithGivenName) > 0:
                    itemNodes = []
                    for nameNode in nodesWithGivenName:
                        # Need to get the actual item node, not the name node.
                        itemNode = self.findItemNodeConnectedToNameNode(nameNode)
                        itemNodes.append(itemNode)
                        # print("ITEM WITH NAME", itemName, ": ", itemNode)
                    # If only one item with that name, then we've found our subject node
                    if len(itemNodes) == 1:
                        self.objectNode = itemNodes[0]
                    # Need to figure out a case if more than one item with the name
            # If the subject reference is another variable, not a proper name
            else:
                objectRefVar = predDirObjRef
                objectNodes = self.ListOfNodesWithValue(objectRefVar)
                if len(objectNodes) > 0:
                    # print("OBJECT NODES", objectNodes)
                    self.objectNode = objectNodes[0]

            # Track how many items and properties, as item-item and item-property have different edges connecting them
            # print("SELF.ITEMCOUNT PRIORITY", self.itemCount)
            # print("SELF.PROPCOUNT PRIORITY", self.propertyCount)
            # print("SELF.SUBJECTNODE", self.subjectNode)
            # print("SELF.OBJECTNODE", self.objectNode)
            if self.subjectNode is not None:
                if CONST_ITEM_NODE in self.subjectNode:
                    self.itemCount = self.itemCount + 1
                elif CONST_PROP_NODE in self.subjectNode:
                    self.propertyCount = self.propertyCount + 1
            if self.objectNode is not None:
                if CONST_ITEM_NODE in self.objectNode:
                    self.itemCount = self.itemCount + 1
                elif CONST_PROP_NODE in self.objectNode:
                    self.propertyCount = self.propertyCount + 1

    def resolveQuestion(self):
        # print("NAMED SUBJECT NODE", self.subjectNode)
        # print("NAMED OBJECT NODE", self.objectNode)

        # Possibly not an actual error condition, just testing this
        if self.objectNode is None or self.subjectNode is None:
            print("Either the subject or object is missing, so something is wrong")
            return None
        else:
            # Assuming that if there is one item and one property, the item is the subject node,
            # so the "Is" edge will be in the outEdges
            # This may be an incorrect assumption, will need to test and check
            # Checking if there is an edge with name "Is", since "Is" is the name given to item->property edges.
            # THIS SHOULD BE ABSTRACTED, THERE SHOULD BE A VARIABLE SOMEWHERE THAT HOLDS IMPORTANT EDGE NAMES
            # print("ITEM COUNT", self.itemCount)
            # print("PROP  COUNT", self.propertyCount)
            if self.itemCount == 1 and self.propertyCount == 1:
                # Try to find positive relationships
                for node in self.nodesWithGivenProperty:
                    # Get the edges between the subject and object nodes
                    edgeBetweenNodes = self.DRSGraph.graph.get_edge_data(self.subjectNode, self.objectNode)
                    # Iterate through each edge connecting the two nodes if not empty list
                    if edgeBetweenNodes is not None:
                        for edge in edgeBetweenNodes.values():
                            # Get the name of the edge
                            edgeValue = edge[CONST_NODE_VALUE_KEY]
                            # If the edge is "Is" then the item has this property and we consider it TRUE
                            if edgeValue == CONST_IS_EDGE:
                                return True
                # Try to find negative relationships (antonyms)
                for antonymNode in self.nodesWithGivenPropertyAntonym:
                    # Get the edges between the subject and object nodes
                    edgeBetweenNodes = self.DRSGraph.graph.get_edge_data(self.subjectNode, self.objectNode)
                    # Iterate through each edge connecting the two nodes if not empty list
                    if edgeBetweenNodes is not None:
                        for edge in edgeBetweenNodes.values():
                            # Get the name of the edge
                            edgeValue = edge[CONST_NODE_VALUE_KEY]
                            # If the edge is "Is" then the item has this property and we consider it TRUE
                            if edgeValue == CONST_IS_EDGE:
                                return False
                # If could not find a positive or negative relationship, then return None (unknown)
                return None

            # Assuming if there are two items, there are no properties in the predicate (again, may need corrections)
            if self.itemCount == 2:
                edgeBetweenNodes = self.DRSGraph.graph.get_edge_data(self.subjectNode, self.objectNode)
                # Iterate through each edge connecting the two nodes if not empty list
                if edgeBetweenNodes is not None:
                    for edge in edgeBetweenNodes.values():
                        # Get the name of the edge
                        edgeValue = edge[CONST_NODE_VALUE_KEY]
                        # If IsEquivalentTo edge is found connecting the subject node and the object node then TRUE
                        if edgeValue == CONST_IS_EQUIVALENT_EDGE:
                            return True
                    # If IsEquivalentTo edge is not found connecting the subject node and the object node then FALSE
                    return False
            # If neither of the above scenarios has occurred, then unknown
            return None

    def ListOfNodesWithValueFromList(self, listOfNyms):
        nodeList = []
        for valueToFind in listOfNyms:
            # print(valueToFind)
            if self.DRSGraph is not None:
                # iterate through all graph nodes
                for node, values in self.DRSGraph.graph.nodes.data():
                    listOfValuesToCheck = values[CONST_NODE_VALUE_KEY].split('|')

                    if valueToFind in listOfValuesToCheck:
                        nodeList.append(node)
        return nodeList

    def ListOfNodesWithValue(self, valueToFind):
        nodeList = []
        if self.DRSGraph is not None:
            # iterate through all graph nodes
            for node, values in self.DRSGraph.graph.nodes.data():
                # If the current Node's value = the value passed in
                # Changed from valueToFind in values to valueToFind == values as "active" was
                # triggering found in "inactive" due to being substr
                if valueToFind == values[CONST_NODE_VALUE_KEY]:
                    nodeList.append(node)
        return nodeList

    def getPropertyNodeFromAdjective(self, adjectiveNode):
        # Get list of edges from the node
        inEdgesFromNode = self.DRSGraph.graph.in_edges(adjectiveNode, data=True)
        outEdgesFromNode = self.DRSGraph.graph.out_edges(adjectiveNode, data=True)
        edgesFromNode = list(inEdgesFromNode) + list(outEdgesFromNode)
        for startNode, endNode, edgeValues in edgesFromNode:
            # If an edge has the value ItemHasName, then we want to modify the end node
            if edgeValues[CONST_NODE_VALUE_KEY] == CONST_PROP_HAS_ADJECTIVE_EDGE:
                # Update graph with name
                return startNode

    # TEMP UNTIL FIGURE OUT NAME HANDLING
    def findItemNodeWithRole(self, strRole):
        # Get list of nodes with the given role
        roleNodes = self.ListOfNodesWithValue(strRole)
        # Handle role nodes
        # Get list of item nodes associated with the role nodes
        for roleNode in roleNodes:
            # print("ROLE NODE", roleNode)
            roleItemNode = self.findItemNodeConnectedToRoleNode(roleNode)
            # print("ROLE ITEM NODE", roleItemNode)
            return roleItemNode

    def findItemNodeWithNameAndRole(self, strName, strRole):
        # Get list of nodes with the given name
        nameNodes = self.ListOfNodesWithValue(strName)
        # Get list of nodes with the given role
        roleNodes = self.ListOfNodesWithValue(strRole)
        # Handle name nodes
        nameItemNodes = []
        # Get list of item nodes associated with the name nodes
        for nameNode in nameNodes:
            nameItemNode = self.findItemNodeWithName(nameNode)
            nameItemNodes.append(nameItemNode)
        # Handle role nodes
        roleItemNodes = []
        # Get list of item nodes associated with the role nodes
        for roleNode in roleNodes:
            roleItemNode = self.findItemNodeConnectedToRoleNode(roleNode)
            roleItemNodes.append(roleItemNode)
        # Find item node which has both the name and role
        # Iterate through role nodes for arbitrary reason
        for potentialItemNode in roleItemNodes:
            if potentialItemNode in nameItemNodes:
                return potentialItemNode

    def findItemNodeConnectedToNameNode(self, nameNode):
        # Edges seem to be a little weird, so getting
        inEdgesFromNode = self.DRSGraph.graph.in_edges(nameNode, data=True)
        for startNode, endNode, edgeValues in inEdgesFromNode:
            # If an edge has the value ItemHasName, then we want to return the start node (the item node itself)
            if edgeValues[CONST_NODE_VALUE_KEY] == CONST_ITEM_HAS_NAME_EDGE:
                # print("FOUND NODE WITH NAME:", startNode)
                return startNode

    def findItemNodeConnectedToRoleNode(self, roleNode):
        inEdgesFromNode = self.DRSGraph.graph.in_edges(roleNode, data=True)
        for startNode, endNode, edgeValues in inEdgesFromNode:
            # If an edge has the value ItemHasRole, then we want to return the start node (the item node itself)
            if edgeValues[CONST_NODE_VALUE_KEY] == CONST_ITEM_HAS_ROLE_EDGE:
                # print("FOUND NODE WITH ROLE:", startNode)
                return startNode


def requestNewTermToNymCheck(originalTerm):
    newTerm = input(
        "Sorry, I don't understand \"" + originalTerm + "\".  Please give me an alternate word and "
                                                        "I'll make the connection.")
    return newTerm


def APEWebserviceCall(phraseToDRS):
    print(phraseToDRS)
    # Make APE Webservice call with given ACE phrase
    urlToRequest = "http://attempto.ifi.uzh.ch/ws/ape/apews.perl?text=" + phraseToDRS + "&solo=drspp"
    # Get the DRS that is sent back
    r = requests.get(urlToRequest)
    returnedDRS = r.text.splitlines()
    DRSLines = []
    error = False
    for line in returnedDRS:
        line = line.strip()
        # Exclude first, useless line
        # Also skip empty lines (if line.strip() returns true if line is non-empty.)
        if line != '[]' and line.strip():
            if line == "importance=\"error\"":
                error = True
            # print(line)
            DRSLines.append(line)
    # Technically it's a little silly to categorize the DRS for a question since it's obviously all
    # a question, but this gets around having to do questionable and inconsistent parsing to deal with
    # the header lines
    # This way, we can just get the question lines, which are what we actually use to process questions
    if error:
        return None
    else:
        symbolLines = getSymbolLines(DRSLines)
        # print("SYMBOLS - ", symbolLines)
        categorizedQuestionDRS = categorizeDRSLines(DRSLines, symbolLines)
        # print(categorizedQuestionDRS)

        questionLines = []
        # Iterate through DRS lines and get only the actual question lines, none of the headers
        for index, line in enumerate(DRSLines):
            if categorizedQuestionDRS.get(index) == CONST_QUESTION_TAG:
                questionLines.append(line)
        # print(questionLines)
        # Return just the lines that are the actual DRS for the question, no headers
        return questionLines


def getNyms(wordToCheck):
    # Iterate through all words to check
    synonyms = []
    hypernyms = []
    hyponyms = []
    deriv = []
    uniqueNymList = []
    uniqueAntonymList = []
    #if CONTROL_IDENTIFY_LEXICAL == True:
    # print(wordToCheck)
    # Get synsets of current word to check
    testWord = wordnet.synsets(wordToCheck)
    # for each synset (meaning)
    for syn in testWord:
        # Get Hypernyms
        if len(syn.hypernyms()) > 0:
            currentHypernyms = syn.hypernyms()
            for hyperSyn in currentHypernyms:
                for lemma in hyperSyn.lemmas():
                    # if(lemma.name() != currentWord):
                    hypernyms.append(lemma.name())
        # Get Hyponyms
        if len(syn.hyponyms()) > 0:
            currentHyponyms = syn.hyponyms()
            for hypoSyn in currentHyponyms:
                for lemma in hypoSyn.lemmas():
                    # if(lemma.name() != currentWord):
                    hyponyms.append(lemma.name())
        # Get direct synonyms
        for lemma in syn.lemmas():
            # if(lemma.name() != currentWord):
            synonyms.append(lemma.name())
            # Get derivationally related forms
            for derivForm in lemma.derivationally_related_forms():
                if derivForm.name() not in deriv:
                    deriv.append(derivForm.name())
            # Get antonyms
            if lemma.antonyms():
                if lemma.antonyms()[0].name() not in uniqueAntonymList:
                    uniqueAntonymList.append(lemma.antonyms()[0].name())
        # print("SYNONYMS: ")
        # print(set(synonyms))
        # print('\n HYPERNYMS:')
        # print(set(hypernyms))
        # print('\n HYPONYMS:')
        # print(set(hyponyms))
        # print('\n DERIVATIONALLY RELATED FORMS:')
        # print(set(deriv))
        nymLists = synonyms + hypernyms + hyponyms + deriv
        uniqueNyms = set(nymLists)
        uniqueNymList = list(uniqueNyms)
        # print(uniqueNymList)
        # print("ANTONYMS", uniqueAntonymList)
    return uniqueNymList, uniqueAntonymList


# TODO: handle 5-item predicate() tags
# TODO: handle conditionals - SPECIFICALLY X -> Y; Y -> Z, how to avoid Y just being stored twice (target appears)
# TODO: make overarching situationGraph which contains Item/Prop graphs and has graph-wide functions (move some to it)

# FORMAT OF A QUESTION:
# QUESTION
# [R,S]
# property(R,active,pos)-7/3
# predicate(S,be,A,R)-7/1

# Concept: See if there is a property "active" (Don't create it) (make a list of all nodes that are property "active")
# Then see if the predicate A has an edge to such a node?
# CURRENTLY QUESTION TEST INVOLVES QUESTION AT END.  WILL NEED TO TEST QUESTION IN MIDDLE
# Alternatively, create the network of the question and then try to map it onto the graph and see if that works?

# TODO: Extend wordnet checking, then add on verbnet and framenet

# CONCEPT: Have a flag on properties that mark them as true or not (isActive, isPresent, etc.)
# CONCEPT: For conditionals, set up a disconnected graph that details what happens if the IF section is true.
# Then, when that statement arrives, trigger the THEN.
# CONCEPT: When a term comes in that is not existing ("ongoing" vis-a-vis "active"), request explanation and
# store explanation alongside the term.
# NOTE: Conditionals are treated as an "and" by default - if you have X, Y => Z, both X and Y must be true.
# In the PVT case, since THE target appears in THE box, the trigger case will be identical,
# save for predicate reference ID, to the conditional case.
# If it were A target appears in A box, then the conditional case would create its own target and box -
# case that would need handling.\
# Because of this, may not need to create disconnected graph for conditionals, instead just store the
# lines that make up the conditional and test each incoming line to see if it triggers?
# Need to be able to check multiple lines if the trigger is multi-line (maybe do a look-ahead if first line is found?)

# Should find some way to encode non-triggered conditionals in case the knowledge is relevant
# (maybe do a look through the conditionals and see if it's found?)
# If it is found in conditional but not in graph, should return that it knows of its existence but that it's not true???

# Alternatively, implement the Transition part of the ontology.

# Potential concern: more synonyms being added to a label may lead to drift and inaccuracy
# Potential risk of recursive conditional triggering: A conditional runs itself
# (or something similar enough to re-trigger)


def DRSToItem():
    import matplotlib.pyplot as plt
    # Declare relevant variables
    DRSGraph = None
    DRSLines = []
    # Read in DRS instructions from file
    DRSFile = open("DRS_read_in.txt", "r")
    for line in DRSFile:
        # Get DRS command and remove any leading and ending whitespace
        DRSLines.append(line.strip())
    # Get numbers of which lines are headers ([A, B, C, ...] and conditionals (=>) )
    symbolLines = getSymbolLines(DRSLines)

    categorizedDRSLines = categorizeDRSLines(DRSLines, symbolLines)

    # Get all if-then sets
    conditionalSets = getConditionals(DRSLines, categorizedDRSLines)

    # print(conditionalSets)
    # Set up the predicate switcher
    predSwitcher = predicateSwitcher()

    # Set up counter for question response
    questionCounter = 1

    # Iterate through the DRS instructions
    for index, currentInstruction in enumerate(DRSLines):
        # take next instruction or exit
        nextStep = ''

        # As long as no "exit" given
        if nextStep != 'exit':
            # print(currentInstruction)
            # If the current line is an instruction
            if categorizedDRSLines.get(index) == CONST_INSTRUCTION_TAG:
                # Get the predicate type and contents
                instructionCountInMatchingIfBlock, conditionalWithMatchingIfBlock = \
                    checkCurrentInstructionIf(DRSLines, index, currentInstruction, conditionalSets)
                if instructionCountInMatchingIfBlock == 0:
                    DRSGraph = splitAndRun(currentInstruction, predSwitcher)

        # Break out of loop with exit
        else:
            break

    # On end of reading in instructions
    # process conditionals first:
    for conditional in conditionalSets:
        if not conditional.processed:
            DRSGraph = runFullConditional(conditional, predSwitcher, DRSGraph, conditionalSets)

    # Set up questionSwitcher
    qSwitcher = questionSwitcher()
    questionInput = input('Please enter a question')
    # "exit" is trigger word to end questioning
    while questionInput != 'exit':
        questionLines = APEWebserviceCall(questionInput)
        while questionLines is None:
            questionInput = input('There was an error with the ACE entered - please try again.')
            questionLines = APEWebserviceCall(questionInput)

        for currentLine in questionLines:
            predicateSplit = currentLine.split('(', 1)
            predicateType = predicateSplit[0]
            predicateContents = predicateSplit[1]
            # print(categorizedDRSLines.get(index))
            qSwitcher.callFunction(predicateType, predicateContents, DRSGraph)
            # print(currentInstruction)

        result = qSwitcher.resolveQuestion()
        if result:
            print("Question", str(questionCounter), "Answer: Yes")
        elif not result and result is not None:
            print("Question", str(questionCounter), "Answer: No")
        else:
            print("Question", str(questionCounter), "Answer: Unknown")
        questionCounter = questionCounter + 1
        # I have my doubts about these lines below but they seem to work
        DRSGraph = qSwitcher.returnDRSGraph()
        predSwitcher.updateDRSGraph(DRSGraph.graph)
        # Reset qSwitcher to be a new question switcher
        qSwitcher = questionSwitcher()
        questionInput = input('Please enter a DRS line for your question')

    # Once "exit" has been entered
    # At end of program, if an ontology was built at all, print it out and export it in GraphML
    if DRSGraph is not None:
        # networkx.draw(DRSGraph.graph, labels=networkx.get_node_attributes(DRSGraph.graph, CONST_NODE_VALUE_KEY))
        # plt.show()
        jsonFile = open("jsonFile.txt", "w")
        jsonSerializable = networkx.readwrite.json_graph.node_link_data(DRSGraph.graph)
        jsonOutput = json.dumps(jsonSerializable)
        jsonFile.write(jsonOutput)
        networkx.write_graphml_lxml(DRSGraph.graph, "DRSGraph.graphml")


DRSToItem()
