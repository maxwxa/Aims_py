from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Dict, Any
from database import DatabaseManager
from models.users import UserAccount
from models.inventory import InventoryItem, ItemRequest, Transaction

class BaseRepository(ABC):
    def __init__(self):
        self._db = DatabaseManager.get_instance() 

    @abstractmethod
    def add(self, entity: Any) -> bool:
        pass                                  

    @abstractmethod
    def delete(self, _id: int) -> bool:
        pass                                     

    @abstractmethod
    def update(self, entity: Any) -> bool:
        pass                                      

    @abstractmethod
    def get_all(self) -> List[Any]:
        pass                                      


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
        pass                                     
        
    def updateUser(self):
        pass                                      
        
    def deleteUser(self):
        pass                                      


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
        pass                                       
        
    def updateItem(self):
        pass                                     
        
    def deleteItem(self):
        pass                                      


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
        pass                                      
        
    def updateRequest(self):
        pass                                       
        
    def deleteRequest(self):
        pass                                     


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
        pass                                      
        
    def archiveTransaction(self):
        pass                                      