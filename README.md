# uagent
Full Undifferentiated Agent, v1

Git Logistics:

Develop is the main branch from which we'll be working, where all the features/modules will be integrated to create the full UA. Each individual feature will be worked on it's own branch. When a feature is ready to be merged into develop, submit a pull (merge) request on github (and preferably, let the curator -- currently Colin -- know on Slack).

Master will be the 'release' branch -- representing bigger, stables changes across develop

Running Agents:

	run/pvt_ua1.py
		Execute: python3 run/pvt_ua1.py (that is, run it from the base uagent directory).
		The main runfile, acting as the 'master' process. It instantiates the think uagent and runs it for the PVT.

	run/pvt_non_ua.py
		Runs the non-undiff PVT agent. (Again, execute from base uagent directory).

Modules:
	
	ares
		Purpose: Integration and training of UAgent in ARES framework
		Primaries: Colin, Daylond, Benji

	ares/cake
		Purpose: Print cakes. Parlay UAgent processing/learning capabilities to act as experimenter controlling an ARES experiment campaign.
		Primaries: ? Pascal, Cogan ?

	gap_res
		Purpose: Knowledge Gap Resolution
		Primaries: Aaron, Daniel

	inst_process
		Purpose: Instruction Understanding. Processes input in the form of Attempto Controlled English (ACE), in order to populate the Ontology
		Primaries: Aaron, Stevens

	ontology (+DaSe API)
		Purpose: Formalized structure of UAgent "knowledge." The DaSe API is how other modules will interact with the OntologyDB.
		Primaries: Cogan, Aaron (Pascal?)

	tasks
		Purpose: Tasks to be run by the UA
		Primaries: Dario, Olivia, Stevens (Colin?)

	think
		Purpose: The Think architecture, an adaptation of ACT-R to be run in Python.
		Primaries: Dario (+Colin, later)

	ua
		Purpose: Code specifically for the UAgent. Currently just ua.py, which has the UndifferentiatedAgent class (for use with Think).
		Primaries: Dario (+Colin)















