import os
from datetime import date, datetime
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image
from tkcalendar import DateEntry
from models.users import Session

DARK_BLUE = "#1c3b7a"
MODAL_BG = "#0b1b42"
MODAL_FONT = ("Segoe UI", 12)
MODAL_TITLE_FONT = ("Segoe UI", 22, "bold")
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"
RED = "#ef4444"
GREEN = "#84cc16"
PURPLE = "#9333ea"


def _modal_field(parent, label, value="", height=36, disabled=False):
    ctk.CTkLabel(parent, text=label, text_color=WHITE, font=MODAL_FONT).pack(
        anchor="w", pady=(6, 2)
    )
    widget = ctk.CTkTextbox(parent, height=height, corner_radius=8) if height > 36 else \
        ctk.CTkEntry(parent, corner_radius=8)
    widget.configure(fg_color=WHITE, text_color="black")
    widget.pack(fill="x", pady=(0, 5))
    if height > 36:
        widget.insert("1.0", value)
    else:
        widget.insert(0, value)
    if disabled:
        widget.configure(state="disabled")
    return widget


def _field_value(widget):
    return widget.get("1.0", "end-1c") if isinstance(widget, ctk.CTkTextbox) else widget.get()


class RequestModal:
    def __init__(self, parent, request, repository, on_changed):
        self.parent = parent
        self.request = request
        self.repository = repository
        self.on_changed = on_changed
        self.modal = ctk.CTkToplevel(parent)
        self.modal.title("Item Request")
        self.modal.geometry("650x500")
        self.modal.configure(fg_color=MODAL_BG)
        self.modal.transient(parent)
        self.modal.grab_set()
        self.modal.protocol("WM_DELETE_WINDOW", self.modal.destroy)

        body = ctk.CTkFrame(self.modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=20)
        ctk.CTkLabel(body, text="Item Request", text_color=WHITE,
                     font=MODAL_TITLE_FONT).pack(anchor="w", pady=(0, 10))

        content = ctk.CTkFrame(body, fg_color="transparent")
        content.pack(fill="both", expand=True)
        content.grid_columnconfigure(0, weight=1, minsize=260)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)
        image_frame = ctk.CTkFrame(content, fg_color=WHITE, corner_radius=8)
        image_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        image_frame.pack_propagate(False)
        image_label = ctk.CTkLabel(image_frame, text="No image", text_color="black")
        image_label.pack(expand=True)
        image_path = request.get("image_path")
        if image_path and os.path.isfile(image_path):
            try:
                source = Image.open(image_path)
                image = ctk.CTkImage(light_image=source, dark_image=source, size=(180, 130))
                image_label.configure(image=image, text="")
                image_label.image = image
            except (OSError, ValueError):
                pass

        details = ctk.CTkScrollableFrame(content, fg_color=MODAL_BG)
        details.grid(row=0, column=1, sticky="nsew")
        user_fields = (
            ("Full Name", request.get("requester_name", "")),
            ("Student No.", request.get("student_id", "")),
            ("Department", request.get("department", "")),
            ("Course", request.get("course", "")),
            ("Address", request.get("address", ""), 55),
            ("Contact No.", request.get("contact_number", "")),
            ("Login Email", request.get("gmail", "")),
        )
        for field in user_fields:
            _modal_field(details, field[0], str(field[1]), height=field[2] if len(field) == 3 else 36, disabled=True)
        _modal_field(details, "Category", request.get("category_name", "N/A"), disabled=True)
        _modal_field(details, "Item ID", str(request.get("item_id", "")), disabled=True)
        _modal_field(details, "Item Details", request.get("item_description", ""), height=65, disabled=True)
        self.quantity = _modal_field(details, "Quantity/Serial No.", str(request.get("quantity", 1)))
        ctk.CTkLabel(details, text="Due Date", text_color=WHITE, font=MODAL_FONT).pack(
            anchor="w", pady=(6, 2)
        )
        self.due_date_entry = DateEntry(
            details,
            width=18,
            date_pattern="yyyy-mm-dd",
            background=TEXT_BLUE,
            foreground=WHITE,
            borderwidth=1,
        )
        self.due_date_entry.pack(fill="x", pady=(0, 6))
        req_due = request.get("due_date")
        if req_due:
            if isinstance(req_due, (datetime, date)):
                self.due_date_entry.set_date(req_due)
            else:
                try:
                    self.due_date_entry.set_date(datetime.strptime(str(req_due)[:10], "%Y-%m-%d").date())
                except Exception:
                    pass
        self.status = ctk.CTkComboBox(
            details, values=["Pending", "Approved", "Cancelled", "Returned"],
            fg_color=WHITE, text_color="black", button_color=WHITE, corner_radius=8,
            state="readonly",
        )
        ctk.CTkLabel(details, text="Unit/Status", text_color=WHITE, font=MODAL_FONT).pack(
            anchor="w", pady=(6, 2)
        )
        self.status.pack(fill="x", pady=(0, 10))
        self.status.set(request.get("request_status", "Pending"))
        self.confirm_button = ctk.CTkButton(
            details, text="", height=40, fg_color=GREEN,
            text_color="black", corner_radius=6, command=self.confirm_lifecycle,
        )
        self.confirm_button.pack(fill="x", pady=(0, 8))
        self._update_confirm_button()

        actions = ctk.CTkFrame(details, fg_color="transparent")
        actions.pack(fill="x", pady=(5, 8))
        for column in range(4):
            actions.grid_columnconfigure(column, weight=1, uniform="request_action")
        ctk.CTkButton(actions, text="UPDATE", height=35, fg_color="#f59e0b",
                      text_color="black", corner_radius=6,
                      command=self.save_edits).grid(row=0, column=0, sticky="ew", padx=2)
        ctk.CTkButton(actions, text="CANCEL", height=35, fg_color="#dc2626",
                      text_color="white", corner_radius=6,
                      command=self._show_cancel_modal).grid(row=0, column=1, sticky="ew", padx=2)
        ctk.CTkButton(actions, text="DELETE", height=35, fg_color=RED,
                      corner_radius=6, command=self.delete).grid(row=0, column=2, sticky="ew", padx=2)
        ctk.CTkButton(actions, text="NOTIFY", height=35, fg_color=PURPLE,
                      corner_radius=6, command=lambda: NotifyModal(self.modal, request, repository)
                      ).grid(row=0, column=3, sticky="ew", padx=2)
    
    def _update_confirm_button(self):
        labels = {
            "Pending": "CONFIRM REQUEST",
            "Approved": "CONFIRM RECEIVED ITEM",
            "Active": "CONFIRM RETURN",
            "Return Requested": "CONFIRM RETURN",
        }
        self.confirm_button.configure(
            text=labels.get(self.request.get("request_status"), "CONFIRM REQUEST")
        )

    def save_edits(self):
        if not messagebox.askyesno("Update Request", "Are you sure you want to update this request?", parent=self.modal):
            return
        try:
            self.request["quantity"] = int(self.quantity.get())
            if hasattr(self, "due_date_entry"):
                self.request["due_date"] = self.due_date_entry.get_date()
            new_status = self.status.get()
            if new_status == "Cancelled" and self.request.get("request_status") != "Cancelled":
                self._show_cancel_modal()
                return
            self.request["request_status"] = new_status
            self.repository.update(self.request)
            self.on_changed()
            messagebox.showinfo("Request Updated", "Request details were updated.", parent=self.modal)
        except (ValueError, Exception) as error:
            messagebox.showerror("Request Error", str(error), parent=self.modal)

    def _show_cancel_modal(self):
        cancel_modal = ctk.CTkToplevel(self.modal)
        cancel_modal.title("Cancel Item Request")
        cancel_modal.geometry("480x280")
        cancel_modal.resizable(False, False)
        cancel_modal.configure(fg_color=MODAL_BG)
        cancel_modal.transient(self.modal)
        cancel_modal.grab_set()

        body = ctk.CTkFrame(cancel_modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=24)
        ctk.CTkLabel(
            body, text="Cancel Item Request", text_color=WHITE,
            font=MODAL_TITLE_FONT,
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(
            body, text="Cancellation Reason:", text_color=WHITE,
            font=MODAL_FONT,
        ).pack(anchor="w", pady=(0, 4))
        reason_box = ctk.CTkTextbox(
            body, height=80, fg_color=WHITE, text_color="black", corner_radius=8,
        )
        reason_box.pack(fill="x", pady=(0, 16))

        def submit_cancel():
            reason_text = reason_box.get("1.0", "end-1c").strip()
            if not reason_text:
                messagebox.showwarning(
                    "Validation", "Cancellation reason is required.", parent=cancel_modal
                )
                return
            if not messagebox.askyesno(
                "Cancel Request",
                f"Cancel this item request with reason:\n\n'{reason_text}'?",
                parent=cancel_modal,
            ):
                return
            try:
                changed = self.repository.cancel(
                    self.request["request_id"],
                    reason=reason_text,
                )
                if not changed:
                    raise ValueError("The request could not be cancelled.")
                cancel_modal.destroy()
                self.modal.destroy()
                self.on_changed()
                messagebox.showinfo(
                    "Request Cancelled",
                    "The item request has been cancelled and logged into transactions.",
                    parent=self.parent,
                )
            except (ValueError, Exception) as error:
                messagebox.showerror("Cancellation Error", str(error), parent=cancel_modal)

        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(fill="x")
        btn_row.grid_columnconfigure((0, 1), weight=1, uniform="cancel_btn")
        ctk.CTkButton(
            btn_row, text="Back", height=36, fg_color=TEXT_BLUE, corner_radius=8,
            command=cancel_modal.destroy,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkButton(
            btn_row, text="Confirm Cancel", height=36, fg_color=RED, corner_radius=8,
            command=submit_cancel,
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def delete(self):
        if not messagebox.askyesno("Delete Request", "Delete this request?", parent=self.modal):
            return
        try:
            self.repository.delete(self.request["request_id"])
            self.modal.destroy()
            self.on_changed()
        except (ValueError, Exception) as error:
            messagebox.showerror("Request Error", str(error), parent=self.modal)

    def approve(self):
        if not messagebox.askyesno("Confirm Request", "Approve this request?", parent=self.modal):
            return
        try:
            self.repository.approve(self.request["request_id"])
            self.modal.destroy()
            self.on_changed()
        except Exception as error:
            messagebox.showerror("Request Error", str(error), parent=self.modal)

    def confirm_lifecycle(self):
        status = self.request.get("request_status")
        if status in {"Active", "Return Requested"}:
            self._show_return_condition_modal()
            return
        if not messagebox.askyesno(
            "Confirm Request", "Confirm this request transition?", parent=self.modal
        ):
            return
        try:
            current_user = Session.load() or {}
            if status == "Pending":
                changed = self.repository.approve(self.request["request_id"])
            elif status == "Approved":
                changed = self.repository.confirm_pickup(
                    self.request["request_id"],
                    current_user.get("user_id", 1),
                    self.request["item_id"],
                    int(self.request["quantity"]),
                )
            else:
                changed = False
            if not changed:
                raise ValueError("The request could not be updated.")
            self.modal.destroy()
            self.on_changed()
        except (ValueError, Exception) as error:
            messagebox.showerror("Request Error", str(error), parent=self.modal)

    def _show_return_condition_modal(self):
        condition_modal = ctk.CTkToplevel(self.modal)
        condition_modal.title("Confirm Return")
        condition_modal.geometry("500x300")
        condition_modal.resizable(False, False)
        condition_modal.configure(fg_color=MODAL_BG)
        condition_modal.transient(self.modal)
        condition_modal.grab_set()

        body = ctk.CTkFrame(condition_modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=24)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            body, text="Return Condition", text_color=WHITE,
            font=MODAL_TITLE_FONT,
        ).pack(anchor="w", pady=(0, 12))
        fields = ctk.CTkFrame(body, fg_color="transparent")
        fields.pack(fill="x", pady=(0, 16))
        fields.grid_columnconfigure((0, 1), weight=1, uniform="condition_field")
        ctk.CTkLabel(
            fields, text="Condition Status", text_color=WHITE, font=MODAL_FONT,
        ).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 4))
        condition = ctk.CTkComboBox(
            fields, values=["Good", "Damaged", "Needs Repair", "Lost"],
            fg_color=WHITE, text_color="black", button_color=WHITE,
            corner_radius=8, state="readonly",
        )
        condition.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        condition.set("Good")
        ctk.CTkLabel(
            fields, text="Condition Notes", text_color=WHITE, font=MODAL_FONT,
        ).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=(0, 4))
        notes = ctk.CTkTextbox(
            fields, height=90, fg_color=WHITE, text_color="black", corner_radius=8,
        )
        notes.grid(row=1, column=1, sticky="ew", padx=(10, 0))

        def submit():
            condition_value = condition.get().strip()
            notes_value = notes.get("1.0", "end-1c").strip()
            if not condition_value or not notes_value:
                messagebox.showwarning(
                    "Validation",
                    "Condition status and notes are required.",
                    parent=condition_modal,
                )
                return
            if not messagebox.askyesno(
                "Confirm Return",
                (
                    "Finalize this return?\n\n"
                    f"Condition: {condition_value}\n"
                    f"Notes: {notes_value}\n\n"
                    "This will complete the return transaction."
                ),
                parent=condition_modal,
            ):
                return
            try:
                current_user = Session.load() or {}
                changed = self.repository.confirm_return(
                    self.request["request_id"],
                    current_user.get("user_id", 1),
                    self.request["item_id"],
                    int(self.request["quantity"]),
                    condition_value,
                    notes_value,
                )
                if not changed:
                    raise ValueError("The return could not be completed.")
                condition_modal.destroy()
                self.modal.destroy()
                self.on_changed()
            except (ValueError, Exception) as error:
                messagebox.showerror("Return Error", str(error), parent=condition_modal)

        actions = ctk.CTkFrame(body, fg_color="transparent")
        actions.pack(fill="x")
        actions.grid_columnconfigure((0, 1), weight=1, uniform="return_action")
        ctk.CTkButton(
            actions, text="Cancel", height=36, fg_color=RED,
            command=condition_modal.destroy,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(
            actions, text="Submit Return", height=36, fg_color=GREEN,
            text_color="black", command=submit,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))


