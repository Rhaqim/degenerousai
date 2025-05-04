import sqlite3
import os
from typing import Optional


class Database:
    """
    Database class for managing SQLite database connections.

    Attributes:
        db_name (str): The name of the SQLite database file. Defaults to "db.sqlite3".
        connection (sqlite3.Connection): The SQLite database connection object.

    Methods:
        __init__(db_name="db.sqlite3"):
            Initializes the Database instance, sets up the database name, and establishes a connection.
        _connect():
            Establishes a connection to the SQLite database. Creates a new database file if it does not exist.
        close():
            Closes the connection to the SQLite database if it is open.
    Example usage:
        db = Database()
        connection = db.connection
        db.close()
    """

    def __init__(self, db_name="db.sqlite3"):
        self.db_name = db_name
        self.connection: Optional[sqlite3.Connection] = None
        self._connect()

    def _connect(self):
        # Check if the database file exists
        db_exists = os.path.exists(self.db_name)

        # Connect to the SQLite database (creates a new one if it doesn't exist)
        self.connection = sqlite3.connect(self.db_name)

        if db_exists:
            print(f"Connected to existing database: {self.db_name}")
        else:
            print(f"Database not found. Created a new database: {self.db_name}")

    def fetch_all(self, query, params=None):
        """
        Fetches all rows from the result of a SQL query.

        Args:
            query (str): The SQL query to execute.
            params (tuple, optional): The parameters to bind to the query. Defaults to None.

        Returns:
            list: A list of dictionaries representing the rows returned by the query.
        """
        cursor = self.execute(query, params)
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return results

    def fetch_one(self, query, params=None):
        """
        Fetches a single row from the result of a SQL query.
        Args:
            query (str): The SQL query to execute.
            params (tuple, optional): The parameters to bind to the query. Defaults to None.
        Returns:
            dict: A dictionary representing the row returned by the query.
        """
        cursor = self.execute(query, params)
        columns = [column[0] for column in cursor.description]
        result = cursor.fetchone()
        if result:
            return dict(zip(columns, result))
        return None

    def execute(self, query, params=None):
        """
        Executes a SQL query with optional parameters.

        Args:
            query (str): The SQL query to execute.
            params (tuple, optional): The parameters to bind to the query. Defaults to None.

        Returns:
            sqlite3.Cursor: The cursor object after executing the query.
        """
        if self.connection is None:
            raise ValueError("Database connection is not established.")
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor

    def commit(self):
        """
        Commits the current transaction to the database.
        """
        if self.connection:
            self.connection.commit()
        else:
            raise ValueError("Database connection is not established.")
        print("Transaction committed.")

    def close(self):
        if self.connection:
            self.connection.close()
            print(f"Connection to database {self.db_name} closed.")

    
