from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Dict, Any
from database import DatabaseManager
from models.users import UserAccount
from models.inventory import InventoryItem, ItemRequest, Transaction, Category

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
        if not entity.validate():
            raise ValueError("Invalid inventory item.")
        if self.exists_duplicate(entity.item_name, entity.item_code, entity.serial_no):
            raise ValueError("Item name, item code, or serial number already exists.")
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO inventory_items
            (category_id, item_name, item_code, description, stock, serial_no,
             unit, expiration_date, image_path, added_date, updated_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (entity.category_id, entity.item_name, entity.item_code,
             entity.description, entity.stock, entity.serial_no, entity.unit,
             entity.expiration_date, entity.image_path, entity.added_date,
             entity.updated_date),
        )
        conn.commit()
        cursor.close()
        return True

    def delete(self, _id: int) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory_items WHERE item_id = %s", (_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        cursor.close()
        return deleted

    def update(self, entity: InventoryItem) -> bool:
        if not entity.validate():
            raise ValueError("Invalid inventory item.")
        if self.exists_duplicate(entity.item_name, entity.item_code, entity.serial_no, entity.item_id):
            raise ValueError("Item name, item code, or serial number already exists.")
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE inventory_items SET category_id=%s, item_name=%s,
            item_code=%s, description=%s, stock=%s, serial_no=%s, unit=%s,
            expiration_date=%s, image_path=%s, updated_date=%s
            WHERE item_id=%s""",
            (entity.category_id, entity.item_name, entity.item_code,
             entity.description, entity.stock, entity.serial_no, entity.unit,
             entity.expiration_date, entity.image_path, entity.updated_date,
             entity.item_id),
        )
        conn.commit()
        updated = cursor.rowcount > 0
        cursor.close()
        return updated

    def exists_duplicate(
        self, item_name: str, item_code: str, serial_no: str, exclude_id: int = 0
    ) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor()
        fields = [(item_name, "item_name"), (item_code, "item_code")]
        if serial_no:
            fields.append((serial_no, "serial_no"))
        clauses = " OR ".join(f"{column}=%s" for _, column in fields)
        cursor.execute(
            f"""SELECT 1 FROM inventory_items WHERE ({clauses})
            AND item_id <> %s LIMIT 1""",
            tuple(value for value, _ in fields) + (exclude_id,),
        )
        result = cursor.fetchone() is not None
        cursor.close()
        return result

    def get_by_id(self, item_id: int):
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT i.*, c.category_name, c.requires_return
            FROM inventory_items i LEFT JOIN categories c
            ON c.category_id=i.category_id WHERE i.item_id=%s""",
            (item_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        return self._from_row(row) if row else None

    def next_id(self) -> int:
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(MAX(item_id), 0) + 1 FROM inventory_items")
        value = cursor.fetchone()[0]
        cursor.close()
        return int(value)

    @staticmethod
    def _from_row(row):
        return InventoryItem(
            item_id=row["item_id"], category_id=row["category_id"],
            item_name=row["item_name"], item_code=row["item_code"],
            description=row.get("description", ""), stock=row["stock"],
            serial_no=row.get("serial_no", ""), expiration_date=row.get("expiration_date"),
            updated_date=row.get("updated_date"), added_date=row.get("added_date"),
            unit=row.get("unit", ""), image_path=row.get("image_path", ""),
            category_name=row.get("category_name", ""),
            requires_return=bool(row.get("requires_return", False)),
        )

    def get_all(self, search_term: str = "", filter_status: str = "All") -> List[InventoryItem]:
        conn = self._db.get_connection() 
        cursor = conn.cursor(dictionary=True)
        query = """SELECT i.*, c.category_name, c.requires_return
                   FROM inventory_items i
                   LEFT JOIN categories c ON c.category_id = i.category_id
                   WHERE i.item_name LIKE %s"""
        cursor.execute(query, (f"%{search_term}%",))
        
        results = cursor.fetchall()
        items = []
        
        for row in results:
            items.append(self._from_row(row))
            
        cursor.close()
        return items


class CategoryRepository(BaseRepository):
    def add(self, entity: Category) -> bool:
        if not entity.validate():
            raise ValueError("Category name is required.")
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO categories
            (category_name, category_desc, requires_return)
            VALUES (%s, %s, %s)""",
            (entity.category_name, entity.category_desc, entity.requires_return),
        )
        conn.commit()
        cursor.close()
        return True

    def delete(self, _id: int) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE category_id=%s", (_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        cursor.close()
        return deleted

    def has_inventory_items(self, category_id: int) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM inventory_items WHERE category_id=%s LIMIT 1",
            (category_id,),
        )
        result = cursor.fetchone() is not None
        cursor.close()
        return result

    def update(self, entity: Category) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE categories SET category_name=%s, category_desc=%s,
            requires_return=%s WHERE category_id=%s""",
            (entity.category_name, entity.category_desc, entity.requires_return,
             entity.category_id),
        )
        conn.commit()
        updated = cursor.rowcount > 0
        cursor.close()
        return updated

    def get_all(self) -> List[Category]:
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT category_id, category_name, category_desc, requires_return "
            "FROM categories ORDER BY category_name"
        )
        rows = cursor.fetchall()
        cursor.close()
        return [Category(
            row["category_id"], row["category_name"], row.get("category_desc", ""),
            bool(row.get("requires_return", False))
        ) for row in rows]

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