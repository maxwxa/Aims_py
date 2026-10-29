import os
import subprocess
import sys
import customtkinter as ctk
from models.users import Session

MODAL_BG = "#0b1b42"
MODAL_FONT = ("Segoe UI", 12)
MODAL_TITLE_FONT = ("Segoe UI", 22, "bold")
WHITE = "#ffffff"
RED = "#ef4444"
GREEN = "#84cc16"


class LogoutConfirmationModal:
    """Modal for confirming logout action."""

    def __init__(self, parent):
        self.parent = parent
        self.modal = ctk.CTkToplevel(parent)
        self.modal.title("Confirm Logout")
        self.modal.geometry("350x200")
        self.modal.configure(fg_color=MODAL_BG)
        self.modal.transient(parent)
        self.modal.grab_set()
        self.modal.protocol("WM_DELETE_WINDOW", self.modal.destroy)

        self.modal.update_idletasks()
        x = (self.modal.winfo_screenwidth() // 2) - 200
        y = (self.modal.winfo_screenheight() // 2) - 150
        self.modal.geometry(f"+{x}+{y}")

        body = ctk.CTkFrame(self.modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=(24, 20))

        ctk.CTkLabel(
            body,
            text="Log Out",
            text_color=WHITE,
            font=MODAL_TITLE_FONT,
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(
            body,
            text="Are you sure you want to log out?",
            text_color="#bfdbfe",
            font=MODAL_FONT,
        ).pack(anchor="w", pady=(0, 20))

        actions = ctk.CTkFrame(body, fg_color="transparent")
        actions.pack(fill="x", pady=(20, 0))
        actions.grid_columnconfigure((0, 1), weight=1, uniform="action")

        ctk.CTkButton(
            actions,
            text="No",
            width=120,
            height=40,
            command=self.modal.destroy,
            fg_color=RED,
            corner_radius=8,
            font=("Arial", 12, "bold"),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkButton(
            actions,
            text="Yes",
            width=120,
            height=40,
            command=self._confirm_logout,
            fg_color=GREEN,
            corner_radius=8,
            font=("Arial", 12, "bold"),
        ).grid(row=0, column=1, sticky="ew", padx=(10, 0))

    def _confirm_logout(self):
        """Handle logout confirmation."""
        self.modal.destroy()
        Session.clear()
        self.parent.destroy()
        subprocess.Popen([
            sys.executable,
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "main.py"),
        ])
