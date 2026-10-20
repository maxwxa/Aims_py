from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Dict, Any

class ValidationError(Exception):
    def __init__(self, error_code: int, field_name: str, message: str):
        self.__error_code = error_code 
        self.__field_name = field_name  
        self.__message = message       
        super().__init__(self.__message)

    def get_message(self) -> str:
        return self.__message          

    def get_field_name(self) -> str:
        return self.__field_name        


class DatabaseError(Exception):
    def __init__(self, error_code: int, query: str, message: str):
        self.__error_code = error_code  
        self.__query = query            
        self.__message = message      
        super().__init__(self.__message)

    def get_query(self) -> str:
        return self.__query             

    def log_error(self):
        print(f"Error [{self.__error_code}] in query '{self.__query}': {self.__message}")  # +log_error()[cite: 6]


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
        return self.__connection       

    def close(self):
        if self.__connection:
            pass 