# Controlled Vocabulary Terms
Controlled vocabulary attempt for Aaron/Colin to work towards ontology instantiation and Think integration

# Terms which need to be known for an initial pass

psychomotor-vigilance
task
screen
space_bar
button
subject
letter
active
appears
presses
hasProperty
in
on
be
be_in
clickable
visible


# Ontology schema mapping

Psychomotor-Vigilance - ISR-MATB Task name
task - ISR-MATB Task
screen - ISR-MATB Location (??)
space_bar - Item
button - ItemRole
subject - ??? (not really a slot for this in the schema, Item maybe?)
letter - Item, ItemRole (?)
active - Property (no slot for property anywhere in the schema?)
appears - Action
presses - Action
hasProperty - Link between task and property (again, no property slot)
in - modifier, specifies that an item is in a location (refersToItemLocation: target of the "in"?)
on - similar to in
be - "is".  Establishes that something is equivalent to or has some value or property
be_in - same as in
clickable - Affordance for the button/space_bar
visible - Affordance for the letter, possible the screen


# Synonyms

screen: canvas
space_bar: space, acknowledge, response
button: key
letter: target, stimulus
appears: appear, show, shows
presses: press, click, clicks, push, pushes
subject: agent, you, participant


# Necessary Think CV/functions

Search (visual attention: looking for a letter to appear on the screen)
Click/Press (manual: press a button/clickable object)
appearsOn - needs to inform the agent that something has appeared and where?
visible - recognize something that is/can be on the screen
clickable - recognize something that can be pressed manually
subject/agent/you/participant - self-awareness to know that an instruction involves an agent action
target/stimulus - recognize something as the goal/trigger in a task
button - recognize the button that needs pressed (may be subsumed/superclassed by clickable)