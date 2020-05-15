from Model.Category import Category

# holds the category that the user is getting quizzed on
# holds methods that interact with category and term for quiz
class Quiz:

    def __init__(self, category, term_list):
        self.category_quiz_is_on = Category(category, term_list)
        self.number_of_terms_in_set = self.category_quiz_is_on.get_number_of_terms_in_category()
        self.current_term = self.category_quiz_is_on.get_random_term_in_category()
        self.number_of_terms_right = 0
        self.number_of_terms_through = 1
        self.percentage_correct = 0

    # checks if the user's input is correct
    def is_user_input_correct(self, user_input):
        is_correct = False
        if self.current_term.get_term_name() == user_input:
            is_correct = True
        return is_correct

    # returns the number of terms correct so far
    def get_number_of_terms_right(self):
        return self.number_of_terms_right

    # gets the number of terms through so far
    def get_number_of_terms_through(self):
        return self.number_of_terms_through

    # gets the total number of terms in set
    def get_number_of_terms_in_set(self):
        return self.number_of_terms_in_set

    # increments the number terms through
    def increment_number_of_terms_through(self):
        self.number_of_terms_through += 1

    # increments the number of terms right
    def increment_number_of_terms_right(self):
        self.number_of_terms_right += 1

    # gets the current term
    def get_term(self):
        return self.current_term

    # updates the percentage correct
    def update_percentage_correct(self):
        self.percentage_correct = (self.number_of_terms_right /
                                   self.number_of_terms_in_set) * 100

    # returns the percentage correct so far
    def get_percentage_correct(self):
        return self.percentage_correct

    # sets the new term for the quiz
    def set_new_term_from_category(self):
        self.current_term = self.category_quiz_is_on.get_random_term_in_category()

    # returns whether or not the game is finished
    def is_game_finished(self):
        if self.number_of_terms_through == self.number_of_terms_in_set:
            return True
        else:
            return False




