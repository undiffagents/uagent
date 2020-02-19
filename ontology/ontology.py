
class OntologyDatabase:
    '''
    This class contains the API to the ontology database used by other modules
    to add and retrieve knowledge.
    '''

    def __init__(self):
        # currently, the database is a simple list;
        # this should be replaced by the real ontology database
        self.db = []

    def add(self, knowledge):
        '''Adds the given knowledge to the database'''
        self.db.extend(knowledge)
        return self

    def get_next_instruction(self):
        '''Retrieves the next instruction from the database'''
        return None
