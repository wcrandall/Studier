from Model.Quiz import Quiz

# the controller for the testing portion of the application
class TestViewController:
    def __init__(self, category, terms_in_category):
        self.quiz = Quiz(category, terms_in_category)

    # checks if the user's guess is correct
    def is_user_input_correct(self, guess):
        return self.quiz.is_user_input_correct(guess)

    # gets the currently set term for the quiz
    def get_term(self):
        term = self.quiz.get_term()
        return term.get_term_name()

    def get_term_definition(self):
        return self.quiz.current_term.get_term_definition()

    # sets a new term for the quiz
    def set_new_term(self):
        self.quiz.set_new_term_from_category()

    # gets the percentage of terms the user has gotten correct thus far
    def get_percentage_correct(self):
        return self.quiz.get_percentage_correct()

    # gets the number of terms in the category the user is being quizzed on
    def get_number_of_terms_in_category(self):
        return str(self.quiz.get_number_of_terms_in_set())

    # gets the number of terms left in the current quiz
    def get_number_of_terms_remaining(self):
        return str(self.quiz.category_quiz_is_on.get_number_of_terms_in_category())

    # gets the number of terms that have already been gone through in the quiz
    def get_number_of_terms_through(self):
        return str(self.quiz.get_number_of_terms_through())

    # checks if the game has finished
    # IE if all terms have been gone over
    def is_game_finished(self):
        return self.quiz.is_game_finished()

    # increments the number of terms correct
    def increment_number_of_terms_right(self):
        self.quiz.increment_number_of_terms_right()

    # updates the percentage the user has in the quiz
    def update_percentage(self):
        self.quiz.update_percentage_correct()

    # increments the number of terms the user has gone through
    def increment_number_of_terms_through(self):
        self.quiz.increment_number_of_terms_through()
