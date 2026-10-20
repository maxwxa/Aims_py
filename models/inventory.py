from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Dict, Any

class Record(ABC):
    def __init__(self, _id: int, _date_added: datetime):
        self._id = _id                         
        self._date_added = _date_added       

    @abstractmethod
    def validate(self) -> bool:
        pass                                   

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass                                  


class InventoryItem(Record):
    def __init__(self, item_id: int, category_id: int, item_name: str, item_code: str, description: str, stock: int, serial_no: str, expiration_date: datetime, updated_date: datetime, added_date: datetime):
        super().__init__(item_id, added_date)
        self.__item_id = item_id               
        self.__category_id = category_id       
        self.__item_name = item_name           
        self.__item_code = item_code            
        self.__description = description        
        self.__stock = stock                
        self.__serial_no = serial_no           
        self.__expiration_date = expiration_date 
        self.__updated_date = updated_date     
        self.__added_date = added_date         

    def update_stock(self, qty: int):
        self.__stock += qty                    

    def validate(self) -> bool:
        return True                            

    def to_dict(self) -> Dict[str, Any]:
        return {"item_id": self.__item_id, "item_name": self.__item_name} 


class Category: # Spelled 'Catogory' in UML[cite: 5]
    def __init__(self, category_id: int, category_name: str, category_desc: str, requires_return: bool):
        self.__category_id = category_id           
        self.__category_name = category_name         
        self.__category_desc = category_desc         
        self.__requires_return = requires_return   
    def validate(self) -> bool:
        return True                                 


class ItemRequest(Record):
    def __init__(self, request_id: int, user_id: int, item_id: int, processed_by: int, request_status: str, quantity: int, request_date: datetime, due_date: datetime):
        super().__init__(request_id, request_date)
        self.__request_id = request_id               
        self.__user_id = user_id                   
        self.__item_id = item_id                  
        self.__processed_by = processed_by         
        self.__request_status = request_status     
        self.__quantity = quantity                   
        self.__request_date = request_date          
        self.__due_date = due_date                  

    def validate(self) -> bool:
        return True                                 

    def to_dict(self) -> Dict[str, Any]:
        return {"request_id": self.__request_id}     

    def update_status(self):
        pass                                     


class Transaction(Record):
    def __init__(self, transaction_id: int, request_id: int, transaction_type: str, quantity: int, condition_status: str, condition_notes: str, handled_by: int, transaction_date: datetime):
        super().__init__(transaction_id, transaction_date)
        self.__transaction_id = transaction_id      
        self.__request_id = request_id            
        self.__transaction_type = transaction_type  
        self.__quantity = quantity                
        self.__condition_status = condition_status  
        self.__condition_notes = condition_notes     
        self.__handled_by = handled_by               
        self.__transaction_date = transaction_date  

    def validate(self) -> bool:
        return True                                 
    def to_dict(self) -> Dict[str, Any]:
        return {"transaction_id": self.__transaction_id} 


class TransactionsArchive:
    def __init__(self, arc_transaction_id: int, orig_transaction_id: int, request_id: int, transaction_type: str, quantity: int, condition_status: str, condition_notes: str, handled_by: int, transaction_date: datetime, archived_date: datetime, archive_reason: str):
        self.__arc_transaction_id = arc_transaction_id
        self.__orig_transaction_id = orig_transaction_id
        self.__request_id = request_id               
        self.__transaction_type = transaction_type  
        self.__quantity = quantity                  
        self.__condition_status = condition_status  
        self.__condition_notes = condition_notes    
        self.__handled_by = handled_by              
        self.__transaction_date = transaction_date  
        self.__archived_date = archived_date        
        self.__archive_reason = archive_reason      