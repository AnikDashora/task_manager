import pymysql
from pymysql.cursors import DictCursor

class SqlConnection:
    def __init__(self, database="task_flow"):
        self.host = "127.0.0.1"
        self.user = "root"
        self.password = "root"
        self.database = database
        self.connection = None
    
    def connect(self):
        """
        Establish connection to the MySQL database
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=3306,
                cursorclass=DictCursor,  # This makes results return as dictionaries
                autocommit=False,
                charset = 'utf8mb4',
            )
            return True
        except pymysql.Error as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """
        Close the database connection
        """
        if self.connection:
            self.connection.close()
            self.connection = None