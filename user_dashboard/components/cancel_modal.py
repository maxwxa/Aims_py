from tkinter import messagebox
import customtkinter as ctk
from repositories import RequestRepository

MODAL_BG = "#0b1b42"
MODAL_FONT = ("Segoe UI", 12)
MODAL_TITLE_FONT = ("Segoe UI", 22, "bold")
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"
RED = "#ef4444"


class CancelConfirmationModal:
    """Modal for confirming request cancellation."""

    def __init__(self, parent, request_id, item_name, status="Pending", on_cancelled=None):
        self.parent = parent
        self.request_id = request_id
        self.item_name = item_name
        self.status = status
        self.on_cancelled = on_cancelled
        self.modal = ctk.CTkToplevel(parent)
        self.modal.title("Cancel Request")
        self.modal.geometry("450x330")
        self.modal.configure(fg_color=MODAL_BG)
        self.modal.transient(parent)
        self.modal.grab_set()
        self.modal.protocol("WM_DELETE_WINDOW", lambda: None)

        self.modal.update_idletasks()
        x = (self.modal.winfo_screenwidth() // 2) - 225
        y = (self.modal.winfo_screenheight() // 2) - 150
        self.modal.geometry(f"+{x}+{y}")

        body = ctk.CTkFrame(self.modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=(24, 20))

        ctk.CTkLabel(
            body,
            text="Cancel Request",
            text_color=WHITE,
            font=MODAL_TITLE_FONT,
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(
            body,
            text=f"Are you sure you want to cancel your request for '{self.item_name}'?",
            text_color="#bfdbfe",
            font=MODAL_FONT,
            wraplength=380,
        ).pack(anchor="w", pady=(0, 20))
        if self.status == "Approved":
            ctk.CTkLabel(
                body,
                text="Cancellation reason (required):",
                text_color=WHITE,
                font=MODAL_FONT,
            ).pack(anchor="w", pady=(0, 4))
            self.reason = ctk.CTkTextbox(
                body,
                height=75,
                corner_radius=6,
                fg_color=WHITE,
                text_color="black",
            )
            self.reason.pack(fill="x", pady=(0, 10))

        actions = ctk.CTkFrame(body, fg_color="transparent")
        actions.pack(fill="x", pady=(20, 0))
        actions.grid_columnconfigure((0, 1), weight=1, uniform="action")

        ctk.CTkButton(
            actions,
            text="No",
            width=120,
            height=40,
            command=self.modal.destroy,
            fg_color=TEXT_BLUE,
            corner_radius=8,
            font=("Arial", 12, "bold"),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkButton(
            actions,
            text="Yes, Cancel",
            width=120,
            height=40,
            command=self._confirm_cancel,
            fg_color=RED,
            corner_radius=8,
            font=("Arial", 12, "bold"),
        ).grid(row=0, column=1, sticky="ew", padx=(10, 0))

    def _confirm_cancel(self):
        """Handle cancel confirmation."""
        try:
            reason = ""
            if self.status == "Approved":
                reason = self.reason.get("1.0", "end-1c").strip()
                if not reason:
                    messagebox.showerror(
                        "Cancellation Reason",
                        "Please provide a reason for cancelling the accepted request.",
                        parent=self.modal,
                    )
                    return
            RequestRepository().cancel(self.request_id, reason)
            messagebox.showinfo(
                "Cancelled",
                f"Your request for '{self.item_name}' has been cancelled.",
                parent=self.parent,
            )
            self.modal.destroy()
            if self.on_cancelled:
                self.on_cancelled()
        except (ValueError, Exception) as error:
            messagebox.showerror("Request Error", str(error), parent=self.modal)
