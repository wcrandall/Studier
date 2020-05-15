from PyQt5 import uic
from PyQt5.QtWidgets import QErrorMessage, QTableView, \
    QAbstractItemView, QMainWindow, QFileDialog, QHeaderView, QListWidgetItem

from Controller.Controller import Controller
from View.EditCategoryView import EditCategoryView
import os.path
from View.HelpView import HelpView
from PyQt5.Qt import Qt
from View.EditAndAddTermsView import EditAndAddTermsView



class MainView(QMainWindow):
    ui_path = os.path.dirname(os.path.abspath(__file__))
    ui_path = os.path.join(ui_path, "studier.ui")

    def __init__(self):
        try:
            super(MainView, self).__init__()
            uic.loadUi(self.ui_path, self)
            self.controller = Controller()

            # creating database and database tables if they don't exist
            self.controller.create_tables()
            # populating the TermCategoriesListWidget
            self.load_term_categories_list_widget()

            '''                          LINKING SIGNALS TO FUNCTIONS                                           '''

            # upon an item being changed in the TermCategoriesListWidget repopulate the TermTableView
            self.TermCategoriesListWidget.currentItemChanged.connect(self.term_categories_list_widget_item_changed)



            # Opens a quiz dialog for the currently selected category
            self.TestButton.clicked.connect(self.test_button_clicked)

            # When the add category option is selected from the top-left menu
            # a dialog to select a file is opened
            # once the file is selected the categories inside are added to database
            self.actionCategories_with_text_file.triggered.connect(self.action_category_with_text_file_clicked)

            # upon the click of the help option in the top-left menu
            # a dialog with information on the application is shown
            self.actionGet_Help.triggered.connect(self.action_help_clicked)

            # upon the click of the EditTermButton the EditAndAddTermsView dialog is opened
            self.EditTermButton.clicked.connect(self.edit_term_button_clicked)

            self.EditCategoriesButton.clicked.connect(self.edit_categories_button_clicked)


            # setting table layout
            self.TermTableView.setSelectionBehavior(QTableView.SelectRows)
            self.TermTableView.setSelectionMode(QAbstractItemView.SingleSelection)
            self.TermTableView.horizontalHeader().setStretchLastSection(True)
            self.TermTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.TermTableView.setColumnHidden(0, True)


        except Exception as e:
            print(str(e))

    # a dialog with information on the application is shown
    def action_help_clicked(self):
        helpView = HelpView()
        helpView.exec_()

    # When the menu bar item add category with text file is clicked
    # this method will split the file into categories to be put into the database
    # by commas and/or newlines
    def action_category_with_text_file_clicked(self):
        try:
            file_name = self.get_file()
            if file_name is not None:
                with open(file_name, "r") as file:
                    for line in file:
                        current_line = line.split(",")
                        for category in current_line:
                            category = category.title()
                            self.controller.insert_category(category.strip())
                self.load_term_categories_list_widget()
        except Exception as e:
            print(str(e))

    # opens the dialog for editing terms
    def edit_term_button_clicked(self):
        try:
            # if there is a category selected pass it
            # if not, default category, All Terms, will be used.
            if self.TermCategoriesListWidget.currentItem() is not None:
                category = self.TermCategoriesListWidget.currentItem().text()
                edit_and_add_terms = EditAndAddTermsView(category)
            else:
                edit_and_add_terms = EditAndAddTermsView()

            edit_and_add_terms.exec_()

            # update terms in view so new ones and edited ones are shown properly
            self.term_categories_list_widget_item_changed()
        except Exception as e:
            print(str(e))




    # opens a dialog that allows the user to chose a file
    # it than returns the file directory
    def get_file(self):
        try:
            dlg = QFileDialog()
            dlg.setFileMode(QFileDialog.AnyFile)
            dlg.setNameFilter("Text files (*.txt)")
            dlg.exec_()
            file_names = dlg.selectedFiles()
        except Exception as e:
            print(str(e))
        if len(file_names) != 0:
            return file_names[0]

    # brings up the test dialog and starts test on terms in
    # the category selected
    def test_button_clicked(self):
        try:
            # getting selected category
            selected_category = self.controller.get_current_category()
            # if the category is not None check if category holds terms
            if selected_category is not None:
                # if category holds terms begin quiz
                if self.controller.get_number_of_terms_in_category() != 0:
                    self.controller.begin_quiz(selected_category)
                else:
                    # if category doesn't hold terms show an error message
                    error_dialog = QErrorMessage(self)
                    error_dialog.showMessage("There are no terms in the selected category")
            else:
                # if there is no selected category show an error message
                error_dialog = QErrorMessage(self)
                error_dialog.showMessage("There is not a category selected")
        except Exception as e:
            print("here " + str(e))

    # load the current categories in the database
    def load_term_categories_list_widget(self):
        try:
            # clear the categories that are currently being displayed
            self.TermCategoriesListWidget.clear()
            # get all categories from database
            categories = self.controller.get_all_categories()

            # create list widget items for each category
            # align each list widget item center
            # add the list widget item to the database
            for category in categories:
                category_list_widget_item = QListWidgetItem(category)
                category_list_widget_item.setTextAlignment(Qt.AlignCenter)
                self.TermCategoriesListWidget.addItem(category_list_widget_item)
        except Exception as e:
            print(str(e))

    # loads the terms for the current category selected
    def term_categories_list_widget_item_changed(self):
        try:
            selected_item = self.TermCategoriesListWidget.currentItem()
            if selected_item is not None:
                selected_item_text = selected_item.text()
                self.controller.set_category(selected_item_text)
                # using the set category a new model is created for the table
                # that holds the set categories terms
                terms_names_and_ids_in_category = self.controller.get_term_names_in_category_and_ids()
                # if the category is not None update term table view
                if terms_names_and_ids_in_category is not None:
                    self.TermTableView.setModel(terms_names_and_ids_in_category)
                    # hiding term ids in the term table view
                    self.TermTableView.setColumnHidden(0, True)


        except Exception as e:
            print(str(e))

    def edit_categories_button_clicked(self):
        edit_category_view = EditCategoryView()
        edit_category_view.exec_()
        self.load_term_categories_list_widget()



