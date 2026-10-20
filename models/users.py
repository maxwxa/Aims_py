from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Dict, Any

class UserAccount(ABC):
    def __init__(self, user_id: int, gmail: str, password_hash: str, role: str, creationdate: datetime):
        self.__user_id = user_id              # -user_id[cite: 4]
        self.__gmail = gmail                  # -gmail[cite: 4]
        self.__password_hash = password_hash  # -password_hash[cite: 4]
        self.__role = role                    # -role[cite: 4]
        self.__creationdate = creationdate    # -creationdate[cite: 4]

    @abstractmethod
    def authenticate(self) -> bool:
        pass                                  # +authenticate()[cite: 4]

    @abstractmethod
    def get_permissions(self) -> List[str]:
        pass                                  # +get_permissions()[cite: 4]


class User(UserAccount):
    def __init__(self, user_id: int, gmail: str, password_hash: str, role: str, creationdate: datetime, department: str, course: str):
        super().__init__(user_id, gmail, password_hash, role, creationdate)
        self.__department = department        # -department[cite: 4]
        self.__course = course                # -course[cite: 4]

    def authenticate(self) -> bool:
        return True

    def get_permissions(self) -> List[str]:
        return ["read_items", "request_items"] # +get_permissions()[cite: 4]


class Admin(UserAccount):
    def __init__(self, user_id: int, gmail: str, password_hash: str, role: str, creationdate: datetime, access_level: int):
        super().__init__(user_id, gmail, password_hash, role, creationdate)
        self.access_level = access_level      # +access_level[cite: 4]

    def authenticate(self) -> bool:
        return True

    def get_permissions(self) -> List[str]:
        return ["all"]                        # +get_permissions()[cite: 4]

    def manage_users(self):
        pass                                  # +manage_users()[cite: 4]


class AccountArchive:
    def __init__(self, arc_user_id: int, original_user_id: int, gmail: str, password_hash: str, role: str, archived_date: datetime, archive_reason: str):
        self.__arc_user_id = arc_user_id             # -arc_user_id[cite: 4]
        self.__original_user_id = original_user_id   # -original_user_id[cite: 4]
        self.__gmail = gmail                         # -gmail[cite: 4]
        self.__password_hash = password_hash         # -password_hash[cite: 4]
        self.__role = role                           # -role[cite: 4]
        self.__archived_date = archived_date         # -archived date[cite: 4]
        self.__archive_reason = archive_reason       # -archive_reason[cite: 4]


class Notification:
    def __init__(self, notif_id: int, user_id: int, notif_message: str, notif_type: str, notif_isread: bool, notif_created_time: datetime):
        self.__notif_id = notif_id                   # -notif_id[cite: 4]
        self.__user_id = user_id                     # -user_id[cite: 4]
        self.__notif_message = notif_message         # -notif_message[cite: 4]
        self.__notif_type = notif_type               # -notif_type[cite: 4]
        self.__notif_isread = notif_isread           # -notif isread[cite: 4]
        self.__notif_created_time = notif_created_time # -notif_created_time[cite: 4]


class Log:
    def __init__(self, log_id: int, user_id: int, action: str, table_affected: str, record_id: int, timestamp: datetime):
        self.__log_id = log_id                       # -log_id[cite: 4]
        self.__user_id = user_id                     # -user_id[cite: 4]
        self.__action = action                       # -action[cite: 4]
        self.__table_affected = table_affected       # -table_affected[cite: 4]
        self.__record_id = record_id                 # -record id[cite: 4]
        self.__timestamp = timestamp                 # -timestamp[cite: 4]


class PersonalInfo:
    def __init__(self, personal_id: int, first_name: str, middle_name: str, last_name: str, birthday: date, contact_number: str, department: str, course: str, student_id: str):
        self.__personal_id = personal_id             # -personal_id[cite: 4]
        self.__first_name = first_name               # -first_name[cite: 4]
        self.__middle_name = middle_name             # -middle_name[cite: 4]
        self.__last_name = last_name                 # -last_name[cite: 4]
        self.__birthday = birthday                   # -birthday[cite: 4]
        self.__contact_number = contact_number       # -contact_number[cite: 4]
        self.__department = department               # -department[cite: 4]
        self.__course = course                       # -course[cite: 4]
        self.__student_id = student_id               # -student_id[cite: 4]