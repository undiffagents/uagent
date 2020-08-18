# Handle object(itemRole), predicate(Action) for now?
# Does it matter if something is part of a conditional?
# This is super primitive first pass

# Onto-to-Think CV mappings need to match up
# For now, hardcoding a mapping from one to the other

from nltk.corpus import wordnet

ThinkToOntoMapping = {'action': 'Action', 'condition': 'Affordance', 'item_role': 'ItemRole'}
OntoToThinkMapping = {'Action': 'action', 'Affordance': 'condition', 'ItemRole': 'item_role'}
DRSToCVMapping = {'object': 'ItemRole', 'predicate': 'Action'}

# These terms are currently being hardcoded to ignore because they're quite generic (or in the case of na, invalid)
# This may be a problem long-term?
# TODO ****
DRSIgnoredTerms = ['na', 'be', 'have']

DRSFileName = 'PVT.txt'
OntoCVFileName = 'OntoCV.txt'
ThinkCVFileName = 'ThinkCV.txt'
paronymListFileName = 'ParonymList.txt'

outputOntoCVFileName = "outputOntoCV.txt"
outputThinkCVFileName = "outputThinkCV.txt"

OntoCV = {}
ThinkCV = {}
DRSElements = {}
paronyms = {}

equivalenciesFound = {}

CONST_DETECT_LEXICAL_GAPS = True
CONST_RESOLVE_LEXICAL_GAPS = True

ofTypeEdge = " :ofType "
refersToItemXEdge = " :refersToItem"
ontoEquivalencyIndicator = " :sameAs "
thinkEquivalencyIndicator = "equivalent "

def parseOntoCVLine(currentLine):
    # Split and get the first/third elements of line (Action/clicking, ItemRole/target, etc.)
    lineElements = currentLine.split(' ')
    CVLineType = lineElements[0]
    CVLineItem = lineElements[2]
    # If the current type hasn't yet been initialized into the dictionary, do so
    if CVLineType not in OntoCV:
        OntoCV.update({CVLineType: []})
    # Get the dictionary entry for this type and append the line item into the appropriate array
    OntoCV[CVLineType].append(CVLineItem)


def parseThinkCVLine(currentLine):
    # Split and get the two elements of line (action_list/click, item_role_list/target, etc.)
    lineElements = currentLine.split(' ')
    ThinkLineType = lineElements[0]
    ThinkLineItem = lineElements[1]
    # Strip off the "_list" from the line type
    ThinkLineType = ThinkLineType.split('_list')[0]
    # Map think type format to onto format - THIS MAY BE A PROBLEM IF WE NEED TO BACK-FEED
    # TODO *******
    if ThinkLineType in ThinkToOntoMapping:
        ThinkLineType = ThinkToOntoMapping.get(ThinkLineType)
    # If the current type hasn't yet been initialized into the dictionary, do so
    if ThinkLineType not in ThinkCV:
        ThinkCV.update({ThinkLineType: []})
    # Get the dictionary entry for this type and append the line item into the appropriate array
    ThinkCV[ThinkLineType].append(ThinkLineItem)


def parseParonymListLine(currentLine):
    lineElements = currentLine.split('|')
    paronymBase = lineElements[0]
    paronymDerivations = lineElements[1:]
    if paronymBase not in paronyms:
        paronyms.update({paronymBase: paronymDerivations})


def parseDRSLine(currentLine):
    # Ignore header lines and '=>' lines
    if currentLine.startswith('[') or currentLine.startswith('=>'):
        return
    # Get the type and contents the DRS line
    lineElements = currentLine.split('(', 1)
    DRSLineType = lineElements[0]
    DRSLineContents = lineElements[1]
    # Check if there is a known mapping - from the DRS type to a CV type - THIS MAY BE A PROBLEM
    # TODO ******
    if DRSLineType in DRSToCVMapping:
        CVType = DRSToCVMapping.get(DRSLineType)
        # For objects and predicates, just grabbing the second element in the contents will always grant the primary
        # term (item role or action verb).  This will likely need to change in the future
        # TODO ****
        DRSTerm = DRSLineContents.split(',')[1]
        # If the current type hasn't yet been initialized into the dictionary, do so
        if CVType not in DRSElements:
            DRSElements.update({CVType: []})
        # Currently ignoring certain terms by hardcoding, this may be a problem long-term?
        # TODO ****
        # Get the dictionary entry for this type and append the line item into the appropriate array
        if DRSTerm not in DRSIgnoredTerms:
            DRSElements[CVType].append(DRSTerm)


