from tkinter import messagebox
import customtkinter as ctk
from models.users import Session
from repositories import TransactionRepository

DARK_BLUE = "#1c3b7a"
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"
BLUE = "#1d4ed8"
RED = "#ef4444"
MODAL_BG = "#0b1b42"
MODAL_FONT = ("Segoe UI", 12)
MODAL_TITLE_FONT = ("Segoe UI", 22, "bold")

class HistoryView(ctk.CTkFrame):
    def __init__(self, parent, app=None):
        super().__init__(
            parent, fg_color=DARK_BLUE, corner_radius=8, border_width=1, border_color="#d1d5db"
        )
        self.app = app or self.winfo_toplevel()
        self.rows = []
        self.current_page = 1
        self.items_per_page = 50

        self._build_view()
        self.fetch_and_render_rows()

    def _build_view(self):
        header_bar = ctk.CTkFrame(self, height=45, fg_color=DARK_BLUE, corner_radius=8)
        header_bar.pack(fill="x", padx=20, pady=(20, 0))
        header_bar.pack_propagate(False)
        ctk.CTkLabel(
            header_bar, text="History", text_color=WHITE, font=("Arial", 16, "bold")
        ).pack(side="left", padx=15)

        toolbar = ctk.CTkFrame(header_bar, fg_color="transparent")
        toolbar.pack(side="right", padx=15)
        ctk.CTkLabel(
            toolbar, text="Search:", text_color=WHITE, font=("Arial", 11, "bold")
        ).pack(side="left", padx=5)
        self.history_search = ctk.CTkEntry(
            toolbar, width=150, height=30, corner_radius=6, fg_color=WHITE, text_color="black"
        )
        self.history_search.pack(side="left", padx=5)

        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=WHITE,
            corner_radius=8,
            border_width=1,
            border_color="#d1d5db",
        )
        self.scroll.pack(fill="both", expand=True, padx=20, pady=(6, 20))

        self.headers = [
            "Transaction ID",
            "Item Name",
            "Transaction Type",
            "Quantity",
            "Approved By",
            "Received By",
            "Date",
        ]
        self.column_widths = (2, 3, 3, 1, 2, 2, 3)

        header = ctk.CTkFrame(
            self.scroll, fg_color="#dbeafe", corner_radius=8, border_width=1, border_color="#d1d5db"
        )
        header.pack(fill="x", padx=10, pady=(0, 6))
        for index, title in enumerate(self.headers):
            ctk.CTkLabel(
                header,
                text=title,
                text_color=TEXT_BLUE,
                font=("Arial", 11, "bold"),
                anchor="w",
            ).grid(row=0, column=index, sticky="ew", padx=8, pady=10)
        for index, width in enumerate(self.column_widths):
            header.grid_columnconfigure(index, weight=width, uniform="col")

        self.rows_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.rows_frame.pack(fill="both", expand=True, padx=10)
        for index, width in enumerate(self.column_widths):
            self.rows_frame.grid_columnconfigure(index, weight=width)

        self.history_search.bind("<KeyRelease>", self.render_rows)
        ctk.CTkButton(
            toolbar,
            text="Search",
            width=70,
            height=30,
            corner_radius=6,
            fg_color=BLUE,
            hover_color="#1e40af",
            command=self.render_rows,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            toolbar,
            text="Refresh",
            width=80,
            height=30,
            corner_radius=6,
            fg_color=WHITE,
            text_color=DARK_BLUE,
            hover_color="#dbeafe",
            command=self.fetch_and_render_rows,
        ).pack(side="left", padx=5)

        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pagination_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.btn_prev = ctk.CTkButton(self.pagination_frame, text="<< Previous", width=100, fg_color=BLUE, command=self.prev_page)
        self.btn_prev.pack(side="left")
        
        self.lbl_page = ctk.CTkLabel(self.pagination_frame, text="Page 1 of 1", font=("Arial", 14, "bold"), text_color=TEXT_BLUE)
        self.lbl_page.pack(side="left", expand=True)
        
        self.btn_next = ctk.CTkButton(self.pagination_frame, text="Next >>", width=100, fg_color=BLUE, command=self.next_page)
        self.btn_next.pack(side="right")

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.render_rows()

    def next_page(self):
        self.current_page += 1
        self.render_rows()

    def fetch_and_render_rows(self, *_args):
        try:
            current_user = Session.load() or {}
            self.rows = TransactionRepository().get_user_history(current_user.get("user_id", 1))
        except Exception as error:
            messagebox.showerror("History Unavailable", str(error), parent=self.app)
            self.rows = []
        self.render_rows()

    def render_rows(self, *_args):
        for widget in self.rows_frame.winfo_children():
            widget.destroy()
        term = self.history_search.get().strip().lower()
        filtered_rows = [
            row
            for row in self.rows
            if not term
            or term in str(row.get("item_name", "")).lower()
            or term in str(row.get("transaction_type", "")).lower()
        ]

        total_items = len(filtered_rows)
        total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > total_pages:
            self.current_page = 1
            
        self.lbl_page.configure(text=f"Page {self.current_page} of {total_pages} (Total: {total_items})")
        self.btn_prev.configure(state="normal" if self.current_page > 1 else "disabled")
        self.btn_next.configure(state="normal" if self.current_page < total_pages else "disabled")

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        display_rows = filtered_rows[start_idx:end_idx]

        for row_index, row in enumerate(display_rows):
            card = ctk.CTkFrame(
                self.rows_frame,
                fg_color=WHITE,
                corner_radius=8,
                border_width=1,
                border_color="#d1d5db",
            )
            card.grid(
                row=row_index, column=0, columnspan=len(self.headers), sticky="ew", pady=5
            )
            date_value = row.get("transaction_date")
            date_text = date_value.strftime("%Y-%m-%d %H:%M") if date_value else ""
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
                row.get("transaction_id", ""),
                row.get("item_name", ""),
                row.get("transaction_type", ""),
                row.get("quantity", ""),
                row.get("approved_by_name") or "N/A",
                received_by,
                date_text,
            ]
            for index, value in enumerate(values):
                label = ctk.CTkLabel(
                    card,
                    text=str(value),
                    text_color=TEXT_BLUE,
                    font=("Arial", 11, "bold") if index == 1 else MODAL_FONT,
                    anchor="w",
                )
                label.grid(row=0, column=index, sticky="ew", padx=8, pady=8)
                label.bind(
                    "<Button-1>",
                    lambda _event=None, transaction=row: self.show_transaction_details_modal(
                        transaction
                    ),
                )
            for index, width in enumerate(self.column_widths):
                card.grid_columnconfigure(index, weight=width, uniform="col")
            card.bind(
                "<Button-1>",
                lambda _event=None, transaction=row: self.show_transaction_details_modal(
                    transaction
                ),
            )

    def show_transaction_details_modal(self, transaction):
        transaction_id = transaction.get("transaction_id")
        if transaction_id:
            try:
                full_details = TransactionRepository().get_details(transaction_id, mode="current")
                if not full_details:
                    full_details = TransactionRepository().get_details(
                        transaction_id, mode="archived"
                    )
                if full_details:
                    transaction = full_details
            except Exception:
                pass

        modal = ctk.CTkToplevel(self.app)
        modal.title("Transaction Details")
        modal.geometry("600x560")
        modal.minsize(480, 400)
        modal.configure(fg_color=MODAL_BG)
        modal.transient(self.app)
        modal.grab_set()
        modal.protocol("WM_DELETE_WINDOW", modal.destroy)
        body = ctk.CTkScrollableFrame(modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=(24, 12))
        ctk.CTkLabel(
            body, text="Transaction Details", text_color=WHITE, font=MODAL_TITLE_FONT
        ).pack(anchor="w", pady=(0, 12))

        date_value = transaction.get("transaction_date")
        date_text = (
            date_value.strftime("%Y-%m-%d %H:%M")
            if hasattr(date_value, "strftime")
            else (date_value or "N/A")
        )
        request_date = transaction.get("request_date")
        request_date_text = (
            request_date.strftime("%Y-%m-%d %H:%M")
            if hasattr(request_date, "strftime")
            else (request_date or "N/A")
        )
        due_date = transaction.get("due_date")
        due_date_text = (
            due_date.strftime("%Y-%m-%d %H:%M")
            if hasattr(due_date, "strftime")
            else (due_date or "Not applicable")
        )

        is_cancelled = (
            str(transaction.get("transaction_type", "")).strip().lower() == "cancelled"
            or str(transaction.get("request_status", "")).strip().lower() == "cancelled"
        )
        condition_label = "Cancellation Reason" if is_cancelled else "Condition Status"
        received_by = (
            "N/A"
            if is_cancelled
            else (transaction.get("requester_name") or transaction.get("confirmed_by_name") or "N/A")
        )

        details = [
            ("Transaction ID", f"TRX-{transaction.get('transaction_id', 'N/A')}"),
            ("Request ID", f"REQ-{transaction.get('request_id', 'N/A')}"),
            ("Item ID", transaction.get("item_id", "N/A")),
            ("Item Name", transaction.get("item_name", "N/A")),
            ("Item Code", transaction.get("item_code", "N/A")),
            ("Serial No.", transaction.get("serial_no") or "N/A"),
            ("Unit", transaction.get("unit") or "N/A"),
            ("Transaction Type", transaction.get("transaction_type", "N/A")),
            ("Quantity", transaction.get("quantity", "N/A")),
            ("Request Status", transaction.get("request_status", "N/A")),
            ("Approved By", transaction.get("approved_by_name") or "N/A"),
            ("Received By", received_by),
            ("Request Date", request_date_text),
            ("Due Date", due_date_text),
            ("Transaction Date", date_text),
            (condition_label, transaction.get("condition_status") or "N/A"),
        ]
        for label, value in details:
            ctk.CTkLabel(
                body,
                text=f"{label}: {value}",
                text_color=WHITE,
                font=MODAL_FONT,
                anchor="w",
                justify="left",
            ).pack(fill="x", pady=3)

        ctk.CTkLabel(
            body,
            text="Item Description",
            text_color=WHITE,
            font=MODAL_FONT,
        ).pack(anchor="w", pady=(12, 2))
        ctk.CTkLabel(
            body,
            text=transaction.get("item_description") or "No description available.",
            text_color="#bfdbfe",
            font=MODAL_FONT,
            wraplength=500,
            anchor="w",
            justify="left",
        ).pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(
            body,
            text="Condition Notes",
            text_color=WHITE,
            font=MODAL_FONT,
        ).pack(anchor="w", pady=(8, 2))
        ctk.CTkLabel(
            body,
            text=transaction.get("condition_notes") or "No condition notes.",
            text_color="#bfdbfe",
            font=MODAL_FONT,
            wraplength=500,
            anchor="w",
            justify="left",
        ).pack(fill="x", pady=(0, 12))
        ctk.CTkButton(
            modal,
            text="Close",
            height=36,
            fg_color=RED,
            command=modal.destroy,
        ).pack(fill="x", padx=24, pady=(0, 20))