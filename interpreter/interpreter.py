import os
import re
import subprocess
import sys

sys.path.insert(1, os.getcwd()+'/ontology')
from ontology import Ontology

class Term:

    def __init__(self,term,*args):
        self.term = self.makeTerm(term)
        self.args = [self.makeTerm(arg) for arg in args]

    def copy(self):
        return Term(self.term,*self.args)
        
    def isInt(s):
        try: 
            s = int(s)
            return s
        except ValueError:
            return False

    def isFloat(s):
        try: 
            s = float(s)
            return s
        except ValueError:
            return False    

    def makeTerm(self,arg):
        if isinstance(arg,Term):
            return arg
        if i := Term.isInt(arg):
            return i
        if f := Term.isFloat(arg):
            return f
        if m := re.match("string\((.*)\)",arg):
            return "'" + m.groups()[0] + "'"
        if m := re.match("named\((.*)\)",arg): 
            return m.groups()[0]
        return arg
    
    def getTerm(self):
        return self.term
    
    def getArgs(self):
        return self.args
    
    def arg(self,i):
        return self.args[i]
    
    def tripleString(self):
        raise

    def __str__(self):
        return str(self.term)

    def __repr__(self):
        return str(self.term)

class Variable(Term):

    def __init__(self,name,*args):
        if not re.match("^([A-Z][0-9]*)$",name):
            raise Exception("Not a DRS variable")
        self.term = self.makeTerm(name)
        self.args = [self.makeTerm(arg) for arg in args]
    
    def tripleString(self):
        return 'a :Variable ; :asString "'+str(self.term) + '"'    

class Function(Term):

    def __init__(self,name,*args):
        self.term = self.makeTerm(name)
        self.args = [self.makeTerm(arg) for arg in args]
    
    def getTerm(self):
        return self

    def tripleString(self):
        return ' a :Function '+(' ; '.join([':hasTerm :'+str(arg) for arg in self.args]) if len(args) > 1 else ' ; :hasTerm :'+str(args[0]))
    
    def __str__(self):
        return str(self.term) + ("" if len(self.args) == 0 else ("(" + ",".join([str(x) for x in self.args]) + ")"))

    def __repr__(self):
        return str(self.term) + ("" if len(self.args) == 0 else ("(" + ",".join([str(x) for x in self.args]) + ")"))

class Constant(Function):

    def __init__(self,name,*args):
        if not isinstance(name,int) and not isinstance(name,float) and re.match("^([A-Z][0-9]*)$",name):
            raise Exception("Not a DRS constant")
        self.term = self.makeTerm(name)
        self.args = [self.makeTerm(arg) for arg in args]  

    def getTerm(self):
        return self.term
    
    def tripleString(self):
        return 'a :Constant ; :asString "' + str(self.term) + '"'    
    
class Predicate:
    '''Corresponds to a prolog predicate arity > 2'''

    def __init__(self,name,*args):
        self.name = Constant(name)
        self.args = []
        for arg in args:
            if isinstance(arg,Term): self.args.append(arg)
            elif Term.isInt(arg): self.args.append(Constant(arg))
            elif Term.isFloat(arg): self.args.append(Constant(arg))
            elif re.match("^([A-Z][0-9]*)$",arg): self.args.append(Variable(arg))
            else: self.args.append(Constant(arg))

    def copy(self):
        return Predicate(self.getName(),*self.getArgs())
        
    def getName(self):
        return self.name.getTerm()

    def arg(self,i):
        return self.args[i].getTerm()

    def getArgs(self):
        return [x.getTerm() for x in self.args]

    def __str__(self):
        return str(self.name) + "(" + (",".join([str(x) for x in self.args]) if len(self.args) > 1 else str(self.args[0])) + ")"

    def __repr__(self):
        return str(self.name) + "(" + (",".join([str(x) for x in self.args]) if len(self.args) > 1 else str(self.args[0])) + ")"

class PredicateList:
    '''List of DRS predicates'''

    def __init__(self):
        self.preds = []

    def append(self,pred):
        if not isinstance(pred,Predicate): 
            raise Exception("Must append Predicates to PredicateList")
        self.preds.append(pred)

    def remove(self,pred):
        if not isinstance(pred,Predicate): 
            raise Exception("Must remove Predicates from PredicateList")
        self.preds.remove(pred)

    def removeAt(self,i):      
        self.preds.pop(i)    

    def getPredicates(self):
        return self.preds

    def predicate(self,i):
        return self.preds[i]
    
    def __len__(self):
        return len(self.preds)    

    def __str__(self):        
        return "[" + ",".join([str(x) for x in self.preds]) + "]"

    def __repr__(self):
        return "[" + ",".join([str(x) for x in self.preds]) + "]"

class Class(Predicate):
    '''Corresponds to both a Descrioption logic Class and a prolog predicate arity /1 read from DRS'''
    def __init__(self,indent,letter,name,inst,num1,num2):
        super().__init__(name,inst,num1,num2)
        self.indent = Constant(indent)
        self.letter = Variable(letter)
        
    def copy(self):
        return Class(self.getIndent(),self.getLetter(),self.getName(),*self.getArgs())              
        
    def getIndent(self):
        return self.indent.getTerm()
    
    def getLetter(self):
        return self.letter.getTerm()
    
    def tripleString(self):
        return 'a :Predicate ; :hasName "' + str(self.getName()) + '" ; :hasArity 1 ; :hasTerm ['+self.args[0].tripleString()+'] ; :asString "'+str(self)+'"'
    
    def getDLName(self):
        return ':'+str(self.getName())
    
    def dlTripleString(self):
        name = self.getDLName()
        return name + ' a owl:Class . :'+str(self.args[0])+' a '+name+' ; a owl:NamedIndividual . '

    def __str__(self):
        return str(self.name) + "(" + str(self.args[0]) + ")"

    def __repr__(self):
        return str(self.name) + "(" + str(self.args[0]) + ")"

class Role(Predicate):
    '''Corresponds to both a Descrioption logic Role and a prolog predicate arity /2 read from DRS'''
    
    def __init__(self,indent,letter,name,subj,obj,num1,num2):
        super().__init__(name,subj,obj,num1,num2)
        self.indent = Constant(indent)
        self.letter = Variable(letter)       

    def copy(self):
        return Role(self.getIndent(),self.getLetter(),self.getName(),*self.getArgs())
    
    def getIndent(self):
        return self.indent.getTerm()
    
    def getLetter(self):
        return self.letter.getTerm()
    
    def tripleString(self):
        return 'a :Predicate ; :hasArity 2 ; :hasName "' + str(self.getName()) + '" ; :hasTerm ['+self.args[0].tripleString()+'] ; :hasTerm ['+self.args[1].tripleString()+'] ; :asString "'+str(self)+'"'
    
    def getDLName(self):
        if not isinstance(self.arg(1),Preposition):
            return ':'+self.getName()
        return ':'+self.getName()+self.arg(1).term[0].capitalize()+self.arg(1).term[1:].lower()
    
    def dlTripleString(self):
        name = self.getDLName()
        arg = str(self.arg(1)) if not isinstance(self.arg(1),Preposition) else str(self.arg(1).arg(0))
        return name + ' a owl:ObjectProperty . :'+self.arg(0)+' '+name+' :'+arg+' ; a owl:NamedIndividual . :'+arg+' a owl:NamedIndividual . '
    
    def __str__(self):
        return str(self.name) + "(" + str(self.args[0]) + "," + str(self.args[1]) + ")"

    def __repr__(self):
        return str(self.name) + "(" + str(self.args[0]) + "," + str(self.args[1]) + ")"

class PropertyRole(Role):
    
    def __init__(self,indent,letter,subj,obj,num1,num2):
        super().__init__(indent,letter,'hasProperty',subj,obj,num1,num2)
    
    def copy(self):
        return PropertyRole(self.getIndent(),self.getLetter(),*self.getArgs())    
    
    def getIndent(self):
        return self.indent.getTerm()
    
    def getLetter(self):
        return self.letter.getTerm()    

class TernaryPredicate(Predicate):
    '''Corresponds to a prolog predicate arity /3 read from DRS'''
    
    def __init__(self,indent,letter,name,subj,iobj,dobj,num1,num2):
        super().__init__(name,subj,iobj,dobj,num1,num2)
        self.indent = Constant(indent)
        self.letter = Variable(letter)        

    def copy(self):
        return TernaryPredicate(self.getIndent(),self.getLetter(),self.getName(),*self.getArgs())
    
    def getIndent(self):
        return self.indent.getTerm()
    
    def getLetter(self):
        return self.letter.getTerm()
    
    def tripleString(self):
        return 'a :Predicate ; :hasArity 3 ; :hasName "' + str(self.getName()) + '" ; :hasTerm ['+self.args[0].tripleString()+'] ; :hasTerm ['+self.args[1].tripleString()+'] ; :hasTerm ['+self.args[2].tripleString()+'] ; :asString "'+str(self)+'"'
    
    def dlTripleString(self):
        raise
    
    def __str__(self):
        return str(self.name) + "(" + str(self.args[0]) + "," + str(self.args[1]) + "," + str(self.args[2]) + ")"

    def __repr__(self):
        return str(self.name) + "(" + str(self.args[0]) + "," + str(self.args[1]) + "," + str(self.args[2]) + ")"

