import sqlite3
import os.path


class DatabaseAccess:
    database_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "studier.db")
    conn = None
    c = None

    # sets up database connection
    def connect(self):
        self.conn = sqlite3.connect(self.database_path)
        self.c = self.conn.cursor()
        self.c.execute('''PRAGMA FOREIGN_KEYS = on''')

    # I modified the destructor for this class
    # The default destructor does not close the connection, so I had to add that to it.
    def __del__(self):
        self.close_connection()


    # def begin_tran(self):
    #     self.conn.isolation_level = None
    #     self.c.execute('''
    #                     BEGIN TRANSACTION''')

    # closes the connection to database
    def close_connection(self):
        self.conn.close()

    # Commits current transaction to database
    def commit(self):
        self.conn.commit()

    # rolls back the changes made in current transaction
    def rollback(self):
        self.conn.rollback()

    # creates the tables needed for this application
    def create_tables(self):
        # creates the table TermCategory which holds terms categories
        # A category holds many terms
        # the category must have a unique name
        self.c.execute('''
                        CREATE TABLE IF NOT EXISTS TermCategory(
                        TermCategoryID INTEGER PRIMARY KEY AUTOINCREMENT
                        , CategoryName VARCHAR NOT NULL UNIQUE
                        ) 
                        ''')

        # The TermCategory table must always have the category All Terms in it
        # so this is added following TermCategory table creation
        self.c.execute('''
                            INSERT INTO TermCategory(CategoryName)
                            SELECT 'All Terms' 
                            WHERE NOT EXISTS(SELECT * 
                                             FROM TermCategory 
                                             WHERE CategoryName = 'All Terms')
                        ''')

        # creates the Terms table
        # There can be multiple terms with the same name (because of homonyms)
        # there can be multiple terms with the same description (because of synonyms)
        # there cannot be multiple terms with both, the same description and name
        # a single term can be in multiple categories
        self.c.execute("CREATE TABLE IF NOT EXISTS Terms ("
                       "TermID INTEGER PRIMARY KEY AUTOINCREMENT"
                       ", TermName VARCHAR NOT NULL"
                       ", TermDescription VARCHAR NOT NULL,"
                       "CONSTRAINT TermName_UQ_TermDescription "
                       "    UNIQUE(TermName,TermDescription)"
                       ")")

        # creates the TermCategoryEntity table
        # used for the many-to-many relationship between Terms and TermCategory tables
        # IE A TermCategory can have many terms and a Term can be in many TermCategories
        self.c.execute('''
                        CREATE TABLE IF NOT EXISTS TermCategoryEntity
                        (
                            TermCategoryID INTEGER NOT NULL,
                            TermID INTEGER NOT NULL,
                            CONSTRAINT TermCategoryEntity_FK_TermCategory
                                FOREIGN KEY(TermCategoryID)
                                REFERENCES TermCategory(TermCategoryID)
                                ON DELETE CASCADE,
                            CONSTRAINT TermCategoryEntity_FK_Term
                                FOREIGN KEY(TermID) 
                                REFERENCES Terms(TermID)
                                ON DELETE CASCADE,
                            CONSTRAINT TermCategoryId_PK_TermID
                                PRIMARY KEY(TermCategoryID, TermID)
                                
                        )
                        ''')

    # gets a term's description with its ID
    def get_term_description_with_id(self, term_id):
        results = self.c.execute('''
                        SELECT TermDescription
                        FROM Terms
                        WHERE TermID = ?
                        ''', (term_id,))
        for row in results:
            term_description = row[0]
        return term_description

    # gets a term's name with its id
    def get_term_name_with_id(self, term_id):
        results = self.c.execute('''
                        SELECT TermName
                        FROM Terms
                        WHERE TermID = ?
                        ''', (term_id,))
        for row in results:
            term_name = row[0]
        return term_name

    # updates the term depending upon what aspect was changed.
    def update_term(self, term_id, term_item, whats_being_updated):

        if whats_being_updated == "TermName":
            # if the term's name was changed get the description with the term id
            term_description = self.get_term_description_with_id(term_id)
            # check if the term already exists with the new term_name and term_description combination
            # if it doesn't update the term
            if not self.check_if_term_exists(term_item, term_description):
                self.c.execute('''
                                UPDATE Terms
                                SET TermName = (?) 
                                WHERE TermId = (?)
                            ''', (term_item, term_id))
                # tell the controller and view the operation completed sucessfully
                return True
            else:
                # the term cannot updated with the specified name
                # there is already a term with that name and description
                return False
        elif whats_being_updated == "TermDescription":
            try:
                # if the terms description was changed get the term's name
                term_name = self.get_term_name_with_id(term_id)
                # check if a term with the new term_name and term_description combination exists
                if not self.check_if_term_exists(term_name, term_item):
                    # if a term with the new term_name and term_description combination
                    # didn't exist update the term
                    self.c.execute('''
                                    UPDATE Terms
                                    SET TermDescription = (?) 
                                    WHERE TermId = (?)
                                ''', (term_item, term_id))
                    # tell the view and controller the operation was successful
                    return True
                else:
                    # tell the view and controller the operation failed
                    # a term with the specified description and name combination already exists
                    return False
            except Exception as e:
                print(str(e))

    def delete_term_category_entity(self, term_id, category_id):
        self.c.execute('''
                        DELETE FROM TermCategoryEntity
                        WHERE TermID = ? AND TermCategoryID = ?
                        ''', (term_id, category_id))

    # updates the categories a term is currently in
    def update_terms_categories(self, term_id, term_categories):
        # gets categories a term is currently in
        terms_current_categories = self.get_all_of_a_terms_categories(term_id)

        # if new term_categories do not equal the previous ones
        # delete all terms current relations
        # except with the category All Terms
        if term_categories != terms_current_categories:
            for term_category in terms_current_categories:
                if term_category != "All Terms":
                    category_id = self.get_category_id_with_name(term_category)
                    if self.check_if_term_category_relationship_exists(term_id, category_id):
                        self.delete_term_category_entity(term_id, category_id)

            # adding new relations for term
            for term_category in term_categories:
                category_id = self.get_category_id_with_name(term_category)
                self.add_new_category_for_term(term_id, category_id)

    # gets the specified category's id with its name
    def get_category_id_with_name(self, category_name):
        results = self.c.execute('''
                                SELECT TermCategoryID 
                                FROM TermCategory 
                                WHERE CategoryName = ?''', (category_name,))
        for row in results:
            term_category_id = row[0]
        return term_category_id

    # gets the term id with its name and description
    def get_term_id_with_name_and_description(self, term_name, term_description):
        results = self.c.execute('''
                                SELECT TermId 
                                FROM Terms
                                WHERE TermName = ? AND TermDescription = ?
                                ''', (term_name, term_description))
        for row in results:
            term_id = row[0]
        return term_id

    # checks if a term exists in the database with either the id or description and name
    # if all inputs = None return false
    def check_if_term_exists(self, term_name=None, term_description=None, term_id=None):
        if term_id != None:
            results = self.c.execute('''
                                    SELECT EXISTS(SELECT * 
                                                  FROM Terms 
                                                  WHERE TermID = ?)
                                    ''', (term_id,))
        elif (term_name != None) and (term_description != None):
            results = self.c.execute('''
                                    SELECT EXISTS(                         
                                    SELECT * 
                                    FROM Terms
                                    WHERE TermName = ? AND TermDescription = ?)
                                    ''', (term_name, term_description))

        for row in results:
            check = row[0]

        if check == 0:
            return False
        else:
            return True


    def check_if_term_category_relationship_exists(self, term_id, category_id):
        results = self.c.execute('''
                                SELECT EXISTS(
                                SELECT * 
                                FROM TermCategoryEntity
                                WHERE TermId = ? AND TermCategoryID = ?
                                )
                            ''', (term_id, category_id))
        for row in results:
            check = row[0]

        if check == 0:
            return False
        else:
            return True

    # adds a category for a term by creating a TermCategoryEntity row
    def add_new_category_for_term(self, term_id, category_id):
        if not self.check_if_term_category_relationship_exists(term_id, category_id):
            self.c.execute('''
                        INSERT INTO TermCategoryEntity(TermId, TermCategoryId)
                        VALUES(?, ?)
                        ''', (term_id, category_id))

    # gets the id of the category All Terms
    def get_all_terms_category_id(self):
        results = self.c.execute('''SELECT TermCategoryID
                          FROM TermCategory
                          WHERE  CategoryName = 'All Terms'
                          ''')
        for row in results:
            all_terms_id = row[0]
        return all_terms_id

    # adds a term into the database and links it to specified categories
    def insert_term(self, term_name, term_definition, category_names):
        # if the term doesn't already exist add it to the database
        if not self.check_if_term_exists(term_name, term_definition):

            # inserting term into Terms
            self.c.execute('''INSERT INTO Terms (TermName, TermDescription)
                               VALUES (?,?)''', (term_name, term_definition))
            #getting term id
            term_id = self.get_term_id_with_name_and_description(term_name, term_definition)

            # connecting the term to the specified categories
            for category_name in category_names:
                category_id = self.get_category_id_with_name(category_name)
                self.add_new_category_for_term(term_id, category_id)

            # connecting the term to All Terms category
            all_terms_id = self.get_all_terms_category_id()

            self.add_new_category_for_term(term_id, all_terms_id)
            return True
        else:
            return False

    # inserting category into database
    def insert_category(self, category_name):

        self.c.execute('''
                        INSERT INTO TermCategory (CategoryName)
                        VALUES (?)''', (category_name,))



    # deleting selected terms
    def delete_terms(self, term_ids):
        for term_id in term_ids:
            self.c.execute('''
                            DELETE  
                            FROM Terms
                            WHERE TermID = (?)
            ''', (term_id,))

    # deletes the category that is selected
    def delete_categories(self, category_ids):
        for category_id in category_ids:
            self.c.execute('''
                    DELETE FROM TermCategory 
                    WHERE TermCategoryID = ?
                    ''', (category_id, ))

    # gets all categories that a term is in
    # the term is specified with its id
    def get_all_of_a_terms_categories(self, term_id):
        results = self.c.execute('''
                                SELECT CategoryName
                                FROM TermCategory TC 
                                    INNER JOIN TermCategoryEntity TCE 
                                        ON TC.TermCategoryID = TCE.TermCategoryID
                                    INNER JOIN Terms T 
                                        ON TCE.TermID = T.TermID
                                WHERE T.TermID = ?
                                ''', (term_id,))
        categories_for_term = []
        for row in results:
            categories_for_term.append(row[0])

        categories_for_term = tuple(categories_for_term)
        return categories_for_term

    # gets the term's id with its name and description
    def get_term_id_with_name_and_description(self, term_name, term_description):
        results = self.c.execute('''
                                SELECT TermID
                                FROM Terms
                                WHERE TermName = ? AND TermDescription = ? 
                                ''', (term_name, term_description))
        for row in results:
            term_id = row[0]
        return term_id

    # returns all terms in database
    def get_all_terms(self):
        return self.c.execute('''
                            SELECT T.TermName, T.TermDescription, TC.CategoryName
                            FROM Terms T 
                                INNER JOIN TermCategoryEntity TCE 
                                    ON T.TermId = TCE.TermID
                                INNER JOIN TermCategory TC 
                                    ON TCE.TermCategoryId = TC.TermCategoryID'''
                              )

    # gets all terms in the specified category
    def get_all_terms_in_category(self, category):
        results = self.c.execute('''
                                SELECT T.TermName, T.TermDescription, T.TermId
                                FROM Terms T 
                                    INNER JOIN TermCategoryEntity TCE 
                                        ON T.TermID = TCE.TermID
                                    INNER JOIN TermCategory TC 
                                        ON TCE.TermCategoryID = TC.TermCategoryID 
                                WHERE TC.CategoryName = ? ''', (category,))
        terms = []
        for row in results:
            term = (row[0], row[1], row[2])
            terms.append(term)

        return terms

    # gets all category names and ids and returns them as a tuple
    def get_all_categories_name_and_id(self):
        results = self.c.execute('''
                                SELECT TermCategoryID, CategoryName
                                FROM TermCategory
                                ''')
        category_names_and_ids = []
        for row in results:
            category_names_and_ids.append((row[0], row[1]))
        category_names_and_ids = tuple(category_names_and_ids)
        return category_names_and_ids

    # checks if a category exists with its id
    def check_if_category_exists(self, category_id):
        results = self.c.execute('''
                        SELECT EXISTS(
                            SELECT * 
                            FROM TermCategory
                            WHERE TermCategoryID = ?)
                        ''', (category_id, ))

        for row in results:
            result = row[0]

        if result == 0:
            return False
        else:
            return True

    # updates a categories name in the database
    def update_category(self, category_id, category_name):
        if self.check_if_category_exists(category_id):
            self.c.execute('''
                            UPDATE TermCategory  
                            SET CategoryName = ?
                            WHERE TermCategoryID = ? 
                            ''', (category_name, category_id))
            return True
        else:
            return False

    # checks if category exists with name
    def check_if_category_exists_with_name(self, category_name):
        results = self.c.execute('''
                        SELECT EXISTS(
                                        SELECT *
                                        FROM TermCategory
                                        WHERE CategoryName = ?  
                                        )
                        ''', (category_name, ))
        for row in results:
            does_category_exist = row[0]

        if does_category_exist == 0:
            return False
        else:
            return True

    # gets all categories in database
    def get_all_categories(self):
        results = self.c.execute('''
                                SELECT CategoryName 
                                FROM TermCategory''')
        categories = []

        for row in results:
            categories.append(row[0])

        return categories
