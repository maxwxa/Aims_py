import os
import customtkinter as ctk
from PIL import Image

DARK_BLUE = "#1c3b7a"
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"
BLUE = "#1d4ed8"
MODAL_TITLE_FONT = ("Segoe UI", 22, "bold")
MODAL_FONT = ("Segoe UI", 12)
CORNER_RADIUS = 8


class ViewDetailsModal:
    """Modal for viewing item details — compact two-column card layout."""

    def __init__(self, parent, item):
        self.item = item
        self.modal = ctk.CTkToplevel(parent)
        self.modal.title("Item Details")
        self.modal.geometry("800x450")
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
            card, text="Item Details", text_color=TEXT_BLUE, font=MODAL_TITLE_FONT
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
                detail_image = ctk.CTkImage(
                    light_image=source, dark_image=source, size=(170, 120)
                )
                image_label.configure(image=detail_image, text="")
                image_label.image = detail_image
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
        fields_frame.pack(fill="both", expand=True)
        fields_frame.grid_columnconfigure(0, weight=1)
        fields_frame.grid_columnconfigure(1, weight=2)

        status_text = item.status_label
        detail_fields = [
            ("Item ID", item.item_id),
            ("Item Name", item.item_name),
            ("Item Code", item.item_code),
            ("Stock", item.stock),
            ("Status", status_text),
            ("Added Date", item.added_date),
            ("Updated Date", item.updated_date),
        ]
        field_row = 0
        for label, value in detail_fields:
            self._readonly_field(fields_frame, label, value, row=field_row)
            field_row += 1

        self._readonly_field(
            fields_frame,
            "Description",
            item.description or "No description available.",
            multiline=True,
            row=field_row,
            columnspan=2,
        )
        field_row += 1

        if item.expiration_date:
            exp_str = str(item.expiration_date)[:10]
            if item.is_expired:
                exp_str += " (Expired)"
            elif item.is_expiring_soon():
                exp_str += " (Expiring Soon)"
            self._readonly_field(fields_frame, "Expiration Date", exp_str, row=field_row)
            field_row += 1

        if item.serial_no:
            self._readonly_field(fields_frame, "Serial No.", item.serial_no, row=field_row)

        close_btn = ctk.CTkButton(
            right,
            text="Close",
            width=100,
            height=32,
            command=self.modal.destroy,
            fg_color=BLUE,
            hover_color="#1e40af",
            corner_radius=6,
            font=("Arial", 12, "bold"),
        )
        close_btn.pack(anchor="se", pady=(6, 0))

    @staticmethod
    def _readonly_field(parent, label, value, multiline=False, row=0, columnspan=1):
        if isinstance(parent, ctk.CTkScrollableFrame):
            field_parent = getattr(parent, "_readonly_grid", None)
            if field_parent is None:
                field_parent = ctk.CTkFrame(parent, fg_color="transparent")
                field_parent.pack(fill="x")
                field_parent.grid_columnconfigure(0, weight=1)
                field_parent.grid_columnconfigure(1, weight=2)
                parent._readonly_grid = field_parent
            parent = field_parent
        ctk.CTkLabel(parent, text=label, text_color=TEXT_BLUE, font=MODAL_FONT).grid(
            row=row,
            column=0,
            columnspan=columnspan,
            sticky="w",
            pady=(2, 1),
        )
        if multiline:
            field = ctk.CTkTextbox(
                parent,
                height=55,
                corner_radius=CORNER_RADIUS,
                fg_color="#f3f4f6",
                text_color="black",
            )
            field.grid(
                row=row,
                column=1,
                columnspan=columnspan,
                sticky="ew",
                padx=(8, 0),
                pady=(2, 5),
            )
            field.insert("1.0", str(value))
            field.configure(state="disabled")
        else:
            field = ctk.CTkEntry(
                parent,
                height=30,
                corner_radius=6,
                fg_color="#f3f4f6",
                text_color="black",
            )
            field.grid(row=row, column=1, sticky="ew", padx=(8, 10), pady=(2, 5))
            field.insert(0, str(value or ""))
            field.configure(state="disabled")