class Object(Constant):
    '''DRS object'''
    def __init__(self,indent,letter,name,quant,stuff1,stuff2,stuff3,num1,num2):
        super().__init__(name,quant,stuff1,stuff2,stuff3,num1,num2)
        self.indent = self.makeTerm(indent)
        self.letter = self.makeTerm(letter)
        
    def getIndent(self):
        return self.indent
    
    def getLetter(self):
        return self.letter
    
    def tripleString(self):
        return 'a :Constant ; :hasName "'+str(self.term) + '" ; :asDRSString '+'"{}object({},{},{})-{}/{}"'.format(self.indent,self.letter,self.term,','.join([str(x) for x in self.args[:-2]]),self.args[-2],self.args[-1])
    
    def copy(self):
        return Object(self.indent,self.letter,self.term,*self.args)
    
    def __str__(self):
        return "'" + str(self.term) + "':" + str(self.letter)

    def __repr__(self):
        return "'" + str(self.term) + "':" + str(self.letter)   

class ObjectList:
    '''List of DRS objects'''

    def __init__(self):
        self.objs = []
        self.var = {}

    def reset(self):
        self.objs = []
        self.var = {}

    def append(self,obj):
        if not isinstance(obj,Object): 
            raise Exception("Must append Objects to ObjectList")
        self.objs.append(obj)

        if obj.letter not in self.var: 
            self.var[obj.letter] = obj.term

    def remove(self,obj):
        if not isinstance(obj,Object): 
            raise Exception("Can only remove Objects from ObjectList")        
        self.objs.remove(obj)
        del self.var[obj.letter]
        for obj in self.objs:
            if obj.letter.term not in self.var:
                self.var[obj.letter] = obj.term

    def removeAt(self,i):      
        self.objs.pop(i)  

    def getObjects(self):
        return self.objs

    def object(self,i):
        return self.objs[i]   

    def nameDictionary(self):
        return self.var

    def __len__(self):
        return len(self.objs)
    
    def __str__(self):        
        return "[" + ",".join([str(x) for x in self.objs]) + "]"

    def __repr__(self):
        return "[" + ",".join([str(x) for x in self.objs]) + "]"

class Property(Constant):
    '''DRS property.'''
    def __init__(self,indent,letter,name,type,num1,num2):
        super().__init__(name,type,num1,num2)
        self.indent = self.makeTerm(indent)
        self.letter = self.makeTerm(letter)
        
    def getIndent(self):
        return self.indent
    
    def getLetter(self):
        return self.letter
    
    def copy(self):
        return Property(self.indent,self.letter,self.term,*self.args)
    
    def tripleString(self):
        return 'a :Constant ; :hasName "'+str(self.term) + '" ; :asDRSString '+'"{}property({},{},{})-{}/{}"'.format(self.indent,self.letter,self.term,','.join([str(x) for x in self.args[:-2]]),self.args[-2],self.args[-1])
    
    def __str__(self):
        return "'" + str(self.term) + "':" + str(self.letter)

    def __repr__(self):
        return "'" + str(self.term) + "':" + str(self.letter)       
    
class PropertyList:
    '''List of DRS properties'''

    def __init__(self):
        self.props = []
        self.var = {}

    def append(self,prop):
        if not isinstance(prop,Property): 
            raise Exception("Must append Properties to PropertyList")
        self.props.append(prop)
        if not prop.letter in self.var: 
            self.var[prop.getLetter()] = prop.term

    def remove(self,prop):
        if not isinstance(prop,Property): 
            raise Exception("Must remove Properties from PropertyList")
        self.props.remove(prop)
        del self.var[prop.letter]
        for prop in self.props:
            if prop.letter not in self.var:
                self.var[prop.getLetter()] = prop.term

    def removeAt(self,i):      
        self.props.pop(i)    

    def getProperties(self):
        return self.props

    def property(self,i):
        return self.props[i]

    def nameDictionary(self):
        return self.var
    
    def __len__(self):
        return len(self.props)    

    def __str__(self):        
        return "[" + ",".join([str(x) for x in self.props]) + "]"

    def __repr__(self):
        return "[" + ",".join([str(x) for x in self.props]) + "]"

class Relation(Class):
    '''DRS relation'''
    def __init__(self,indent,letter,name,to,num1,num2):
        super().__init__(indent,letter,name,to,num1,num2)
    
    def tripleString(self):
        raise  
    
    def copy(self):
        return Relation(self.getIndent(),self.getLetter(),self.getName(),*self.args)    

    def getIndent(self):
        return self.indent.getTerm()
    
    def getLetter(self):
        return self.letter.getTerm()
    
class RelationList:
    '''List of DRS relations'''

    def __init__(self):
        self.rels = []

    def append(self,rel):
        if not isinstance(rel,Relation): 
            raise Exception("Must append Relations to RelationList")
        self.rels.append(rel)

    def remove(self,rel):
        if not isinstance(rel,Relation): 
            raise Exception("Must remove Relations from RelationList")
        self.rels.remove(rel)    

    def removeAt(self,i):      
        self.preps.pop(i)

    def getRelations(self):
        return self.rels

    def relation(self,i):
        return self.rels[i]   

    def __len__(self):
        return len(self.rels)
    
    def __str__(self):        
        return "[" + ",".join([str(x) for x in self.rels]) + "]"

    def __repr__(self):
        return "[" + ",".join([str(x) for x in self.rels]) + "]"

class Preposition(Function):
    '''DRS relation'''
    def __init__(self,indent,letter,name,to,num1,num2):
        super().__init__(name,to,num1,num2) 
        self.indent = self.makeTerm(indent)
        self.letter = self.makeTerm(letter)

    def getIndent(self):
        return self.indent
    
    def getLetter(self):
        return self.letter
    
    def tripleString(self):
        if re.match("^([A-Z][0-9]*)$",self.arg(0)):
            string = 'a :Variable ; :asString "'+str(self.args[0])+'"'
        else:
            string = 'a :Constant ; :asString "'+str(self.args[0])+'"'
        return 'a :Function ; :asString "'+str(self)+'" ; :hasName "'+str(self.term)+'" ; :hasTerm ['+string+']'  
    
    def copy(self):
        return Preposition(self.indent,self.letter,self.term,*self.args)
    
    def __str__(self):
        return self.term + "(" + self.args[0] + ")"

    def __repr__(self):
        return self.term + "(" + self.args[0] + ")"

class PrepositionList:
    '''List of DRS prepositions'''

    def __init__(self):
        self.preps = []

    def append(self,prep):
        if not isinstance(prep,Preposition): 
            raise Exception("Must append Prepositions to PrepositionList")
        self.preps.append(prep)

    def remove(self,prep):
        if not isinstance(prep,Preposition): 
            raise Exception("Can only remove Prepositions from PrepositionList")        
        self.preps.remove(prep)

    def removeAt(self,i):      
        self.preps.pop(i)    

    def getPrepositions(self):
        return self.preps

    def preposition(self,i):
        return self.preps[i]
    
    def __len__(self):
        return len(self.preps)    

    def __str__(self):        
        return "[" + ",".join([str(x) for x in self.preps]) + "]"

    def __repr__(self):
        return "[" + ",".join([str(x) for x in self.preps]) + "]"

