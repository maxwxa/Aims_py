from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
from database import DatabaseManager
from models.users import UserAccount, Session
from models.password_utils import hash_password, verify_password
from models.account_validation import validate_email, validate_new_account, validate_password
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


class AuditLogRepository:
    def __init__(self):
        self._db = DatabaseManager.get_instance()

    def log_action(
        self,
        user_id: int | None,
        action_type: str,
        table_affected: str,
        description: str,
    ) -> None:
        conn = self._db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO system_logs
                   (user_id, action, table_affected, record_id, timestamp)
                   VALUES (%s, %s, %s, %s, NOW())""",
                (user_id, action_type, table_affected, str(description)),
            )
            conn.commit()
        finally:
            cursor.close()

def _log_action(action: str, table: str, record_id: Any) -> None:
    AuditLogRepository().log_action(
        Session.load().get("user_id"),
        action,
        table,
        str(record_id),
    )

class UserRepository(BaseRepository):
    def get_by_id(self, user_id: int) -> Dict[str, Any] | None:
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT ua.user_id, ua.gmail, ua.password_hash, ua.role,
                      ua.creationdate, ua.status,
                      pi.personal_id, pi.student_id, pi.first_name,
                      pi.middle_name, pi.last_name, pi.contact_number,
                      pi.birthday, pi.gender, pi.address, pi.department, pi.course
               FROM user_account ua
               LEFT JOIN personal_info pi ON ua.user_id=pi.user_id
               WHERE ua.user_id=%s""",
            (user_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        return row

    def get_user_history(self, user_id: int) -> List[Dict[str, Any]]:
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT t.transaction_id, t.request_id, ii.item_id, ii.item_name,
                      ii.item_code, ii.description AS item_description,
                      t.transaction_type, t.quantity, t.transaction_date,
                      t.conditon_status AS condition_status, t.condition_notes,
                      ir.request_status, ir.request_date, ir.due_date,
                      ir.approved_by, ir.confirmed_by,
                      COALESCE(
                          NULLIF(CONCAT_WS(' ', approved_pi.first_name,
                                           approved_pi.middle_name,
                                           approved_pi.last_name), ''),
                          CONCAT('User #', ir.approved_by)
                      ) AS approved_by_name,
                      COALESCE(
                          NULLIF(CONCAT_WS(' ', confirmed_pi.first_name,
                                           confirmed_pi.middle_name,
                                           confirmed_pi.last_name), ''),
                          CONCAT('User #', ir.confirmed_by)
                      ) AS confirmed_by_name
               FROM transactions t
               JOIN item_requests ir ON ir.request_id=t.request_id
               JOIN inventory_items ii ON ii.item_id=ir.item_id
               LEFT JOIN personal_info approved_pi ON approved_pi.user_id=ir.approved_by
               LEFT JOIN personal_info confirmed_pi ON confirmed_pi.user_id=ir.confirmed_by
               WHERE ir.requester_id=%s
               UNION ALL
               SELECT ta.arc_transaction_id AS transaction_id, ta.request_id,
                      ii.item_id, ii.item_name, ii.item_code,
                      ii.description AS item_description,
                      ta.transaction_type, ta.quantity, ta.transaction_date,
                      ta.conditon_status AS condition_status, ta.condition_notes,
                      ir.request_status, ir.request_date, ir.due_date,
                      ir.approved_by, ir.confirmed_by,
                      COALESCE(
                          NULLIF(CONCAT_WS(' ', approved_pi.first_name,
                                           approved_pi.middle_name,
                                           approved_pi.last_name), ''),
                          CONCAT('User #', ir.approved_by)
                      ) AS approved_by_name,
                      COALESCE(
                          NULLIF(CONCAT_WS(' ', confirmed_pi.first_name,
                                           confirmed_pi.middle_name,
                                           confirmed_pi.last_name), ''),
                          CONCAT('User #', ir.confirmed_by)
                      ) AS confirmed_by_name
               FROM transactions_archive ta
               JOIN item_requests ir ON ir.request_id=ta.request_id
               JOIN inventory_items ii ON ii.item_id=ir.item_id
               LEFT JOIN personal_info approved_pi ON approved_pi.user_id=ir.approved_by
               LEFT JOIN personal_info confirmed_pi ON confirmed_pi.user_id=ir.confirmed_by
               WHERE ir.requester_id=%s
               ORDER BY transaction_date DESC""",
            (user_id, user_id),
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_all_accounts(self, mode: str = "current") -> List[Dict[str, Any]]:
        if mode not in {"current", "archived"}:
            raise ValueError("Account mode must be 'current' or 'archived'.")
        if mode == "current":
            query = """SELECT ua.user_id AS account_id, pi.student_id, ua.gmail, ua.role,
                              ua.status AS account_status, ua.creationdate
                       FROM user_account ua
                       LEFT JOIN personal_info pi ON pi.user_id=ua.user_id
                       WHERE ua.status <> 'Archived'
                       ORDER BY ua.creationdate DESC"""
        else:
            query = """SELECT aa.arc_user_id AS account_archive_id,
                              aa.original_user_id AS account_id,
                              pi.student_id, aa.gmail, aa.role,
                              'Archived' AS account_status,
                              aa.archived_date AS creationdate
                       FROM account_archive aa
                       LEFT JOIN personal_info pi ON pi.user_id=aa.original_user_id
                       ORDER BY aa.archived_date DESC"""
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def add_user(
        self, account_data: Dict[str, Any], personal_data: Dict[str, Any]
    ) -> int:
        required = ("gmail", "password", "role", "status")
        if any(not str(account_data.get(key, "")).strip() for key in required):
            raise ValueError("Email, password, role, and status are required.")
        validate_new_account(account_data, personal_data)
        conn = self._db.get_connection()
        cursor = conn.cursor()
        try:
            email = account_data["gmail"].strip().lower()
            cursor.execute(
                """SELECT user_id FROM user_account
                   WHERE LOWER(TRIM(gmail))=%s LIMIT 1""",
                (email,),
            )
            if cursor.fetchone():
                raise ValueError("This email address is already registered.")
            student_id = str(personal_data.get("student_id", "")).strip().upper()
            cursor.execute(
                """SELECT personal_id
                   FROM personal_info
                   WHERE UPPER(TRIM(student_id))=%s
                   LIMIT 1""",
                (student_id,),
            )
            if cursor.fetchone():
                raise ValueError("This Student No. is already registered.")
            cursor.execute(
                """INSERT INTO user_account
                   (gmail, password_hash, role, creationdate, status)
                   VALUES (%s, %s, %s, NOW(), %s)""",
                (
                    email,
                    hash_password(account_data["password"]),
                    account_data["role"],
                    account_data["status"],
                ),
            )
            account_id = cursor.lastrowid
            cursor.execute(
                """INSERT INTO personal_info
                   (user_id, student_id, first_name, middle_name, last_name,
                    birthday, contact_number, department, course, gender, address)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    account_id,
                    student_id,
                    personal_data.get("first_name"),
                    personal_data.get("middle_name"),
                    personal_data.get("last_name"),
                    personal_data.get("birthday"),
                    personal_data.get("contact_number"),
                    personal_data.get("department"),
                    personal_data.get("course"),
                    personal_data.get("gender"),
                    personal_data.get("address"),
                ),
            )
            conn.commit()
            _log_action("INSERT", "user_account/personal_info", account_id)
            return int(account_id)
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def update_user(
        self,
        user_id: int,
        account_data: Dict[str, Any],
        personal_data: Dict[str, Any],
    ) -> bool:
        if any(not str(account_data.get(key, "")).strip()
               for key in ("gmail", "role", "status")):
            raise ValueError("Email, role, and status are required.")
        validate_email(account_data["gmail"])
        conn = self._db.get_connection()
        cursor = conn.cursor()
        try:
            email = account_data["gmail"].strip().lower()
            cursor.execute(
                """SELECT user_id FROM user_account
                   WHERE LOWER(TRIM(gmail))=%s AND user_id<>%s LIMIT 1""",
                (email, user_id),
            )
            if cursor.fetchone():
                raise ValueError("This email address is already registered.")
            account_values = [
                email,
                account_data["role"],
                account_data["status"],
            ]
            password = str(account_data.get("password", "")).strip()
            account_query = (
                "UPDATE user_account SET gmail=%s, role=%s, status=%s"
            )
            if password:
                validate_password(password)
                account_query += ", password_hash=%s"
                account_values.append(hash_password(password))
            account_query += " WHERE user_id=%s"
            account_values.append(user_id)
            cursor.execute(account_query, tuple(account_values))
            account_changed = cursor.rowcount > 0

            cursor.execute(
                """UPDATE personal_info
                   SET student_id=%s, first_name=%s, middle_name=%s,
                       last_name=%s, birthday=%s, contact_number=%s,
                       department=%s, course=%s, gender=%s, address=%s
                   WHERE user_id=%s""",
                (
                    personal_data.get("student_id"),
                    personal_data.get("first_name"),
                    personal_data.get("middle_name"),
                    personal_data.get("last_name"),
                    personal_data.get("birthday"),
                    personal_data.get("contact_number"),
                    personal_data.get("department"),
                    personal_data.get("course"),
                    personal_data.get("gender"),
                    personal_data.get("address"),
                    user_id,
                ),
            )
            cursor.execute(
                "SELECT personal_id FROM personal_info WHERE user_id=%s LIMIT 1",
                (user_id,),
            )
            if cursor.fetchone() is None:
                cursor.execute(
                    """INSERT INTO personal_info
                       (user_id, student_id, first_name, middle_name, last_name,
                        birthday, contact_number, department, course, gender, address)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        user_id,
                        personal_data.get("student_id"),
                        personal_data.get("first_name"),
                        personal_data.get("middle_name"),
                        personal_data.get("last_name"),
                        personal_data.get("birthday"),
                        personal_data.get("contact_number"),
                        personal_data.get("department"),
                        personal_data.get("course"),
                        personal_data.get("gender"),
                        personal_data.get("address"),
                    ),
                )
            conn.commit()
            _log_action("UPDATE", "user_account/personal_info", user_id)
            return account_changed
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def create_account(self, data: Dict[str, Any]) -> int:
        account_data = dict(data)
        account_data.setdefault("status", "Active")
        return self.add_user(account_data, {})

    def update_account(self, account_id: int, data: Dict[str, Any]) -> bool:
        account_data = dict(data)
        account_data.setdefault("status", "Active")
        return self.update_user(account_id, account_data, {})

    def change_password(self, account_id: int, password: str) -> bool:
        validate_password(password)
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE user_account SET password_hash=%s WHERE user_id=%s",
            (hash_password(password), account_id),
        )
        conn.commit()
        changed = cursor.rowcount > 0
        cursor.close()
        if changed:
            _log_action("UPDATE", "user_account", account_id)
        return changed

    def verify_password(self, account_id: int, password: str) -> bool:
        row = self.get_by_id(account_id)
        return bool(row and verify_password(password, row.get("password_hash", "")))

    def archive_user(self, account_id: int) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO account_archive
                   (original_user_id, gmail, password_hash, role,
                    archived_date, archive_reason)
                   SELECT user_id, gmail, password_hash, role, NOW(), %s
                   FROM user_account WHERE user_id=%s""",
                ("Archived by administrator", account_id),
            )
            if cursor.rowcount != 1:
                conn.rollback()
                return False
            cursor.execute(
                "UPDATE user_account SET status='Archived' WHERE user_id=%s",
                (account_id,),
            )
            conn.commit()
            _log_action("INSERT", "account_archive", account_id)
            return True
        except Exception as error:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def restore_user(self, arc_user_id: int) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """UPDATE user_account ua
                   JOIN account_archive aa
                     ON aa.original_user_id=ua.user_id
                   SET ua.status='Active'
                   WHERE aa.arc_user_id=%s""",
                (arc_user_id,),
            )
            if cursor.rowcount != 1:
                conn.rollback()
                return False
            cursor.execute(
                "DELETE FROM account_archive WHERE arc_user_id=%s", (arc_user_id,)
            )
            conn.commit()
            _log_action("DELETE", "account_archive", arc_user_id)
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def delete_archived(self, arc_user_id: int) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """SELECT original_user_id
                   FROM account_archive
                   WHERE arc_user_id=%s
                   FOR UPDATE""",
                (arc_user_id,),
            )
            archived_account = cursor.fetchone()
            if archived_account is None:
                conn.rollback()
                return False

            original_user_id = archived_account[0]
            cursor.execute(
                "DELETE FROM account_archive WHERE arc_user_id=%s",
                (arc_user_id,),
            )
            cursor.execute(
                "DELETE FROM personal_info WHERE user_id=%s",
                (original_user_id,),
            )
            cursor.execute(
                "SELECT COUNT(*) FROM personal_info WHERE user_id=%s",
                (original_user_id,),
            )
            if cursor.fetchone()[0] != 0:
                conn.rollback()
                raise ValueError(
                    "The account personal information could not be deleted."
                )

            cursor.execute(
                "DELETE FROM user_account WHERE user_id=%s",
                (original_user_id,),
            )
            if cursor.rowcount != 1:
                conn.rollback()
                return False

            conn.commit()
            _log_action("DELETE", "account_archive/user_account", arc_user_id)
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

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
    def adjust_stock(self, item_id: int, quantity_delta: int, conn=None) -> bool:
        connection = conn or self._db.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """UPDATE inventory_items
               SET stock=stock+%s
               WHERE item_id=%s AND stock+%s >= 0""",
            (quantity_delta, item_id, quantity_delta),
        )
        changed = cursor.rowcount > 0
        cursor.close()
        if conn is None and changed:
            connection.commit()
        return changed

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
        _log_action("INSERT", "inventory_items", entity.item_id)
        return True

    def delete(self, _id: int) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM item_requests WHERE item_id = %s",
                (_id,),
            )
            request_count = int(cursor.fetchone()[0])
            if request_count:
                raise ValueError(
                    "This item cannot be deleted because it has existing "
                    "requests. Archive or retain the item instead."
                )
            cursor.execute("DELETE FROM inventory_items WHERE item_id = %s", (_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
        if deleted:
            _log_action("DELETE", "inventory_items", _id)
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
        if updated:
            _log_action("UPDATE", "inventory_items", entity.item_id)
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
        _log_action("INSERT", "categories", entity.category_id)
        return True

    def delete(self, _id: int) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE category_id=%s", (_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        cursor.close()
        if deleted:
            _log_action("DELETE", "categories", _id)
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
        if updated:
            _log_action("UPDATE", "categories", entity.category_id)
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
        if isinstance(entity, dict):
            return self.add_request(
                entity["item_id"], entity["requester_id"], entity["quantity"],
                entity.get("due_date"),
            )
        raise TypeError("Requests must be created with a request details dictionary.")

    def delete(self, _id: int) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT request_id FROM item_requests WHERE request_id=%s",
                (_id,),
            )
            if cursor.fetchone() is None:
                return False

            cursor.execute(
                """SELECT 1 FROM transactions WHERE request_id=%s
                   UNION ALL
                   SELECT 1 FROM transactions_archive WHERE request_id=%s
                   LIMIT 1""",
                (_id, _id),
            )
            if cursor.fetchone() is not None:
                raise ValueError(
                    "This request has transaction history and cannot be deleted."
                )

            cursor.execute(
                "DELETE FROM item_requests WHERE request_id=%s",
                (_id,),
            )
            deleted = cursor.rowcount > 0
            conn.commit()
            if deleted:
                _log_action("DELETE", "item_requests", _id)
            return deleted
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def update(self, entity: ItemRequest) -> bool:
        if isinstance(entity, dict):
            request_id = entity.get("request_id")
            quantity = entity.get("quantity")
            status = entity.get("request_status")
        elif isinstance(entity, ItemRequest):
            request_id = entity.request_id
            quantity = entity.quantity
            status = entity.request_status
        else:
            raise TypeError("Request updates require an ItemRequest or request details dictionary.")

        if not request_id or quantity is None or not status:
            raise ValueError("Request ID, quantity, and status are required.")

        try:
            quantity = int(quantity)
        except (TypeError, ValueError) as error:
            raise ValueError("Quantity must be a whole number.") from error
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE item_requests
               SET quantity=%s, request_status=%s
               WHERE request_id=%s""",
            (quantity, status, request_id),
        )
        conn.commit()
        updated = cursor.rowcount > 0
        cursor.close()
        if updated:
            _log_action("UPDATE", "item_requests", request_id)
        return updated

    def approve(self, _id: int) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT requester_id, item_id
                   FROM item_requests
                   WHERE request_id=%s AND request_status='Pending'""",
                (_id,),
            )
            request = cursor.fetchone()
            if not request:
                return False
            cursor.execute(
                """UPDATE item_requests
                   SET request_status='Approved', processed_by=%s, approved_by=%s
                   WHERE request_id=%s AND request_status='Pending'""",
                (Session.load().get("user_id"), Session.load().get("user_id"), _id),
            )
            if cursor.rowcount != 1:
                conn.rollback()
                return False
            cursor.execute(
                """SELECT item_name FROM inventory_items WHERE item_id=%s""",
                (request["item_id"],),
            )
            item = cursor.fetchone()
            item_name = item["item_name"] if item else "your requested item"
            cursor.execute(
                """INSERT INTO notifications
                   (user_id, notif_message, notif_type, notif_isread, notif_create)
                   VALUES (%s, %s, 'Admin', 0, NOW())""",
                (
                    request["requester_id"],
                    f"Your request for '{item_name}' was accepted. Please pickup the item.",
                ),
            )
            conn.commit()
            _log_action("UPDATE", "item_requests", _id)
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def confirm_received(self, request_id: int, student_user_id: int) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT ir.item_id, ir.quantity, ir.approved_by, c.requires_return
                   FROM item_requests ir
                   JOIN inventory_items ii ON ii.item_id=ir.item_id
                   LEFT JOIN categories c ON c.category_id=ii.category_id
                   WHERE ir.request_id=%s AND ir.requester_id=%s
                     AND ir.request_status='Approved'""",
                (request_id, student_user_id),
            )
            request = cursor.fetchone()
            if not request:
                return False
            status = "Active" if request["requires_return"] else "Transaction Completed"
            cursor.execute(
                """UPDATE item_requests
                   SET request_status=%s, confirmed_by=%s
                   WHERE request_id=%s AND requester_id=%s
                     AND request_status='Approved'""",
                (status, student_user_id, request_id, student_user_id),
            )
            if cursor.rowcount != 1:
                conn.rollback()
                return False
            cursor.execute(
                """INSERT INTO transactions
                   (request_id, transaction_type, transaction_date, quantity, handled_by)
                   VALUES (%s, 'Checkout', NOW(), %s, %s)""",
                (request_id, request["quantity"], request["approved_by"]),
            )
            if not InventoryRepository().adjust_stock(
                request["item_id"], -request["quantity"], conn
            ):
                raise ValueError("Insufficient stock or item does not exist.")
            conn.commit()
            _log_action("UPDATE", "item_requests/transactions/inventory_items", request_id)
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def confirm_pickup(
        self, request_id: int, admin_user_id: int, item_id: int, quantity: int
    ) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            if quantity < 1:
                raise ValueError("Quantity must be at least 1.")
            cursor.execute(
                """SELECT c.requires_return
                   FROM item_requests ir
                   JOIN inventory_items ii ON ii.item_id=ir.item_id
                   LEFT JOIN categories c ON c.category_id=ii.category_id
                   WHERE ir.request_id=%s AND ir.item_id=%s
                     AND ir.quantity=%s AND ir.request_status='Approved'""",
                (request_id, item_id, quantity),
            )
            request = cursor.fetchone()
            if not request:
                return False
            status = "Active" if request["requires_return"] else "Transaction Completed"
            cursor.execute(
                """UPDATE item_requests
                   SET request_status=%s, processed_by=%s, confirmed_by=%s
                   WHERE request_id=%s AND item_id=%s AND quantity=%s
                     AND request_status='Approved'""",
                (status, admin_user_id, admin_user_id, request_id, item_id, quantity),
            )
            if cursor.rowcount != 1:
                conn.rollback()
                return False
            cursor.execute(
                """INSERT INTO transactions
                   (request_id, transaction_type, transaction_date, quantity, handled_by)
                   VALUES (%s, 'Checkout', NOW(), %s, %s)""",
                (request_id, quantity, admin_user_id),
            )
            if not InventoryRepository().adjust_stock(item_id, -quantity, conn):
                raise ValueError("Insufficient stock or item does not exist.")
            conn.commit()
            _log_action("UPDATE", "item_requests/transactions/inventory_items", request_id)
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def confirm_return(
        self,
        request_id: int,
        admin_user_id: int,
        item_id: int,
        quantity: int,
        condition: str,
        notes: str,
    ) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor()
        try:
            if quantity < 1:
                raise ValueError("Quantity must be at least 1.")
            if not condition.strip():
                raise ValueError("Condition status is required.")
            if not notes.strip():
                raise ValueError("Condition notes are required.")
            cursor.execute(
                """UPDATE item_requests
                   SET request_status='Returned', processed_by=%s
                   WHERE request_id=%s AND item_id=%s AND quantity=%s
                     AND request_status IN ('Active', 'Return Requested')""",
                (admin_user_id, request_id, item_id, quantity),
            )
            if cursor.rowcount != 1:
                conn.rollback()
                return False
            cursor.execute(
                """INSERT INTO transactions
                   (request_id, transaction_type, transaction_date, quantity,
                    conditon_status, condition_notes, handled_by)
                   VALUES (%s, 'Return', NOW(), %s, %s, %s, %s)""",
                (request_id, quantity, condition, notes, admin_user_id),
            )
            if not InventoryRepository().adjust_stock(item_id, quantity, conn):
                raise ValueError("Item does not exist.")
            conn.commit()
            _log_action("UPDATE", "item_requests/transactions/inventory_items", request_id)
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def cancel(self, _id: int, reason: str = "") -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT requester_id, request_status, item_id, quantity
                   FROM item_requests WHERE request_id=%s""",
                (_id,),
            )
            request = cursor.fetchone()
            if not request:
                return False
            if request["request_status"] == "Approved" and not reason.strip():
                raise ValueError("A cancellation reason is required after acceptance.")
            user_session = Session.load()
            current_user_id = user_session.get("user_id") if user_session else None
            cursor.execute(
                """UPDATE item_requests
                   SET request_status='Cancelled', processed_by=%s
                   WHERE request_id=%s
                     AND request_status IN ('Pending', 'Approved', 'Active', 'Return Requested')""",
                (current_user_id, _id),
            )
            if cursor.rowcount != 1:
                conn.rollback()
                return False

            if request.get("request_status") == "Active":
                InventoryRepository().adjust_stock(request["item_id"], request["quantity"], conn)

            cancellation_reason = reason.strip() if reason and reason.strip() else "Cancelled"
            cursor.execute(
    """INSERT INTO transactions 
       (request_id, transaction_type, transaction_date, quantity, 
        conditon_status, condition_notes, handled_by) 
       VALUES (%s, 'Cancelled', NOW(), %s, NULL, %s, %s)""",
    (_id, request["quantity"], cancellation_reason, current_user_id)
)

            cursor.execute(
                "SELECT item_name FROM inventory_items WHERE item_id=%s",
                (request["item_id"],),
            )
            item = cursor.fetchone()
            item_name = item["item_name"] if item else "an item"

            cursor.execute(
                "SELECT role FROM user_account WHERE user_id=%s",
                (current_user_id,),
            )
            user_row = cursor.fetchone()
            is_admin = bool(user_row and str(user_row.get("role", "")).lower() == "admin")

            if is_admin:
                cursor.execute(
                    """INSERT INTO notifications
                       (user_id, notif_message, notif_type, notif_isread, notif_create)
                       VALUES (%s, %s, 'Admin', 0, NOW())""",
                    (
                        request["requester_id"],
                        f"Your request for '{item_name}' was cancelled. Reason: {cancellation_reason}",
                    ),
                )
            else:
                if reason.strip():
                    cursor.execute(
                        """SELECT user_id FROM user_account
                           WHERE LOWER(role)='admin' AND status='Active'"""
                    )
                    admins = cursor.fetchall()
                    for admin in admins:
                        cursor.execute(
                            """INSERT INTO notifications
                               (user_id, notif_message, notif_type, notif_isread, notif_create)
                               VALUES (%s, %s, 'System', 0, NOW())""",
                            (
                                admin["user_id"],
                                f"Student cancelled '{item_name}'. Reason: {reason.strip()}",
                            ),
                        )
            conn.commit()
            _log_action("UPDATE", "item_requests/transactions", _id)
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def mark_notification_read(self, notification_id: int, user_id: int) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """UPDATE notifications SET notif_isread=1
                   WHERE notif_id=%s AND user_id=%s""",
                (notification_id, user_id),
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def request_return(self, _id: int) -> bool:
        return self._set_status(_id, "Return Requested")

    def _set_status(self, _id: int, status: str) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE item_requests
               SET request_status=%s, processed_by=%s
               WHERE request_id=%s""",
            (status, Session.load().get("user_id"), _id),
        )
        conn.commit()
        approved = cursor.rowcount > 0
        cursor.close()
        if approved:
            _log_action("UPDATE", "item_requests", _id)
        return approved

    def get_all(self) -> List[Dict[str, Any]]:
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT ir.request_id, ir.requester_id, ir.item_id,
                      ir.processed_by, ir.request_status, ir.quantity,
                      ir.request_date, ir.due_date,
                      ua.gmail,
                      CONCAT_WS(' ', pi.first_name, pi.middle_name, pi.last_name) AS requester_name,
                   pi.student_id, pi.department, pi.course, pi.address,
                   pi.contact_number,
                   ii.item_name, ii.item_code, ii.description AS item_description,
                      ii.image_path, c.category_name
               FROM item_requests ir
               JOIN user_account ua ON ua.user_id = ir.requester_id
               LEFT JOIN personal_info pi ON pi.user_id = ua.user_id
               JOIN inventory_items ii ON ii.item_id = ir.item_id
               LEFT JOIN categories c ON c.category_id = ii.category_id
               WHERE ir.request_status NOT IN ('Returned', 'Completed', 'Transaction Completed')
               ORDER BY ir.request_date DESC"""
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT ir.request_id, ir.item_id, ir.requester_id, ir.quantity,
                      ir.request_date, ir.due_date, ir.request_status,
                      ir.processed_by, ii.item_name, ii.item_code, ii.image_path,
                      ii.description AS item_description, c.category_name
               FROM item_requests ir
               JOIN inventory_items ii ON ii.item_id=ir.item_id
               LEFT JOIN categories c ON c.category_id=ii.category_id
               WHERE ir.requester_id=%s
                 AND ir.request_status NOT IN
                     ('Returned', 'Completed', 'Transaction Completed', 'Cancelled')
               ORDER BY ir.request_date DESC""",
            (user_id,),
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def has_active_request(self, user_id: int, item_id: int) -> bool:
        """Return whether a user has a request that still blocks a new request."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT 1
               FROM item_requests
               WHERE requester_id=%s AND item_id=%s
                 AND request_status IN
                     ('Pending', 'Approved', 'Active', 'Return Requested')
               LIMIT 1""",
            (user_id, item_id),
        )
        result = cursor.fetchone() is not None
        cursor.close()
        return result

    def notify(self, user_id: int, message: str, notif_type: str = "Admin") -> bool:
        if not message.strip():
            raise ValueError("Notification message is required.")
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO notifications
               (user_id, notif_message, notif_type, notif_isread, notif_create)
               VALUES (%s, %s, %s, 0, NOW())""",
            (user_id, message.strip(), notif_type),
        )
        conn.commit()
        created = cursor.rowcount > 0
        cursor.close()
        return created

    def add_request(
        self, item_id: int, requester_id: int, quantity: int, due_date=None
    ) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT c.requires_return
                   FROM inventory_items ii
                   LEFT JOIN categories c ON c.category_id=ii.category_id
                   WHERE ii.item_id=%s""",
                (item_id,),
            )
            item = cursor.fetchone()
            if not item:
                raise ValueError("The requested item no longer exists.")
            if item["requires_return"]:
                if due_date is None:
                    raise ValueError("A due date is required for returnable items.")
                if isinstance(due_date, datetime):
                    due_date = due_date.date()
                if not isinstance(due_date, date):
                    raise ValueError("Due date must be a valid calendar date.")
                today = date.today()
                if due_date < today or due_date > today + timedelta(days=90):
                    raise ValueError("Items can only be borrowed for up to 3 months.")
            else:
                due_date = None
            cursor.execute(
                """INSERT INTO item_requests
                   (item_id, requester_id, quantity, request_status, request_date, due_date)
                   VALUES (%s, %s, %s, 'Pending', NOW(), %s)""",
                (item_id, requester_id, quantity, due_date),
            )
            conn.commit()
            created = cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
        if created:
            _log_action("INSERT", "item_requests", item_id)
        return created

    def get_notifications(self, user_id: int) -> List[Dict[str, Any]]:
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT notif_id, user_id, notif_message, notif_type,
                      notif_isread, notif_create
               FROM notifications WHERE user_id=%s
               ORDER BY notif_create DESC""",
            (user_id,),
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def addRequest(self):
        pass                                      
        
    def updateRequest(self):
        pass                                       
        
    def deleteRequest(self):
        pass                                     


