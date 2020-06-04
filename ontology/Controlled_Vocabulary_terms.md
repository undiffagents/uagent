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

## THINK CV
Terms explicitly defined within uagent/uagent.py
(XX) indicates terms not defined in the Ontology
- action_list
	- press (XX)
	- click
	- remember (XX)
- condition_list (basically affordance in Ontology at the moment)
	- appearsOn (XX)
	- visible (treated identically to appearsOn for now)
- item_role_list
	- target
	- stimulus
	- distractor
	- responseButton
	- infoButton
- agent_synonym_list (XX) (terms that let the UAgent know it is the subject of an action/rule/whatever)
	- subject
	- participant
	- you

## Potential CV Additions
CV terms likely to be necessary, which can be added to existing Ontology structures.

- Action; :ofType
	- typing
	- pressing
	CK: what about more general actions (responding), which are then mapped with other words?
- Affordance; :ofType
	- pressable
	- typable (??)


## Potential CV Expansions
CV terms likely to be necessary, but which would require Ontology alterations (new classes)
- Agent Identifiers
	- Subject
	- Participant
	- ?
- Sensory Mapping
	- appearsOn - > visible, etc
























