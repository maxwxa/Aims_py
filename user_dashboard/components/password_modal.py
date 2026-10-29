from tkinter import messagebox
import customtkinter as ctk
from repositories import UserRepository

MODAL_BG = "#0b1b42"
MODAL_TITLE_FONT = ("Segoe UI", 22, "bold")
MODAL_FONT = ("Segoe UI", 12)
TEXT_BLUE = "#1e3a8a"
WHITE = "#ffffff"
GREEN = "#84cc16"
BLUE = "#1d4ed8"


class PasswordModal:
    def __init__(self, parent, user_id):
        self.parent = parent
        self.user_id = user_id
        self.modal = ctk.CTkToplevel(parent)
        self.modal.title("Change Password")
        self.modal.geometry("350x400")
        self.modal.configure(fg_color=MODAL_BG)
        self.modal.transient(parent)
        self.modal.grab_set()
        body = ctk.CTkFrame(self.modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=24)
        ctk.CTkLabel(
            body, text="Change Password", text_color=WHITE, font=MODAL_TITLE_FONT
        ).pack(anchor="w", pady=(0, 12))
        self.old = self._entry(body, "Old Password")
        self.new = self._entry(body, "New Password")
        self.confirm = self._entry(body, "Re-enter New Password")
        self.show_password = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            body,
            text="Show password",
            variable=self.show_password,
            command=self._toggle_password_visibility,
            text_color=WHITE,
            fg_color=BLUE,
            hover_color="#1e40af",
            corner_radius=4,
        ).pack(anchor="w", pady=(10, 0))
        ctk.CTkButton(
            body,
            text="SAVE",
            height=38,
            fg_color=GREEN,
            text_color="black",
            corner_radius=6,
            command=self.save,
        ).pack(fill="x", pady=(14, 0))

    def _entry(self, parent, label):
        ctk.CTkLabel(parent, text=label, text_color=TEXT_BLUE, font=MODAL_FONT).pack(
            anchor="w", pady=(5, 2)
        )
        entry = ctk.CTkEntry(
            parent, show="*", corner_radius=6, fg_color=WHITE, text_color="black"
        )
        entry.pack(fill="x")
        return entry

    def _toggle_password_visibility(self):
        show = "" if self.show_password.get() else "*"
        for entry in (self.old, self.new, self.confirm):
            entry.configure(show=show)

    def save(self):
        old, new, confirm = self.old.get(), self.new.get(), self.confirm.get()
        try:
            repository = UserRepository()
            if not repository.verify_password(self.user_id, old):
                raise ValueError("The old password is incorrect.")
            if new != confirm:
                raise ValueError("The new passwords do not match.")
            repository.change_password(self.user_id, new)
            self.modal.destroy()
            messagebox.showinfo(
                "Password Updated", "Your password was changed.", parent=self.parent
            )
        except (ValueError, Exception) as error:
            messagebox.showerror("Password Error", str(error), parent=self.modal)
