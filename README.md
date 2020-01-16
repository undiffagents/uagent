# uagent
Full Undifferentiated Agent, v1


Files:

	uagent.py
		The main runfile, acting as the 'master' process. It instantiates a think-agent and runs an experimental task, calling upon other modules as appropriate. Loosely, this is the 'executive control' of the UAgent. 

	README.md
		Inception.

Modules:
	
	ares
		Purpose: Integration and training of UAgent in ARES framework
		Primaries: Colin, Daylond, Benji

	cake
		Purpose: Print cakes. Idea is to parlay the UAgent's processing and learning capabilities into a new type of UAgent (MARS?) that can act as the experimenter controlling an ARES experiment campaign.
		Primaries: ? Pascal, Cogan ?

	gap-res
		Purpose: Knowledge Gap Resolution
		Primaries: Aaron, Daniel

	inst-process
		Purpose: Instruction Understanding. Processes input in the form of Attempto Controlled English (ACE), in order to populate the OntologyDB
		Primaries: Aaron, Stevens

	inst-exec-learn
		Purpose: Executing instructions in the UA, and allowing the UA to "learn"
		Primaries: Dario (+Colin, later)

	ontology-db (+DaSe API)
		Purpose: Formalized structure of UAgent "knowledge." The DaSe API is how other modules will interact with the OntologyDB.
		Primaries: Cogan, Aaron (Pascal?)

	task
		Purpose: Tasks to be run by the UA
		Primaries: Olivia, Stevens (Dario, Colin?)

	think-ua
		Purpose: The think architecture, an adaptation of ACT-R to be run in Python.
		Primaries: Dario (+Colin, later)

	trained-agents
		Purpose: External agents (hand-coded, etc) to allow for active comparisons of the UAgent to more traditional 
		Primaries: Stevens















