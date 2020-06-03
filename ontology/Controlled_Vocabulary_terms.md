# Controlled Vocabulary Terms
Description of the Controlled Vocabulary used by the UAgent. In particular, these terms serve as a form of language grounding. 


## Ontology defined Controlled Vocabulary (CV):
Format:
- Class :link (triple describing parent if appropriate)
	- CV term1
___ indicates the CV term is used in the link description.

- Action :ofType
	- clicking
	- reading
	- retrieving
	- searching
	- listening-for
	- watching-for
- ItemDescription :refersToItem____
	- Location 
	- Color
	- Shape
	- Type
- ItemRole :ofType
	- target
	- stimulus
	- distractor
	- responseButton
	- infoButton
- Affordance :ofType (Item :affords :Affordance)
	- clickable
	- searchable
	- retrievable
	- findable
	- audible
	- visible


## Potential CV Additions
CV terms likely to be necessary, which can be added to existing Ontology structures.

- Action; :ofType
	- typing
	- pressing
	- ?
	CK: what about more general actions (responding), which are then mapped with other words?
- Affordance; :ofType
	- pressable
	- typable (??)
	- ?


## Potential CV Expansions
CV terms likely to be necessary, but which would require Ontology alterations (new classes)
- Agent Identifiers
	- Subject
	- Participant
	- ?
- Sensory Mapping
	- appearsOn - > visible, etc
























