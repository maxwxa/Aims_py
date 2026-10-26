from abc import ABC, abstractmethod
from datetime import datetime
import os
from typing import List

class Session:
    _current_user = {}
    _session_keys = ("AIMS_USER_ID", "AIMS_USER_GMAIL", "AIMS_USER_ROLE")

    @staticmethod
    def save(user_id: int, gmail: str, role: str) -> None:
        Session._current_user = {"user_id": user_id, "gmail": gmail, "role": role}
        os.environ["AIMS_USER_ID"] = str(user_id)
        os.environ["AIMS_USER_GMAIL"] = gmail
        os.environ["AIMS_USER_ROLE"] = role

    @staticmethod
    def load() -> dict:
        if not Session._current_user:
            user_id = os.environ.get("AIMS_USER_ID")
            gmail = os.environ.get("AIMS_USER_GMAIL")
            role = os.environ.get("AIMS_USER_ROLE")
            if user_id and gmail and role:
                Session._current_user = {
                    "user_id": int(user_id),
                    "gmail": gmail,
                    "role": role,
                }
        return dict(Session._current_user)

    @staticmethod
    def clear() -> None:
        Session._current_user = {}
        for key in Session._session_keys:
            os.environ.pop(key, None)


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