from owlready2 import *

#onto = get_ontology("file://uagent.owl").load()
onto = get_ontology("http://www.lesfleursdunormal.fr/static/_downloads/pizza_onto.owl").load()

print(list(onto.classes()))

with onto:
    print(onto.CheeseTopping.iri)
    myTopping = onto.Topping()
    print(myTopping)
    print(myTopping.name)
    print(myTopping.iri)

#with onto:
#    testAction = Action("action")