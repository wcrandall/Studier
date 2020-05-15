from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
from Controller.TestViewController import TestViewController
import os.path


class TestView(QDialog):
    ui_path = os.path.dirname(os.path.abspath(__file__))
    ui_path = os.path.join(ui_path, "TermQuiz.ui")

    def __init__(self, category, terms_in_category):
        try:
            super(TestView, self).__init__()
            uic.loadUi(self.ui_path, self)

            # setting up game and ui
            self.test_view_controller = TestViewController(category, terms_in_category)
            self.TermDescriptionLabel.setText(self.test_view_controller.get_term_definition())
            self.CheckButton.clicked.connect(self.check_button_clicked)
            self.QuitButton.clicked.connect(self.quit_button_clicked)
            self.TermOnLabel.setText(self.test_view_controller.get_number_of_terms_through() + "/"
                                     + self.test_view_controller.get_number_of_terms_in_category())
            self.QuizProgressBar.setValue(0)
            self.EnterTermLineEdit.setFocus()

        except Exception as e:
            print(str(e))


    def quit_button_clicked(self):
        self.close()

    # checks if the user's guess is correct or not
    def check_button_clicked(self):
        user_input = self.EnterTermLineEdit.text().strip()
        if self.test_view_controller.is_user_input_correct(user_input):
            try:
                # if the guess given by the user is correct update the percentage and set progress bar
                self.test_view_controller.increment_number_of_terms_right()
                self.test_view_controller.update_percentage()
                self.QuizProgressBar.setValue(self.test_view_controller.get_percentage_correct())
            except Exception as e:
                print(str(e))
        else:
            # give the user a message telling them the correct answer if they got it wrong
            messageBox = QMessageBox()
            messageBox.setText("The correct answer was " + str(self.test_view_controller.get_term()))
            messageBox.exec_()

        # check if the game is finished
        # if the game is finished give the user a message with there score
        if self.test_view_controller.is_game_finished():
            msg = QMessageBox()
            msg.setText("You received a " + str(self.test_view_controller.get_percentage_correct()))
            msg.exec_()
            self.close()
        # if its not finished set up a new term for the user to guess
        else:
            self.test_view_controller.set_new_term()
            self.TermDescriptionLabel.setText(self.test_view_controller.get_term_definition())
            # increment the number of terms through
            self.test_view_controller.increment_number_of_terms_through()
            self.TermOnLabel.setText(self.test_view_controller.get_number_of_terms_through()
                                     + "/" + self.test_view_controller.get_number_of_terms_in_category())
        # clear the enter term line edit and focus on it
        self.EnterTermLineEdit.clear()
        self.EnterTermLineEdit.setFocus()
