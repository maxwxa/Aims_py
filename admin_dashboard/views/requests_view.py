import os
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image
from repositories import RequestRepository, InventoryRepository
from admin_dashboard.components.request_modal import RequestModal, NotifyModal, _modal_field

BG_BLUE = "#eef2ff"
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"
GREEN = "#84cc16"
BLUE = "#1d4ed8"
MODAL_BG = "#0b1b42"
MODAL_FONT = ("Segoe UI", 12)
MODAL_TITLE_FONT = ("Segoe UI", 22, "bold")


class RequestsView(ctk.CTkFrame):
    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color=BG_BLUE, corner_radius=0)
        self.app = app or self.winfo_toplevel()
        self.request_repo = RequestRepository()
        self.selected = {"request": None, "rows": []}

        self._build_view()
        self.display_requests()

    def _build_view(self):
        header = ctk.CTkFrame(self, height=45, fg_color="#1c3b7a", corner_radius=8)
        header.pack(fill="x", padx=20, pady=(20, 0))
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="Requests", font=("Arial", 16, "bold"), text_color=WHITE).pack(
            side="left", padx=15
        )

        toolbar_frame = ctk.CTkFrame(header, fg_color="transparent")
        toolbar_frame.pack(side="right", padx=20)
        refresh_button = ctk.CTkButton(
            toolbar_frame,
            text="Refresh",
            width=80,
            height=30,
            fg_color=WHITE,
            text_color="#1c3b7a",
            hover_color="#e5e7eb",
            corner_radius=6,
            command=self.display_requests,
        )
        refresh_button.pack(side="left", padx=5)
        self.filter_combo = ctk.CTkComboBox(
            toolbar_frame,
            width=120,
            height=30,
            values=["All", "Pending", "Approved", "Active"],
            fg_color=WHITE,
            text_color="black",
            button_color=WHITE,
            corner_radius=6,
            command=lambda _val=None: self.display_requests(),
            state="readonly",
        )
        self.filter_combo.set("All")
        self.filter_combo.pack(side="left", padx=5)

        self.search_entry = ctk.CTkEntry(
            toolbar_frame,
            width=150,
            height=30,
            fg_color=WHITE,
            text_color="black",
            corner_radius=6,
            placeholder_text="Search",
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda _event=None: self.display_requests())

        column_specs = (
            (0, 1, 100),
            (1, 2, 150),
            (2, 1, 100),
            (3, 1, 110),
            (4, 2, 180),
            (5, 1, 140),
            (6, 1, 130),
        )
        header_frame = ctk.CTkFrame(
            self,
            fg_color="#dbeafe",
            corner_radius=8,
            border_width=1,
            border_color="#d1d5db",
        )
        header_frame.pack(fill="x", padx=20, pady=(20, 0))
        for column, weight, minsize in column_specs:
            header_frame.grid_columnconfigure(column, weight=weight, minsize=minsize)
        headings = [
            "Request No.",
            "Request By",
            "Code",
            "Status",
            "Request Details",
            "Date/Time",
            "Item Details",
        ]
        for column, heading in enumerate(headings):
            ctk.CTkLabel(
                header_frame,
                text=heading,
                fg_color="#dbeafe",
                text_color=TEXT_BLUE,
                font=("Arial", 11, "bold"),
                anchor="w",
            ).grid(row=0, column=column, sticky="ew", padx=8, pady=8)

        self.table = ctk.CTkScrollableFrame(
            self,
            fg_color=WHITE,
            corner_radius=8,
            border_width=1,
            border_color="#d1d5db",
        )
        self.table.pack(fill="both", expand=True, padx=20, pady=(6, 20))
        for column, weight, minsize in column_specs:
            self.table.grid_columnconfigure(column, weight=weight, minsize=minsize)

        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(fill="x", padx=20, pady=(0, 20))
        ctk.CTkButton(
            controls,
            text="MANAGE REQUEST",
            height=36,
            fg_color=GREEN,
            text_color="black",
            hover_color="#65a30d",
            corner_radius=6,
            command=self.manage_selected,
        ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            controls,
            text="NOTIFY",
            height=36,
            fg_color="#f59e0b",
            text_color="black",
            hover_color="#d97706",
            corner_radius=6,
            command=self.notify_selected,
        ).pack(side="left")

    def show_request_item_details(self, item_id):
        item = InventoryRepository().get_by_id(item_id)
        if not item:
            messagebox.showerror("Inventory", "Item could not be found.", parent=self.app)
            return
        modal = ctk.CTkToplevel(self.app)
        modal.title("Item Details")
        modal.geometry("800x710")
        modal.configure(fg_color=MODAL_BG)
        modal.transient(self.app)
        modal.grab_set()
        modal.protocol("WM_DELETE_WINDOW", modal.destroy)
        ctk.CTkLabel(
            modal, text="Item Details", text_color=WHITE, font=MODAL_TITLE_FONT
        ).pack(anchor="w", padx=24, pady=(20, 8))
        content = ctk.CTkFrame(modal, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        content.grid_columnconfigure(0, weight=1, minsize=250)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)
        preview = ctk.CTkFrame(content, fg_color=WHITE, corner_radius=8)
        preview.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        preview_label = ctk.CTkLabel(
            preview, text="No image", text_color="black", font=MODAL_FONT
        )
        preview_label.pack(expand=True)
        if item.image_path and os.path.isfile(item.image_path):
            try:
                source = Image.open(item.image_path)
                image = ctk.CTkImage(light_image=source, dark_image=source, size=(240, 280))
                preview_label.configure(image=image, text="")
                preview_label.image = image
            except (OSError, ValueError):
                pass
        details = ctk.CTkFrame(content, fg_color="transparent")
        details.grid(row=0, column=1, sticky="nsew")
        for row, (label, value) in enumerate((
            ("Item ID", item.item_id),
            ("Item Name", item.item_name),
            ("Item Code", item.item_code),
            ("Category", item.category_name),
            ("Stock", item.stock),
            ("Serial No.", item.serial_no or "N/A"),
            ("Added Date", item.added_date or "N/A"),
            ("Updated Date", item.updated_date or "N/A"),
        )):
            _modal_field(details, label, str(value), disabled=True)
        ctk.CTkButton(
            modal, text="Close", width=110, height=36, fg_color=BLUE, command=modal.destroy
        ).pack(anchor="e", padx=24, pady=(0, 18))

    def select_request(self, request, row_widgets):
        if self.selected["rows"]:
            for widget in self.selected["rows"]:
                widget.configure(fg_color=WHITE)
        self.selected["request"] = request
        self.selected["rows"] = row_widgets
        for widget in row_widgets:
            widget.configure(fg_color="#bfdbfe")

    def display_requests(self):
        for widget in self.table.winfo_children():
            widget.destroy()
        self.selected["request"] = None
        self.selected["rows"] = []
        try:
            rows = self.request_repo.get_all()
        except Exception as error:
            messagebox.showerror("Requests Unavailable", str(error), parent=self.app)
            return

        filter_value = self.filter_combo.get()
        search_value = self.search_entry.get().strip().lower()
        row_number = 1
        for request in rows:
            searchable = " ".join(
                str(request.get(key, "") or "")
                for key in (
                    "request_id",
                    "requester_name",
                    "gmail",
                    "item_code",
                    "item_name",
                    "request_status",
                )
            ).lower()
            if filter_value != "All" and request.get("request_status") != filter_value:
                continue
            if search_value and search_value not in searchable:
                continue

            date_value = request.get("request_date")
            date_text = date_value.strftime("%Y-%m-%d %H:%M") if date_value else ""
            values = [
                f"REQ-{request['request_id']}",
                request.get("requester_name") or request.get("gmail", "Unknown user"),
                request.get("item_code", ""),
                request.get("request_status", ""),
                f"{request.get('item_name', '')} x{request.get('quantity', 0)}",
                date_text,
            ]
            row_widgets = []
            for column, value in enumerate(values):
                label = ctk.CTkLabel(
                    self.table,
                    text=str(value),
                    fg_color=WHITE,
                    text_color="black",
                    anchor="w",
                    wraplength=180,
                )
                label.grid(row=row_number, column=column, sticky="ew", padx=3, pady=3)
                label.bind(
                    "<Button-1>",
                    lambda _event=None, item=request, widgets=row_widgets: self.select_request(
                        item, widgets
                    ),
                )
                row_widgets.append(label)
            details_button = ctk.CTkButton(
                self.table,
                text="View Item Details",
                width=120,
                height=26,
                fg_color=BLUE,
                hover_color="#254b91",
                corner_radius=6,
                command=lambda item_id=request["item_id"]: self.show_request_item_details(item_id),
            )
            details_button.grid(row=row_number, column=6, sticky="ew", padx=3, pady=3)
            row_number += 1

    def require_selection(self):
        if self.selected["request"] is None:
            messagebox.showwarning("Select Request", "Select a request first.", parent=self.app)
            return None
        return self.selected["request"]

    def manage_selected(self):
        request = self.require_selection()
        if request:
            RequestModal(self.app, request, self.request_repo, self.display_requests)

    def notify_selected(self):
        request = self.require_selection()
        if request:
            NotifyModal(self.app, request, self.request_repo)


def create_requests_tab(parent_frame, app=None):
    return RequestsView(parent_frame, app=app)