class Expression:
    '''One DRS expression, composed of DRS components'''

    def __init__(self):
        self.predicates = PredicateList()
        self.relations = RelationList()
        self.prepositions = PrepositionList()
        self.objects = ObjectList()
        self.properties = PropertyList()
        self.empty = True

    def getAllParts(self):
        return self.getPredicates()+self.getRelations()+self.getPrepositions()+self.getObjects()+self.getProperties()
    
    def copy(self):
        ex = Expression()
        for thing in self.getAllParts():
            ex.append(thing.copy())
        return ex
        
    def append(self,thing):
        if isinstance(thing,Predicate):
            self.predicates.append(thing)
            self.empty = False
        elif isinstance(thing,Relation):
            self.relations.append(thing)
            self.empty = False
        elif isinstance(thing,Preposition):
            self.prepositions.append(thing)
            self.empty = False
        elif isinstance(thing,Object):
            self.objects.append(thing)
            self.empty = False
        elif isinstance(thing,Property):
            self.properties.append(thing)
            self.empty = False
        else:
            raise Exception("Can only append Predicate,Relation,Preposition,Object,or Property")

    def remove(self,thing):
        if isinstance(thing,Predicate):
            self.predicates.remove(thing)
            self.empty = all([len(x) == 0 for x in [self.predicates,self.relations,self.prepositions,self.objects,self.properties]])
        elif isinstance(thing,Relation):
            self.relations.remove(thing)
            self.empty = all([len(x) == 0 for x in [self.predicates,self.relations,self.prepositions,self.objects,self.properties]])
        elif isinstance(thing,Preposition):
            self.prepositions.remove(thing)
            self.empty = all([len(x) == 0 for x in [self.predicates,self.relations,self.prepositions,self.objects,self.properties]])
        elif isinstance(thing,Object):
            self.objects.remove(thing)
            self.empty = all([len(x) == 0 for x in [self.predicates,self.relations,self.prepositions,self.objects,self.properties]])
        elif isinstance(properties,Property):
            self.properties.remove(thing)
            self.empty = all([len(x) == 0 for x in [self.predicates,self.relations,self.prepositions,self.objects,self.properties]])
        else:
            raise Exception("Can only remove Predicate,Relation,Preposition,Object,or Property")

    def removePredicateAt(self,i):
        self.predicates.removeAt(i)

    def removeRelationAt(self,i):
        self.predicates.removeAt(i)

    def removePrepositionAt(self,i):
        self.predicates.removeAt(i)

    def removeObjectAt(self,i):
        self.predicates.removeAt(i)

    def removePropertyAt(self,i):
        self.predicates.removeAt(i)

    def getPredicates(self):
        return self.predicates.getPredicates()

    def predicate(self,i):
        return self.predicates.predicate(i)

    def getRelations(self):
        return self.relations.getRelations()

    def relation(self,i):
        return self.relations.relation(i)

    def getPrepositions(self):
        return self.prepositions.getPrepositions()

    def preposition(self,i):
        return self.prepositions.preposition(i)

    def getObjects(self):
        return self.objects.getObjects()
    
    def getObjectDictionary(self):
        return self.objects.nameDictionary()    

    def object(self,i):
        return self.objects.object(i)
    
    def getProperties(self):
        return self.properties.getProperties()
    
    def getPropertyDictionary(self):
        return self.properties.nameDictionary()    

    def property(self,i):
        return self.properties.property(i)
    
    def tripleString(self):
        string = ''
        for object in self.getObjects():
            string = string + '[] '+object.tripleString()+' .'
        for predicate in self.getPredicates():
            string = string +'[] '+predicate.tripleString()+' ; :asDRSString '+'"{}predicate({},{},{})-{}/{}"'.format(predicate.indent,predicate.letter,predicate.name,','.join([str(x) for x in predicate.args[:-2]]),predicate.args[-2],predicate.args[-1])+' .'
        for preposition in self.getPrepositions():
            string = string +'[] '+preposition.tripleString()+' ; :asDRSString '+'"{}modifier_pp({},{},{})-{}/{}"'.format(preposition.indent,preposition.letter,preposition.term,','.join([str(x) for x in preposition.args[:-2]]),preposition.args[-2],preposition.args[-1])+' .'
        for relation in self.getRelations():
            string = string +'[] '+relation.tripleString()+' .'
        for property in self.getProperties():
            string = string +'[] '+property.tripleString()+' .'
        return string
        
    def __str__(self):        
        return "predicates [" + ",".join([str(x) for x in self.getPredicates()]) + "]\nrelations [" + ",".join([str(x) for x in self.getRelations()]) + "]\nprepositions [" + ",".join([str(x) for x in self.getPrepositions()]) + "]\nobjects [" + ",".join([str(x) for x in self.getObjects()]) + "]\nproperties [" + ",".join([str(x) for x in self.getProperties()]) + "]"

    def __repr__(self):
        return "predicates [" + ",".join([str(x) for x in self.getPredicates()]) + "]\nrelations [" + ",".join([str(x) for x in self.getRelations()]) + "]\nprepositions [" + ",".join([str(x) for x in self.getPrepositions()]) + "]\nobjects [" + ",".join([str(x) for x in self.getObjects()]) + "]\nproperties [" + ",".join([str(x) for x in self.getProperties()]) + "]"
    
class NestedExpression:
    
    def __init__(self):
        self.typeIDCharacter = None
        self.first = None
        self.second = None        
    
    def setTypeIDCharacter(self,idchar):
        if not (isinstance(idchar,str) and len(idchar)==1): 
            raise Exception("Must use Characters")          
        self.typeIDCharacter = idchar
        
    def setFirstExpression(self,first):
        if not (isinstance(first,NestedExpression) or isinstance(first,Expression)): 
            raise Exception("Must use NestedExpressions or Expressions")        
        self.first = first
    
    def setSecondExpression(self,second):
        if not (isinstance(second,NestedExpression) or isinstance(second,Expression)): 
            raise Exception("Must use NestedExpressions or Expressions")        
        self.second = second  
        
    def firstExpression(self):
        return self.first
    
    def secondExpression(self):
        return self.second
    
    def typeCharacter(self):
        return self.typeIDCharacter
    
    def tripleString(self):
        string = ''
        if self.typeIDCharacter == 'i':
            if isinstance(self.first,NestedExpression) or isinstance(self.second,NestedExpression): raise
            else:
                head = ''
                body = ''
                string = string + '[] :asDRSString "'
                for object in self.first.getObjects():
                    string = string + '{}object({},{},{})-{}/{}\\n'.format(object.indent,object.letter,object.term,','.join([str(x) for x in object.args[:-2]]),object.args[-2],object.args[-1])
                for predicate in self.first.getPredicates():
                    string = string +'{}predicate({},{},{})-{}/{}\\n'.format(predicate.indent,predicate.letter,predicate.name,','.join([str(x) for x in predicate.args[:-2]]),predicate.args[-2],predicate.args[-1])
                for preposition in self.first.getPrepositions():
                    string = string +'{}modifier_pp({},{},{})-{}/{}\\n'.format(preposition.indent,preposition.letter,preposition.term,','.join([str(x) for x in preposition.args[:-2]]),preposition.args[-2],preposition.args[-1])
                for relation in self.first.getRelations():
                    string = string +'{}relation({},{},{})-{}/{}\\n'.format(relation.indent,relation.letter,relation.name,','.join([str(x) for x in relation.args[:-2]]),relation.args[-2],relation.args[-1])  
                for property in self.first.getProperties():
                    string = string +'{}property({},{},{})-{}/{}\\n'.format(property.indent,property.letter,property.term,','.join([str(x) for x in property.args[:-2]]),property.args[-2],property.args[-1])
                string = string + '   =>\\n'
                for object in self.second.getObjects():
                    string = string + '{}object({},{},{})-{}/{}\\n'.format(object.indent,object.letter,object.term,','.join([str(x) for x in object.args[:-2]]),object.args[-2],object.args[-1])
                for predicate in self.second.getPredicates():
                    string = string +'{}predicate({},{},{})-{}/{}\\n'.format(predicate.indent,predicate.letter,predicate.name,','.join([str(x) for x in predicate.args[:-2]]),predicate.args[-2],predicate.args[-1])
                for preposition in self.second.getPrepositions():
                    string = string +'{}modifier_pp({},{},{})-{}/{}\\n'.format(preposition.indent,preposition.letter,preposition.term,','.join([str(x) for x in preposition.args[:-2]]),preposition.args[-2],preposition.args[-1])
                for relation in self.second.getRelations():
                    string = string +'{}relation({},{},{})-{}/{}\\n'.format(relation.indent,relation.letter,relation.name,','.join([str(x) for x in relation.args[:-2]]),relation.args[-2],relation.args[-1])  
                for property in self.second.getProperties():
                    string = string +'{}property({},{},{})-{}/{}\\n'.format(property.indent,property.letter,property.term,','.join([str(x) for x in property.args[:-2]]),property.args[-2],property.args[-1])            
                return string + '" .'
        elif self.setTypeIDCharacter == 'v':
            pass
        raise
    
    def __str__(self):        
        return "type = " + str(self.typeIDCharacter) + "\n\nfirst expression:\n\n" + str(self.first) + "\n\nsecond expression:\n\n" + str(self.second)

    def __repr__(self):
        return "type = " + str(self.typeIDCharacter) + "\n\nfirst expression:\n\n" + str(self.first) + "\n\nsecond expression:\n\n" + str(self.second)    

