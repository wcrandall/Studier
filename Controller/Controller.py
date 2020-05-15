from Database.DatabaseAccess import DatabaseAccess
from View.TestView import TestView
from Model.Category import Category
from Model.Term import Term
from Model.TermTableModel import TermTableModel


class Controller:
    category = None

    # creates the tables in the database that are needed for this application
    def create_tables(self):
        database = DatabaseAccess()
        database.connect()
        database.create_tables()
        database.commit()
        database.close_connection()


    # gettings all terms in new category from database
    def get_all_terms_in_category(self, category):
        database = DatabaseAccess()
        database.connect()
        results = database.get_all_terms_in_category(category)
        database.close_connection()
        terms = []
        for result in results:
            term = Term(result[0], result[1], result[2])
            terms.append(term)

        return terms

    # setting a new category selection
    def set_category(self, category_name):
        term_list = self.get_all_terms_in_category(category_name)
        self.category = Category(category_name, term_list)

    # get term names and ids in the currently selected category
    def get_term_names_in_category_and_ids(self):
        terms_and_ids = self.category.get_all_term_names_and_ids()
        if terms_and_ids == ():
            term_table_model = TermTableModel(("",))
        else:
            term_table_model = TermTableModel(terms_and_ids)
        return term_table_model

    def get_empty_term_table_view_model(self):
        return TermTableModel(("", ))

    # get all categories currently stored in database
    def get_all_categories(self):
        database = DatabaseAccess()
        database.connect()
        results = database.get_all_categories()
        database.close_connection()
        return results

    # open the quiz dialog
    def begin_quiz(self, category):
        terms_in_category = self.get_all_terms_in_category(category)
        test_view = TestView(category, terms_in_category)
        test_view.exec_()

    # gets the currently selected category
    def get_current_category(self):
        if self.category is not None:
            return self.category.get_category_name()

    # def get_all_of_a_terms_categories(self, term_id):
    #     database = DatabaseAccess()
    #     results = database.get_all_of_a_terms_categories(term_id)
    #     database.close_connection()
    #     return results

    # gets the number of terms in currently selected category
    def get_number_of_terms_in_category(self):
        return self.category.get_number_of_terms_in_category()


