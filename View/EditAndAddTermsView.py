from PyQt5.QtWidgets import QDialog, QListWidgetItem
from PyQt5 import uic
from PyQt5.QtWidgets import QErrorMessage
import os.path
from PyQt5.QtWidgets import QTableWidgetItem, QAbstractItemView, QHeaderView, QListWidget
from Controller.EditAndAddTermsController import EditAndAddTermsController
from View.EditCategoriesForTermView import EditCategoriesForTermView
from PyQt5.Qt import Qt

class EditAndAddTermsView(QDialog):
    # setting the path of the ui
    ui_path = os.path.dirname(os.path.abspath(__file__))
    ui_path = os.path.join(ui_path, "EditAndAddTermsDialog.ui")
    ''' when the user edits a term name or description the prior must be saved 
    in order to check if the user actually edited the name or description '''
    before_cell_is_edited = ""

    def __init__(self, category="All Terms"):
        self.category = category
        super(EditAndAddTermsView, self).__init__()
        uic.loadUi(self.ui_path, self)

        # if anything has been changed the database must be comitted to before categories can be edited
        # also used to check if data must be committed when done is clicked
        # working with flags
        self.must_be_saved = False

        # initializing controller for this ui
        self.edit_and_add_terms_controller = EditAndAddTermsController()
        self.edit_and_add_terms_controller.connect_to_database()

        # populating table widget
        self.initialize_term_table_widget(category)

        # formatting term table widget
        self.TermsToEditTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.TermsToEditTableWidget.horizontalHeader().setStretchLastSection(True)
        self.TermsToEditTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.TermsToEditTableWidget.setHorizontalHeaderLabels(
            ["Term ID", "Term Name", "Term Description", "Categories"])
        # formatting and populating category list widget
        # setting up category list widget
        categories = self.edit_and_add_terms_controller.get_all_categories()
        for category in categories:
            if category != "All Terms":
                category_list_widget_item = QListWidgetItem(category)
                category_list_widget_item.setTextAlignment(Qt.AlignCenter)
                self.CategoryListWidget.addItem(category_list_widget_item)
                if category == self.category:
                    self.CategoryListWidget.setCurrentItem(category_list_widget_item)

        # allowing multiple terms to be selected at once
        self.CategoryListWidget.setSelectionMode(QListWidget.MultiSelection)

        # linking add button to function
        self.AddTermButton.clicked.connect(self.add_button_clicked)

        # linkinng edit categories button
        self.EditCategoriesButton.clicked.connect(self.edit_categories_button_clicked)

        # linking cancel button
        self.CancelButton.clicked.connect(self.cancel_button_clicked)

        # linking done editing button
        self.DoneEditingButton.clicked.connect(self.done_editing_button_clicked)

        # linking delete terms button
        self.DeleteTermsButton.clicked.connect(self.delete_terms_button_clicked)

        # linking item double clicked for terms to edit table widget
        self.TermsToEditTableWidget.itemDoubleClicked.connect(self.terms_to_edit_table_widget_double_clicked)

        # linking save button
        self.SaveButton.clicked.connect(self.save_button_clicked)

        # linking clear button to a function that will clear term inputs
        self.ClearSelectionButton.clicked.connect(self.clear_selection_button_clicked)

    # clears the term inputs
    def clear_selection_button_clicked(self):
        self.TermNameLineEdit.clear()
        self.TermDescriptionTextEdit.clear()
        self.CategoryListWidget.clearSelection()

    # commits transaction to database
    ''' all change currently shown in the term table widget will be saved'''
    def save_button_clicked(self):
        self.edit_and_add_terms_controller.commit_to_database()
        self.must_be_saved = False

    def terms_to_edit_table_widget_double_clicked(self, item):
        ''' gets the text of the table widget cell before it is edited by user '''
        self.before_cell_is_edited = item.text()
        ''' the only time a itemChanged should be linked is after a cell is double clicked 
            this ensures that the only time changing a selected cell on the table widget calls terms_to_edit_table_widget_item_changed
            is after a user is done editing a term name or description '''
        self.TermsToEditTableWidget.itemChanged.connect(self.terms_to_edit_table_widget_item_changed)


    def terms_to_edit_table_widget_item_changed(self, item):
        try:
            ''' if the text entered by the user is the same as the text in the cell before 
             DO NOTHING '''
            if item.text() != self.before_cell_is_edited:

                # get the id of the term that was edited
                item_id = self.TermsToEditTableWidget.item(item.row(), 0).text()

                # if the column edited was 1, a term name was changed
                if item.column() == 1:
                    whats_being_updated = "TermName"
                # if the column edited was 2, a description was changed
                elif item.column() == 2:
                    whats_being_updated = "TermDescription"
                # update the term
                # if the update is not successful, throw an error message and set the term table widget cell back to its previous text
                if not self.edit_and_add_terms_controller.update_term(int(item_id), item.text(), whats_being_updated):
                    error_message = QErrorMessage(self)
                    error_message.showMessage("Term with that description and name already enetered ")
                    self.TermsToEditTableWidget.itemChanged.disconnect()
                    self.TermsToEditTableWidget.setItem(item.row(), item.column(),
                                                        QTableWidgetItem(self.before_cell_is_edited))
                    self.TermsToEditTableWidget.itemChanged.disconnect()
                else:
                    # the update was successful disconnect itemchanged
                    # so no unwanted actions are done
                    self.TermsToEditTableWidget.itemChanged.disconnect()
                    # since there is now changed data in the table, the transaction must be committed before categories are edited
                    # or the transaction must be rolledback if the X button is clicked
                    self.must_be_saved = True
        except Exception as e:
            print(str(e))

    # user has finished editing
    # save the database and close the dialog
    def done_editing_button_clicked(self):
        self.edit_and_add_terms_controller.commit_to_database()
        self.close()

    # user wants to cancel previous actions they have performed
    # rollback current transaction and close the window
    def cancel_button_clicked(self):
        self.edit_and_add_terms_controller.rollback_database()
        self.close()

    # deletes all the currently selected term rows in the table
    def delete_terms_button_clicked(self):
        try:
            term_ids = []
            rows_number = []
            # for each row that is selected record the row number and the term id
            for row in self.TermsToEditTableWidget.selectionModel().selectedRows():
                rows_number.append(row.row())
                term_ids.append(int(self.TermsToEditTableWidget.item(row.row(), row.column()).text()))

            ''' the row numbers must be reversed. If they are not reversed, deleting row 1 makes row 2 row 1
            IE numbers are dynamic
            if deleted backwards, higher numbers transforming to lower ones is no concern '''
            rows_number.sort(reverse=True)
            # removing rows from table
            for row in rows_number:
                self.TermsToEditTableWidget.removeRow(row)

            # deleting terms from the database
            self.edit_and_add_terms_controller.delete_terms(term_ids)

            # the data is changed so it must committed before categories are edited or rolledback upon X
            self.must_be_saved = True

        except Exception as e:
            print(str(e))

    # overriding te default closeEvent to avoid database errors
    def closeEvent(self, event):
        # if the data in database has been entered in any way roll back the database
        if self.must_be_saved:
            self.edit_and_add_terms_controller.rollback_database()
        event.accept()

    # adds the terms in the selected category to the term table widget
    # if there is no category given it defaults to All Terms
    def initialize_term_table_widget(self, category="All Terms"):
        try:
            # if there are any rows already in the term table widget remove them
            while self.TermsToEditTableWidget.rowCount() > 0:
                self.TermsToEditTableWidget.removeRow(0)

            # get all the terms in the category given
            terms = self.edit_and_add_terms_controller.get_all_terms_in_category(category)


            for term in terms:
                # gets all the categories the term is in
                categories = self.edit_and_add_terms_controller.get_all_of_a_terms_categories(term.get_term_id())
                # adds the row to the term table widget
                self.add_row_to_term_table_widget(term.get_term_id(), term.get_term_name(),
                                                 term.get_term_definition(), categories)
        except Exception as e:
            print(str(e))

    # adds a row to term table widget
    def add_row_to_term_table_widget(self, term_id, term_name, term_description, term_categories):
        # gets the position in table the row must be added
        row_position = self.TermsToEditTableWidget.rowCount()
        # inserts a blank row
        self.TermsToEditTableWidget.insertRow(row_position)

        # creating a cell item with the term id
        term_id_widget_item = QTableWidgetItem(str(term_id))
        # setting text alignment to center for cell
        term_id_widget_item.setTextAlignment(Qt.AlignCenter)
        #  setting the specified cell in the table to the cell item
        self.TermsToEditTableWidget.setItem(row_position, 0, term_id_widget_item)
        # makes item not selectable
        self.TermsToEditTableWidget.item(row_position, 0).setFlags(Qt.ItemIsSelectable)

        term_name_widget_item = QTableWidgetItem(term_name)
        term_name_widget_item.setTextAlignment(Qt.AlignCenter)
        self.TermsToEditTableWidget.setItem(row_position, 1, term_name_widget_item)

        term_description_widget_item = QTableWidgetItem(term_description)
        term_description_widget_item.setTextAlignment(Qt.AlignCenter)
        self.TermsToEditTableWidget.setItem(row_position, 2, term_description_widget_item)

        # creating a string of the categories the term is in
        categories_string = ""
        i = 0
        for category in term_categories:
            if i != len(term_categories) - 1:
                categories_string += category + ", "
            else:
                categories_string += category
            i += 1

        category_widget_item = QTableWidgetItem(categories_string)
        category_widget_item.setTextAlignment(Qt.AlignCenter)
        self.TermsToEditTableWidget.setItem(row_position, 3, category_widget_item)
        self.TermsToEditTableWidget.item(row_position, 3).setFlags(Qt.ItemIsSelectable)

    # activated when add button is clicked
    def add_button_clicked(self):
        try:
            # getting the ListWidgetItems selected in the category list widget
            results = self.CategoryListWidget.selectedItems()
            categories = []

            # getting the categories out of the list widget item
            for result in results:
                categories.append(result.text())

            # getting the term name
            term_name = self.TermNameLineEdit.text().strip()
            # getting the term description
            term_description = self.TermDescriptionTextEdit.toPlainText().strip()

            # if the term doesn't exist, the term_name isn't empty, and the term description isn't empty, add the term.
            if not self.edit_and_add_terms_controller.check_if_term_already_exists(term_name,
                                                                                   term_description) and term_name != "" and term_description != "":
                # if the term is inserted correctly
                if self.edit_and_add_terms_controller.insert_term(term_name, term_description, categories):
                    '''the database must be committed too before categories 
                    can be edited or the database must be rolled back if Xed'''
                    self.must_be_saved = True
                    # get the term id of the newly added term
                    term_id = self.edit_and_add_terms_controller.get_term_id_with_name_and_description(term_name,
                                                                                                       term_description)
                    # add the term to the table widget for terms
                    self.add_row_to_term_table_widget(term_id, term_name, term_description,
                                                     self.edit_and_add_terms_controller.get_all_of_a_terms_categories(
                                                         term_id))
            else:
                # show an error message if the term was not added correctly
                error_message = QErrorMessage(self)
                error_message.showMessage(
                    "The term with that description and name already exists or one of the fields was left empty.")
            # clear selection upon addition or failure of addition
            self.clear_selection_button_clicked()
        except Exception as e:
            print(str(e))

    def edit_categories_button_clicked(self):
        try:
            # if the database doesn't need to be committed and a term one term is selected, open the edit categories dialog.
            if not self.must_be_saved:
                if len(self.TermsToEditTableWidget.selectionModel().selectedRows()) != 1:
                    error_dialog = QErrorMessage(self)
                    error_dialog.showMessage("Only one term can be selected when editing categories")
                else:
                    # getting the term that is selected
                    for row in self.TermsToEditTableWidget.selectionModel().selectedRows():
                        term = (int(self.TermsToEditTableWidget.item(row.row(), row.column()).text()),
                                self.TermsToEditTableWidget.item(row.row(), 1).text())
                    self.edit_and_add_terms_controller.close_connection()

                    # launching edit categories view
                    edit_categories_for_term_view = EditCategoriesForTermView(term)
                    edit_categories_for_term_view.exec_()

                    # reconnect to database after category editing is done
                    self.edit_and_add_terms_controller.connect_to_database()

                    # reinitialize term table widget so the category change is shown
                    self.initialize_term_table_widget(self.category)
            else:
                # tell the user they must save the current transaction
                # IE there is edited data that hasn't been committed to the database
                error_dialog = QErrorMessage(self)
                error_dialog.showMessage("You must Save transaction before you edit categories")
        except Exception as e:
            print(str(e))