def findMismatches():
    # Iterate through the types found in the DRS
    for termType in DRSElements:
        # Get all items of that type from the DRS
        DRSTerms = DRSElements.get(termType)
        # Get all items of that type from both the ontology and think CVs.
        # (Should these be treated as one or separately?  Would it be beneficial to know whether the ontology knows a
        # term and Think doesn't or vice versa?
        # TODO ****
        # OntoCVTerms = OntoCV.get(termType)
        # ThinkCVTerms = ThinkCV.get(termType)
        # Iterate through all of the terms in the DRS
        # TODO **** may not want to lock DRS type to CV type - subject comes in as item Role but should be agentSynonym?
        for term in DRSTerms:
            # If the ontology doesn't know the term, attempt resolution and return result
            if checkTermInCVs(termType, term, OntoCV) == False:
                print("TERM MISMATCH IDENTIFIED: The ontology doesn't know " + term + ".")
                # The question then is which nyms are appropriate and how to "correct" the CVs
                if CONST_RESOLVE_LEXICAL_GAPS == True:
                    corrected = resolveMismatch(termType, term, "O")
                    if corrected == True:
                        print("SUCCESS: Term mismatch corrected!")
                    else:
                        print("FAILURE: Term mismatch NOT corrected!")
            # If Think doesn't know the term, attempt resolution and return result
            if checkTermInCVs(termType, term, ThinkCV) == False:
                print("TERM MISMATCH IDENTIFIED: Think doesn't know " + term + ".")
                if CONST_RESOLVE_LEXICAL_GAPS == True:
                    corrected = resolveMismatch(termType, term, "T")
                    if corrected == True:
                        print("SUCCESS: Term mismatch corrected!")
                    else:
                        print("FAILURE: Term mismatch NOT corrected!")


def checkTermInCVs(termType, term, CVToCheck):
    # Get the list of terms from the selected CV, based on the term type
    CVTerms = CVToCheck.get(termType)
    # If the term passed in is not in the CV, return false, else return true
    if term not in CVTerms:
        return False
    else:
        return True


def paronymCheck(term, CVTermsOfType):
    # Double check that term is in the paronyms list.
    if term in paronyms:
        # If so, then check all of the term's paronyms and see if any of them are in the ontology CV.
        alternateTerms = paronyms.get(term)
        # Run through all of the alternatives and check if they're in the CV terms
        for alternative in alternateTerms:
            if alternative in CVTermsOfType:
                # If found, return
                return alternative
    # If nothing found, return nothing
    return ''


def resolveMismatch(termType, term, ontoOrThink):
    # If ontoOrThink is "O", then the mismatch occurs on the ontology level
    if ontoOrThink == "O":
        OntoCVTerms = OntoCV.get(termType)
        # Check if the term in question has paronyms - if so, check the paronyms of the term to see if any of those
        # are known
        if term in paronyms:
            paronymFound = paronymCheck(term, OntoCVTerms)
            if paronymFound != '':
                print("Paronym found for " + term + ".  The paronym is " + paronymFound + ".")
                # Add the equivalency between the paronym and the CV term.
                if term not in equivalenciesFound:
                    equivalenciesFound.update({paronymFound: term})
                return True
        # print("The ontology doesn't know " + term + ".")
        # Check for nyms of the term that would match any terms of the relevant CV type
        (CVTermFound, successfulMatchTerm) = searchForNymMatchingCV(term, OntoCVTerms)
        if successfulMatchTerm != None:
            # Add the equivalency between the new term and the found CV term.
            if term not in equivalenciesFound:
                equivalenciesFound.update({CVTermFound: successfulMatchTerm})
            OntoCV[termType].append(successfulMatchTerm)
            return True
        # If no such nyms exist, then ask the user for a new term to try
        else:
            tryCount = 0
            successfulMatch = False
            # Ask until success or 2 attempts, whichever comes first
            while successfulMatch == False and tryCount < 2:
                # Ask the user for a new term
                newTerm = requestNewTermToNymCheck(term)
                # Check if new term is in the ontology CV.
                successfulMatch = checkTermInCVs(termType, newTerm, OntoCV)
                if successfulMatch == False:
                    (CVTermFound, successfulMatchTerm) = searchForNymMatchingCV(term, OntoCVTerms)
                    if successfulMatchTerm != None:
                        # Add the equivalency between the new term and the found CV term.
                        if term not in equivalenciesFound:
                            equivalenciesFound.update({CVTermFound: successfulMatchTerm})
                        OntoCV[termType].append(successfulMatchTerm)
                        successfulMatch = True
                # Increase the number of tries
                tryCount = tryCount + 1
            return successfulMatch


    # If ontoOrThink is "T", then the mismatch occurs with the Think CV
    if ontoOrThink == "T":
        ThinkCVTerms = ThinkCV.get(termType)
        # print("Think doesn't know " + term + ".  Next steps to come.")
        # Check for nyms of the term that would match any terms of the relevant CV type
        (CVTermFound, successfulMatchTerm) = searchForNymMatchingCV(term, ThinkCVTerms)
        if successfulMatchTerm != None:
            # Add the equivalency between the new term and the found CV term.
            if term not in equivalenciesFound:
                equivalenciesFound.update({CVTermFound: successfulMatchTerm})
            ThinkCV[termType].append(successfulMatchTerm)
            return True
        # If no such nyms exist, then ask the user for a new term to try
        else:
            tryCount = 0
            successfulMatch = False
            # Ask until success or 2 attempts, whichever comes first
            while successfulMatch == False and tryCount < 2:
                # Ask the user for a new term
                newTerm = requestNewTermToNymCheck(term)
                # Check if new term is in the ontology CV.
                successfulMatch = checkTermInCVs(termType, newTerm, ThinkCV)
                if successfulMatch == False:
                    (CVTermFound, successfulMatchTerm) = searchForNymMatchingCV(term, ThinkCVTerms)
                    if successfulMatchTerm != None:
                        # Add the equivalency between the new term and the found CV term.
                        if term not in equivalenciesFound:
                            equivalenciesFound.update({CVTermFound: successfulMatchTerm})
                        ThinkCV[termType].append(successfulMatchTerm)
                        successfulMatch = True
                # Increase the number of tries
                tryCount = tryCount + 1
            return successfulMatch