class NotifyModal:
    def __init__(self, parent, request, repository):
        self.parent = parent
        self.repository = repository
        self.request = request
        self.modal = ctk.CTkToplevel(parent)
        self.modal.title("Send Notification")
        self.modal.geometry("450x300")
        self.modal.configure(fg_color=MODAL_BG)
        self.modal.transient(parent)
        self.modal.grab_set()
        body = ctk.CTkFrame(self.modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=24)
        recipient = request.get("requester_name") or request.get("gmail", "Unknown user")
        ctk.CTkLabel(body, text=f"To: {recipient}", text_color=WHITE,
                     font=MODAL_FONT).pack(anchor="w", pady=(0, 12))
        self.message = ctk.CTkTextbox(body, height=130, corner_radius=8,
                                      fg_color=WHITE, text_color="black")
        self.message.pack(fill="both", expand=True, pady=(0, 15))
        ctk.CTkButton(body, text="SEND", height=38, fg_color=PURPLE,
                      corner_radius=6, command=self.send).pack(fill="x")

    def send(self):
        try:
            self.repository.notify(self.request["requester_id"], _field_value(self.message))
            self.modal.destroy()
            messagebox.showinfo("Notification Sent", "The notification was sent.", parent=self.parent)
        except (ValueError, Exception) as error:
            messagebox.showerror("Notification Error", str(error), parent=self.modal)