class NestedExpressionList:
    '''List of nested DRS expressions'''

    def __init__(self):
        self.exps = []

    def append(self,exp):
        if not isinstance(exp,NestedExpression): 
            raise Exception("Must append NestedExpressions to NestedExpressionList")
        self.exps.append(exp)

    def remove(self,exp):
        if not isinstance(exp,NestedExpression): 
            raise Exception("Must remove NestedExpressions from NestedExpressionList")
        self.exps.remove(exp)

    def removeAt(self,i):      
        self.exps.pop(i)    

    def expressions(self):
        return self.exps

    def expression(self,i):
        return self.exps[i]

    def __len__(self):
        return len(self.exps)
    
    def __str__(self):        
        return "[" + "\n\n,".join([str(x) for x in self.exps]) + "]"

    def __repr__(self):
        return "[" + "\n\n,".join([str(x) for x in self.exps]) + "]"
    
class Body(PredicateList):
    '''Body of a prolog rule. append and remove maintain a list of terms for verification.'''
    
    def __init__(self,preds):
        super().__init__()
        self.var = set()
        for pred in preds:
            self.append(pred)

    def copy(self):
        return Body([x.copy() for x in self.preds])
    
    def append(self,pred):
        if not isinstance(pred,Predicate): raise
        
        self.preds.append(pred)
        
        if isinstance(pred,Class) and not pred.args[0] in self.var: 
            self.var.add(pred.args[0])
        elif isinstance(pred,Role):
            if not pred.args[0] in self.var: self.var.add(pred.args[0])
            if not pred.args[1] in self.var: self.var.add(pred.args[1])
        elif isinstance(pred,TernaryPredicate):
            if not pred.args[0] in self.var: self.var.add(pred.args[0])
            if not pred.args[1] in self.var: self.var.add(pred.args[1])
            if not pred.args[2] in self.var: self.var.add(pred.args[2])

    def remove(self,pred):
        if not isinstance(pred,Predicate): raise
        
        oldVars = set()
        
        if isinstance(pred,Class): oldVars.add(pred.args[0])
        elif isinstance(pred,Role): oldVars.add(pred.args[0]) ; oldVars.add(pred.args[1])
        elif isinstance(pred,TernaryPredicate): oldVars.add(pred.args[0]) ; oldVars.add(pred.args[1]) ; oldVars.add(pred.args[2])
        
        self.body.remove(pred)
        
        for pred in self.preds:
            if isinstance(pred,Class) and pred.args[0] in oldVars:
                oldVars.remove(pred.args[0])
                if len(oldVars) == 0: return
            elif isinstance(pred,Role) and pred.args[0] in oldVars:
                oldVars.remove(pred.args[0])
                if len(oldVars) == 0: return                
            elif isinstance(pred,Role) and pred.args[1] in oldVars:
                oldVars.remove(pred.args[1])
                if len(oldVars) == 0: return
            elif isinstance(pred,TernaryPredicate) and pred.args[0] in oldVars:
                oldVars.remove(pred.args[0])
                if len(oldVars) == 0: return                
            elif isinstance(pred,TernaryPredicate) and pred.args[1] in oldVars:
                oldVars.remove(pred.args[1])
                if len(oldVars) == 0: return
            elif isinstance(pred,TernaryPredicate) and pred.args[2] in oldVars:
                oldVars.remove(pred.args[2])
                if len(oldVars) == 0: return 
                
        for var in oldVars:
            self.var.remove(var)
    
    def getTerms(self):
        return self.var
    
    def dlTripleString(self):
        raise
    
    def __str__(self):        
        return ",".join([str(x) for x in self.preds])

    def __repr__(self):
        return ",".join([str(x) for x in self.preds])

class Head:
    
    def __init__(self,pred):
        if not isinstance(pred,Predicate): raise
        self.pred = pred
        self.var = self.getVarsFromPred(pred)
        
    def copy(self):
        return Head(self.pred.copy())
    
    def getVarsFromPred(self,pred):
        if isinstance(pred,Class): 
            return {pred.args[0]}
        elif isinstance(pred,Role):
            return {pred.args[0],pred.args[1]}
        elif isinstance(pred,TernaryPredicate):
            return {pred.args[0],pred.args[1],pred.args[2]}   
    
    def getPredicate(self):
        return self.pred
    
    def getTerms(self):
        return self.var
    
    def __str__(self):
        return str(self.pred) 

    def __repr__(self):
        return str(self.pred)   
        
class Rule:
    '''Prolog Rule'''
    
    def __init__(self,body,head):
        if not (isinstance(body,Body) or isinstance(head,Head)): raise 
        self.head = head
        self.body = body

    def copy(self):
        return Rule(self.body.copy(),self.head.copy())
        
    def toRule(self):
        return str(self.body) + " => " + str(self.head)
    
    def __str__(self):        
        return str(self.head) + ":-" + str(self.body)

    def __repr__(self):
        return str(self.head) + ":-" + str(self.body)
    
class Disjunction(Expression):
    '''Or'''
    
    def __init__(self,a,b):
        self.first = a
        self.second = b

    def toRule(self):
        return str(self.first) + " v " + str(self.second)

    def __str__(self):        
        return str(self.first) + ";" + str(self.second)

    def __repr__(self):
        return str(self.first) + ";" + str(self.second)

def checkDictsForKey(key,*dicts):
    for i in range(len(dicts)):
        if key in dicts[i]:
            return (dicts[i][key],i) if dicts[i][key] not in dicts[i] else (dicts[i][dicts[i][key]],i)
    return key,i
    
def writePrologFile(facts, rules, newRules, prologfile, factFile, groundFile):
    '''writes a prolog file that executes a logic program built from 
    the instructions that will produce all facts it enatils in one 
    file and all solved rules it used to obtain enatilments facts in another'''    
    program = sorted(rules+newRules+facts, key=lambda x: x[0])
    
    selector = lambda thing: '({})'.format(thing[0]+","+",".join(thing[1][:-1] if not thing[1][-2] == 'order(ZZ)' else thing[1][:-2]))
    
    groundTerms = lambda thing: ',write(Stream2,","),'.join(['writeq(Stream2,{})'.format(cutCounter(stuff)) for stuff in (thing[1][:-1] if not thing[1][-2] == 'order(ZZ)' else thing[1][:-2])])
    groundWriter = lambda thing: 'writeq(Stream2,ZZZ),write(Stream2," : "),{},write(Stream2," => "),writeq(Stream2,{}),writeln(Stream2,"")'.format(groundTerms(thing),cutCounter(thing[0]))
    factWriter = lambda thing: 'writeq(Stream,ZZZ),write(Stream," : "),writeq(Stream,{}),writeln(Stream,"")'.format(cutCounter(thing[0]))
    
    writer = lambda thing: '({},{})'.format(groundWriter(thing),factWriter(thing))
    
    output = ['forall({},{}),\n'.format(selector(thing),writer(thing)) for thing in rules]
    open(prologfile, "w").write('{}\n:- open("{}",write, Stream),open("{}",write, Stream2),\n{}close(Stream),close(Stream2),halt.\n'.format(''.join(['{}\n'.format('{} :- {}.'.format(thing[0], ",".join(thing[1])) if isinstance(thing, list) else "{}.".format(thing)) for thing in program]), factFile, groundFile, ''.join(output)))

def cutCounter(thing):
    thing = re.split(",(?:ZZZ|ZZ)\)$",thing)
    return thing[0] if len(thing) == 1 else thing[0] + ')'
    
def runProlog(facts,rules,makeLogFiles):
    '''runs the prolog file and reads and discards its output files
    returns the lines from the files it discards'''
    
    factFile = "interpreter/reasonerFacts.txt"
    groundFile = "interpreter/groundRules.txt"
    prologfile = "interpreter/prolog.pl"
    
    heads = [x.head.getPredicate() for x in rules]
    newRules = []
    
    for rule in rules:
        inHeads = False
        for pred in rule.body.getPredicates():
            for head in heads:
                if sameVariablePredicate(pred,head):
                    inHeads = True
                    break
            if inHeads: break
        if not inHeads:
            rule.body.preds.append(Class('','Z','order','ZZ',-1,-1))
        else:
            for i in range(len(rule.body.preds)):
                for head in heads:
                    if sameVariablePredicate(rule.body.preds[i],head):
                        rule.body.preds[i] = Predicate(*([rule.body.preds[i].getName()] + rule.body.preds[i].args[:-2] + ['ZZ']))
        
        newRules.append(Rule(Body([Predicate(*([rule.head.pred.getName()] + rule.head.pred.args[:-2] + ['_']))]),Head(rule.head.pred)))
        rule.head.pred = Predicate(*([rule.head.pred.getName()] + rule.head.pred.args[:-2] + ['ZZZ']))
    
    ruleStr = [[str(rule.head),[str(b) for b in rule.body.preds]+['ZZZ is ZZ + 1']] for rule in rules]
    newRuleStr = [[str(rule.head),[str(b) for b in rule.body.preds]] for rule in newRules]
    factStr = [str(fact) for fact in facts+[Class('','Z','order','0',-1,-1)]]
    
    writePrologFile(factStr,ruleStr,newRuleStr,prologfile,factFile,groundFile)

    print("Reasoning...")
    subprocess.call(['swipl', prologfile])

    reasonerFacts = []
    for x in open(factFile, "r").read().splitlines():
        x = x.split(" : ")
        reasonerFacts.append((int(x[0]),makeFactFromString(x[1])))
        
    groundRules = [makeRuleFromString(x) for x in open(groundFile, "r").read().splitlines()]

    if not makeLogFiles: os.remove(factFile)
    if not makeLogFiles: os.remove(groundFile)
    if not makeLogFiles: os.remove(prologfile)

    return reasonerFacts, groundRules

