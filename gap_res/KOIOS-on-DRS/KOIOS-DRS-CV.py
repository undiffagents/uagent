# Handle object(itemRole), predicate(Action) for now?
# Does it matter if something is part of a conditional?
# This is super primitive first pass

# Onto-to-Think CV mappings need to match up
# For now, hardcoding a mapping from one to the other

from nltk.corpus import wordnet

ThinkToOntoMapping = {'action': 'Action', 'condition': 'Affordance', 'item_role': 'ItemRole'}
DRSToCVMapping = {'object': 'ItemRole', 'predicate': 'Action'}

# These terms are currently being hardcoded to ignore because they're quite generic (or in the case of na, invalid)
# This may be a problem long-term?
# TODO ****
DRSIgnoredTerms = ['na', 'be', 'have']

DRSFileName = 'PVT.txt'
OntoCVFileName = 'OntoCV.txt'
ThinkCVFileName = 'ThinkCV.txt'

OntoCV = {}
ThinkCV = {}
DRSElements = {}


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
    for elementType in DRSElements:
        # Get all items of that type from the DRS
        DRSTerms = DRSElements.get(elementType)
        # Get all items of that type from both the ontology and think CVs.
        # (Should these be treated as one or separately?  Would it be beneficial to know whether the ontology knows a
        # term and Think doesn't or vice versa?
        # TODO ****
        OntoCVTerms = OntoCV.get(elementType)
        ThinkCVTerms = ThinkCV.get(elementType)
        # Iterate through all of the terms in the DRS
        for term in DRSTerms:
            # If the ontology doesn't know the term, inform the user of such
            # TODO: **** This is probably where WordNet would come in and kick back appropriate nyms.
            # The question then is which nyms are appropriate and
            if term not in OntoCVTerms:
                resolveMismatch(term, "O", OntoCVTerms)
            # If Think doesn't know the term, also inform the user of that
            if term not in ThinkCVTerms:
                resolveMismatch(term, "T", ThinkCVTerms)


def resolveMismatch(term, ontoOrThink, CVTermsOfSameType):
    # If ontoOrThink is "O", then the mismatch occurs on the ontology level
    if ontoOrThink == "O":
        print("The ontology doesn't know " + term + ".  Next steps to come.")
        nyms, antonyms = getNyms(term)
        #print(term, nyms, antonyms)
        nymsThatMatchCV = set(CVTermsOfSameType).intersection(nyms)
        if len(nymsThatMatchCV) > 0:
            print("FOUND A CV TERM IN " + term + "'S NYMS")
            print(nymsThatMatchCV)
    # If ontoOrThink is "T", then the mismatch occurs with the Think CV
    if ontoOrThink == "T":
        print("Think doesn't know " + term + ".  Next steps to come.")
        nyms, antonyms = getNyms(term)
        #print(term, nyms, antonyms)
        nymsThatMatchCV = set(CVTermsOfSameType).intersection(nyms)
        if len(nymsThatMatchCV) > 0:
            print("FOUND A CV TERM IN " + term + "'S NYMS")
            print(nymsThatMatchCV)


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
    print(OntoCV)
    print('\n')
    print(ThinkCV)
    print('\n')
    print(DRSElements)
    # Now that everything is parsed in, iterate through the DRS terms passed in and see if any of them can't be found
    # in the CVs
    findMismatches()

main()