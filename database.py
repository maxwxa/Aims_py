import mysql.connector

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._connection = None
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_connection(self):
        if self._connection is None:
            self._connect()
        else:
            try:
                if not self._connection.is_connected():
                    self._connect()
                else:
                    self._connection.ping(reconnect=True, attempts=1, delay=0)
            except Exception:
                self._connect()
        return self._connection

    def _connect(self):
        self._connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="aims_db",
        )

    def close(self):
        if self._connection is not None and self._connection.is_connected():
            self._connection.close()
            self._connection = None