def requestNewTermToNymCheck(originalTerm):
    newTerm = input("No CV terms found in the nyms for " + originalTerm
                    + ".  Please enter a new term which can be tried.")
    return newTerm


# TODO: **** NEED TO FIGURE OUT WHICH NYMS ARE APPROPRIATE
def getNyms(wordToCheck):
    # Iterate through all words to check
    synonyms = []
    hypernyms = []
    hyponyms = []
    deriv = []
    uniqueNymList = []
    uniqueAntonymList = []
    # Get synsets of current word to check
    testWord = wordnet.synsets(wordToCheck)
    # for each synset (meaning)
    for syn in testWord:
        # Get Hypernyms
        if len(syn.hypernyms()) > 0:
            currentHypernyms = syn.hypernyms()
            for hyperSyn in currentHypernyms:
                for lemma in hyperSyn.lemmas():
                    hypernyms.append(lemma.name())
        # Get Hyponyms
        if len(syn.hyponyms()) > 0:
            currentHyponyms = syn.hyponyms()
            for hypoSyn in currentHyponyms:
                for lemma in hypoSyn.lemmas():
                    hyponyms.append(lemma.name())
        # Get direct synonyms
        for lemma in syn.lemmas():
            synonyms.append(lemma.name())
            # Get derivationally related forms
            for derivForm in lemma.derivationally_related_forms():
                if derivForm.name() not in deriv:
                    deriv.append(derivForm.name())
            # Get antonyms
            if lemma.antonyms():
                if lemma.antonyms()[0].name() not in uniqueAntonymList:
                    uniqueAntonymList.append(lemma.antonyms()[0].name())
        # TODO ***** Currently cutting out hypernyms/hyponyms
        #nymLists = synonyms + hypernyms + hyponyms + deriv
        nymLists = synonyms + deriv
        uniqueNyms = set(nymLists)
        uniqueNymList = list(uniqueNyms)
    return uniqueNymList, uniqueAntonymList


