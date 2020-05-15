from Database.DatabaseAccess import DatabaseAccess

class EditAndAddCategoriesController():
    def __init__(self):
        self.database = DatabaseAccess()

    # opens connection to database
    def connect_to_database(self):
        self.database.connect()

    # closes database connection
    def close_connection(self):
        self.database.close_connection()

    # gets all categories names and ids
    # returned as tuple
    def get_all_categories_name_and_id(self):
        return self.database.get_all_categories_name_and_id()

    # updates the categories name in the database
    def update_category(self, category_id, category_name):
        return self.database.update_category(category_id, category_name)

    # rolls back database
    def rollback_database(self):
        self.database.rollback()

    # saves current transaction to database
    def commit_to_database(self):
        self.database.commit()

    # checks if a category exists with its name
    def check_if_category_exists_with_name(self, category_name):
        return self.database.check_if_category_exists_with_name(category_name)

    # inserts a category if it doesn't already exist
    def insert_category(self, category_name):
        self.database.insert_category(category_name)

    # gets the categories id with its name
    def get_category_id_with_name(self, category_name):
        return self.database.get_category_id_with_name(category_name)

    # deletes all selected category
    def delete_categories(self, category_ids):
        self.database.delete_categories(category_ids)
