import os
from datetime import date, timedelta
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image
from tkcalendar import DateEntry
from models.users import Session
from repositories import (
    RequestRepository,
    InventoryRepository,
    borrow_due_date_bounds,
    validate_borrow_due_date,
)
from user_dashboard.components.details_modal import ViewDetailsModal

DARK_BLUE = "#1c3b7a"
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"
RED = "#ef4444"
MODAL_TITLE_FONT = ("Segoe UI", 22, "bold")
MODAL_FONT = ("Segoe UI", 12)


class ItemRequestModal:
    """Modal for requesting an item — compact two-column card layout."""

    def __init__(self, parent, item, on_requested=None):
        self.parent = parent
        self.item = item
        self.on_requested = on_requested

        self.modal = ctk.CTkToplevel(parent)
        self.modal.title("Item Request")
        self.modal.geometry("800x650")
        self.modal.configure(fg_color=DARK_BLUE)
        self.modal.transient(parent)
        self.modal.grab_set()
        self.modal.protocol("WM_DELETE_WINDOW", self.modal.destroy)

        self.modal.update_idletasks()
        x = (self.modal.winfo_screenwidth() // 2) - 400
        y = (self.modal.winfo_screenheight() // 2) - 225
        self.modal.geometry(f"+{x}+{y}")

        card = ctk.CTkFrame(
            self.modal,
            width=740,
            height=400,
            fg_color=WHITE,
            corner_radius=8,
            border_width=1,
            border_color="#d1d5db",
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            card, text="Item Request", text_color=TEXT_BLUE, font=MODAL_TITLE_FONT
        ).pack(anchor="w", padx=20, pady=(14, 8))

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 14))
        content.grid_columnconfigure(0, weight=0, minsize=220)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(content, fg_color="#f3f4f6", corner_radius=8)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_rowconfigure(0, weight=1)

        image_frame = ctk.CTkFrame(left, width=200, height=160, fg_color=WHITE, corner_radius=6)
        image_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 6))
        image_frame.grid_propagate(False)
        image_label = ctk.CTkLabel(
            image_frame, text="No image", text_color="black", font=("Arial", 10)
        )
        image_label.pack(expand=True)

        image_path = item.image_path
        if image_path and os.path.isfile(image_path):
            try:
                source = Image.open(image_path)
                req_image = ctk.CTkImage(light_image=source, dark_image=source, size=(170, 120))
                image_label.configure(image=req_image, text="")
                image_label.image = req_image
            except (OSError, ValueError):
                pass

        ctk.CTkLabel(
            left,
            text=item.item_name,
            text_color=TEXT_BLUE,
            font=("Arial", 13, "bold"),
            wraplength=200,
        ).grid(row=1, column=0, padx=10, pady=(2, 2))
        ctk.CTkLabel(
            left, text=f"Code: {item.item_code}", text_color="#4b5563", font=("Arial", 11)
        ).grid(row=2, column=0, padx=10, pady=(0, 10))

        right = ctk.CTkFrame(content, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(1, weight=1)

        fields_frame = ctk.CTkFrame(right, fg_color="transparent")
        fields_frame.pack(fill="x")
        fields_frame.grid_columnconfigure(0, weight=1)
        fields_frame.grid_columnconfigure(1, weight=2)

        detail_fields = [
            ("Item ID", item.item_id),
            ("Item Name", item.item_name),
            ("Item Code", item.item_code),
            ("Stock", item.stock),
            ("Updated Date", item.updated_date),
        ]
        field_row = 0
        for label, value in detail_fields:
            ViewDetailsModal._readonly_field(fields_frame, label, value, row=field_row)
            field_row += 1

        ViewDetailsModal._readonly_field(
            fields_frame,
            "Description",
            item.description or "No description available.",
            multiline=True,
            row=field_row,
            columnspan=2,
        )
        field_row += 1

        if item.expiration_date:
            ViewDetailsModal._readonly_field(
                fields_frame, "Expiration Date", item.expiration_date, row=field_row
            )
            field_row += 1

        if item.serial_no:
            ViewDetailsModal._readonly_field(
                fields_frame, "Serial No.", item.serial_no, row=field_row
            )
            field_row += 1

        ctk.CTkLabel(right, text="Quantity", text_color=TEXT_BLUE, font=MODAL_FONT).pack(
            anchor="w", pady=(4, 1)
        )
        validate_quantity = self.modal.register(self._validate_quantity)
        self.quantity_entry = ctk.CTkEntry(
            right,
            height=30,
            corner_radius=6,
            fg_color="#f3f4f6",
            text_color="black",
        )
        self.quantity_entry.configure(
            validate="key",
            validatecommand=(validate_quantity, "%P"),
        )
        self.quantity_entry.pack(fill="x", pady=(0, 4))
        self.quantity_entry.insert(0, "1")
        if item.category_name.strip().lower() in {"assets", "asset"}:
            self.quantity_entry.configure(state="disabled")

        self.due_date_entry = None
        if item.requires_return:
            ctk.CTkLabel(
                right,
                text="Due Date",
                text_color=TEXT_BLUE,
                font=MODAL_FONT,
            ).pack(anchor="w", pady=(4, 1))
            today = date.today()
            min_allowed = today + timedelta(days=7)
            max_allowed = today + timedelta(days=90)
            
            self.due_date_entry = DateEntry(
                right,
                width=18,
                date_pattern="yyyy-mm-dd",
                background=TEXT_BLUE,
                foreground=WHITE,
                borderwidth=1,
                mindate=min_allowed,
                maxdate=max_allowed,
            )
            self.due_date_entry.pack(fill="x", pady=(0, 6))
            self.due_date_entry.set_date(min_allowed)

            def on_cal_open(e):
                if e.widget == self.due_date_entry._top_cal:
                    self.modal.grab_release()

            def on_cal_close(e):
                if e.widget == self.due_date_entry._top_cal and self.modal.winfo_exists():
                    self.modal.grab_set()
                    self.modal.focus_set()

            self.due_date_entry._top_cal.bind("<Map>", on_cal_open, add="+")
            self.due_date_entry._top_cal.bind("<Unmap>", on_cal_close, add="+")

        ctk.CTkLabel(
            right, text="Unit/Serial No.", text_color=TEXT_BLUE, font=MODAL_FONT
        ).pack(anchor="w", pady=(4, 1))

        unit_options = []
        if item.unit:
            unit_values = [u.strip() for u in item.unit.split(",") if u.strip()]
            unit_options.extend(unit_values)
        if not unit_options:
            unit_options = ["Any"]

        self.unit_combo = ctk.CTkComboBox(
            right,
            height=30,
            corner_radius=6,
            fg_color="#f3f4f6",
            text_color="black",
            button_color=WHITE,
            values=unit_options if unit_options else ["Any"],
            state="readonly",
        )
        self.unit_combo.pack(fill="x", pady=(0, 6))
        self.unit_combo.set(unit_options[0])

        actions = ctk.CTkFrame(right, fg_color="transparent")
        actions.pack(fill="x", pady=(6, 0))
        actions.grid_columnconfigure((0, 1), weight=1)

        send_btn = ctk.CTkButton(
            actions,
            text="SEND REQUEST",
            height=34,
            command=self._send_request,
            fg_color="#22c55e",
            hover_color="#16a34a",
            corner_radius=6,
            font=("Arial", 13, "bold"),
        )
        send_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        ctk.CTkButton(
            actions,
            text="Cancel",
            height=34,
            command=self.modal.destroy,
            fg_color=RED,
            hover_color="#dc2626",
            corner_radius=6,
            font=("Arial", 12, "bold"),
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0))

    @staticmethod
    def _validate_quantity(proposed):
        return proposed == "" or (proposed.isdigit() and len(proposed) <= 2)

    def _send_request(self):
        qty_str = self.quantity_entry.get().strip()
        try:
            quantity = int(qty_str)
            if quantity <= 0:
                messagebox.showerror(
                    "Invalid Quantity",
                    "Quantity must be a positive integer.",
                    parent=self.modal,
                )
                return
        except ValueError:
            messagebox.showerror(
                "Invalid Quantity",
                "Quantity must contain digits only.",
                parent=self.modal,
            )
            return

        try:
            current_item = InventoryRepository().get_by_id(self.item.item_id)
        except Exception as error:
            messagebox.showerror(
                "Inventory Error",
                f"Could not verify the current stock: {error}",
                parent=self.modal,
            )
            return
        if not current_item or current_item.stock <= 0:
            messagebox.showwarning(
                "Out of Stock",
                f"'{self.item.item_name}' is currently out of stock and cannot be requested.",
                parent=self.modal,
            )
            return
        if current_item.is_expired:
            messagebox.showwarning(
                "Item Expired",
                f"'{self.item.item_name}' has expired and cannot be requested.",
                parent=self.modal,
            )
            return
        if current_item.is_expiring_soon():
            exp_date = current_item.expiration_date
            exp_str = (
                exp_date.strftime("%Y-%m-%d")
                if hasattr(exp_date, "strftime")
                else str(exp_date)[:10]
            )
            if not messagebox.askyesno(
                "Expiring Soon",
                f"'{self.item.item_name}' is expiring soon on {exp_str}. Continue to request?",
                parent=self.modal,
            ):
                return
        if quantity > current_item.stock:
            messagebox.showwarning(
                "Stock Unavailable",
                f"Only {current_item.stock} units are currently available in stock.",
                parent=self.modal,
            )
            return

        category = self.item.category_name.strip().lower()
        unit = self.unit_combo.get().strip().lower()
        due_date = None
        if self.item.requires_return:
            try:
                due_date = validate_borrow_due_date(self.due_date_entry.get_date())
            except ValueError as error:
                messagebox.showwarning("Invalid Due Date", str(error), parent=self.modal)
                return
        if category in {"assets", "asset"}:
            if quantity != 1:
                messagebox.showerror(
                    "Invalid Quantity",
                    "Assets can only be requested in a quantity of 1.",
                    parent=self.modal,
                )
                return
        elif category in {"consumables", "consumable"}:
            limit = 5 if unit == "pcs" else 1 if unit in {"box", "set", "unit"} else None
            if limit is None:
                messagebox.showerror(
                    "Invalid Unit",
                    "Select pcs, box, set, or unit for consumables.",
                    parent=self.modal,
                )
                return
            if quantity > limit:
                messagebox.showerror(
                    "Quantity Limit",
                    f"Consumable requests using '{unit}' are limited to {limit}.",
                    parent=self.modal,
                )
                return
        if not messagebox.askyesno(
            "Confirm Request",
            f"Request {quantity} unit(s) of '{self.item.item_name}'?",
            parent=self.modal,
        ):
            return
        try:
            current_user = Session.load() or {}
            RequestRepository().add_request(
                self.item.item_id, current_user.get("user_id", 1), quantity, due_date
            )

            messagebox.showinfo(
                "Success",
                f"Request for '{self.item.item_name}' has been submitted.",
                parent=self.parent,
            )
            self.modal.destroy()
            if self.on_requested:
                self.on_requested()

        except (ValueError, Exception) as e:
            messagebox.showerror("Error", f"Failed to submit request: {e}", parent=self.modal)
