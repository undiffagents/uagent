# KOIOS
Knowledge Gap identification and resolution prototype

## Setup

Ensure necessary dependencies are installed (running setup.sh _should_ install necessary dependencies, but I'm somewhat unsure about that; also it might not work too well on Windows)
Dependencies used are:

- requests
- json
- re
- networkx
- nltk
- ssl

Run setup_nltk.py to get the NLTK packages used in KOIOS.

# Running

Set configuration settings in ControlPanel.py 

- Which gaps to identify/resolve
- Which input file to use

Run DRSProcessing.py.  At this point, the input file should be processed into a network-based graph (which will be output in GraphML and JSON formats upon proper exit).

Query the knowledge system by entering ACE questions in the terminal.  KOIOS should return Yes/No/Unknown, as well as any identified gaps.

To end the program run and output the knowledge graph, type 'exit' into the terminal when prompted for a new question.

# Sample Question Battery
## PVT
- Is the task active?

- Is the task inactive?

- Is the task ongoing?

- Is the computer active?

- Is the computer ongoing?

- Is Psychomotor-Vigilance active?

- Does the subject click the button?

- Does the subject click Acknowledge?

- Does the subject remember the letter?

- Is there a task?

- Does the target appear?

- Is the target the task?

- Does the box remember the letter?

- Does the subject ask the letter?

## Visual Search

- Does the target match the letter?

- Does the letter match the target?

- Is the target the letter?

- Is there a key?

- Is p:R pressed?