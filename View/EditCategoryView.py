from PyQt5.QtWidgets import QDialog, QErrorMessage
from PyQt5 import uic
from PyQt5.QtWidgets import QTableWidgetItem, QAbstractItemView, QHeaderView
from Controller.EditAndAddCategoriesController import EditAndAddCategoriesController
import os.path
from Controller.EditAndAddCategoriesController import EditAndAddCategoriesController
from PyQt5.Qt import Qt





class EditCategoryView(QDialog):
    # setting up the ui path
    file_path = os.path.dirname(os.path.abspath(__file__))

    ui_path = os.path.join(file_path, "EditCategory.ui")

    # used to ensure the edited cell data is not the same as original
    before_cell_is_edited = ""

    def __init__(self):
        super(EditCategoryView, self).__init__()
        # taking out Question mark button by x button
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        uic.loadUi(self.ui_path, self)

        # setting up controller and connecting to the database
        self.edit_and_add_categories_controller = EditAndAddCategoriesController()
        self.edit_and_add_categories_controller.connect_to_database()

        # populates the category table widget
        self.initialize_category_table_widget()


        # formatting Category table widget
        self.CategoryTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.CategoryTableWidget.horizontalHeader().setStretchLastSection(True)
        self.CategoryTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.CategoryTableWidget.setHorizontalHeaderLabels(
            ["Category ID", "Category Name"])

        ''' linking ui buttons and table cells to methods '''
        self.CategoryTableWidget.itemDoubleClicked.connect(self.category_table_widget_cell_double_clicked)
        self.DoneButton.clicked.connect(self.done_button_clicked)
        self.CancelButton.clicked.connect(self.cancel_button_clicked)
        self.AddCategoryButton.clicked.connect(self.add_category_button_clicked)
        self.ClearButton.clicked.connect(self.clear_button_clicked)
        self.DeleteCategoriesButton.clicked.connect(self.delete_categories_button_clicked)

    # grabs the data from the Insert category line edit and adds it to the database
    # unless the category already exists
    def add_category_button_clicked(self):
        # getting the category the user entered
        category_name = self.InsertCategoryLineEdit.text()
        # taking out spaces at end and beginning
        category_name = category_name.strip()
        # capitalizing first letter in every word
        category_name = category_name.title()
        # if the category doesn't exist and the name isn't an empty string
        # insert the category into the database
        if (not self.edit_and_add_categories_controller.check_if_category_exists_with_name(category_name)) and (category_name != ""):
            self.edit_and_add_categories_controller.insert_category(category_name)
             # get the newly inserted category's id
            category_id = self.edit_and_add_categories_controller.get_category_id_with_name(category_name)
            # add the category to the category table widget
            self.add_row_to_category_table_widget(category_id, category_name)
        else:
            # if the category already existed or was an empty string display an error message
            error_message = QErrorMessage(self)
            error_message.showMessage("The category either already exists or the name input was left blank")
        self.clear_button_clicked()

    # clears the category input
    def clear_button_clicked(self):
        self.InsertCategoryLineEdit.clear()

    # commits transaction  to database and closes the window
    def done_button_clicked(self):
        self.edit_and_add_categories_controller.commit_to_database()
        self.close()

    # rolls back transaction and closes the window
    def cancel_button_clicked(self):
        self.edit_and_add_categories_controller.rollback_database()
        self.close()

    # populates the category table widget
    def initialize_category_table_widget(self):
        # gets all category names and ids
        categories = self.edit_and_add_categories_controller.get_all_categories_name_and_id()

        # add all categories except All Terms to the category table widget
        # All Terms is not added because it should not be edited
        for category in categories:
            if category[1] != "All Terms":
                self.add_row_to_category_table_widget(category[0], category[1])

    # adds a row to the category table widget
    def add_row_to_category_table_widget(self, category_id, category_name):
        # obtains the the row position the new row will be inserted at
        row_position = self.CategoryTableWidget.rowCount()
        # creates empty row in category table widget
        self.CategoryTableWidget.insertRow(row_position)
        # creating table widget item to populate a cell in the table widget
        category_id_widget_item = QTableWidgetItem(str(category_id))
        # making the table widget item's contents centered
        category_id_widget_item.setTextAlignment(Qt.AlignCenter)
        # setting a cell in the category table widget to the new table widget item
        self.CategoryTableWidget.setItem(row_position, 0, category_id_widget_item)
        # disabling editing and selecting for table widget cell
        self.CategoryTableWidget.item(row_position, 0).setFlags(Qt.ItemIsSelectable)

        # SEE ABOVE (its the same dealio)
        category_name_widget_item = QTableWidgetItem(category_name)
        category_name_widget_item.setTextAlignment(Qt.AlignCenter)
        self.CategoryTableWidget.setItem(row_position, 1, category_name_widget_item)

    # when a cell in the category table widget is clicked
    # get the text before the cell is edited
    # link item changed
    ''' the linking of item changed allows us to complete some action when the cell is clicked off of by the user 
    IE when they are done editing '''
    def category_table_widget_cell_double_clicked(self, item):
        self.before_cell_is_edited = item.text()
        self.CategoryTableWidget.itemChanged.connect(self.category_table_widget_item_changed)

    def category_table_widget_item_changed(self, item):
        try:
            # remove extra spaces before text and after text
            category_name = item.text().strip()
            # if the newly entered category name and the old category name are not the same
            # start updating category process
            if category_name != self.before_cell_is_edited:
                # get the id of category from category table widget
                item_id = self.CategoryTableWidget.item(item.row(), 0).text()
                # capitalize the first letter in every word
                category_name = category_name.title()
                # get the row of the edited category in the category table widget
                category_name_row = item.row()
                # get the column of the edited category in the category table widget
                category_name_column = item.column()

                # if the category doesn't already exist continue updating process
                if not self.edit_and_add_categories_controller.check_if_category_exists_with_name(category_name):
                    # put new category into table widget item
                    category_name_widget_item = QTableWidgetItem(category_name)
                    # center the table widget item's contents
                    category_name_widget_item.setTextAlignment(Qt.AlignCenter)

                    # if the category is not updated sucessfully throw an error message
                    if not self.edit_and_add_categories_controller.update_category(item_id, category_name):
                        error_message = QErrorMessage(self)
                        error_message.showMessage("The category with the specified name already exists")
                    else:
                        ''' if the category update was successfull itemChanged must be disconnected because the user 
                        is done editing the cell. We only want this on while the user is editing a cell '''
                        self.CategoryTableWidget.itemChanged.disconnect()
                        # put the new category in the category table widget
                        self.CategoryTableWidget.setItem(category_name_row, category_name_column, category_name_widget_item)
                else:
                    '''itemChanged must be disconnected because the user 
                        is done editing the cell. We only want this on while the user is editing a cell'''
                    self.CategoryTableWidget.itemChanged.disconnect()
                    # the new category already exists. Since the new category was not added,
                    # change the cell of the category table widget back to what it previously was and
                    # add nothing to the database
                    category_name_widget_item_previous = QTableWidgetItem(self.before_cell_is_edited)
                    category_name_widget_item_previous.setTextAlignment(Qt.AlignCenter)
                    self.CategoryTableWidget.setItem(category_name_row, category_name_column, category_name_widget_item_previous)
                    # throw an error message telling the user the category already exists
                    error_message = QErrorMessage(self)
                    error_message.showMessage("The category already exists.")

            else:
                self.CategoryTableWidget.itemChanged.disconnect()




        except Exception as e:
            print(str(e))

    # deletes all selected categories
    def delete_categories_button_clicked(self):
        category_ids = []
        rows_number = []
        ''' get the row numbers and category ids of the selected rows in the 
        category table widget '''
        for row in self.CategoryTableWidget.selectionModel().selectedRows():
            rows_number.append(row.row())
            category_ids.append(int(self.CategoryTableWidget.item(row.row(), row.column()).text()))

        # mus tbe sorted in reverse if I attempt to remove low numbers first the big numbers change to lower ones
        rows_number.sort(reverse=True)

        # removing rows form category table widget
        for row in rows_number:
            self.CategoryTableWidget.removeRow(row)

        # removing categories from database
        self.edit_and_add_categories_controller.delete_categories(category_ids)

    # overrode closeEvent to ensure that the transactions are closed
    def closeEvent(self, event):
        self.edit_and_add_categories_controller.rollback_database()