def sameVariablePredicate(predA,predB):
    '''Double Check Me'''
    
    if not type(predA) == type(predB) or not predA.getName() == predB.getName() or not len(predA.args) == len(predB.args): return False
    for i in range(len(predA.args)-2):
        if isinstance(predA.arg(i),Function) and isinstance(predB.arg(i),Function):
            if not (re.match("[A-Z][0-9]*",predA.arg(i).args[0]) and  re.match("[A-Z][0-9]*",predB.arg(i).args[0])): return False
        elif isinstance(predA.arg(i),Function): return False
        elif isinstance(predB.arg(i),Function): return False
        elif not ((re.match("[A-Z][0-9]*",predA.arg(i)) and re.match("[A-Z][0-9]*",predB.arg(i))) or (predA.arg(i) == predB.arg(i))): return False
    return True
    
def makeFactFromString(string):
    m = re.match("^([^\(]+)\((.*)\)$",string)
    terms = m.groups()[1].split(",")
    name = m.groups()[0]
    if name == 'hasProperty':
        return PropertyRole('','Z',terms[0],terms[1],-1,-1)
    elif len(terms) == 1:
        return Class('','Z',name,terms[0],-1,-1)
    elif len(terms) == 2:
        if m := re.match("^([^\(]+)\((.*)\)$",terms[1]):
            return Role('','Z',name,terms[0],Preposition('','Z',m.groups()[0],m.groups()[1],-1,-1),-1,-1)
        return Role('','Z',name,terms[0],terms[1],-1,-1)
    elif len(terms) == 3:
        return TernaryPredicate('','Z',name,terms[0],terms[1],terms[2],-1,-1)

def makeRuleFromString(string):
    num = string.split(" : ")
    halves = num[1].split(" => ")
    return int(num[0]),Rule(Body([makeFactFromString(x) for x in re.split("(?<=\))\,(?=\w)",halves[0])]),Head(makeFactFromString(halves[1])))    
    
