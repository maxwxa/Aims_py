from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Dict, Any
from database import DatabaseManager
from models.users import UserAccount
from models.inventory import InventoryItem, ItemRequest, Transaction

class BaseRepository(ABC):
    def __init__(self):
        self._db = DatabaseManager.get_instance()  # #_db: DatabaseManager (protected)[cite: 6]

    @abstractmethod
    def add(self, entity: Any) -> bool:
        pass                                       # +add(entity)[cite: 6]

    @abstractmethod
    def delete(self, _id: int) -> bool:
        pass                                       # +delete(id)[cite: 6]

    @abstractmethod
    def update(self, entity: Any) -> bool:
        pass                                       # +update(entity)[cite: 6]

    @abstractmethod
    def get_all(self) -> List[Any]:
        pass                                       # +get_all()[cite: 6]


class UserRepository(BaseRepository):
    def add(self, entity: UserAccount) -> bool:
        pass

    def delete(self, _id: int) -> bool:
        pass

    def update(self, entity: UserAccount) -> bool:
        pass

    def get_all(self) -> List[UserAccount]:
        pass

    def addUser(self):
        pass                                       # +addUser()[cite: 6]
        
    def updateUser(self):
        pass                                       # +updateUser()[cite: 6]
        
    def deleteUser(self):
        pass                                       # +deleteUser()[cite: 6]


class InventoryRepository(BaseRepository):
    def add(self, entity: InventoryItem) -> bool:
        pass

    def delete(self, _id: int) -> bool:
        pass

    def update(self, entity: InventoryItem) -> bool:
        pass

    def get_all(self) -> List[InventoryItem]:
        pass

    def addItem(self):
        pass                                       # +addItem()[cite: 6]
        
    def updateItem(self):
        pass                                       # +updateItem()[cite: 6]
        
    def deleteItem(self):
        pass                                       # +deleteItem()[cite: 6]


class RequestRepository(BaseRepository):
    def add(self, entity: ItemRequest) -> bool:
        pass

    def delete(self, _id: int) -> bool:
        pass

    def update(self, entity: ItemRequest) -> bool:
        pass

    def get_all(self) -> List[ItemRequest]:
        pass

    def addRequest(self):
        pass                                       # +addRequest()[cite: 6]
        
    def updateRequest(self):
        pass                                       # +updateRequest()[cite: 6]
        
    def deleteRequest(self):
        pass                                       # +deleteRequest()[cite: 6]


class TransactionRepository(BaseRepository):
    def add(self, entity: Transaction) -> bool:
        pass

    def delete(self, _id: int) -> bool:
        pass

    def update(self, entity: Transaction) -> bool:
        pass

    def get_all(self) -> List[Transaction]:
        pass

    def addTransaction(self):
        pass                                       # +addTransaction()[cite: 6]
        
    def archiveTransaction(self):
        pass                                       # +archiveTransaction()[cite: 6]