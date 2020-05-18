import os.path
from PyQt5.QtWidgets import QDialog, QListWidget,QListWidgetItem
from PyQt5 import uic
from PyQt5.Qt import Qt
from Controller.EditAndAddTermsController import EditAndAddTermsController

class EditCategoriesForTermView(QDialog):
    # setting up the path of the ui file
    file_path = os.path.dirname(os.path.abspath(__file__))
    ui_path = os.path.join(file_path, "EditCategoriesForTerm.ui")

    def __init__(self, term_editing_categories_for):
        # getting the controller ready
        self.edit_and_add_terms_controller = EditAndAddTermsController()
        # connecting to database
        self.edit_and_add_terms_controller.connect_to_database()

        super(EditCategoriesForTermView, self).__init__()
        # taking out Question mark button by x button
        self.setWindowFlags(self.windowFlags() & Qt.WindowContextHelpButtonHint)

        uic.loadUi(self.ui_path, self)

        self.term_editing_categories_for = term_editing_categories_for

        # gets the categories the term is already in so they can be preselected in the
        # categegory list widget
        categories_term_is_already_in = self.edit_and_add_terms_controller.\
            get_all_of_a_terms_categories(self.term_editing_categories_for[0])

        # getting every category present in database
        categories = self.edit_and_add_terms_controller.get_all_categories()
        # setting up category list widget
        # allowing the user to select multiple categories from the category list widget
        self.CategoryListWidget.setSelectionMode(QListWidget.MultiSelection)
        # adding each category except All Terms to the Category List Widget
        # All Terms is not added because terms are not allowed to be taken out of this category unless they are deleted
        for category in categories:
            if category != "All Terms":
                category_list_widget_item = QListWidgetItem(category)
                category_list_widget_item.setTextAlignment(Qt.AlignCenter)
                self.CategoryListWidget.addItem(category_list_widget_item)
                ''' check if the category that was added is a category that the term
                 is already in. 
                 if it is a category the term was already in, select it to show the users'''
                for category_term_is_already_in in categories_term_is_already_in:
                    if category == category_term_is_already_in:
                        self.CategoryListWidget.setCurrentItem(category_list_widget_item)

        # used to ensure user actually chagned categories before updating upon done button's click
        self.selected_categories = self.CategoryListWidget.selectedItems()



        # linking close button
        self.CancelButton.clicked.connect(self.cancel_button_clicked)

        #linking done button
        self.DoneButton.clicked.connect(self.done_button_clicked)

    # when the cancel button is clicked, rollback the database
    def cancel_button_clicked(self):
        self.edit_and_add_terms_controller.rollback_database()
        self.close()

    # overrode the closeEvent to ensure that the database transaction is closed
    def closeEvent(self, event):
        self.edit_and_add_terms_controller.rollback_database()
        event.accept()

    # commits the transaction unless current selected
    # are the same as previous than rolls back to close transaction and
    # closes the window
    def done_button_clicked(self):
        try:
            if self.CategoryListWidget.selectedItems() != self.selected_categories:
                categories = []
                results = self.CategoryListWidget.selectedItems()
                for result in results:
                    categories.append(result.text())
                self.edit_and_add_terms_controller.update_terms_categories(self.term_editing_categories_for[0], tuple(categories))
                self.edit_and_add_terms_controller.commit_to_database()
            else:
                self.edit_and_add_terms_controller.rollback_database()
            self.close()
        except Exception as e:
            print(str(e))
