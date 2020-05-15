class Term:
    def __init__(self, term_name, term_definition=None, term_id=None):
        self.term_name = term_name
        self.term_definition = term_definition
        self.term_id = term_id

    def get_term_definition(self):
        return self.term_definition

    def get_term_name(self):
        return self.term_name

    def get_term_id(self):
        return self.term_id


