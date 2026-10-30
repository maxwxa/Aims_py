from tkinter import messagebox
import customtkinter as ctk
from tkcalendar import DateEntry
from models.account_validation import validate_new_account, validate_password

WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"
GREEN = "#84cc16"
PURPLE = "#9333ea"
MODAL_BG = "#0b1b42"
MODAL_TITLE_FONT = ("Segoe UI", 22, "bold")


class AccountEditor:
    department_data = {
        "College of Arts & Sciences": [
            "ABCom - Bachelor of Arts in Communication",
            "ABEng - Bachelor of Arts in English",
            "BSM - Bachelor of Science in Mathematics",
            "BSP - Bachelor of Science in Psychology",
        ],
        "College of Business & Accountancy": [
            "ABA - Associate in Business Administration",
            "BSAIS - Bachelor of Science in Accounting Information System",
            "BSA - Bachelor of Science in Accountancy",
            "BSMA - Bachelor of Science in Management Accounting",
            "BSREM - Bachelor of Science in Real Estate Management",
            "BSIA - Bachelor of Science in Internal Auditing",
            "BSLM - Bachelor of Science in Legal Management",
            "BSBA - Bachelor of Science in Business Administration",
        ],
        "College of Computer Studies": [
            "ACT - Associate in Computer Technology",
            "BSCS - Bachelor of Science in Computer Science",
            "BSIT - Bachelor of Science in Information Technology",
            "BSIS - Bachelor of Science in Information System",
        ],
        "College of Teacher Education": [
            "BECEd - Bachelor in Early Childhood Education",
            "BELEMEd - Bachelor in Elementary Education",
            "BSEd - Bachelor in Secondary Education",
            "BTVTEd - Bachelor in Technical Vocational Teacher Education",
            "CPT - Certificate in Teaching Program",
        ],
        "College of Criminology & Administration": [
            "BSC - Bachelor of Science in Criminology",
            "BSISM - Bachelor of Science in Industrial Security Management",
            "BPA - Bachelor in Public Administration",
        ],
        "College of Engineering": [
            "BSCE - Bachelor of Science in Computer Engineering",
            "BSELE - Bachelor of Science in Electronics Engineering",
        ],
        "College of Health Sciences": [
            "BSMedTech - Bachelor of Science in Medical Technology",
            "BSN - Bachelor of Science in Nursing",
            "BSRadTech - Bachelor of Science in Radiologic Technology",
            "DHWA - Diploma in Health Care & Wellness Associate",
        ],
        "International School of Hospitality & Tourism Management": [
            "BSHM - Bachelor of Science in Hospitality Management",
            "BSTM - Bachelor of Science in Tourism Management",
            "DHRM1 - Diploma in Hotel & Restaurant Management-1",
            "DHRM2 - Diploma in Hotel & Restaurant Management-2",
        ],
        "Senior High Department": ["ACADEMIC-TRACK", "TECH-PRO-TRACK"],
    }

    def __init__(self, parent, repository, account=None, on_changed=None):
        self.repository = repository
        self.account = account
        self.on_changed = on_changed or (lambda: None)
        details = {}
        if account is not None:
            details = repository.get_by_id(account["account_id"]) or {}
        self.modal = ctk.CTkToplevel(parent)
        self.modal.title("Create Account" if account is None else "Update Account")
        self.modal.geometry("700x700")
        self.modal.configure(fg_color="#1e3a8a")
        self.modal.transient(parent)
        self.modal.grab_set()
        card = ctk.CTkFrame(
            self.modal, fg_color=WHITE, corner_radius=15,
            border_width=1, border_color="#d1d5db",
        )
        card.pack(fill="both", expand=True, padx=24, pady=24)
        card.grid_columnconfigure(0, weight=1, uniform="account")
        card.grid_columnconfigure(1, weight=0)
        card.grid_columnconfigure(2, weight=2, uniform="account")
        card.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(
            card, text=self.modal.title(), text_color=TEXT_BLUE,
            font=("Arial", 24, "bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=28, pady=(20, 8))

        left = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0)
        left.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=(28, 20), pady=(0, 24))
        right = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0)
        right.grid(row=1, column=2, rowspan=2, sticky="nsew", padx=(20, 28), pady=(0, 24))
        ctk.CTkFrame(card, width=2, fg_color="#d1d5db").grid(
            row=1, column=1, rowspan=2, sticky="ns", pady=(0, 24)
        )
        left.grid_columnconfigure(0, weight=1)
        right.grid_columnconfigure((0, 1), weight=1, uniform="personal")

        ctk.CTkLabel(
            left, text="Account Information", text_color=TEXT_BLUE,
            font=("Arial", 15, "bold"),
        ).pack(anchor="w", padx=4, pady=(0, 8))
        left_form = ctk.CTkFrame(left, fg_color=WHITE, corner_radius=0)
        left_form.pack(fill="x")
        left_form.grid_columnconfigure(0, weight=1)
        left_row = 0
        if account is not None:
            ctk.CTkLabel(
                left_form, text="Account ID", text_color=TEXT_BLUE,
            ).grid(row=left_row * 2, column=0, sticky="w", padx=4, pady=(4, 2))
            account_id_entry = ctk.CTkEntry(
                left_form, corner_radius=8, fg_color="#e5e7eb",
                text_color="#374151",
            )
            account_id_entry.grid(
                row=left_row * 2 + 1, column=0, sticky="ew",
                padx=4, pady=(0, 8),
            )
            account_id_entry.insert(0, str(account["account_id"]))
            account_id_entry.configure(state="disabled")
            left_row += 1
        self.email = self._entry(
            left_form, "Email", details.get("gmail", ""), left_row
        )
        left_row += 1
        self.password = self._entry(
            left_form, "Password" if account is None else "Password (optional)",
            "", left_row, masked=True,
        )
        self.show_password = ctk.CTkCheckBox(
            left_form, text="Show Password", text_color=TEXT_BLUE,
            command=self.toggle_password_visibility,
        )
        self.show_password.grid(
            row=left_row * 2 + 2, column=0, sticky="w", padx=4, pady=(0, 6)
        )
        left_row += 2
        self.role = self._combo(
            left_form, "Role", ["Admin", "Student"],
            details.get("role", "Student"),
            left_row,
        )
        left_row += 1
        self.status = self._combo(
            left_form, "Status", ["Active", "Inactive", "Disabled"],
            details.get("status", (account or {}).get("account_status", "Active")),
            left_row,
        )

        ctk.CTkLabel(
            right, text="Personal Information", text_color=TEXT_BLUE,
            font=("Arial", 15, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        self.personal_entries = {}
        for row, fields in enumerate(
            (
                (("first_name", "First Name"), ("middle_name", "Middle Name")),
                (("last_name", "Last Name"), ("contact_number", "Contact No.")),
                (("student_id", "Student No."),),
            ),
            1,
        ):
            for column, (key, label) in enumerate(fields):
                self.personal_entries[key] = self._entry(
                    right, label, details.get(key, ""), row, column
                )
            if len(fields) == 1:
                self.personal_entries[key].grid_configure(columnspan=2)
        self.birthday = self._date_entry(right, "Birthday", details.get("birthday"), 4)
        self.gender = self._combo(
            right, "Gender", ["Male", "Female", "Other"],
            details.get("gender", ""), 4, 1,
        )
        self.department = self._combo(
            right, "Department", list(self.department_data.keys()),
            details.get("department", ""), 5, 0,
            command=self.update_courses,
        )
        self.course = self._combo(
            right, "Course", self.department_data.get(details.get("department", ""), []),
            details.get("course", ""), 5, 1,
        )
        self.address = self._textbox(right, "Address", details.get("address", ""), 6)
        ctk.CTkButton(
            card, text="Create" if account is None else "Update", width=130,
            height=38, fg_color=GREEN, text_color="black", corner_radius=8,
            command=self.save,
        ).grid(row=3, column=2, sticky="e", padx=28, pady=(0, 20))

    @staticmethod
    def _entry(parent, label, value="", row=0, column=0, masked=False):
        ctk.CTkLabel(parent, text=label, text_color=TEXT_BLUE).grid(
            row=row * 2, column=column, sticky="w", padx=4, pady=(4, 2)
        )
        entry = ctk.CTkEntry(
            parent, corner_radius=8, fg_color="#f3f4f6",
            text_color="black", show="*" if masked else "",
        )
        entry.grid(row=row * 2 + 1, column=column, sticky="ew", padx=4, pady=(0, 6))
        entry.insert(0, value)
        return entry

    @staticmethod
    def _combo(parent, label, values, value, row=0, column=0, command=None):
        ctk.CTkLabel(parent, text=label, text_color=TEXT_BLUE).grid(
            row=row * 2, column=column, sticky="w", padx=4, pady=(4, 2)
        )
        combo = ctk.CTkComboBox(
            parent, values=values, corner_radius=8, fg_color="#f3f4f6",
            text_color="black", button_color="#d1d5db", command=command,
            state="readonly",
        )
        combo.grid(row=row * 2 + 1, column=column, sticky="ew", padx=4, pady=(0, 6))
        combo.set(value)
        return combo

    @staticmethod
    def _date_entry(parent, label, value, row):
        ctk.CTkLabel(parent, text=label, text_color=TEXT_BLUE).grid(
            row=row * 2, column=0, sticky="w", padx=4, pady=(4, 2)
        )
        date_entry = DateEntry(
            parent, date_pattern="yyyy-mm-dd", width=16,
            background="#1e3a8a", foreground="white",
            borderwidth=1, relief="solid",
        )
        date_entry.grid(row=row * 2 + 1, column=0, sticky="ew", padx=4, pady=(0, 6))
        date_entry.delete(0, "end")
        if value:
            try:
                date_entry.set_date(value)
            except (TypeError, ValueError):
                date_entry.insert(0, str(value)[:10])
        return date_entry

    @staticmethod
    def _textbox(parent, label, value="", row=0):
        ctk.CTkLabel(parent, text=label, text_color=TEXT_BLUE).grid(
            row=row * 2, column=0, columnspan=2, sticky="w", padx=4, pady=(4, 2)
        )
        textbox = ctk.CTkTextbox(
            parent, height=75, corner_radius=8,
            fg_color="#f3f4f6", text_color="black",
        )
        textbox.grid(
            row=row * 2 + 1, column=0, columnspan=2,
            sticky="nsew", padx=4, pady=(0, 6),
        )
        textbox.insert("1.0", value or "")
        return textbox

    def update_courses(self, department=None):
        selected = department or self.department.get()
        courses = self.department_data.get(selected, [])
        self.course.configure(values=courses)
        if self.course.get() not in courses:
            self.course.set(courses[0] if courses else "")

    def toggle_password_visibility(self):
        show = "" if self.show_password.get() else "*"
        self.password.configure(show=show)

    def save(self):
        if not messagebox.askyesno(
            "Confirm Account Creation" if self.account is None else "Confirm Changes",
            "Are you sure you want to create this account?" if self.account is None else "Are you sure you want to save these changes?",
            parent=self.modal,
        ):
            return
        try:
            account_data = {
                "gmail": self.email.get(),
                "password": self.password.get(),
                "role": self.role.get(),
                "status": self.status.get(),
            }
            personal_data = {
                key: entry.get() for key, entry in self.personal_entries.items()
            }
            personal_data["birthday"] = self.birthday.get_date()
            personal_data["gender"] = self.gender.get()
            personal_data["department"] = self.department.get()
            personal_data["course"] = self.course.get()
            personal_data["address"] = self.address.get("1.0", "end-1c")
            if self.account is None:
                validate_new_account(account_data, personal_data)
                self.repository.add_user(account_data, personal_data)
            else:
                if account_data["password"].strip():
                    validate_password(account_data["password"])
                self.repository.update_user(
                    self.account["account_id"], account_data, personal_data
                )
            self.modal.destroy()
            self.on_changed()
        except (ValueError, Exception) as error:
            messagebox.showerror("Account Error", str(error), parent=self.modal)


class AdminPasswordModal:
    def __init__(self, parent, repository, account, on_changed=None):
        self.repository = repository
        self.account = account
        self.on_changed = on_changed or (lambda: None)
        self.modal = ctk.CTkToplevel(parent)
        self.modal.title("Change Password")
        self.modal.geometry("400x300")
        self.modal.configure(fg_color=MODAL_BG)
        self.modal.transient(parent)
        self.modal.grab_set()
        body = ctk.CTkFrame(self.modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=24)
        ctk.CTkLabel(body, text="Change Password", text_color=WHITE,
                     font=MODAL_TITLE_FONT).pack(anchor="w", pady=(0, 10))
        ctk.CTkLabel(body, text="New Password", text_color=WHITE).pack(anchor="w")
        self.password = ctk.CTkEntry(body, show="*", corner_radius=6,
                                     fg_color=WHITE, text_color="black")
        self.password.pack(fill="x", pady=(2, 12))
        ctk.CTkLabel(body, text="Re-enter Password", text_color=WHITE).pack(
            anchor="w"
        )
        self.confirm_password = ctk.CTkEntry(
            body, show="*", corner_radius=6, fg_color=WHITE, text_color="black"
        )
        self.confirm_password.pack(fill="x", pady=(2, 8))
        self.show_password = ctk.CTkCheckBox(
            body, text="Show Password", text_color=WHITE,
            command=self.toggle_password_visibility,
        )
        self.show_password.pack(anchor="w", pady=(0, 12))
        ctk.CTkButton(body, text="SAVE", height=36, fg_color=PURPLE,
                      corner_radius=6, command=self.save).pack(fill="x")

    def toggle_password_visibility(self):
        show = "" if self.show_password.get() else "*"
        self.password.configure(show=show)
        self.confirm_password.configure(show=show)

    def save(self):
        if not messagebox.askyesno(
            "Confirm Changes",
            "Are you sure you want to save these changes?",
            parent=self.modal,
        ):
            return
        try:
            if self.password.get() != self.confirm_password.get():
                raise ValueError("The passwords do not match.")
            validate_password(self.password.get())
            self.repository.change_password(self.account["account_id"], self.password.get())
            self.modal.destroy()
            self.on_changed()
        except (ValueError, Exception) as error:
            messagebox.showerror("Password Error", str(error), parent=self.modal)
