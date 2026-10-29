import os
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image
from repositories import RequestRepository, InventoryRepository

MODAL_BG = "#0b1b42"
MODAL_FONT = ("Segoe UI", 12)
TEXT_BLUE = "#1e3a8a"
WHITE = "#ffffff"
RED = "#ef4444"
GREEN = "#84cc16"


class ItemReturnModal:
    """Modal for returning an item."""

    def __init__(self, parent, request, on_returned=None):
        self.parent = parent
        self.request = request
        self.on_returned = on_returned

        self.modal = ctk.CTkToplevel(parent)
        self.modal.title("Return Item")
        self.modal.geometry("800x510")
        self.modal.configure(fg_color=MODAL_BG)
        self.modal.transient(parent)
        self.modal.grab_set()
        self.modal.protocol("WM_DELETE_WINDOW", self.modal.destroy)
        self.modal.update_idletasks()
        x = (self.modal.winfo_screenwidth() // 2) - 400
        y = (self.modal.winfo_screenheight() // 2) - 275
        self.modal.geometry(f"+{x}+{y}")

        card_frame = ctk.CTkFrame(self.modal, fg_color="white", corner_radius=10)
        card_frame.pack(fill="both", expand=True, padx=20, pady=20)

        card_frame.grid_columnconfigure(0, weight=1)
        card_frame.grid_columnconfigure(1, weight=2)
        card_frame.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        ctk.CTkLabel(
            left_frame, text="Return Item", text_color=TEXT_BLUE, font=("Arial", 20, "bold")
        ).pack(anchor="w", pady=(0, 15))

        image_bg = ctk.CTkFrame(
            left_frame, fg_color="#f3f4f6", corner_radius=10, width=220, height=220
        )
        image_bg.pack(pady=(0, 15))
        image_bg.pack_propagate(False)

        image_label = ctk.CTkLabel(
            image_bg, text="No image", text_color="gray", font=("Arial", 12)
        )
        image_label.pack(expand=True)

        image_path = request.get("image_path")
        if image_path and os.path.isfile(image_path):
            try:
                source = Image.open(image_path)
                return_image = ctk.CTkImage(
                    light_image=source, dark_image=source, size=(200, 200)
                )
                image_label.configure(image=return_image, text="")
                image_label.image = return_image
            except (OSError, ValueError):
                pass

        item_name = request.get("item_name", "N/A")
        item_code = request.get("item_code", "N/A")

        ctk.CTkLabel(
            left_frame, text=item_name, text_color=TEXT_BLUE, font=("Arial", 14, "bold"), wraplength=200
        ).pack()
        ctk.CTkLabel(
            left_frame, text=f"Code: {item_code}", text_color="gray", font=("Arial", 12)
        ).pack()

        right_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=40)

        right_frame.grid_columnconfigure(0, weight=0, minsize=120)
        right_frame.grid_columnconfigure(1, weight=1)

        try:
            item = InventoryRepository().get_by_id(request["item_id"])
        except Exception as error:
            messagebox.showerror("Item Unavailable", str(error), parent=self.modal)
            item = None

        details = [
            ("Request Code", f"REQ-{request.get('request_id', 'N/A')}"),
            ("Item ID", request.get("item_id", "N/A")),
            ("Request Status", request.get("request_status", "N/A")),
        ]

        if item:
            details.extend([
                ("Serial No.", item.serial_no or "N/A"),
                ("Added Date", item.added_date or "N/A"),
            ])

        for idx, (label_text, value) in enumerate(details):
            ctk.CTkLabel(
                right_frame, text=label_text, text_color=TEXT_BLUE, font=("Arial", 12)
            ).grid(row=idx, column=0, sticky="w", pady=5)

            entry = ctk.CTkEntry(
                right_frame,
                fg_color="#f9fafb",
                text_color="black",
                border_color="#d1d5db",
                height=30,
            )
            entry.grid(row=idx, column=1, sticky="ew", pady=5, padx=(10, 0))
            entry.insert(0, str(value))
            entry.configure(state="readonly")

        desc_idx = len(details)
        ctk.CTkLabel(
            right_frame, text="Description", text_color=TEXT_BLUE, font=("Arial", 12)
        ).grid(row=desc_idx, column=0, sticky="nw", pady=(10, 5))

        desc_box = ctk.CTkTextbox(
            right_frame,
            height=60,
            fg_color="#f9fafb",
            text_color="black",
            border_color="#d1d5db",
            border_width=1,
        )
        desc_box.grid(row=desc_idx, column=1, sticky="ew", pady=(10, 5), padx=(10, 0))
        desc_text = (
            item.description if item else request.get("item_description", "")
        ) or "No description available."
        desc_box.insert("1.0", desc_text)
        desc_box.configure(state="disabled")

        ctk.CTkLabel(
            right_frame,
            text="Return this item to the admin. The admin will inspect its condition.",
            text_color="gray",
            font=("Arial", 11, "italic"),
        ).grid(row=desc_idx + 1, column=1, sticky="w", pady=(5, 10), padx=(10, 0))

        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.grid(row=desc_idx + 2, column=1, sticky="e", pady=(20, 0), padx=(10, 0))

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=100,
            height=35,
            command=self.modal.destroy,
            fg_color=RED,
            hover_color="#dc2626",
            font=("Arial", 12, "bold"),
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Initiate Return",
            width=130,
            height=35,
            command=self._confirm_return,
            fg_color=GREEN,
            hover_color="#16a34a",
            font=("Arial", 12, "bold"),
        ).pack(side="left")

    @staticmethod
    def _readonly_field(parent, label, value, multiline=False):
        ctk.CTkLabel(parent, text=label, text_color=TEXT_BLUE, font=MODAL_FONT).pack(
            anchor="w", pady=(6, 2)
        )
        if multiline:
            field = ctk.CTkTextbox(
                parent, height=65, corner_radius=8, fg_color=WHITE, text_color="black"
            )
            field.pack(fill="x", pady=(0, 6))
            field.insert("1.0", str(value))
        else:
            field = ctk.CTkEntry(
                parent, corner_radius=8, fg_color=WHITE, text_color="black"
            )
            field.pack(fill="x", pady=(0, 6))
            field.insert(0, str(value))
        field.configure(state="disabled")

    def _confirm_return(self):
        """Notify the admin that the item is ready to be returned."""
        if not messagebox.askyesno(
            "Confirm Return",
            f"Confirm return of '{self.request['item_name']}'?",
            parent=self.modal,
        ):
            return

        try:
            changed = RequestRepository().request_return(self.request["request_id"])
            if not changed:
                raise ValueError("The return request could not be submitted.")
            messagebox.showinfo(
                "Success",
                f"Return initiated for '{self.request['item_name']}'.",
                parent=self.parent,
            )
            self.modal.destroy()
            if self.on_returned:
                self.on_returned()
        except (ValueError, Exception) as error:
            messagebox.showerror("Return Error", str(error), parent=self.modal)
