from abc import ABC, abstractmethod
from datetime import datetime
import json
from pathlib import Path
from typing import List

SESSION_PATH = Path(__file__).resolve().parent.parent / "session.json"


class Session:
    @staticmethod
    def save(user_id: int, gmail: str, role: str) -> None:
        session_data = {"user_id": user_id, "gmail": gmail, "role": role}
        SESSION_PATH.write_text(json.dumps(session_data), encoding="utf-8")

    @staticmethod
    def load() -> dict:
        try:
            return json.loads(SESSION_PATH.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def clear() -> None:
        SESSION_PATH.unlink(missing_ok=True)


class UserAccount(ABC):
    def __init__(self, user_id: int, gmail: str, password_hash: str, role: str, creationdate: datetime):
        self.__user_id = user_id              
        self.__gmail = gmail                  
        self.__password_hash = password_hash  
        self.__role = role                    
        self.__creationdate = creationdate    

    @property
    def gmail(self) -> str:
        return self.__gmail
        
    @property
    def password_hash(self) -> str:
        return self.__password_hash

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
        return self.password_hash == input_password 
    
    def get_permissions(self) -> List[str]:
        return ["read_items", "request_items"]