import re

STUDENT_NUMBER_PATTERN = re.compile(r"^[A-Z]{2}\d{9}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+$")

def validate_email(email: str) -> None:
    if not EMAIL_PATTERN.fullmatch(email.strip()):
        raise ValueError("Email must contain a valid address with '@'.")


def validate_student_number(student_number: str) -> None:
    if not STUDENT_NUMBER_PATTERN.fullmatch(student_number.strip().upper()):
        raise ValueError("Student No. must contain exactly 2 letters followed by 9 numbers.")


def validate_contact_number(contact_number: str) -> None:
    if not re.fullmatch(r"\d{11}", contact_number.strip()):
        raise ValueError("Contact No. must contain exactly 11 digits.")


def validate_password(password: str) -> None:
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter.")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError("Password must contain at least one symbol.")


def validate_new_account(account_data: dict, personal_data: dict) -> None:
    required_account = {
        "email": account_data.get("gmail", ""),
        "password": account_data.get("password", ""),
    }
    required_personal = {
        "student_no": personal_data.get("student_id", ""),
        "name": " ".join(
            str(personal_data.get(key, "")).strip()
            for key in ("first_name", "last_name")
        ),
        "course": personal_data.get("course", ""),
    }
    missing = [
        label for label, value in {**required_account, **required_personal}.items()
        if not str(value).strip()
    ]
    if missing:
        raise ValueError("Required fields are missing: " + ", ".join(missing) + ".")
    validate_email(str(required_account["email"]))
    validate_student_number(str(required_personal["student_no"]))
    validate_contact_number(str(personal_data.get("contact_number", "")))
    validate_password(str(required_account["password"]))
