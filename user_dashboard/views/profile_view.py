from tkinter import messagebox
import customtkinter as ctk
from models.users import Session
from repositories import UserRepository
from user_dashboard.components.password_modal import PasswordModal

DARK_BLUE = "#1c3b7a"
BG_BLUE = "#eef2ff"
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"
RED = "#ef4444"
MODAL_FONT = ("Segoe UI", 12)


class ProfileView(ctk.CTkFrame):
    def __init__(self, parent, app=None):
        super().__init__(
            parent, fg_color=DARK_BLUE, corner_radius=8, border_width=1, border_color="#d1d5db"
        )
        self.app = app or self.winfo_toplevel()
        self._build_view()

    def _build_view(self):
        body = ctk.CTkScrollableFrame(self, fg_color=BG_BLUE, corner_radius=8)
        body.pack(fill="both", expand=True, padx=20, pady=20)
        body.grid_columnconfigure((0, 1), weight=1, uniform="profile")

        current_user = Session.load() or {}
        user_id = current_user.get("user_id", 1)
        try:
            profile = UserRepository().get_by_id(user_id) or {}
        except Exception as error:
            messagebox.showerror("Profile Unavailable", str(error), parent=self.app)
            profile = dict(current_user)

        left = ctk.CTkFrame(
            body, fg_color=WHITE, corner_radius=8, border_width=1, border_color="#d1d5db"
        )
        right = ctk.CTkFrame(
            body, fg_color=WHITE, corner_radius=8, border_width=1, border_color="#d1d5db"
        )
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)

        ctk.CTkLabel(
            left, text="Account Information", text_color=TEXT_BLUE, font=("Arial", 18, "bold")
        ).pack(anchor="w", padx=20, pady=(18, 8))

        fields = [
            ("Account No.", profile.get("user_id", current_user.get("user_id", ""))),
            ("Account Role", profile.get("role", current_user.get("role", ""))),
            ("Email", profile.get("gmail", current_user.get("gmail", ""))),
            ("Account Status", profile.get("status", "Active")),
            ("Account Created Date", profile.get("creationdate", "")),
        ]
        for label, value in fields:
            self._profile_entry(left, label, value)

        ctk.CTkButton(
            left,
            text="Change Password",
            height=36,
            fg_color=RED,
            corner_radius=6,
            command=lambda: PasswordModal(self.app, user_id),
        ).pack(fill="x", padx=20, pady=(12, 20))

        ctk.CTkLabel(
            right, text="Personal Information", text_color=TEXT_BLUE, font=("Arial", 18, "bold")
        ).pack(anchor="w", padx=20, pady=(18, 8))

        personal = [
            ("First Name", profile.get("first_name", "")),
            ("Middle Name", profile.get("middle_name", "")),
            ("Last Name", profile.get("last_name", "")),
            ("Contact No.", profile.get("contact_number", "")),
            ("Gender", profile.get("gender", "")),
            ("Student No.", profile.get("student_id", "")),
            ("Department", profile.get("department", "")),
            ("Course", profile.get("course", "")),
        ]
        for label, value in personal:
            self._profile_entry(right, label, value)

        ctk.CTkLabel(
            right, text="Address", text_color=TEXT_BLUE, font=MODAL_FONT
        ).pack(anchor="w", padx=20, pady=(6, 2))
        address = ctk.CTkTextbox(
            right, height=55, corner_radius=6, fg_color="#f3f4f6", text_color="black"
        )
        address.pack(fill="x", padx=20, pady=(0, 18))
        address.insert("1.0", profile.get("address", ""))
        address.configure(state="disabled")

    @staticmethod
    def _profile_entry(parent, label, value):
        ctk.CTkLabel(parent, text=label, text_color=TEXT_BLUE, font=MODAL_FONT).pack(
            anchor="w", padx=20, pady=(4, 2)
        )
        entry = ctk.CTkEntry(
            parent, height=30, corner_radius=6, fg_color="#f3f4f6", text_color="black"
        )
        entry.pack(fill="x", padx=20, pady=(0, 3))
        entry.insert(0, str(value or ""))
        entry.configure(state="disabled")
