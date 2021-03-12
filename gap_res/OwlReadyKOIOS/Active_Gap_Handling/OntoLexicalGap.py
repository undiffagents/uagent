from owlready2 import *
import sys
from nltk.corpus import wordnet

sys.path.append('/mnt/t/Projects/uagent-new/ontology')
sys.path.append('/mnt/t/Projects/uagent-new/lib')

from ontology import Ontology

owlReadyOnto = get_ontology("http://localhost:3030/uagent-initialized").load()

ontoClass = Ontology()

# What we want to do as a first pass here is take in a word from the command line arguments and search through the
# ontology to see if we find a node that contains that word.  If so, we return it.  If not, we kick it back to WordNet
# and try to find a related term.

# If we have a command line argument, then we use that as our search term
# For now we only work on one words
def start_up():
    if len(sys.argv) > 1:
        search_term = sys.argv[1]
    else:
        print("Please run this program with a single word to be searched for as a command line argument.")
        exit(0)

    # Get the classes, individuals, and roles from the DLGraph queries in order to get a list of all of the named
    # items and actions in the ontology
    # TODO **** Find some way to remove duplicates?  Or maybe if something is in each type, we want that to be known
    # Storing ontology DL Graph terms here so that only one query needs to happen instead of in every search
    ontologyTerms = {}
    ontologyTerms.update({"classes": ontoClass.getDLGraphClasses()})
    ontologyTerms.update({"roles": ontoClass.getDLGraphRoles()})
    ontologyTerms.update({"individuals": ontoClass.getDLGraphIndividuals()})

    # Search for the keyword in the lists of classes, roles, and individuals
    (termFoundInClasses, termFoundInRoles, termFoundInIndividuals) = search_for_term(search_term, ontologyTerms)

    # Print out the results of the search (found (if so, where) or not)
    found = print_results_of_search(termFoundInClasses, termFoundInRoles, termFoundInIndividuals, search_term, True)

    # If not found, then search Wordnet for related terms and check the ontology for each of those terms
    if found is False:
        (uniqueNymList, uniqueAntonymList) = wordnet_query_for_term(search_term)
        print(uniqueNymList)

        for nym in uniqueNymList:
            # Search and print results
            (nymFoundInClasses, nymFoundInRoles, nymFoundInIndividuals) = search_for_term(nym, ontologyTerms)
            print_results_of_search(nymFoundInClasses, nymFoundInRoles, nymFoundInIndividuals, nym, False)


def search_for_term(target, ontologyTerms):
    #for node in ontology.individuals():
    #    print(node)
    #    print(node.get_properties())
    termFoundInClasses = ""
    termFoundInRoles = ""
    termFoundInIndividuals = ""

    # Track where the search term is found, if at all
    if target in ontologyTerms.get("classes"):
        termFoundInClasses = target
    if target in ontologyTerms.get("roles"):
        termFoundInRoles = target
    if target in ontologyTerms.get("individuals"):
        termFoundInIndividuals = target

    # print(ontologyTerms)
    return (termFoundInClasses, termFoundInRoles, termFoundInIndividuals)


def print_results_of_search(termFoundInClasses, termFoundInRoles, termFoundInIndividuals, search_term, initial_search):
    # If the term was found somewhere in the ontology, output such
    if termFoundInClasses != "":
        print("found \"" + search_term + "\" in list of classes")
    if termFoundInRoles != "":
        print("found \"" + search_term + "\" in list of roles")
    if termFoundInIndividuals != "":
        print("found \"" + search_term + "\" in list of individuals")

    # If not, state that it was not found and move on to WordNet search (only do this for the initial term, not nyms)
    if termFoundInRoles == "" and termFoundInClasses == "" and termFoundInIndividuals == "" and initial_search is True:
        print("Search term \"" + search_term + "\" not found in the ontology - querying WordNet for related terms")
        # Return false if not found, for easy tracking
        return False

    # Return true otherwise
    return True

# Ripped straight from KOIOS
def wordnet_query_for_term(search_term):
    # Iterate through all words to check
    synonyms = []
    hypernyms = []
    hyponyms = []
    deriv = []
    uniqueNymList = []
    uniqueAntonymList = []
    # Get synsets of current word to check
    testWord = wordnet.synsets(search_term)
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
        nymLists = synonyms + hypernyms + hyponyms + deriv
        uniqueNyms = set(nymLists)
        uniqueNymList = list(uniqueNyms)
    return (uniqueNymList, uniqueAntonymList)


start_up()