def getDRSFromACE(ace):
    '''Runs APE on the ACE file and returns the lines of the DRS it created'''    
    print("Interpreting ACE...")

    process = subprocess.Popen(['lib/ape/ape.exe', '-cdrspp'],stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    process.stdin.write(ace.encode('utf-8'))
    drs = process.communicate()[0].decode('utf-8').splitlines()
    process.stdin.close()  # possibly unnecessary when function returns? not great at subprocess

    return drs

def initEmpties():

    ObjectList.empty = ObjectList()
    PropertyList.empty = PropertyList()

def compileRegexes():

    # these match all possible DRS lines as defined by the current semantics
    xmlBeforeDRSPattern = re.compile("^\s*(?:<.*>)?$")
    variablesPattern = re.compile("^\s*<drspp>\s*\[([A-Z][0-9]*(?:,[A-Z][0-9]*)*)?\]\s*")
    objectPattern = re.compile("^()object\(([A-Z][0-9]*),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    unaryPredicatePattern = re.compile("^()predicate\(([A-Z][0-9]*),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    binaryPredicatePattern = re.compile("^()predicate\(([A-Z][0-9]*),([^,]+),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    ternaryPredicatePattern = re.compile("^()predicate\(([A-Z][0-9]*),([^,]+),([^,]+),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    propertyPattern = re.compile("^()property\(([A-Z][0-9]*),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    expressionPattern = re.compile("^(\s+)[^\s]+.*")   
    doneReadingPattern = re.compile("^\s*</drspp>.*")
    prepositionPattern = re.compile("^()modifier_pp\(([A-Z][0-9]*),([^,]+),([A-Z][0-9]*)\)-(\d+)/(\d+)\s*")
    relationPattern = re.compile("^()relation\(([A-Z][0-9]*),([^,]+),([A-Z][0-9]*)\)-(\d+)/(\d+)\s*")

    # expressions have the same stuff as the facts, they are just indented (\s+)
    expressionVariablesPattern = re.compile("^(\s+)\[([A-Z][0-9]*(?:,[A-Z][0-9]*)*)?\]\s*")
    expressionAnonymousPattern = re.compile("^(\s+)\[\]\s*")
    implicationSignPattern = re.compile("^(\s+)(=&gt;)\s*")
    disjunctionSignPattern = re.compile("^(\s+v)\s*")
    expressionObjectPattern = re.compile("^(\s+)object\(([A-Z][0-9]*),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    expressionUnaryPredicatePattern = re.compile("^(\s+)predicate\(([A-Z][0-9]*),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    expressionBinaryPredicatePattern = re.compile("^(\s+)predicate\(([A-Z][0-9]*),([^,]+),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    expressionTernaryPredicatePattern = re.compile("^(\s+)predicate\(([A-Z][0-9]*),([^,]+),([^,]+),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    expressionPropertyPattern = re.compile("^(\s+)property\(([A-Z][0-9]*),([^,]+),([^,]+)\)-(\d+)/(\d+)\s*")
    expressionPrepositionPattern = re.compile("^(\s+)modifier_pp\(([A-Z][0-9]*),([^,]+),([A-Z][0-9]*)\)-(\d+)/(\d+)\s*")
    expressionRelationPattern = re.compile("^(\s+)relation\(([A-Z][0-9]*),([^,]+),([A-Z][0-9]*)\)-(\d+)/(\d+)\s*")
    expressionDonePattern = re.compile("^[^\s]+.*")   

    return {'xmlBeforeDRS':xmlBeforeDRSPattern,'variables':variablesPattern,'object':objectPattern,'unaryPredicate':unaryPredicatePattern,
            'binaryPredicate':binaryPredicatePattern,'ternaryPredicate':ternaryPredicatePattern,'property':propertyPattern,'expression':expressionPattern,'doneReading':doneReadingPattern,
            'preposition':prepositionPattern,'expressionVariables':expressionVariablesPattern,'implicationSign':implicationSignPattern,
            'disjunctionSign':disjunctionSignPattern,'expressionObject':expressionObjectPattern,'expressionUnaryPredicate':expressionUnaryPredicatePattern,
            'expressionBinaryPredicate':expressionBinaryPredicatePattern,'expressionTernaryPredicate':expressionTernaryPredicatePattern,'expressionProperty':expressionPropertyPattern,'expressionPreposition':expressionPrepositionPattern,
            'relation':relationPattern,'expressionRelation':expressionRelationPattern,'expressionDone':expressionDonePattern,'expressionAnonymous':expressionAnonymousPattern}

def appendToDRSFile(drsline):
    '''Self explanatory'''    
    open("interpreter/DRS.txt","a").write(drsline + '\n')

def partitionListWithFunction(list,condition):
    selected, other = [], []
    for x in list:
        (other,selected)[condition(x)].append(x)
    return selected,other

def makeFacts(factsExpression):
    
    facts = []
    knownInstances = set()
    factsFunctions = factsExpression.getPrepositions()
    
    # partition the predicates
    classes,otherExpressions = partitionListWithFunction(factsExpression.getPredicates(),lambda x: isinstance(x,Class))
    roles,otherExpressions = partitionListWithFunction(otherExpressions,lambda x: isinstance(x,Role))
    isas,roles = partitionListWithFunction(roles,lambda x: x.getName() == 'be')
    ternaries,otherExpressions = partitionListWithFunction(otherExpressions,lambda x: isinstance(x,TernaryPredicate))
    
    
    if not len(otherExpressions) == 0: raise Exception("Undefined Behavior")        
    
    # first make all the is-a type roles into class facts, saving any dictionary mappings learned
    for predicate in isas:
        cOrP = makeClassFactOrPropertyFactFromRole(predicate,factsExpression)
        facts.append(cOrP)
        if isinstance(cOrP,Class):
            knownInstances.add(cOrP.getName())
            knownInstances.add(cOrP.arg(0))
        elif cOrP.getName() == 'equals':
            facts.append(Class(cOrP.getIndent(),cOrP.getLetter(),cOrP.arg(0),cOrP.arg(1),cOrP.arg(2),cOrP.arg(3)))
            
    # do roles
    for predicate in roles:
        facts.append(makeFactFromRole(predicate,factsExpression))
            
    # do classes
    for predicate in classes:
        facts.append(makeFactFromClass(predicate,factsExpression))  
            
    # do ternary predicates
    for predicate in ternaries:
        facts.append(makeFactFromTernary(predicate,factsExpression))      
    
    # add instances for all of the types of objects that were not stated
    for objectClass in factsExpression.getObjects():
        if objectClass.getTerm() in knownInstances: continue
        facts.append(Class(objectClass.getIndent(),objectClass.getLetter(),objectClass.getTerm(),objectClass.getTerm(),objectClass.arg(-2),objectClass.arg(-1)))
    
    
         
    return facts,factsExpression

def makeFactFromClass(predicate,factsExpression):
    '''Checks to see if a class should be rewritten as a class with an instance of a role with a preposition as its term'''
    
    if isinstance(predicate,Class):
        
        # property
        for preposition in factsExpression.getPrepositions():
            if predicate.getLetter() == preposition.getLetter():
                thingInTheRole,_ = checkDictsForKey(predicate.arg(0),factsExpression.getObjectDictionary(),factsExpression.getPropertyDictionary()) if isinstance(predicate.args[0],Variable) else (predicate.arg(0),0)
                thingInThePreposition = factsExpression.getObjectDictionary()[preposition.arg(0)] if preposition.arg(0) in factsExpression.getObjectDictionary() else factsExpression.getPropertyDictionary()[preposition.arg(0)]
                preposition.args[0] = thingInThePreposition
                return Role(predicate.getIndent(),predicate.getLetter(),predicate.getName(),thingInTheRole,preposition,predicate.arg(1),predicate.arg(2))
            
        # instance of a class
        for object in factsExpression.getObjects():
            if predicate.arg(0) == object.getLetter():
                instance,_ = checkDictsForKey(predicate.arg(0),factsExpression.getObjectDictionary()) if isinstance(predicate.args[0],Variable) else (predicate.arg(0),0)
                return Class(predicate.getIndent(),predicate.getLetter(),predicate.getName(),instance,predicate.arg(1),predicate.arg(2))        
        
    raise Exception("Undefined Behavior")

def makeFactFromRole(predicate,factsExpression):
    
    if isinstance(predicate,Role):
        
        # property
        for preposition in factsExpression.getPrepositions():
            if predicate.getLetter() == preposition.getLetter():
                first,err = checkDictsForKey(predicate.arg(0),factsExpression.getObjectDictionary(),factsExpression.getPropertyDictionary()) if isinstance(predicate.args[0],Variable) else (predicate.arg(0),0)
                second,prop = checkDictsForKey(predicate.arg(1),factsExpression.getObjectDictionary(),factsExpression.getPropertyDictionary()) if isinstance(predicate.args[1],Variable) else (predicate.arg(1),0)
                thingInThePreposition = factsExpression.getObjectDictionary()[preposition.arg(0)] if preposition.arg(0) in factsExpression.getObjectDictionary() else factsExpression.getPropertyDictionary()[preposition.arg(0)]
                preposition.args[0] = thingInThePreposition
                return TernaryPredicate(predicate.getIndent(),predicate.getLetter(),predicate.getName(),first,second,preposition,predicate.arg(1),predicate.arg(2))        
        
        first,err = checkDictsForKey(predicate.arg(0),factsExpression.getObjectDictionary(),factsExpression.getPropertyDictionary()) if isinstance(predicate.args[0],Variable) else (predicate.arg(0),0)
        second,prop = checkDictsForKey(predicate.arg(1),factsExpression.getObjectDictionary(),factsExpression.getPropertyDictionary()) if isinstance(predicate.args[1],Variable) else (predicate.arg(1),0)
        
        if err == 1:
            raise Exception("Undefined Behavior")
        elif prop == 1:
            return PropertyRole(predicate.getIndent(),predicate.getLetter(),predicate.getName(),first,second,predicate.arg(2),predicate.arg(3))
        else:
            return Role(predicate.getIndent(),predicate.getLetter(),predicate.getName(),first,second,predicate.arg(2),predicate.arg(3))
    
    raise Exception("Undefined Behavior")

def makeFactFromTernary(predicate,factsExpression):
    
    print(predicate)
    
    if isinstance(predicate,TernaryPredicate):
        
        pass
    
    raise Exception("Undefined Behavior")

def makeClassFactOrPropertyFactFromRole(predicate,factsExpression):
    '''Checks Roles to see if they should be rewritten as class facts or property facts'''
    
    if isinstance(predicate,Role):
        
        # both terms are variables
        if re.match("^([A-Z][0-9]*)$",predicate.arg(0)) and re.match("^([A-Z][0-9]*)$",predicate.arg(1)):
            
            thingInTheClass,i = checkDictsForKey(predicate.arg(0),factsExpression.getObjectDictionary(),factsExpression.getPropertyDictionary())
            classThingIsIn,j = checkDictsForKey(predicate.arg(1),factsExpression.getObjectDictionary(),factsExpression.getPropertyDictionary())
            
            # both are objects
            if i == 0 and j == 0:
                
                newPredicate = Class(predicate.getIndent(),predicate.getLetter(),classThingIsIn,thingInTheClass,predicate.arg(2),predicate.arg(3))
                
                # update the object dictionary to contain the new Class
                if thingInTheClass not in factsExpression.getObjectDictionary():
                    factsExpression.getObjectDictionary()[thingInTheClass] = classThingIsIn
                    factsExpression.getObjectDictionary()[predicate.arg(1)] = thingInTheClass
                    #del factsExpression.getObjectDictionary()[predicate.arg(0)]
            
            # second is a property
            elif i == 0:
                
                newPredicate = PropertyRole(predicate.getIndent(),predicate.getLetter(),factsExpression.getObjectDictionary()[predicate.arg(0)],classThingIsIn,predicate.arg(2),predicate.arg(3))
            
            else:
                raise Exception("Undefined Behavior")
            
        # first term is a variable and second is a string
        elif re.match("^([A-Z][0-9]*)$",predicate.arg(0)) and re.match("^\'(.*)\'$",predicate.arg(1)):
            
            thingInTheClass = predicate.arg(1)
            classThingIsIn,i = checkDictsForKey(predicate.arg(0),factsExpression.getObjectDictionary(),factsExpression.getPropertyDictionary())
            
            if i == 0:
            
                newPredicate = Role(predicate.getIndent(),predicate.getLetter(),'equals',classThingIsIn,thingInTheClass,predicate.arg(2),predicate.arg(3))
                    
            else:
                raise Exception("Undefined Behavior")      
        
        # first term is a variable
        elif re.match("^([A-Z][0-9]*)$",predicate.arg(0)):
            
            raise Exception("Undefined Behavior")
            
        # second term is a variable
        elif re.match("^([A-Z][0-9]*)$",predicate.arg(1)):
            
            thingInTheClass = predicate.arg(0)
            classThingIsIn,i = checkDictsForKey(predicate.arg(1),factsExpression.getObjectDictionary(),factsExpression.getPropertyDictionary())
            
            if i == 0:
            
                newPredicate = Class(predicate.getIndent(),predicate.getLetter(),classThingIsIn,thingInTheClass,predicate.arg(2),predicate.arg(3))
                
                # update the object dictionary to contain the new Class
                if thingInTheClass not in factsExpression.getObjectDictionary():
                    factsExpression.getObjectDictionary()[thingInTheClass] = classThingIsIn
                    factsExpression.getObjectDictionary()[predicate.arg(1)] = thingInTheClass
                    
            else:
                raise Exception("Undefined Behavior")
                              
                
        # already a fact, YAY
        else: 
            newPredicate = predicate
    
        return newPredicate
    
    raise Exception("Undefined Behavior")

def makeRules(interpretedFactsExpression,nestedExpression):
    
    rules = []
    
    for expression in nestedExpression.expressions():
        
        # easy case, flat implication
        if not isinstance(expression.firstExpression(),NestedExpression) and not isinstance(expression.secondExpression(),NestedExpression) and expression.typeCharacter() == 'i':
            
            bodyPredicates,knownVariables,classes = makeHalfRule(interpretedFactsExpression,expression.firstExpression(),set(),[])
            headPredicates,_,classesForVariables = makeHalfRule(interpretedFactsExpression,expression.secondExpression(),knownVariables,[])
            
            for head in headPredicates:
                thisBody = bodyPredicates+classes
                for predicate in classesForVariables:
                    if matchesTermInHead(head,predicate):
                        thisBody.append(predicate)
                rules.append(Rule(Body(thisBody),Head(head)))
            
        else:
            raise Exception("Undefined Behavior")
        
    return rules

def matchesTermInHead(head,predicate):
    
    # class
    if isinstance(head,Class): 
        return predicate.arg(0) == head.arg(0)
    # Role
    elif isinstance(head,Role):
        if isinstance(head.arg(1),Preposition):
            return predicate.arg(0) == head.arg(0) or predicate.arg(0) == head.arg(1).arg(0)             
        return predicate.arg(0) == head.arg(0) or predicate.arg(0) == head.arg(1)
    # ternary
    elif isinstance(head,TernaryPredicate):
        return predicate.arg(0) == head.arg(0) or predicate.arg(0) == head.arg(1) or predicate.arg(0) == head.arg(2)

def makeHalfRule(interpretedFactsExpression,expression,previousVariables,classesForVariables):
    
    # partition the predicates
    classes,otherExpressions = partitionListWithFunction(expression.getPredicates(),lambda x: isinstance(x,Class))
    roles,otherExpressions = partitionListWithFunction(otherExpressions,lambda x: isinstance(x,Role))
    isas,roles = partitionListWithFunction(roles,lambda x: x.getName() == 'be')
    ternaries,otherExpressions = partitionListWithFunction(otherExpressions,lambda x: isinstance(x,TernaryPredicate))
    
    if not len(otherExpressions) == 0: raise Exception("Undefined Behavior") 
    
    predicates = roles + ternaries
    knownVariables = set()
    
    for predicate in roles:
        
        # property
        for preposition in expression.getPrepositions():
            if predicate.getLetter() == preposition.getLetter():
                p = TernaryPredicate(predicate.getIndent(),predicate.getLetter(),predicate.getName(),predicate.arg(0),predicate.arg(1),preposition,predicate.arg(1),predicate.arg(2))
                
                predicates.append(p)
                predicates.remove(predicate)
                
                knownVariables.add(p.arg(2).arg(0))
                
        knownVariables.add(predicate.arg(0))
        knownVariables.add(predicate.arg(1))
    
    for predicate in ternaries:
        knownVariables.add(predicate.arg(0))
        knownVariables.add(predicate.arg(1))
        knownVariables.add(predicate.arg(2))
    
    for predicate in isas:
        cOrP = makePropertyFromRole(predicate,interpretedFactsExpression,expression)
        predicates.append(cOrP)
        knownVariables.add(cOrP.arg(0))
    
    for predicate in classes:
        roleOrClass = tryToMakeRoleFromClass(predicate,interpretedFactsExpression,expression)
        
        if isinstance(roleOrClass,Class):
            knownVariables.add(roleOrClass.arg(0))
        else:
            a = roleOrClass.arg(1)
            knownVariables.add(roleOrClass.arg(0))
            knownVariables.add(roleOrClass.arg(1).arg(0))
            
        predicates.append(roleOrClass)
    
    terms = set()    
    # add variable classes for all of the types of objects that were not stated
    for objectClass in interpretedFactsExpression.getObjects()+expression.getObjects():
        if objectClass.getLetter() in knownVariables - previousVariables:
            term,_ = checkDictsForKey(objectClass.getLetter(),interpretedFactsExpression.getObjectDictionary(),expression.getObjectDictionary())
            classesForVariables.append(Class(objectClass.getIndent(),objectClass.getLetter(),term,objectClass.getLetter(),objectClass.arg(-2),objectClass.arg(-1)))
            terms.add(term)
            
    for obj in expression.getObjects():
        if obj.getTerm() in terms:
            pass
        else:
            classesForVariables.append(Class(obj.getIndent(),obj.getLetter(),obj.getTerm(),obj.getLetter(),obj.arg(-2),obj.arg(-1)))
        
    return predicates,knownVariables,classesForVariables


def makePropertyFromRole(predicate,interpretedFactsExpression,expression):
    '''Checks Roles to see if they should be rewritten as property predicates'''
    
    if isinstance(predicate,Role):
        
        # both terms are variables
        if re.match("^([A-Z][0-9]*)$",predicate.arg(0)) and re.match("^([A-Z][0-9]*)$",predicate.arg(1)):
            
            propertyTest,i = checkDictsForKey(predicate.arg(1),interpretedFactsExpression.getPropertyDictionary(),expression.getPropertyDictionary())
            
            # second is a property
            if i == 1:                
                newPredicate = PropertyRole(predicate.getIndent(),predicate.getLetter(),predicate.arg(0),propertyTest,predicate.arg(2),predicate.arg(3))
            # no property, done
            else:
                newPredicate = predicate
            
        # second term is a variable
        elif re.match("^([A-Z][0-9]*)$",predicate.arg(1)):
            
            propertyTest,i = checkDictsForKey(predicate.arg(1),interpretedFactsExpression.getPropertyDictionary(),expression.getPropertyDictionary())
            
            # second is a property
            if i == 1:                
                newPredicate = PropertyRole(predicate.getIndent(),predicate.getLetter(),predicate.arg(0),propertyTest,predicate.arg(2),predicate.arg(3))
            # no property, done
            else:
                newPredicate = predicate
                              
                
        # already a valid role, YAY
        else: 
            newPredicate = predicate
        
        return newPredicate
    
    raise Exception("Undefined Behavior")

def tryToMakeRoleFromClass(predicate,interpretedFactsExpression,expression):
    '''Checks to see if a class should be rewritten as a role with a preposition as its term'''
    
    if isinstance(predicate,Class):
                   
        # property    
        for preposition in interpretedFactsExpression.getPrepositions()+expression.getPrepositions():
            if predicate.getLetter() == preposition.getLetter():
                return Role(predicate.getIndent(),predicate.getLetter(),predicate.getName(),predicate.arg(0),preposition,predicate.arg(1),predicate.arg(2))
        
        return predicate
           
    raise Exception("Undefined Behavior")

def readNestedExpression(drs,globalLineIndex,regexPatterns,makeLogFiles):

    nestedExpression = NestedExpression()
    currentExpression = Expression()

    thisExpressionLocalLineIndex = 0

    for currentReadingIndex in range(globalLineIndex,len(drs)):
        
        # manage the indexes for nested expressions
        if thisExpressionLocalLineIndex >= currentReadingIndex: thisExpressionLocalLineIndex += 1
        currentReadingIndex = max(thisExpressionLocalLineIndex,currentReadingIndex)
        line = drs[currentReadingIndex]
        
        # check if expression is over
        if re.match(regexPatterns['doneReading'],line):
            if not currentExpression.empty and nestedExpression.firstExpression():
                nestedExpression.setSecondExpression(currentExpression)
                return currentReadingIndex-1,nestedExpression   
            elif not currentExpression.empty and not nestedExpression.typeCharacter():
                nestedExpression.setFirstExpression(currentExpression)
                return currentReadingIndex-1,currentExpression             
            else: 
                raise Exception("BAD! shouldn't happen, fix me")
        if re.match(regexPatterns['expressionDone'],line):
            nestedExpression.setSecondExpression(currentExpression)
            return currentReadingIndex-1,nestedExpression

        # is there another expression in the expresion?
                
        # anonymous expression
        if m := re.match(regexPatterns['expressionAnonymous'],line):
            
            if makeLogFiles: appendToDRSFile(line)
            
            # add to second
            if not currentExpression.empty and nestedExpression.firstExpression():
                nestedExpression.setSecondExpression(currentExpression)
                return currentReadingIndex-1,nestedExpression
            # add to first
            elif not currentExpression.empty:
                nestedExpression.setFirstExpression(currentExpression)
                currentExpression = Expression()
            # nested, skip this one
            else: continue
        
        # flat expression
        elif m := re.match(regexPatterns['expressionVariables'],line):
            
            # add to second
            if not currentExpression.empty and nestedExpression.firstExpression():
                nestedExpression.setSecondExpression(currentExpression)
                return currentReadingIndex-1,nestedExpression
            
            if makeLogFiles: appendToDRSFile(line)
            
            # add to first
            if not currentExpression.empty:
                nestedExpression.setFirstExpression(currentExpression)
                currentExpression = Expression()
            # nested, skip this one
            else: continue

        # expression type identifiers
        
        # implies
        elif m := re.match(regexPatterns['implicationSign'],line):
            if makeLogFiles: appendToDRSFile(m.groups()[0]+'=>')
            
            # is it the big => ?
            if nestedExpression.typeCharacter() and len(m.groups()[0]) == 3:
                nestedExpression.setSecondExpression(currentExpression)
                newExpression = NestedExpression()
                newExpression.setFirstExpression(nestedExpression)
                nestedExpression = newExpression
                newExpression = None
                currentExpression = Expression()
            # nested =>
            elif nestedExpression.typeCharacter():
                currentReadingIndex += 1
                if makeLogFiles: appendToDRSFile(drs[currentReadingIndex])
                thisExpressionLocalLineIndex,expression = readNestedExpression(drs,currentReadingIndex+1,regexPatterns,makeLogFiles)
                newExpression = NestedExpression()
                newExpression.setFirstExpression(currentExpression)
                newExpression.setSecondExpression(expression)
                newExpression.setTypeIDCharacter('i')
                nestedExpression.setSecondExpression(newExpression)
                return thisExpressionLocalLineIndex,nestedExpression           
            
            nestedExpression.setTypeIDCharacter('i')
        
        # or        
        elif m := re.match(regexPatterns['disjunctionSign'],line):
            if makeLogFiles: appendToDRSFile(m.groups()[0])
            
            # v is always nested, just need to check if it's flat
            if nestedExpression.typeCharacter():
                currentReadingIndex += 1
                if makeLogFiles: appendToDRSFile(drs[currentReadingIndex])
                thisExpressionLocalLineIndex,expression = readNestedExpression(drs,currentReadingIndex+1,regexPatterns,makeLogFiles)
                newExpression = NestedExpression()
                newExpression.setFirstExpression(currentExpression)
                newExpression.setSecondExpression(expression)
                newExpression.setTypeIDCharacter('d')
                nestedExpression.setSecondExpression(newExpression)
                return thisExpressionLocalLineIndex,nestedExpression
            else:
                nestedExpression.setTypeIDCharacter('d')

        # DRS components
        elif m := re.match(regexPatterns['expressionObject'],line): 
            if makeLogFiles: appendToDRSFile(line)
            currentExpression.append(Object(*m.groups()))
        elif m:= re.match(regexPatterns['expressionUnaryPredicate'],line): 
            if makeLogFiles: appendToDRSFile(line)
            currentExpression.append(Class(*m.groups()))        
        elif m:= re.match(regexPatterns['expressionBinaryPredicate'],line): 
            if makeLogFiles: appendToDRSFile(line)
            currentExpression.append(Role(*m.groups()))
        elif m:= re.match(regexPatterns['expressionTernaryPredicate'],line): 
            if makeLogFiles: appendToDRSFile(line)
            currentExpression.append(TernaryPredicate(*m.groups()))        
        elif m := re.match(regexPatterns['expressionProperty'],line): 
            if makeLogFiles: appendToDRSFile(line)
            currentExpression.append(Property(*m.groups()))
        elif m := re.match(regexPatterns['expressionRelation'],line):
            if makeLogFiles: appendToDRSFile(line)
            currentExpression.append(Relation(*m.groups()))
        elif m := re.match(regexPatterns['expressionPreposition'],line):
            if makeLogFiles: appendToDRSFile(line)
            currentExpression.append(Preposition(*m.groups()))  
        else:
            # there are things we can add, depending on the requirements
            # just need to define the behavior to fix this exception
            raise Exception("Undefined Interpretation for DRS Expression",line)        

def readExpressions(drs,regexPatterns,makeLogFiles):
        
    factsExpression = Expression()
    nestedExpressions = NestedExpressionList()

    thisExpressionLocalLineIndex = 0

    for currentReadingIndex in range(len(drs)):
        
        # manage the indexes for nested expressions
        if thisExpressionLocalLineIndex >= currentReadingIndex: thisExpressionLocalLineIndex += 1
        currentReadingIndex = max(thisExpressionLocalLineIndex,currentReadingIndex)
        line = drs[currentReadingIndex]
        
        #check if the DRS is over or hasn't started yet
        if re.match(regexPatterns['doneReading'],line): break
        elif m := re.match(regexPatterns['xmlBeforeDRS'],line): continue

        # starting global variable pattern
        elif m := re.match(regexPatterns['variables'],line):
            if makeLogFiles: appendToDRSFile('['+('' if not m.groups()[0] else m.groups()[0])+']')

        # if there's an expression starting, read those components separately
        elif m := re.match(regexPatterns['expression'],line):
            if makeLogFiles: appendToDRSFile(line)
            thisExpressionLocalLineIndex,expression = readNestedExpression(drs,currentReadingIndex+1,regexPatterns,makeLogFiles)
            nestedExpressions.append(expression)

        # DRS components
        elif m := re.match(regexPatterns['object'],line): 
            if makeLogFiles: appendToDRSFile(line)
            factsExpression.append(Object(*m.groups()))
        elif m := re.match(regexPatterns['unaryPredicate'],line):
            if makeLogFiles: appendToDRSFile(line)
            factsExpression.append(Class(*m.groups()))        
        elif m := re.match(regexPatterns['binaryPredicate'],line):
            if makeLogFiles: appendToDRSFile(line)
            factsExpression.append(Role(*m.groups()))
        elif m := re.match(regexPatterns['ternaryPredicate'],line):
            if makeLogFiles: appendToDRSFile(line)
            factsExpression.append(TernaryPredicate(*m.groups()))        
        elif m := re.match(regexPatterns['property'],line):
            if makeLogFiles: appendToDRSFile(line)
            factsExpression.append(Property(*m.groups()))
        elif m := re.match(regexPatterns['relation'],line):
            if makeLogFiles: appendToDRSFile(line)
            factsExpression.append(Relation(*m.groups()))
        elif m := re.match(regexPatterns['preposition'],line):
            if makeLogFiles: appendToDRSFile(line)
            factsExpression.append(Preposition(*m.groups()))
        else:
            # there are things we can add, depending on the requirements
            # just need to define the behavior to fix this exception
            raise Exception("Undefined Interpretation for DRS Expression",line)
    
    return factsExpression,nestedExpressions 
    
def interpret_ace(ace,makeLogFiles=False):
    '''interpret the ACE to obtain facts,rules,as well as new reasoner facts and rules'''
    
    # get DRS
    drs = getDRSFromACE(ace)   
    if makeLogFiles and os.path.isfile("interpreter/DRS.txt"): os.remove("interpreter/DRS.txt")

    # get ready to read
    initEmpties()
    regexPatterns = compileRegexes()

    # read DRS
    factsExpression,nestedExpressions = readExpressions(drs,regexPatterns,makeLogFiles)
    
    # interpret expressions as rules
    facts,interpretedFactsExpression = makeFacts(factsExpression.copy())    
    rules = makeRules(interpretedFactsExpression,nestedExpressions)
    
    # reason over rules
    reasonerFacts,groundRules = runProlog([x.copy() for x in facts],[x.copy() for x in rules],makeLogFiles)
    
    if makeLogFiles:
        for fact in facts: print(fact)
        for rule in rules: print(rule)
        for reasonerFact in reasonerFacts: print(reasonerFact[1])
        for groundRule in groundRules: print(groundRule[1])
    
    return ace,factsExpression,nestedExpressions,facts,rules,reasonerFacts,groundRules

def main():
    
    if os.path.isfile("interpreter/reasonerFacts.txt"): os.remove("interpreter/reasonerFacts.txt")
    if os.path.isfile("interpreter/groundRules.txt"): os.remove("interpreter/groundRules.txt")
    if os.path.isfile("interpreter/DRS.txt"): os.remove("interpreter/DRS.txt")
    if os.path.isfile("interpreter/prolog.pl"): os.remove("interpreter/prolog.pl")

    ontology = Ontology(stopOldServer=True,loadFile='uagent.owl')

    ontology.add_instruction_knowledge(*interpret_ace(open("interpreter/ace.txt","r").read(),makeLogFiles=True))
    
    logfile = open("logfile.txt","w")
    
    logfile.write("Facts:\n")
    for fact in ontology.get_instruction_facts():
        logfile.write("{}\n".format(str(fact)))
        
    logfile.write("\nLearned Facts:\n")
    for fact in ontology.get_instruction_reasoner_facts():
        logfile.write("{}\n".format(str(fact)))
        
    logfile.write("\nRules:\n")
    for rule in ontology.get_instruction_rules():
        logfile.write("{}\n".format(str(rule)))
    
    logfile.write("\nSolved Rules:\n")
    for rule in ontology.get_instruction_ground_rules():
        logfile.write("{}\n".format(str(rule)))   
    
    logfile.write("\n{} DRS Strings:\n".format(str(ontology.countDRSStrings())))
    for drs in ontology.get_DRS_Strings():
        logfile.write("{}\n".format(str(drs)))
    
    logfile.write("\n{} ACE Strings:\n".format(str(ontology.countACEStrings())))
    for ace in ontology.get_ACE_Strings():
        logfile.write("{}\n".format(str(ace)))
    
    logfile.close()
    
def demo(ace):
    
    ace,factsExpression,nestedExpressions,facts,rules,reasonerFacts,groundRules = interpret_ace(ace,makeLogFiles=True)
    
    print()
    
class Interpreter:

    def __init__(self, memory):
        self.memory = memory

    def interpret_ace(self,ace):
        '''Interprets ACE text and adds the resulting knowledge to memory'''
        self.memory.add_instruction_knowledge(interpret_ace(ace))

if __name__ == "__main__":
    
    #demo(open("interpreter/demo.txt","r").read())
    
    main()