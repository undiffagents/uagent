# interpreter old

def groundExpressions(predicates,objects,properties,fact=True):
    '''performs a "grounding" on DRS objects so that the proper terms
    are uniformly substituted in accordance with the semantics to
    obtain Classes and Roles for use in a logic or rules-based program'''
    
    sameThings = []
    
    # ground all the predicates from DRS
    for i in range(len(predicates)):
        if isinstance(predicates[i],Role):
            predicates[i] = groundDRSPredicate(predicates[i],objects if fact else ObjectList(),properties)        
        elif isinstance(predicates[i],Predicate): 
            newTerms = []
            for term in predicates[i].terms:
                if fact and term in objects.var and term in objects.var.values():
                    newTerms.append(term)
                elif fact and term in objects.var:
                    newTerms.append(objects.var[term])
                elif term in properties.var:
                    newTerms.append(properties.var[term])
                else:
                    newTerms.append(term)
            predicates[i].terms = newTerms
            continue
        
        if predicates[i].name == 'equal': sameThings.append(predicates[i])
        elif predicates[i].name == 'be':
            objects.var[predicates[i].args[0]] = objects.var[predicates[i].args[1]]
            del objects.var[predicates[i].args[1]]
            predicates[i] = Class(predicates[i].letter,objects.var[predicates[i].args[0]],predicates[i].args[0])
    
    # figure out all the class and instance names
    if fact: 
        cs = list(filter(lambda x: isinstance(x,Class),predicates))
        classes = set([y.name for y in cs] + [y.args[0] for y in cs])    
    
    # add predicates for anything that is a name for something else
    sameNames = []
    for same in sameThings:
        
        # if it is an ininstantiated class, make this an instance of that class (since there won't be one)
        if same.args[0] in objects.var.values() and same.args[0] not in classes:
            predicates.append(Class(same.letter,same.args[1],same.args[0]))
            classes.add(same.args[0])
        elif same.args[1] in objects.var.values() and same.args[1] not in classes: 
            predicates.append(Class(same.letter,same.args[1],same.args[0]))
            classes.add(same.args[1])
        
        # make the same facts about the thing as its equal
        for pred in predicates:            
            if pred.name == 'equal': continue
            if isinstance(pred,Class):
                if pred.args[0] == same.args[1] and pred.args[0] != same.args[0]:
                    classes.add(pred.args[0])
                    sameNames.append(Class(pred.indent,pred.letter,pred.name,same.args[0],pred.args[-2],pred.args[-1]))
                elif pred.args[0] == same.args[0] and pred.args[0] != same.args[1] and not (pred.args[0] in objects.var and same.args[1] in objects.var and objects.var[same.args[1]] in objects.var):
                    classes.add(pred.args[0])
                    sameNames.append(Class(pred.indent,pred.letter,pred.name,same.args[1],pred.args[-2],pred.args[-1]))
            elif isinstance(pred,Role): 
                if pred.args[1] == same.args[1] and pred.args[1] != same.args[0]:
                    sameNames.append(Role(pred.indent,pred.letter,pred.name,pred.args[0],same.args[0],pred.args[-2],pred.args[-1]))
                elif pred.args[1] == same.args[0] and pred.args[1] != same.args[1]:
                    sameNames.append(Role(pred.indent,pred.letter,pred.name,pred.args[0],same.args[1],pred.args[-2],pred.args[-1]))    
                if pred.args[0] == same.args[1] and pred.args[0] != same.args[0]:
                    sameNames.append(Role(pred.indent,pred.letter,pred.name,same.args[0],pred.args[1],pred.args[-2],pred.args[-1]))
                elif pred.args[0] == same.args[0] and pred.args[0] != same.args[1]:
                    sameNames.append(Role(pred.indent,pred.letter,pred.name,same.args[1],pred.args[1],pred.args[-2],pred.args[-1]))
                 
    if fact:
        # add facts for objects that have no named instance
        for obj in objects.objs:
            if obj.name in classes: continue
            else: 
                if objects.var[obj.letter] in objects.var:
                    predicates.append(Class(obj.indent,obj.letter,objects.var[objects.var[obj.letter]],objects.var[obj.letter],obj.args[-2],obj.args[-1]))
                else:
                    predicates.append(Class(obj.indent,obj.letter,obj.name,obj.name,obj.args[-2],obj.args[-1]))
                if obj.letter in properties.var:
                    predicates.append(Role(obj.indent,obj.letter,"hasProperty",obj.name,properties.var[obj.letter],obj.args[-2],obj.args[-1]))
            classes.add(obj.name)
    else:
        # add variable Classes for objects that have no named instance, renaming if a global instance
        for obj in objects.objs:
            if obj.letter in objects.var:
                predicates.append(Class(obj.indent,obj.letter,objects.var[obj.name] if obj.name in objects.var else obj.name,obj.letter,obj.args[-2],obj.args[-1])) 
    
    predicates = predicates + sameNames
    
    return predicates

def groundDRSPredicate(pred,objects,properties):
    '''"Grounds" one DRS predicate'''
    
    subjectVar = re.match("^([A-Z][0-9]*)$",pred.args[0])
    objectVar  = re.match("^([A-Z][0-9]*)$",pred.args[1])
    
    subjectVar = None if not subjectVar else subjectVar.groups()[0]    
    objectVar = None if not objectVar else objectVar.groups()[0]
    
    # both terms are variables
    if subjectVar and objectVar:
        for var in objects.var:
            
            if var == subjectVar:
                pred.args[0] = objects.var[var]
                subjectVar = None
            elif var == objectVar:
                pred.args[1] = objects.var[var]
                objectVar = None
                
            if pred.name == 'be' and objectVar == None and len(objects.var) == 1:
                objects.var[pred.args[0]] = pred.args[1]
                if var in objects.var:
                    del objects.var[var]
                return Class(pred.indent,pred.letter,pred.args[1],pred.args[0],pred.args[-2],pred.args[-1]) 
            elif pred.name == 'be' and subjectVar == None and len(objects.var) == 1:
                objects.var[pred.args[1]] = pred.args[0]
                if var in objects.var:
                    del objects.var[var]
                return Class(pred.indent,pred.letter,pred.args[1],pred.args[0],pred.args[-2],pred.args[-1])      
            elif subjectVar == None and objectVar == None and pred.name == 'be':
                if objects.var[var] in objects.var:
                    return Class(pred.indent,pred.letter,objects.var[objects.var[var]],checkDictsForKey(var,objects.var),pred.args[-2],pred.args[-1])
                elif pred.args[1] in objects.var:
                    return Class(pred.indent,pred.letter,objects.var[objects.var[var]],objects.var[var],pred.args[-2],pred.args[-1])                
                elif objects.var[var] == pred.args[0]:
                    objects.var[var] = pred.args[1]
                else:
                    objects.var[var] = pred.args[0]
                objects.var[pred.args[0]] = pred.args[1]
                return Class(pred.indent,pred.letter,pred.args[1],pred.args[0],pred.args[-2],pred.args[-1])
            elif subjectVar == None and objectVar == None:
                return pred
                     
        for var in properties.var:
            if var == objectVar:
                return Role(pred.indent,pred.letter,"hasProperty",pred.args[0],properties.var[var],pred.args[-2],pred.args[-1])
        
        return pred
    # object is a variable
    elif objectVar:   
        for var in objects.var:
            if var == objectVar and pred.name == 'be' and re.match("^\'.*\'$",pred.args[0]):                
                return Role(pred.indent,pred.letter,"equal",objects.var[pred.args[1]],pred.args[0],pred.args[-2],pred.args[-1])            
            elif var == objectVar and pred.name == 'be':
                objects.var[pred.args[0]] = objects.var[var]
                objects.var[var] = pred.args[0]
                #print(Class(pred.indent,pred.letter,objects.var[pred.args[0]],objects.var[var]))
                return Class(pred.indent,pred.letter,objects.var[pred.args[0]],objects.var[var],pred.args[-2],pred.args[-1])                          
            elif var == objectVar:
                return Role(pred.indent,pred.letter,pred.name,pred.args[0],objects.var[var],pred.args[-2],pred.args[-1])                  
        for var in properties.var:
            if var == objectVar:
                return Role(pred.indent,pred.letter,"hasProperty",pred.args[0],properties.var[var],pred.args[-2],pred.args[-1])
        if pred.name == 'be' and re.match("^\'.*\'$",pred.args[0]):
            return Role(pred.indent,pred.letter,"equal",pred.args[0],pred.args[1],pred.args[-2],pred.args[-1]) 
        else:
            return pred
    # subject is a variable
    elif subjectVar:        
        for var in objects.var:
            if var == subjectVar and pred.name == 'be' and re.match("^\'.*\'$",pred.args[1]):
                return Role(pred.indent,pred.letter,"equal",objects.var[pred.args[0]],pred.args[1],pred.args[-2],pred.args[-1])             
            elif var == subjectVar and pred.name == 'be':
                objects.var[pred.args[0]] = objects.var[var]
                objects.var[var] = pred.args[0]
                return Class(pred.indent,pred.letter,objects.var[pred.args[0]],objects.var[var],pred.args[-2],pred.args[-1])                          
            elif var == objectVar:
                return Role(pred.indent,pred.letter,pred.name,pred.args[0],objects.var[var],pred.args[-2],pred.args[-1])  
        for var in properties.var:
            if var == objectVar:
                return Role(pred.indent,pred.letter,"hasProperty",pred.args[0],properties.var[var],pred.args[-2],pred.args[-1])   
        if pred.name == 'be' and re.match("^\'.*\'$",pred.args[1]):
            return Role(pred.indent,pred.letter,"equal",pred.args[0],pred.args[1],pred.args[-2],pred.args[-1]) 
        else:
            return pred
    
    # shouldn't ground a fact
    raise Exception("Undefined Semantics",pred)

