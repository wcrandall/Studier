import random


class Category:

    def __init__(self, category, term_list):
        # category name
        self.category = category
        # the list of terms in category
        self.term_list = term_list

    def get_term_list(self):
        return self.term_list

    # gets all of the term's names and ids that are in the category
    def get_all_term_names_and_ids(self):
        term_names = []

        for term in self.term_list:
            term_names.append([term.get_term_id(), term.get_term_name()])

        for i in range(0, len(term_names)):
            term_names[i] = tuple(term_names[i])
        term_names = tuple(term_names)

        return term_names

    # returns all terms in category
    def get_all_terms_in_category(self):
        return self.term_list

    # sets the term list for the category
    def set_term_list(self, term_list):
        self.term_list = term_list

    # gets the categories name
    def get_category_name(self):
        return self.category

    def get_number_of_terms_in_category(self):
        return len(self.term_list)

    # returns a random term in category
    def get_random_term_in_category(self):
        term_index = random.randint(0, self.get_number_of_terms_in_category() - 1)
        return self.term_list.pop(term_index)

