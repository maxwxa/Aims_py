from abc import ABC, abstractmethod
from datetime import datetime, date
import hashlib
import hmac
import secrets
from typing import List


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        600_000,
    )
    return f"pbkdf2_sha256$600000${salt.hex()}${password_hash.hex()}"


def verify_password(password: str, stored_password: str) -> bool:
    try:
        algorithm, iterations_text, salt_hex, hash_hex = stored_password.split("$")
        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations_text)
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
    except (ValueError, TypeError):
        return False

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
        dklen=len(expected_hash),
    )
    return hmac.compare_digest(password_hash, expected_hash)

class UserAccount(ABC):
    def __init__(self, user_id: int, gmail: str, password_hash: str, role: str, creationdate: datetime):
        self.__user_id = user_id              
        self.__gmail = gmail                  
        self.__password_hash = password_hash  
        self.__role = role                    
        self.__creationdate = creationdate    

    @abstractmethod
    def authenticate(self, input_password: str) -> bool:
        pass                                  

    @abstractmethod
    def get_permissions(self) -> List[str]:
        pass                                  


class User(UserAccount):
    def __init__(self, user_id: int, gmail: str, password_hash: str, role: str, creationdate: datetime, department: str, course: str):
        super().__init__(user_id, gmail, password_hash, role, creationdate)
        self.__department = department        
        self.__course = course                

    def authenticate(self, input_password: str) -> bool:
        return verify_password(input_password, self._UserAccount__password_hash)

    def get_permissions(self) -> List[str]:
        return ["read_items", "request_items"] 


class Admin(UserAccount):
    def __init__(self, user_id: int, gmail: str, password_hash: str, role: str, creationdate: datetime, access_level: int):
        super().__init__(user_id, gmail, password_hash, role, creationdate)
        self.access_level = access_level      

    def authenticate(self, input_password: str) -> bool:
        return verify_password(input_password, self._UserAccount__password_hash)

    def get_permissions(self) -> List[str]:
        return ["all"]                        

    def manage_users(self):
        pass