def addGlobalValuesToPredicateList(l,globalObjects,globalProperties):
    '''Extend local variables in implications with the global variables from the DRS'''
    
    # properties are global
    l[2].var.update(globalProperties.var)
        
    gloInst = [(k,globalObjects.var[k]) for k in filter(lambda x: not re.match("[A-Z][0-9]*",x),globalObjects.var)]
    loc = [(k,l[1].var[k]) for k in l[1].var]
        
     # objects are local (named instances may require renaming, so the names are added)
    for k in gloInst + loc:
        l[1].var[k[0]] = k[1]
    
    return l

def removeDuplicates(body):
    '''Self explanatory'''
    
    noDups = []
    for atom in body.body:
        unique = True
        for atom2 in noDups:
            if str(atom) == str(atom2): unique = False ; break
        if unique: noDups.append(atom)
    body.body = noDups
    return body

def groundImplication(body,head,globalObjects,globalProperties):
    '''performs a "grounding" on each DRS object in an implication'''
    
    newImps = [] 
    
    # ground the head and body
    if head[0] == "i":
        head = groundImplication(head[1],head[2],globalObjects,globalProperties)
    else:
        head = set(groundExpressions(*addGlobalValuesToPredicateList(head,globalObjects,globalProperties),False))
    
    newBody = Body()    
    if body[0] == "i":
        imps = groundImplication(body[1],body[2],globalObjects,globalProperties)
        for imp in imps:
            newBody.append(imp.head)
            for pred in imp.body.body:
                newBody.append(pred)
    else:
        for pred in set(groundExpressions(*addGlobalValuesToPredicateList(body,globalObjects,globalProperties),False)):
            newBody.append(pred)                     
        
    # if a Class or Role in the head has a variable that isn't in the body, it should be moved to the body (language quirk)
    for pred in set(filter(lambda x: isinstance(x,Class),head)):
        if re.match("[A-Z][0-9]*",pred.args[0]) and pred.args[0] not in newBody.var:
            newBody.append(pred)
            head.remove(pred)
    for pred in set(filter(lambda x: isinstance(x,Role),head)):
        if re.match("[A-Z][0-9]*",pred.args[0]) and pred.args[0] not in newBody.var and pred.args[0] in globalObjects.var:
            newBody.append(Class(pred.indent,pred.args[0],checkDictsForKey(pred.args[0],globalObjects.var),pred.args[0],pred.args[-2],pred.args[-1]))
        if (re.match("[A-Z][0-9]*",pred.args[1]) and pred.args[1] not in newBody.var):
            newBody.append(Class(pred.indent,pred.args[1],checkDictsForKey(pred.args[1],globalObjects.var),pred.args[1],pred.args[-2],pred.args[-1]))
    
    # if a Class or Role in the body has a variable that is a DRS global variable, make a class with that variable in the body
    for pred in set(filter(lambda x: isinstance(x,Class),newBody.body)):
        if pred.args[0] in globalObjects.var:
            newBody.append(Class(pred.indent,pred.args[0],checkDictsForKey(pred.args[0],globalObjects.var),pred.args[0],pred.args[-2],pred.args[-1]))
    for pred in set(filter(lambda x: isinstance(x,Role),newBody.body)):
        if pred.args[0] in globalObjects.var:
            newBody.append(Class(pred.indent,pred.args[0],checkDictsForKey(pred.args[0],globalObjects.var),pred.args[0],pred.args[-2],pred.args[-1]))
        if pred.args[1] in globalObjects.var:
            newBody.append(Class(pred.indent,pred.args[1],checkDictsForKey(pred.args[1],globalObjects.var),pred.args[1],pred.args[-2],pred.args[-1]))
    
    # make an implication from each head with the same body
    for atom in head:
        newImps.append(Implication(removeDuplicates(newBody),atom))
    
    return newImps