class TransactionRepository(BaseRepository):
    def add(self, entity: Transaction) -> bool:
        if isinstance(entity, dict):
            return self.addTransaction(entity["request_id"], entity.get("quantity"))
        raise TypeError("Transactions must be created with a transaction details dictionary.")

    def delete(self, _id: int) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM transactions_archive WHERE arc_transaction_id=%s",
            (_id,),
        )
        conn.commit()
        deleted = cursor.rowcount > 0
        cursor.close()
        if deleted:
            _log_action("DELETE", "transactions_archive", _id)
        return deleted


    def update(self, entity: Transaction) -> bool:
        if not isinstance(entity, dict):
            raise TypeError("Transactions must be updated with a transaction details dictionary.")
        transaction_id = entity.get("transaction_id")
        if not transaction_id:
            raise ValueError("Transaction ID is required.")
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE transactions
               SET conditon_status=%s, condition_notes=%s
               WHERE transaction_id=%s""",
            (entity.get("condition_status", "Good"),
             entity.get("condition_notes", ""), transaction_id),
        )
        conn.commit()
        updated = cursor.rowcount > 0
        cursor.close()
        if updated:
            _log_action("UPDATE", "transactions", transaction_id)
        return updated

    def get_all(self, mode: str = "current") -> List[Dict[str, Any]]:
        if mode not in {"current", "archived"}:
            raise ValueError("Transaction mode must be 'current' or 'archived'.")
        table = "transactions" if mode == "current" else "transactions_archive"
        id_column = "t.transaction_id" if mode == "current" else "t.arc_transaction_id"
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            f"""SELECT {id_column} AS transaction_id, t.request_id,
                       t.transaction_type, t.quantity, t.conditon_status AS condition_status,
                       t.condition_notes, t.handled_by, t.transaction_date,
                       ir.request_status, ir.approved_by, ir.confirmed_by,
                       ii.item_name, ii.item_code,
                       CONCAT_WS(' ', approved_pi.first_name, approved_pi.middle_name,
                                 approved_pi.last_name) AS approved_by_name,
                       CONCAT_WS(' ', confirmed_pi.first_name, confirmed_pi.middle_name,
                                 confirmed_pi.last_name) AS confirmed_by_name,
                       CONCAT_WS(' ', pi.first_name, pi.middle_name, pi.last_name) AS requester_name
                FROM {table} t
                JOIN item_requests ir ON ir.request_id=t.request_id
                JOIN inventory_items ii ON ii.item_id=ir.item_id
                LEFT JOIN personal_info pi ON pi.user_id=ir.requester_id
                LEFT JOIN personal_info approved_pi ON approved_pi.user_id=ir.approved_by
                LEFT JOIN personal_info confirmed_pi ON confirmed_pi.user_id=ir.confirmed_by
                ORDER BY t.transaction_date DESC"""
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_details(
        self, transaction_id: int, mode: str = "current"
    ) -> Dict[str, Any] | None:
        if mode not in {"current", "archived"}:
            raise ValueError("Transaction mode must be 'current' or 'archived'.")
        table = "transactions" if mode == "current" else "transactions_archive"
        id_column = "t.transaction_id" if mode == "current" else "t.arc_transaction_id"
        archive_fields = (
            "NULL AS archived_date, NULL AS archive_reason"
            if mode == "current"
            else "t.archived_date, t.archive_reason"
        )
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            f"""SELECT {id_column} AS transaction_id, t.request_id,
                       t.transaction_type, t.quantity,
                       t.conditon_status AS condition_status,
                       t.condition_notes, t.handled_by, t.transaction_date,
                       {archive_fields},
                       ir.requester_id, ir.item_id, ir.quantity AS requested_quantity,
                       ir.request_status, ir.request_date, ir.due_date,
                       ir.processed_by, ir.approved_by, ir.confirmed_by,
                       ii.item_name, ii.item_code, ii.description AS item_description,
                       ii.stock, ii.serial_no, ii.unit,
                       CONCAT_WS(' ', requester_pi.first_name,
                                 requester_pi.middle_name,
                                 requester_pi.last_name) AS requester_name,
                       requester_pi.student_id, requester_pi.contact_number,
                       requester_pi.birthday, requester_pi.gender,
                       requester_pi.address, requester_pi.department,
                       requester_pi.course,
                       CONCAT_WS(' ', processed_pi.first_name,
                                 processed_pi.middle_name,
                                 processed_pi.last_name) AS processed_by_name,
                       CONCAT_WS(' ', approved_pi.first_name,
                                 approved_pi.middle_name,
                                 approved_pi.last_name) AS approved_by_name,
                       CONCAT_WS(' ', confirmed_pi.first_name,
                                 confirmed_pi.middle_name,
                                 confirmed_pi.last_name) AS confirmed_by_name,
                       CONCAT_WS(' ', handled_pi.first_name,
                                 handled_pi.middle_name,
                                 handled_pi.last_name) AS handled_by_name
                FROM {table} t
                JOIN item_requests ir ON ir.request_id=t.request_id
                JOIN inventory_items ii ON ii.item_id=ir.item_id
                LEFT JOIN personal_info requester_pi
                       ON requester_pi.user_id=ir.requester_id
                LEFT JOIN personal_info processed_pi
                       ON processed_pi.user_id=ir.processed_by
                LEFT JOIN personal_info approved_pi
                       ON approved_pi.user_id=ir.approved_by
                LEFT JOIN personal_info confirmed_pi
                       ON confirmed_pi.user_id=ir.confirmed_by
                LEFT JOIN personal_info handled_pi
                       ON handled_pi.user_id=t.handled_by
                WHERE {id_column}=%s""",
            (transaction_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        return row

    def get_for_user(self, user_id: int, mode: str = "current") -> List[Dict[str, Any]]:
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        table = "transactions" if mode == "current" else "transactions_archive"
        id_column = "t.transaction_id" if mode == "current" else "t.arc_transaction_id"
        cursor.execute(
            f"""SELECT {id_column} AS transaction_id, t.request_id,
                       t.transaction_type, t.quantity, t.conditon_status AS condition_status,
                       t.condition_notes, t.handled_by, t.transaction_date,
                       ir.request_status, ir.requester_id, ir.approved_by,
                       ir.confirmed_by, ii.item_name,
                       CONCAT_WS(' ', approved_pi.first_name, approved_pi.middle_name,
                                 approved_pi.last_name) AS approved_by_name,
                       CONCAT_WS(' ', confirmed_pi.first_name, confirmed_pi.middle_name,
                                 confirmed_pi.last_name) AS confirmed_by_name
                FROM {table} t
                JOIN item_requests ir ON ir.request_id=t.request_id
                JOIN inventory_items ii ON ii.item_id=ir.item_id
                LEFT JOIN personal_info approved_pi ON approved_pi.user_id=ir.approved_by
                LEFT JOIN personal_info confirmed_pi ON confirmed_pi.user_id=ir.confirmed_by
                WHERE ir.requester_id=%s""",
            (user_id,),
        )
        user_rows = cursor.fetchall()
        cursor.close()
        return user_rows

    def get_user_history(self, user_id: int) -> List[Dict[str, Any]]:
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT t.transaction_id, t.request_id, t.transaction_type,
                      t.quantity, t.conditon_status AS condition_status,
                      t.condition_notes, t.handled_by, t.transaction_date,
                      ir.requester_id, ir.item_id, ir.quantity AS requested_quantity,
                      ir.request_status, ir.request_date, ir.due_date,
                      ir.processed_by, ir.approved_by, ir.confirmed_by,
                      ii.item_name, ii.item_code, ii.description AS item_description,
                      ii.stock, ii.serial_no, ii.unit,
                      CONCAT_WS(' ', requester_pi.first_name, requester_pi.middle_name,
                                requester_pi.last_name) AS requester_name,
                      CONCAT_WS(' ', approved_pi.first_name, approved_pi.middle_name,
                                approved_pi.last_name) AS approved_by_name,
                      CONCAT_WS(' ', confirmed_pi.first_name, confirmed_pi.middle_name,
                                confirmed_pi.last_name) AS confirmed_by_name,
                      CONCAT_WS(' ', handled_pi.first_name, handled_pi.middle_name,
                                handled_pi.last_name) AS handled_by_name
               FROM transactions t
               JOIN item_requests ir ON ir.request_id=t.request_id
               JOIN inventory_items ii ON ii.item_id=ir.item_id
               LEFT JOIN personal_info requester_pi ON requester_pi.user_id=ir.requester_id
               LEFT JOIN personal_info approved_pi ON approved_pi.user_id=ir.approved_by
               LEFT JOIN personal_info confirmed_pi ON confirmed_pi.user_id=ir.confirmed_by
               LEFT JOIN personal_info handled_pi ON handled_pi.user_id=t.handled_by
               WHERE ir.requester_id=%s
               UNION ALL
               SELECT ta.arc_transaction_id AS transaction_id, ta.request_id, ta.transaction_type,
                      ta.quantity, ta.conditon_status AS condition_status,
                      ta.condition_notes, ta.handled_by, ta.transaction_date,
                      ir.requester_id, ir.item_id, ir.quantity AS requested_quantity,
                      ir.request_status, ir.request_date, ir.due_date,
                      ir.processed_by, ir.approved_by, ir.confirmed_by,
                      ii.item_name, ii.item_code, ii.description AS item_description,
                      ii.stock, ii.serial_no, ii.unit,
                      CONCAT_WS(' ', requester_pi.first_name, requester_pi.middle_name,
                                requester_pi.last_name) AS requester_name,
                      CONCAT_WS(' ', approved_pi.first_name, approved_pi.middle_name,
                                approved_pi.last_name) AS approved_by_name,
                      CONCAT_WS(' ', confirmed_pi.first_name, confirmed_pi.middle_name,
                                confirmed_pi.last_name) AS confirmed_by_name,
                      CONCAT_WS(' ', handled_pi.first_name, handled_pi.middle_name,
                                handled_pi.last_name) AS handled_by_name
               FROM transactions_archive ta
               JOIN item_requests ir ON ir.request_id=ta.request_id
               JOIN inventory_items ii ON ii.item_id=ir.item_id
               LEFT JOIN personal_info requester_pi ON requester_pi.user_id=ir.requester_id
               LEFT JOIN personal_info approved_pi ON approved_pi.user_id=ir.approved_by
               LEFT JOIN personal_info confirmed_pi ON confirmed_pi.user_id=ir.confirmed_by
               LEFT JOIN personal_info handled_pi ON handled_pi.user_id=ta.handled_by
               WHERE ir.requester_id=%s
               ORDER BY transaction_date DESC""",
            (user_id, user_id),
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def addTransaction(self, request_id: int, quantity: int = None) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        if quantity is None:
            cursor.execute(
                "SELECT quantity FROM item_requests WHERE request_id=%s",
                (request_id,),
            )
            row = cursor.fetchone()
            quantity = row["quantity"] if row else None
        cursor.close()
        if quantity is None:
            return False
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO transactions
               (request_id, transaction_type, transaction_date, quantity, handled_by)
               VALUES (%s, 'Checkout', NOW(), %s, %s)""",
            (request_id, quantity, Session.load().get("user_id")),
        )
        conn.commit()
        created = cursor.rowcount > 0
        cursor.close()
        if created:
            _log_action("INSERT", "transactions", request_id)
        return created
        
    def archiveTransaction(self, _id: int) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO transactions_archive
                   (request_id, transaction_type, quantity,
                    conditon_status, condition_notes, handled_by,
                    transaction_date, archived_date, archive_reason)
                   SELECT request_id, transaction_type, quantity,
                          conditon_status, condition_notes, handled_by,
                          transaction_date, NOW(), 'Archived'
                   FROM transactions
                   WHERE transaction_id=%s""",
                (_id,),
            )
            if cursor.rowcount == 0:
                conn.rollback()
                return False
            cursor.execute(
                "DELETE FROM transactions WHERE transaction_id=%s",
                (_id,),
            )
            conn.commit()
            _log_action("DELETE", "transactions", _id)
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def restoreTransaction(self, _id: int) -> bool:
        conn = self._db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO transactions
                   (request_id, transaction_type, transaction_date, quantity,
                    conditon_status, condition_notes, handled_by)
                   SELECT request_id, transaction_type, transaction_date, quantity,
                          conditon_status, condition_notes, handled_by
                   FROM transactions_archive
                   WHERE arc_transaction_id=%s""",
                (_id,),
            )
            if cursor.rowcount == 0:
                conn.rollback()
                return False
            cursor.execute(
                "DELETE FROM transactions_archive WHERE arc_transaction_id=%s",
                (_id,),
            )
            conn.commit()
            _log_action("INSERT", "transactions", _id)
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

class AnalyticsRepository:
    def __init__(self):
        self._db = DatabaseManager.get_instance()

    def get_top_requested_items(self, limit: int = 5) -> List[Dict[str, Any]]:
        if limit < 1:
            raise ValueError("Limit must be at least 1.")
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT ii.item_name, COUNT(*) AS request_count
               FROM item_requests ir
               JOIN inventory_items ii ON ii.item_id=ir.item_id
               GROUP BY ii.item_id, ii.item_name
               ORDER BY request_count DESC
               LIMIT %s""",
            (limit,),
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_category_request_distribution(self) -> List[Dict[str, Any]]:
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT COALESCE(c.category_name, 'Uncategorized') AS category_name,
                      COUNT(*) AS request_count,
                      ROUND(COUNT(*) * 100.0 / totals.total_count, 2) AS percentage
               FROM item_requests ir
               JOIN inventory_items ii ON ii.item_id=ir.item_id
               LEFT JOIN categories c ON c.category_id=ii.category_id
               CROSS JOIN (
                   SELECT COUNT(*) AS total_count FROM item_requests
               ) totals
               GROUP BY c.category_id, c.category_name, totals.total_count
               ORDER BY request_count DESC"""
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_summary_stats(self) -> Dict[str, int]:
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        # Note: Adjust 'Approved' to whatever status you use for active/borrowed items
        cursor.execute(
            """SELECT
                   (SELECT COALESCE(SUM(stock), 0) FROM inventory_items) AS total_stock,
                   (SELECT COUNT(*) FROM item_requests WHERE request_status='Pending') AS pending_requests,
                   (SELECT COUNT(*) FROM user_account WHERE status='Active') AS active_users,
                   (SELECT COUNT(*) FROM item_requests WHERE request_status='Approved') AS active_requests,
                   (SELECT COUNT(*) FROM inventory_items WHERE stock <= 0) AS out_of_stock_count,
                   (SELECT COUNT(*) FROM item_requests WHERE request_status='Approved' AND due_date <= CURRENT_DATE) AS due_for_return_count"""
        )
        row = cursor.fetchone() or {}
        cursor.close()
        return {
            "total_stock": int(row.get("total_stock", 0)),
            "pending_requests": int(row.get("pending_requests", 0)),
            "active_users": int(row.get("active_users", 0)),
            "active_requests": int(row.get("active_requests", 0)),
            "out_of_stock_count": int(row.get("out_of_stock_count", 0)),
            "due_for_return_count": int(row.get("due_for_return_count", 0))
        }

    def get_out_of_stock_items(self) -> List[Dict[str, Any]]:
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT item_id, item_name, stock 
               FROM inventory_items 
               WHERE stock <= 0 
               ORDER BY item_name ASC"""
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_due_items(self) -> List[Dict[str, Any]]:
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        # Assuming 'Approved' is the status for items currently checked out
        cursor.execute(
            """SELECT ir.request_id, ii.item_name, ir.due_date
               FROM item_requests ir
               JOIN inventory_items ii ON ir.item_id = ii.item_id
               WHERE ir.request_status = 'Approved' AND ir.due_date <= CURRENT_DATE
               ORDER BY ir.due_date ASC"""
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_recent_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        if limit < 1:
            raise ValueError("Limit must be at least 1.")
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        # Changed sl.record_id AS description to AS item_id to support the UI's ID formatting
        cursor.execute(
            """SELECT sl.log_id, sl.user_id, ua.gmail AS user,
                      sl.action, sl.table_affected,
                      sl.record_id AS item_id, sl.timestamp
               FROM system_logs sl
               LEFT JOIN user_account ua ON ua.user_id=sl.user_id
               ORDER BY sl.timestamp DESC
               LIMIT %s""",
            (limit,),
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows