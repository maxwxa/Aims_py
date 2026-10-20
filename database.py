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