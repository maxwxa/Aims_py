from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Dict, Any

class Record(ABC):
    def __init__(self, _id: int, _date_added: datetime):
        self._id = _id                          # #_id (protected)[cite: 5]
        self._date_added = _date_added          # #_date_added (protected)[cite: 5]

    @abstractmethod
    def validate(self) -> bool:
        pass                                    # +validate()[cite: 5]

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass                                    # +to_dict()[cite: 5]


class InventoryItem(Record):
    def __init__(self, item_id: int, category_id: int, item_name: str, item_code: str, description: str, stock: int, serial_no: str, expiration_date: datetime, updated_date: datetime, added_date: datetime):
        super().__init__(item_id, added_date)
        self.__item_id = item_id                # -item id[cite: 5]
        self.__category_id = category_id        # -category_id[cite: 5]
        self.__item_name = item_name            # -item_name[cite: 5]
        self.__item_code = item_code            # -item_code[cite: 5]
        self.__description = description        # -description[cite: 5]
        self.__stock = stock                    # -stock[cite: 5]
        self.__serial_no = serial_no            # -serial_no[cite: 5]
        self.__expiration_date = expiration_date # -expiration_date[cite: 5]
        self.__updated_date = updated_date      # -updated_date[cite: 5]
        self.__added_date = added_date          # -added date[cite: 5]

    def update_stock(self, qty: int):
        self.__stock += qty                     # +update_stock(qty)[cite: 5]

    def validate(self) -> bool:
        return True                             # +validate()[cite: 5]

    def to_dict(self) -> Dict[str, Any]:
        return {"item_id": self.__item_id, "item_name": self.__item_name} # +to_dict()[cite: 5]


class Category: # Spelled 'Catogory' in UML[cite: 5]
    def __init__(self, category_id: int, category_name: str, category_desc: str, requires_return: bool):
        self.__category_id = category_id             # -category_id[cite: 5]
        self.__category_name = category_name         # -category_name[cite: 5]
        self.__category_desc = category_desc         # -category_desc[cite: 5]
        self.__requires_return = requires_return     # -requires_return[cite: 5]

    def validate(self) -> bool:
        return True                                  # +validate()[cite: 5]


class ItemRequest(Record):
    def __init__(self, request_id: int, user_id: int, item_id: int, processed_by: int, request_status: str, quantity: int, request_date: datetime, due_date: datetime):
        super().__init__(request_id, request_date)
        self.__request_id = request_id               # -request_id[cite: 5]
        self.__user_id = user_id                     # -user_id[cite: 5]
        self.__item_id = item_id                     # -item_id[cite: 5]
        self.__processed_by = processed_by           # -processed_by[cite: 5]
        self.__request_status = request_status       # -request_status[cite: 5]
        self.__quantity = quantity                   # -quantity[cite: 5]
        self.__request_date = request_date           # -request_date[cite: 5]
        self.__due_date = due_date                   # -due date[cite: 5]

    def validate(self) -> bool:
        return True                                  # +validate()[cite: 5]

    def to_dict(self) -> Dict[str, Any]:
        return {"request_id": self.__request_id}     # +to_dict() inherited from Record[cite: 5]

    def update_status(self):
        pass                                         # +update_status()[cite: 5]


class Transaction(Record):
    def __init__(self, transaction_id: int, request_id: int, transaction_type: str, quantity: int, condition_status: str, condition_notes: str, handled_by: int, transaction_date: datetime):
        super().__init__(transaction_id, transaction_date)
        self.__transaction_id = transaction_id       # -transaction_id[cite: 5]
        self.__request_id = request_id               # -request_id[cite: 5]
        self.__transaction_type = transaction_type   # -transaction_type[cite: 5]
        self.__quantity = quantity                   # -quantity[cite: 5]
        self.__condition_status = condition_status   # -condition_status[cite: 5]
        self.__condition_notes = condition_notes     # -condition_notes[cite: 5]
        self.__handled_by = handled_by               # -handled by[cite: 5]
        self.__transaction_date = transaction_date   # -transaction_date[cite: 5]

    def validate(self) -> bool:
        return True                                  # +validate()[cite: 5]

    def to_dict(self) -> Dict[str, Any]:
        return {"transaction_id": self.__transaction_id} # +to_dict() inherited from Record[cite: 5]


class TransactionsArchive:
    def __init__(self, arc_transaction_id: int, orig_transaction_id: int, request_id: int, transaction_type: str, quantity: int, condition_status: str, condition_notes: str, handled_by: int, transaction_date: datetime, archived_date: datetime, archive_reason: str):
        self.__arc_transaction_id = arc_transaction_id # -arc_transaction_id[cite: 5]
        self.__orig_transaction_id = orig_transaction_id # -orig_transaction_id[cite: 5]
        self.__request_id = request_id               # -request_id[cite: 5]
        self.__transaction_type = transaction_type   # -transaction_type[cite: 5]
        self.__quantity = quantity                   # -quantity[cite: 5]
        self.__condition_status = condition_status   # -condition_status[cite: 5]
        self.__condition_notes = condition_notes     # -condition_notes[cite: 5]
        self.__handled_by = handled_by               # -handled_by[cite: 5]
        self.__transaction_date = transaction_date   # -transaction date[cite: 5]
        self.__archived_date = archived_date         # -archived date[cite: 5]
        self.__archive_reason = archive_reason       # -archive_reason[cite: 5]