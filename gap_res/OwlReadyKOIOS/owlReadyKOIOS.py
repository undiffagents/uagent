from owlready2 import *
from Passive_Gap_Handling.OntoContextGap import *
from ControlPanel import *
from owlReadyInitializer import *
from Active_Gap_Handling.userInteraction import *
from Active_Gap_Handling.ItemQuestionHandling import *

onto = None
ontologyLoaded = True

# Method to load in the initialized ontology
def loadOntology():
    global onto
    onto = get_ontology("http://localhost:3030/uagent-initialized").load()


# Method to check for context gaps (aka edges/node connections which are expected but missing)
def checkContextGap():
    generateNodeSets()
    checkInitializedGraphEdges(onto)


def main():
    # Initialize the ontology
    if ontologyLoaded == False:
        initializeOntology()
        pass
    # Load the initialized ontology
    loadOntology()
    # Check context gaps if enabled
    if CONTROL_IDENTIFY_CONTEXT == True:
        print("Checking for context gaps")
        checkContextGap()
        print("Context gap checking complete")
    # If user interaction is enabled, get user questions and handle them
    if CONTROL_USER_INTERACTION == True:
        questionInput = input('Please enter a question: ')
        # "exit"/"quit"/"q" are trigger words to end questioning
        while questionInput != 'exit' and questionInput != 'quit' and questionInput != 'q':
            # TO BE DEALT WITH VIA INTERPRETER HOOKUP
            # questionLines = ACEQuestiontoDRS(questionInput)
            # print(questionLines)

            # CURRENTLY NEED TO HAND-ENTER INTERPRETER FORMAT QUESTIONS (ITEM ONLY RIGHT NOW)
            # e.g. item(screen), item(button), item(button, space_bar), etc.
            inputSplit = questionInput.split('(', 1)
            inputType = inputSplit[0]
            inputContents = inputSplit[1].split(')')[0]
            # If it's in the format item(x,[y]), then query the existence of said item
            if inputType == 'item':
                response = itemQuestion(onto, inputContents)
            questionInput = input('Please enter a question: ')


main()
