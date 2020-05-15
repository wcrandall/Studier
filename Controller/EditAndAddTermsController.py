from Database.DatabaseAccess import DatabaseAccess
from Model.Term import Term

# the controller for the editing and adding terms portion of the application
class EditAndAddTermsController:

    def __init__(self):
        self.database = DatabaseAccess()

    def connect_to_database(self):
        self.database.connect()

    # begins a transaction in the database
    # def begin_tran(self):
    #     self.database.begin_tran()

    # commits current edits to database
    # IE ends tran and saves edits
    def commit_to_database(self):
        self.database.commit()

    # undoes the edits done in current transaction
    def rollback_database(self):
        self.database.rollback()

    # inserts a term into database
    def insert_term(self, term_name, term_description, term_categories):
        return self.database.insert_term(term_name, term_description, term_categories)

    # updates a term in database
    def update_term(self, term_id, term_item, whats_being_updated):
        return self.database.update_term(term_id, term_item, whats_being_updated)

    # deletes term in database
    def delete_terms(self, term_ids):
        self.database.delete_terms(term_ids)

    def get_term_id_with_name_and_description(self, term_name, term_description):
        return self.database.get_term_id_with_name_and_description(term_name, term_description)

    def check_if_term_already_exists(self, term_name=None, term_description=None, term_id=None):
        return self.database.check_if_term_exists(term_name, term_description, term_id)

    # updates the categories for selected term
    def update_terms_categories(self, term_id, term_categories):
        return self.database.update_terms_categories(term_id, term_categories)

    def get_all_of_a_terms_categories(self, term_id):
        return self.database.get_all_of_a_terms_categories(term_id)

    def get_all_categories(self):
        results = self.database.get_all_categories()
        return results

    # gets all terms in selected category
    def get_all_terms_in_category(self, category):
        results = self.database.get_all_terms_in_category(category)
        terms = []
        for result in results:
            term = Term(result[0], result[1], result[2])
            terms.append(term)

        return terms

    # closes database connection
    def close_connection(self):
        self.database.close_connection()

    # gets all categories for selected term
    def get_all_of_a_terms_categories(self, term_id):
        return self.database.get_all_of_a_terms_categories(term_id)


