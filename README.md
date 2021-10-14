# uagent
Full Undifferentiated Agent, v1. README last updated: 10/4/2021.

## Git Logistics

Develop is the main branch from which we'll be working, where all the features/modules will be integrated to create the full UA. Each individual feature will be worked on it's own branch. When a feature is ready to be merged into develop, submit a pull (merge) request on github (and preferably, let the curator -- currently Colin -- know on Slack).

Master will be the 'release' branch -- representing bigger, stables changes across develop

## Dependencies

Verified 2021/09/24; some packages have newer versions, be careful to install the designated version to ensure compatibility.

- /input/APE/ must be setup on each machine
	- Install SWI-Prolog - http://www.swi-prolog.org
	- Compile APE: within the /input/APE/ directory, 'make install' on unix, 'make_exe.bat' on windows
- Python (3.7.4) - most of the code is in Python
- Java (11.0.5) - for input processing
- Ruby (2.5.1p57) - for input processing

## Testing Interpreter & Ontology loading

- Interpreter & Ontology
	- interpreter.py allows for direct testing of ACE instruction interpretation, independently from full UAgent simulation.
		- python3 interpreter/interpreter.py --ace "ACEFILE.TXT"
	- Running this tests if the ACE can be interpreted correctly, and further, if the processed information can be instatiated within the triple-store

## Running a full UAgent simulation

- /uagent/uagent.py
	- This is where the UAgent 'lives' so to speak. This file contains the primary functionality of the UAgent, including cognition, enviromental interactions, and other behaviors.  
	- Processes ACE input to populate the Ontology, then instantiates a local query server. (Note: if run from terminal, said server runs until manually killed). See comments in script for manual query example.

## Running a Targeted Knowledge Gap Test

- bash gaptest.sh --GAPNAME
	- Gap testing limited to PVT currently. Must be stored as .txt files in the tasks/pvt/gaptests/ folder. 
	- Creates logfiles for: Console output (including thrown errors), Interpreter processing, and Think behavior simulation. All stored in data/logs/

## Modules
	
- agents

- ares
	- Purpose: Integration and training of UAgent in ARES framework
	- Primaries: Colin, Daylond, Benji

- ares/cake
	- Purpose: Print cakes. Parlay UAgent processing/learning capabilities to act as experimenter controlling an ARES experiment campaign.
	- Primaries: ? Pascal, Cogan ?

- gap_res (DEPRECATED as DS left team)
	- Purpose: Knowledge Gap Resolution
	- Primaries: Aaron, Daniel

- input
	- Purpose: Instruction Understanding. Processes input in the form of Attempto Controlled English (ACE), in order to populate the Ontology. Checks instructions with simple reasoner to see if they make sense.
	- Primaries: Aaron, Stevens

- ontology (+DaSe API)
	- Purpose: Formalized structure of UAgent "knowledge." The DaSe API is how other modules will interact with the OntologyDB.
	- Primaries: Cogan, Aaron (Pascal?)

- tasks
	- Purpose: Tasks to be run by the UA
	- Primaries: Dario, Olivia, Stevens (Colin?)

- think
	- Purpose: The Think architecture, an adaptation of ACT-R to be run in Python.
	- Primaries: Dario (+Colin, later)

- uagent
	- Purpose: primary runfiles for the UAgent. Primarily uagent.py, which has the UndifferentiatedAgent class
	- Primaries: Dario (+Colin)

## Other Directories

- lib
	- Directory for tools used by the UA, including APE and Fuseki (for Ontology server functions).

- run
	- Directory used as the local 'server' for the in input process. (The agent runfiles are now in /agents/).

- webapp
	- Used in input processing.














