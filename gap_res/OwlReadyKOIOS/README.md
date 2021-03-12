AARON:

Basic workflow for this (on my machine, and possibly including unnecessary steps, I haven't fully vetted it):
    In one WSL window, run 'python3 interpreter/interpreter.py' in uagent-new
    In another window, run 'python3 gap_res/OwlReadyKOIOS/dlGraphInitializer.py' to instantiate data into the knowledge graph
    Finally, for context gap validation, run 'python3 gap_res/OwlReadyKOIOS/Passive_Gap_Handling/OntoContextGap.py' in uagent-new.
    For lexical gaps, run 'python3 gap_res/OwlReadyKOIOS/Active_Gap_Handing/OntoLexicalGap.py' with one command line argument, which will be the search term.
    	In order to run this, you may need to run 'pip3 install nltk' and 'python3 gap_res/setup_nltk.py' for Wordnet

IGNORE BELOW

Nothing much here yet, just trying to compile all of the gap_res work into one spot.

Context gaps are automatically identified if the control for that is enabled.
If user interaction is enabled, then questions may be asked of the system.  Currently, the question format is limited to hand-entering interpreter-format data, which will then be attempted to be found.

Currently also limited to only items, i.e. item(button)/item(button,space_bar) or item(computer), which will succeed and fail, respectively.

Current querying options with successful examples:
Existence of item by role: item(button)
Existence of item by role and name: item(button,space_bar)
Existence of item by name only: item(,space_bar)
Names of item with given role: item(button,?)
Roles of item with given name: item(?,space_bar)

To get failures, just change the terms to something which is not within the ontology (e.g., role: "computer" or name: "enter")