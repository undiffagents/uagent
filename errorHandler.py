class ErrorMessage(dict):
    '''
    Class for Error Messages
    Error Messages indicate potentially fatal/crashing behavior
    '''
    
    def __init__(self,error):
        if not type(error)==dict:raise Exception()        
        self.update(error)
        
    def __str__(self):
        return "\n".join(["\t{:<15}{}".format(k+":",self[k]) for k in self.keys()])

    def __repr__(self):
        return str(self)    
        
class WarningMessage(dict):
    '''
    Class for Warning Messages
    Warning Messages indicate potentially incorrect behavior that is not necessarilygoing to break the program.
    '''    

    def __init__(self,warning):
        if not type(warning)==dict:raise Exception()
        self.update(warning)
        
    def __str__(self):
        return "\n".join(["\t{:<15}{}".format(k+":",self[k]) for k in self.keys()])

    def __repr__(self):
        return str(self)  
        
class Messages:
    '''
    Class for Error and Warning messages for a program
    '''
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def getErrors(self):
        return self.errors
    
    def getAPEErrors(self):
        return self.getErrorsFromSource("APE")
    
    def getPrologErrors(self):
        return self.getErrorsFromSource("Prolog")   
    
    def getErrorsFromSource(self,source):
        return list(filter(lambda x: x["source"]==source, self.errors))
    
    def getWarnings(self):
        return self.warnings
    
    def getAPEWarnings(self):
        return self.getWarningsFromSource("APE")
    
    def getPrologWarnings(self):
        return self.getWarningsFromSource("Prolog")
    
    def getWarningsFromSource(self,source):
        return list(filter(lambda x: x["source"]==source, self.warnings))
    
    def append(self,message):
        if isinstance(message,ErrorMessage):
            self.errors.append(message)
        elif isinstance(message,WarningMessage):
            self.warnings.append(message)
        else:
            raise Exception() 
    
    def appendError(self,message):
        self.errors.append(ErrorMessage(message))
    
    def appendWarning(self,message):
        self.warnings.append(WarningMessage(message))
    
    def __str__(self):
        return "Errors:\n{}\nWarnings:\n{}\n".format('\n'.join(['{}\n'.format(str(x)) for x in self.errors]),'\n'.join(['{}\n'.format(str(x)) for x in self.warnings]))

    def __repr__(self):
        return str(self)