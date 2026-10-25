import mysql.connector

class DatabaseManager:
    __instance = None                  

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(DatabaseManager, cls).__new__(cls)
            cls.__instance.__connection = None  
        return cls.__instance

    @staticmethod
    def get_instance():
        return DatabaseManager()        

    def get_connection(self):
        if self.__connection is None or not self.__connection.is_connected():
            self.__connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="aims_db",
            )
        return self.__connection

    def close(self):
        if self.__connection:
            pass 