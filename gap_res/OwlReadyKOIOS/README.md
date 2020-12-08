AARON:

    In one WSL window, run 'bash start_server.sh' in uagent-new
    In another window, run 'python3 run.py' in uagent-new to run Think (I think this loads some information into the ontology, but I'm uncertain)
   Then go to gap_res/OwlReadyKOIOS and run 'python3 owlReadyInitializer.py'.  This should initialize a bunch of data into uagent-initialized on the Jena Fuseki server.

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