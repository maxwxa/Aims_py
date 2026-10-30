from tkinter import messagebox
import customtkinter as ctk
from repositories import TransactionRepository

BG_BLUE = "#eef2ff"
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"
GREEN = "#84cc16"
RED = "#ef4444"
MODAL_BG = "#0b1b42"
MODAL_FONT = ("Segoe UI", 12)
MODAL_TITLE_FONT = ("Segoe UI", 22, "bold")


class TransactionsView(ctk.CTkFrame):
    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color=BG_BLUE, corner_radius=0)
        self.app = app or self.winfo_toplevel()
        self.repository = TransactionRepository()
        self.state = {"mode": "current", "selected": None, "widgets": []}
        self.current_page = 1
        self.items_per_page = 50
        self._build_view()
        self.update_actions()
        self.load_rows()

    def _build_view(self):
        header = ctk.CTkFrame(self, height=45, fg_color="#1c3b7a", corner_radius=8)
        header.pack(fill="x", padx=20, pady=(20, 0))
        header.pack_propagate(False)
        ctk.CTkLabel(
            header, text="Transactions", text_color=WHITE, font=("Arial", 16, "bold")
        ).pack(side="left", padx=15)

        self.toggle = ctk.CTkButton(
            header,
            text="ARCHIVE",
            width=90,
            height=30,
            fg_color="#507ace",
            hover_color="#254b91",
            corner_radius=6,
            command=self.switch_mode,
        )
        self.toggle.pack(side="left", padx=10)

        toolbar = ctk.CTkFrame(header, fg_color="transparent")
        toolbar.pack(side="right", padx=20)
        ctk.CTkButton(
            toolbar,
            text="Refresh",
            width=80,
            height=30,
            fg_color=WHITE,
            text_color="#1c3b7a",
            corner_radius=6,
            command=self.refresh,
        ).pack(side="left", padx=5)

        self.filter_combo = ctk.CTkComboBox(
            toolbar,
            width=120,
            height=30,
            values=["All", "Cancelled", "Returned"],
            fg_color=WHITE,
            text_color="black",
            button_color=WHITE,
            corner_radius=6,
            state="readonly",
        )
        self.filter_combo.set("All")
        self.filter_combo.pack(side="left", padx=5)
        self.filter_combo.configure(command=lambda _value=None: self.load_rows())

        self.search = ctk.CTkEntry(
            toolbar,
            width=150,
            height=30,
            fg_color=WHITE,
            text_color="black",
            corner_radius=6,
            placeholder_text="Search",
        )
        self.search.pack(side="left", padx=5)
        self.search.bind("<KeyRelease>", lambda _event=None: self.load_rows())

        self.table = ctk.CTkScrollableFrame(self, fg_color=WHITE, corner_radius=8)
        self.table.pack(fill="both", expand=True, padx=20, pady=20)
        widths = [100, 130, 250, 130, 150, 150, 150]
        for index, width in enumerate(widths):
            self.table.grid_columnconfigure(index, weight=1 if index == 2 else 0, minsize=width)
        for index, title in enumerate(
            [
                "Track No.",
                "Requested Item No.",
                "Transaction Details",
                "Request Status",
                "Approved By",
                "Received By",
                "Date/Time",
            ]
        ):
            ctk.CTkLabel(
                self.table,
                text=title,
                fg_color="#dbeafe",
                text_color=TEXT_BLUE,
                font=("Arial", 11, "bold"),
                anchor="w",
            ).grid(row=0, column=index, sticky="ew", padx=1, pady=1)

        self.actions = ctk.CTkFrame(self, fg_color="transparent")
        self.actions.pack(fill="x", padx=20, pady=(0, 20))
        self.current_button = ctk.CTkButton(
            self.actions,
            text="ARCHIVED",
            height=36,
            fg_color=GREEN,
            text_color="black",
            corner_radius=6,
            command=lambda: self.confirm_action(
                "Archive Transaction",
                "Archive this transaction?",
                self.repository.archiveTransaction,
            ),
        )
        self.restore_button = ctk.CTkButton(
            self.actions,
            text="RESTORE",
            height=36,
            fg_color=GREEN,
            text_color="black",
            corner_radius=6,
            command=lambda: self.confirm_action(
                "Restore Transaction",
                "Restore this transaction?",
                self.repository.restoreTransaction,
            ),
        )
        self.delete_button = ctk.CTkButton(
            self.actions,
            text="DELETE",
            height=36,
            fg_color=RED,
            corner_radius=6,
            command=lambda: self.confirm_action(
                "Delete Transaction",
                "Delete this archived transaction?",
                self.repository.delete,
            ),
        )

        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pagination_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.btn_prev = ctk.CTkButton(self.pagination_frame, text="<< Previous", width=100, fg_color="#1d4ed8", command=self.prev_page)
        self.btn_prev.pack(side="left")
        
        self.lbl_page = ctk.CTkLabel(self.pagination_frame, text="Page 1 of 1", font=("Arial", 14, "bold"), text_color="#1e3a8a")
        self.lbl_page.pack(side="left", expand=True)
        
        self.btn_next = ctk.CTkButton(self.pagination_frame, text="Next >>", width=100, fg_color="#1d4ed8", command=self.next_page)
        self.btn_next.pack(side="right")

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_rows()

    def next_page(self):
        self.current_page += 1
        self.load_rows()

    def refresh(self):
        self.load_rows()

    def select(self, row, widgets):
        for widget in self.state["widgets"]:
            widget.configure(fg_color=WHITE)
        self.state["selected"] = row
        self.state["widgets"] = widgets
        for widget in widgets:
            widget.configure(fg_color="#bfdbfe")

    def load_rows(self):
        for widget in self.table.winfo_children():
            if int(widget.grid_info().get("row", 0)) > 0:
                widget.destroy()
        self.state["selected"] = None
        self.state["widgets"] = []
        try:
            rows = self.repository.get_all(self.state["mode"])
        except (ValueError, Exception) as error:
            messagebox.showerror("Transactions Unavailable", str(error), parent=self.app)
            return

        filter_value = self.filter_combo.get()
        term = self.search.get().strip().lower()
        
        filtered_rows = []
        for row in rows:
            text = " ".join(str(value or "") for value in row.values()).lower()
            if filter_value != "All" and row.get("transaction_type") != filter_value:
                continue
            if term and term not in text:
                continue
            filtered_rows.append(row)

        total_items = len(filtered_rows)
        total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > total_pages:
            self.current_page = 1
            
        self.lbl_page.configure(text=f"Page {self.current_page} of {total_pages} (Total: {total_items})")
        self.btn_prev.configure(state="normal" if self.current_page > 1 else "disabled")
        self.btn_next.configure(state="normal" if self.current_page < total_pages else "disabled")

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        display_items = filtered_rows[start_idx:end_idx]

        row_index = 1
        for row in display_items:
            date_value = row.get("transaction_date")
            is_cancelled = (
                str(row.get("transaction_type", "")).strip().lower() == "cancelled"
                or str(row.get("request_status", "")).strip().lower() == "cancelled"
            )
            received_by = (
                "N/A"
                if is_cancelled
                else (row.get("requester_name") or row.get("confirmed_by_name") or "N/A")
            )
            values = [
                f"TRX-{row['transaction_id']}",
                f"REQ-{row['request_id']}",
                f"{row.get('transaction_type', '')}: {row.get('item_name', '')} "
                f"x{row.get('quantity', 0)}",
                row.get("request_status", ""),
                row.get("approved_by_name") or "N/A",
                received_by,
                date_value.strftime("%Y-%m-%d %H:%M") if date_value else "",
            ]
            widgets = []
            for column, value in enumerate(values):
                label = ctk.CTkLabel(
                    self.table,
                    text=str(value),
                    fg_color=WHITE,
                    text_color="black",
                    anchor="w",
                    wraplength=240,
                )
                label.grid(row=row_index, column=column, sticky="ew", padx=1, pady=1)
                label.bind(
                    "<Button-1>",
                    lambda _event=None, item=row, cells=widgets: self.select(item, cells),
                )
                label.bind(
                    "<Double-Button-1>",
                    lambda _event=None, item=row: self.show_transaction_details(item),
                )
                widgets.append(label)
            row_index += 1

    def show_transaction_details(self, row):
        try:
            transaction = self.repository.get_details(row["transaction_id"], self.state["mode"])
        except (ValueError, Exception) as error:
            messagebox.showerror("Transaction Details Unavailable", str(error), parent=self.app)
            return
        if transaction is None:
            messagebox.showerror(
                "Transaction Details Unavailable",
                "The selected transaction could not be found.",
                parent=self.app,
            )
            return

        modal = ctk.CTkToplevel(self.app)
        modal.title("Transaction Details")
        modal.geometry("680x720")
        modal.minsize(520, 500)
        modal.configure(fg_color=MODAL_BG)
        modal.transient(self.app)
        modal.grab_set()

        body = ctk.CTkScrollableFrame(modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=(24, 12))

        ctk.CTkLabel(
            body,
            text="Transaction Details",
            text_color=WHITE,
            font=MODAL_TITLE_FONT,
        ).pack(anchor="w", pady=(0, 12))

        def add_section(title, fields):
            ctk.CTkLabel(
                body,
                text=title,
                text_color="#93c5fd",
                font=("Arial", 14, "bold"),
            ).pack(anchor="w", pady=(10, 4))
            for label, key in fields:
                value = key(transaction) if callable(key) else transaction.get(key)
                if value is None or value == "":
                    value = "N/A"
                ctk.CTkLabel(
                    body,
                    text=f"{label}: {value}",
                    text_color=WHITE,
                    font=MODAL_FONT,
                    anchor="w",
                    justify="left",
                    wraplength=590,
                ).pack(fill="x", pady=2)

        add_section(
            "Transaction",
            [
                ("Transaction ID", lambda details: f"TRX-{details.get('transaction_id', 'N/A')}"),
                ("Request ID", lambda details: f"REQ-{details.get('request_id', 'N/A')}"),
                ("Type", "transaction_type"),
                ("Quantity", "quantity"),
                ("Condition Status", "condition_status"),
                ("Condition Notes", "condition_notes"),
                ("Transaction Date", "transaction_date"),
                ("Transaction Handler", "handled_by_name"),
            ],
        )
        add_section(
            "Request",
            [
                ("Status", "request_status"),
                ("Requested Quantity", "requested_quantity"),
                ("Request Date", "request_date"),
                ("Due Date", "due_date"),
                ("Request Handler", "processed_by_name"),
                ("Approved By", "approved_by_name"),
                ("Confirmed By", "confirmed_by_name"),
            ],
        )
        add_section(
            "Item",
            [
                ("Item ID", "item_id"),
                ("Name", "item_name"),
                ("Item Code", "item_code"),
                ("Description", "item_description"),
                ("Serial No.", "serial_no"),
                ("Unit", "unit"),
                ("Current Stock", "stock"),
            ],
        )
        add_section(
            "Requester Personal Details",
            [
                ("User ID", "requester_id"),
                ("Name", "requester_name"),
                ("Student ID", "student_id"),
                ("Contact Number", "contact_number"),
                ("Birthday", "birthday"),
                ("Gender", "gender"),
                ("Address", "address"),
                ("Department", "department"),
                ("Course", "course"),
            ],
        )
        if self.state["mode"] == "archived":
            add_section(
                "Archive",
                [("Archived Date", "archived_date"), ("Archive Reason", "archive_reason")],
            )

        ctk.CTkButton(
            modal,
            text="Close",
            height=36,
            fg_color=RED,
            command=modal.destroy,
        ).pack(fill="x", padx=24, pady=(0, 20))

    def require_selected(self):
        if self.state["selected"] is None:
            messagebox.showwarning(
                "Select Transaction", "Select a transaction first.", parent=self.app
            )
        return self.state["selected"]

    def confirm_action(self, title, message, action):
        row = self.require_selected()
        if row is None or not messagebox.askyesno(title, message, parent=self.app):
            return
        try:
            if not action(row["transaction_id"]):
                raise ValueError("The transaction could not be updated.")
            self.load_rows()
        except (ValueError, Exception) as error:
            messagebox.showerror("Transaction Error", str(error), parent=self.app)

    def switch_mode(self):
        self.state["mode"] = "archived" if self.state["mode"] == "current" else "current"
        self.toggle.configure(text="CURRENT" if self.state["mode"] == "archived" else "ARCHIVE")
        self.load_rows()
        self.update_actions()

    def update_actions(self):
        for button in (self.current_button, self.restore_button, self.delete_button):
            button.pack_forget()
        if self.state["mode"] == "current":
            self.current_button.pack(side="left")
        else:
            self.delete_button.pack(side="right", padx=(10, 0))
            self.restore_button.pack(side="right")


def create_transactions_tab(parent_frame, app=None):
    return TransactionsView(parent_frame, app=app)