def searchForNymMatchingCV(term, CVTermsOfType):
    nyms, antonyms = getNyms(term)
    # Get the set of nyms which match some CV term
    nymsThatMatchCV = list(set(CVTermsOfType).intersection(nyms))
    # If such nyms exist, then inform the user
    # TODO: **** Going to need to figure out how to "correct" the CVs to provide functionality for new term
    # Some sort of "SameAs" link between terms?
    if len(nymsThatMatchCV) > 0:
        print("FOUND A CV TERM IN " + term + "'S NYMS")
        print(nymsThatMatchCV)
        if len(nymsThatMatchCV) == 1:
            # TODO **** Figure out how to use nymsThatMatchCV[0] to
            DRSTerm = term
            CVTermFound = nymsThatMatchCV[0]
            # Return a tuple consisting of the CV Term (known term) and the new term introduced
            return CVTermFound, DRSTerm
        else:
            # TODO **** Handle multiple matching terms for the nym
            print("Multiple nyms found that match the CV - HANDLE THIS CASE")
            return None, None
    # If none of the nyms return match the CV, check if any of them have relevant paronyms
    else:
        for nym in nyms:
            # Check if the term in question has paronyms - if so, check the paronyms of the term to see if any of those
            # are known
            if nym in paronyms:
                paronymFound = paronymCheck(nym, CVTermsOfType)
                if paronymFound != '':
                    print("Paronym found for " + nym + ", a nym of " + term + ".  The paronym is " + paronymFound + ".")
                    DRSTerm = term
                    return paronymFound, DRSTerm
    # If no nyms or paronyms of nyms found, return false
    return None, None


def outputUpdatedOntoCV():
    updatedOntoCV = open(outputOntoCVFileName, "w+")
    # Iterate through ontology CV types
    for type in OntoCV:
        # Get values for current type
        valuesOfType = OntoCV.get(type)
        # For ItemDescription, handle in special case
        if type == "ItemDescription":
            for value in valuesOfType:
                # Constructing "ItemDescription :refersToItemXYZ XYZ"
                outputString = type + refersToItemXEdge + value + " " + value + '\n'
                updatedOntoCV.write(outputString)
        else:
            # For any other type, just assemble
            for value in valuesOfType:
                outputString = type + ofTypeEdge + value + '\n'
                updatedOntoCV.write(outputString)
    # Iterate through equivalencies and establish a "SameAs" relationship
    for knownTerm in equivalenciesFound:
        newTerm = equivalenciesFound.get(knownTerm)
        outputString = knownTerm + ontoEquivalencyIndicator + newTerm + '\n'
        updatedOntoCV.write(outputString)
    updatedOntoCV.close()


def outputUpdatedThinkCV():
    updatedThinkCV = open(outputThinkCVFileName, "w+")
    # Iterate through Think CV types
    for type in ThinkCV:
        # Get values for current type
        valuesOfType = ThinkCV.get(type)
        # Convert the type back to ThinkCV format
        if type in OntoToThinkMapping:
            type = OntoToThinkMapping.get(type)
        for value in valuesOfType:
            # Construction of "type_list item" format
            outputString = type + "_list " + value + '\n'
            updatedThinkCV.write(outputString)
    # TODO **** Is this a good move?
    # Add the ontology CV elements which aren't in the Think CV to Think's CV
    for type in OntoCV:
        # If current type is in the mapping between the ontology and think
        if type in OntoToThinkMapping:
            # Get the values for this type
            newValuesOfType = OntoCV.get(type)
            existingValuesOfType = ThinkCV.get(type)
            type = OntoToThinkMapping.get(type)
            for value in newValuesOfType:
                if value not in existingValuesOfType:
                    # Construct output item format
                    outputString = type + "_list " + value + '\n'
                    updatedThinkCV.write(outputString)
    # Iterate through equivalencies and establish a "SameAs" relationship
    for knownTerm in equivalenciesFound:
        newTerm = equivalenciesFound.get(knownTerm)
        outputString = thinkEquivalencyIndicator + knownTerm + " " + newTerm + '\n'
        updatedThinkCV.write(outputString)
    updatedThinkCV.close()


def main():
    # Read in the Ontology CV and parse it in
    OntoCVFile = open(OntoCVFileName, "r")
    for line in OntoCVFile:
        parseOntoCVLine(line.strip())
    # Read in the Think CV and parse it in
    ThinkCVFile = open(ThinkCVFileName, "r")
    for line in ThinkCVFile:
        parseThinkCVLine(line.strip())
    # Read in the DRS instructions and check each line against the CVs
    DRSFile = open(DRSFileName, "r")
    for line in DRSFile:
        parseDRSLine(line.strip())
    paronymFile = open(paronymListFileName, "r")
    for line in paronymFile:
        parseParonymListLine(line.strip())
    print(OntoCV)
    print('\n')
    print(ThinkCV)
    print('\n')
    print(DRSElements)
    # Now that everything is parsed in, iterate through the DRS terms passed in and see if any of them can't be found
    # in the CVs
    if CONST_DETECT_LEXICAL_GAPS == True:
        findMismatches()
    outputUpdatedOntoCV()
    outputUpdatedThinkCV()


main()