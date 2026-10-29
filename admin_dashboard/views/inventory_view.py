import os
from datetime import datetime
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
from models.inventory import InventoryItem, Category
from repositories import InventoryRepository, CategoryRepository

BG_BLUE = "#eef2ff"
DARK_BLUE = "#1c3b7a"
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"
RED = "#ef4444"
BLUE = "#1d4ed8"
GREEN = "#84cc16"
PURPLE = "#9333ea"
MODAL_BG = "#0b1b42"
MODAL_FONT = ("Segoe UI", 12)
MODAL_TITLE_FONT = ("Segoe UI", 22, "bold")


class InventoryView(ctk.CTkFrame):
    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color=BG_BLUE, corner_radius=0)
        self.app = app or self.winfo_toplevel()
        self.inventory_repo = InventoryRepository()
        self.category_repo = CategoryRepository()

        self._build_view()
        self.load_categories_filter()
        self.load_inventory_cards()

    def _build_view(self):
        header = ctk.CTkFrame(self, fg_color=DARK_BLUE, height=45, corner_radius=8)
        header.pack(fill="x", padx=20, pady=(20, 0))
        header.pack_propagate(False)
        ctk.CTkLabel(
            header, text="Items Catalogue", font=("Arial", 14, "bold"), text_color=WHITE
        ).pack(side="left", padx=15)

        toolbar = ctk.CTkFrame(header, fg_color="transparent")
        toolbar.pack(side="right", padx=20)
        refresh_button = ctk.CTkButton(
            toolbar,
            text="Refresh",
            width=80,
            height=30,
            fg_color=WHITE,
            text_color="#1c3b7a",
            hover_color="#e5e7eb",
            corner_radius=6,
            command=self.refresh_inventory,
        )
        refresh_button.pack(side="left", padx=5)

        self.filter_combo = ctk.CTkComboBox(
            toolbar,
            width=120,
            height=30,
            values=["All"],
            fg_color=WHITE,
            text_color="black",
            button_color=WHITE,
            corner_radius=6,
            command=lambda _val=None: self.load_inventory_cards(),
            state="readonly",
        )
        self.filter_combo.set("All")
        self.filter_combo.pack(side="left", padx=5)
        self.filter_combo.bind("<<ComboboxSelected>>", lambda _event=None: self.load_inventory_cards())

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
        self.search.bind("<KeyRelease>", lambda _event=None: self.load_inventory_cards())

        self.cards = ctk.CTkScrollableFrame(self, fg_color=WHITE, corner_radius=8)
        self.cards.pack(fill="both", expand=True, padx=20, pady=20)
        self.cards.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(
            self,
            text="ADD",
            font=("Arial", 18, "bold"),
            width=100,
            command=self.select_category,
            fg_color="#86efac",
            text_color="black",
        ).pack(anchor="w", padx=30, pady=(0, 30))

    @staticmethod
    def _value_text(value):
        return "" if value is None else str(value)

    @staticmethod
    def _modal_text(parent, label, value="", height=36, readonly=False):
        ctk.CTkLabel(parent, text=label, text_color=WHITE, font=MODAL_FONT).pack(
            anchor="w", pady=(5, 2)
        )
        widget = (
            ctk.CTkTextbox(parent, height=height, corner_radius=8)
            if height > 36
            else ctk.CTkEntry(parent, corner_radius=8)
        )
        widget.configure(fg_color=WHITE, text_color="black")
        widget.pack(fill="x", pady=(0, 4))
        if height > 36:
            widget.insert("1.0", value)
        else:
            widget.insert(0, value)
        if readonly:
            widget.configure(state="disabled")
        return widget

    @staticmethod
    def _modal_heading(parent, title, subtitle=""):
        ctk.CTkLabel(parent, text=title, text_color=WHITE, font=MODAL_TITLE_FONT).pack(
            anchor="w", pady=(0, 2)
        )
        if subtitle:
            ctk.CTkLabel(
                parent, text=subtitle, text_color="#bfdbfe", font=("Segoe UI", 10)
            ).pack(anchor="w", pady=(0, 14))

    @staticmethod
    def _text_value(widget):
        return widget.get("1.0", "end-1c") if isinstance(widget, ctk.CTkTextbox) else widget.get()

    @staticmethod
    def _date_value(raw):
        raw = raw.strip()
        if not raw:
            return None
        if hasattr(raw, "strftime"):
            return raw
        raw = raw[:10]
        try:
            return datetime.strptime(raw, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Dates must use YYYY-MM-DD format.")

    def create_category(self, parent, on_created):
        modal = ctk.CTkToplevel(parent)
        modal.title("Create Category")
        modal.geometry("400x450")
        modal.configure(fg_color=MODAL_BG)
        modal.transient(parent)
        modal.grab_set()
        modal.protocol("WM_DELETE_WINDOW", lambda: None)
        body = ctk.CTkFrame(modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=(24, 20))
        self._modal_heading(body, "Create Category", "Add a category for inventory items.")
        name = self._modal_text(body, "Category Name")
        description = self._modal_text(body, "Category Description", height=90)
        requires = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            body,
            text="Requires return",
            variable=requires,
            text_color=WHITE,
            font=MODAL_FONT,
            checkbox_width=20,
            checkbox_height=20,
        ).pack(anchor="w", pady=(10, 0))

        def save():
            category_name = name.get().strip()
            if not category_name:
                messagebox.showwarning("Validation", "Category name is required.", parent=modal)
                return
            try:
                self.category_repo.add(
                    Category(
                        0,
                        category_name,
                        self._text_value(description).strip(),
                        requires.get(),
                    )
                )
                modal.destroy()
                on_created(category_name)
            except (ValueError, Exception) as error:
                messagebox.showerror("Category Error", str(error), parent=modal)

        actions = ctk.CTkFrame(body, fg_color="transparent")
        actions.pack(fill="x", pady=18)
        ctk.CTkButton(
            actions, text="Cancel", width=100, height=36, command=modal.destroy, fg_color=RED, corner_radius=8
        ).pack(side="left", padx=(0, 5))
        ctk.CTkButton(
            actions, text="Create", width=100, height=36, command=save, fg_color=GREEN, corner_radius=8
        ).pack(side="right", padx=(5, 0))

    def edit_category(self, parent, category, on_updated):
        modal = ctk.CTkToplevel(parent)
        modal.title("Edit Category")
        modal.geometry("400x450")
        modal.configure(fg_color=MODAL_BG)
        modal.transient(parent)
        modal.grab_set()
        modal.protocol("WM_DELETE_WINDOW", lambda: None)
        body = ctk.CTkFrame(modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=(24, 20))
        self._modal_heading(body, "Edit Category", "Update the category details.")
        name = self._modal_text(body, "Category Name", category.category_name)
        description = self._modal_text(
            body, "Category Description", category.category_desc, height=90
        )
        requires = ctk.BooleanVar(value=category.requires_return)
        ctk.CTkCheckBox(
            body,
            text="Requires return",
            variable=requires,
            text_color=WHITE,
            font=MODAL_FONT,
            checkbox_width=20,
            checkbox_height=20,
        ).pack(anchor="w", pady=(10, 0))

        def save():
            category_name = name.get().strip()
            if not category_name:
                messagebox.showwarning("Validation", "Category name is required.", parent=modal)
                return
            if not messagebox.askyesno(
                "Update Category", "Would you like to update this category?", parent=modal
            ):
                return
            try:
                self.category_repo.update(
                    Category(
                        category.category_id,
                        category_name,
                        self._text_value(description).strip(),
                        requires.get(),
                    )
                )
                modal.destroy()
                on_updated(category_name)
            except (ValueError, Exception) as error:
                messagebox.showerror("Category Error", str(error), parent=modal)

        actions = ctk.CTkFrame(body, fg_color="transparent")
        actions.pack(fill="x", pady=18)
        ctk.CTkButton(
            actions, text="Cancel", width=100, height=36, command=modal.destroy, fg_color=RED, corner_radius=8
        ).pack(side="left", padx=(0, 5))
        ctk.CTkButton(
            actions, text="Save", width=100, height=36, command=save, fg_color=GREEN, corner_radius=8
        ).pack(side="right", padx=(5, 0))

    def select_category(self):
        modal = ctk.CTkToplevel(self.app)
        modal.title("Select Category")
        modal.geometry("500x480")
        modal.configure(fg_color=MODAL_BG)
        modal.transient(self.app)
        modal.grab_set()
        modal.protocol("WM_DELETE_WINDOW", lambda: None)
        body = ctk.CTkFrame(modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=(24, 20))
        self._modal_heading(body, "Select Category", "Choose the category for the new item.")
        selected = {"category": None}
        dropdown = ctk.CTkComboBox(
            body,
            values=[],
            corner_radius=8,
            font=MODAL_FONT,
            dropdown_font=MODAL_FONT,
            fg_color=WHITE,
            text_color="black",
            button_color=WHITE,
            dropdown_fg_color=WHITE,
            state="readonly",
        )
        ctk.CTkLabel(body, text="Category Name", text_color=WHITE, font=MODAL_FONT).pack(
            anchor="w", pady=(0, 4)
        )
        dropdown.pack(fill="x", pady=(0, 8))
        description = ctk.CTkTextbox(
            body, height=90, corner_radius=8, fg_color=WHITE, text_color="black"
        )
        ctk.CTkLabel(body, text="Description", text_color=WHITE, font=MODAL_FONT).pack(
            anchor="w", pady=(0, 4)
        )
        description.pack(fill="x", pady=(0, 8))
        description.configure(state="disabled")
        return_label = ctk.CTkLabel(
            body, text="Requires return: -", text_color=WHITE, font=MODAL_FONT
        )
        return_label.pack(anchor="w", pady=(0, 8))

        def refresh(selected_name="", clear_selection=False):
            try:
                categories = self.category_repo.get_all()
            except (ValueError, Exception) as error:
                messagebox.showerror("Category Error", str(error), parent=modal)
                return
            by_display = {
                f"{category.category_id} - {category.category_name}": category
                for category in categories
            }
            values = list(by_display)
            dropdown.configure(values=values or ["No categories available"])
            target = "" if clear_selection else next(
                (item for item in values if selected_name in item),
                values[0] if values else "",
            )
            dropdown.set(target)
            selected["category"] = by_display.get(target)
            category = selected["category"]
            description.configure(state="normal")
            description.delete("1.0", "end")
            description.insert("1.0", category.category_desc if category else "")
            description.configure(state="disabled")
            return_label.configure(
                text="Requires return: " + ("Yes" if category and category.requires_return else "No")
            )

        def edit_selected():
            category = selected["category"]
            if category is None:
                messagebox.showwarning("Edit Category", "Choose a valid category first.", parent=modal)
                return
            self.edit_category(modal, category, refresh)

        def delete_selected():
            category = selected["category"]
            if category is None:
                messagebox.showwarning("Delete Category", "Choose a valid category first.", parent=modal)
                return
            try:
                if self.category_repo.has_inventory_items(category.category_id):
                    messagebox.showwarning(
                        "Delete Category",
                        "This category cannot be deleted because inventory items are assigned to it.",
                        parent=modal,
                    )
                    return
            except Exception as error:
                messagebox.showerror("Category Error", str(error), parent=modal)
                return
            if not messagebox.askyesno(
                "Delete Category", "Are you sure you want to delete this category?", parent=modal
            ):
                return
            try:
                self.category_repo.delete(category.category_id)
                refresh(clear_selection=True)
            except (ValueError, Exception) as error:
                messagebox.showerror("Category Error", str(error), parent=modal)

        def changed(display):
            refresh(display)

        dropdown.configure(command=changed)
        refresh()

        def proceed():
            if selected["category"] is None:
                messagebox.showwarning("Select Category", "Choose a valid category first.", parent=modal)
                return
            modal.destroy()
            self.item_form(category=selected["category"])

        category_actions = ctk.CTkFrame(body, fg_color="transparent")
        category_actions.pack(fill="x", pady=(18, 8))
        category_actions.grid_columnconfigure((0, 1, 2), weight=1, uniform="category_action")
        ctk.CTkButton(
            category_actions,
            text="Create New Category",
            height=36,
            command=lambda: self.create_category(modal, refresh),
            fg_color=PURPLE,
            corner_radius=8,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ctk.CTkButton(
            category_actions,
            text="Edit Category",
            height=36,
            command=edit_selected,
            fg_color="#f59e0b",
            corner_radius=8,
        ).grid(row=0, column=1, sticky="ew", padx=4)
        ctk.CTkButton(
            category_actions,
            text="Delete Category",
            height=36,
            command=delete_selected,
            fg_color=RED,
            corner_radius=8,
        ).grid(row=0, column=2, sticky="ew", padx=(4, 0))

        actions = ctk.CTkFrame(body, fg_color="transparent")
        actions.pack(fill="x", pady=(0, 18))
        actions.grid_columnconfigure((0, 1), weight=1, uniform="navigation_action")
        ctk.CTkButton(
            actions, text="Cancel", height=36, command=modal.destroy, fg_color=RED, corner_radius=8
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ctk.CTkButton(
            actions, text="Proceed", height=36, command=proceed, fg_color=GREEN, corner_radius=8
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0))

    def item_form(self, item=None, category=None, manage=False):
        category = category or next(
            (c for c in self.category_repo.get_all() if c.category_id == item.category_id), None
        )
        if category is None:
            messagebox.showerror("Category Error", "The item's category no longer exists.")
            return
        modal = ctk.CTkToplevel(self.app)
        modal.title("Manage" if manage else "Item Information")
        modal.geometry("400x600")
        modal.configure(fg_color=MODAL_BG)
        modal.transient(self.app)
        modal.grab_set()
        body = ctk.CTkScrollableFrame(modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=(24, 20))
        self._modal_heading(
            body,
            "Manage" if manage else "Item Information",
            "Update the item details below." if manage else "Add a new inventory item.",
        )
        item_id = item.item_id if item else self.inventory_repo.next_id()
        top = ctk.CTkFrame(body, fg_color="transparent")
        top.pack(fill="x", pady=(0, 10))
        selected_category = {"value": category}
        category_dropdown = None
        category_name_label = None
        preview_column = ctk.CTkFrame(top, fg_color="transparent", width=220)
        preview_column.pack(anchor="center")
        preview = ctk.CTkFrame(preview_column, width=220, height=180, fg_color=WHITE, corner_radius=8)
        preview.pack()
        preview.pack_propagate(False)
        preview_label = ctk.CTkLabel(preview, text="Image Preview", text_color="black", font=MODAL_FONT)
        preview_label.pack(pady=(10, 10), anchor="center", expand=True)
        ctk.CTkButton(
            preview,
            text="Select Image",
            command=lambda: choose_image(),
            fg_color=BLUE,
            corner_radius=8,
        ).pack(fill="x", padx=10, pady=(0, 10), anchor="center")
        ctk.CTkLabel(
            preview_column,
            text=f"Item ID: {item_id}",
            text_color=WHITE,
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(8, 4))
        if manage:
            ctk.CTkLabel(preview_column, text="Category", text_color=WHITE, font=MODAL_FONT).pack(
                anchor="w", pady=(0, 4)
            )
            category_dropdown = ctk.CTkComboBox(
                preview_column,
                values=[f"{c.category_id} - {c.category_name}" for c in self.category_repo.get_all()],
                corner_radius=8,
                font=MODAL_FONT,
                dropdown_font=MODAL_FONT,
                fg_color=WHITE,
                text_color="black",
                button_color=WHITE,
                dropdown_fg_color=WHITE,
                state="readonly",
            )
            category_dropdown.pack(fill="x", pady=(0, 6))
            category_dropdown.set(f"{category.category_id} - {category.category_name}")
            category_name_label = ctk.CTkLabel(
                preview_column,
                text=f"Category Name: {category.category_name}",
                text_color=WHITE,
                font=MODAL_FONT,
            )
            category_name_label.pack(anchor="w", pady=(0, 6))
        else:
            ctk.CTkLabel(
                preview_column,
                text=f"Category: {category.category_id} - {category.category_name}",
                text_color=WHITE,
                font=MODAL_FONT,
            ).pack(anchor="w", pady=(0, 6))
        name = self._modal_text(body, "Item Name", self._value_text(item.item_name if item else ""))
        code = self._modal_text(body, "Item Code", self._value_text(item.item_code if item else ""))
        description = self._modal_text(
            body, "Description", self._value_text(item.description if item else ""), height=70
        )
        stock = self._modal_text(body, "Stock", self._value_text(item.stock if item else 1))
        serial_frame = ctk.CTkFrame(body, fg_color="transparent")
        serial = self._modal_text(
            serial_frame, "Serial No.", self._value_text(item.serial_no if item else "")
        )
        serial_enabled = ctk.BooleanVar(value=bool(item and item.serial_no))
        serial_row = ctk.CTkFrame(body, fg_color="transparent")
        serial_row.pack(fill="x", pady=(8, 0))
        ctk.CTkCheckBox(
            serial_row,
            text="Serial No.",
            variable=serial_enabled,
            text_color=WHITE,
            font=MODAL_FONT,
            checkbox_width=20,
            checkbox_height=20,
        ).pack(anchor="w")
        unit = ctk.CTkComboBox(
            body,
            values=["pcs", "box", "set", "unit"],
            corner_radius=8,
            font=MODAL_FONT,
            dropdown_font=MODAL_FONT,
            fg_color=WHITE,
            text_color="black",
            button_color=WHITE,
            dropdown_fg_color=WHITE,
            state="readonly",
        )
        ctk.CTkLabel(body, text="Unit", text_color=WHITE, font=MODAL_FONT).pack(
            anchor="w", pady=(0, 4)
        )
        unit.pack(fill="x", pady=(0, 6))
        unit.set(self._value_text(item.unit if item else "pcs") or "pcs")
        expiration_frame = ctk.CTkFrame(body, fg_color="transparent")
        expiration = self._modal_text(
            expiration_frame,
            "Expiration Date (YYYY-MM-DD)",
            self._value_text(item.expiration_date if item else ""),
        )
        perishable = ctk.BooleanVar(value=bool(item and item.expiration_date))
        perishable_row = ctk.CTkFrame(body, fg_color="transparent")
        perishable_row.pack(fill="x", pady=(8, 0))
        ctk.CTkCheckBox(
            perishable_row,
            text="Perishable Item",
            variable=perishable,
            text_color=WHITE,
            font=MODAL_FONT,
            checkbox_width=20,
            checkbox_height=20,
        ).pack(anchor="w")
        expiration_frame.pack(fill="x", before=perishable_row)
        image_path = {"value": self._value_text(item.image_path if item else "")}

        def toggle_serial():
            if serial_enabled.get():
                serial_frame.pack(fill="x", before=serial_row)
            else:
                serial.delete(0, "end")
                serial_frame.pack_forget()

        def toggle_expiration():
            if perishable.get():
                expiration_frame.pack(fill="x", before=perishable_row)
                expiration.configure(state="normal")
            else:
                expiration.configure(state="normal")
                expiration.delete(0, "end")
                expiration.configure(state="disabled")
                expiration_frame.pack_forget()

        serial_widget = serial_row.winfo_children()[0]
        serial_widget.configure(command=toggle_serial)
        perishable_widget = perishable_row.winfo_children()[0]
        perishable_widget.configure(command=toggle_expiration)

        def category_changed(display):
            category_id = int(display.split(" - ", 1)[0])
            selected_category["value"] = next(
                c for c in self.category_repo.get_all() if c.category_id == category_id
            )
            if category_name_label is not None:
                category_name_label.configure(
                    text=f"Category Name: {selected_category['value'].category_name}"
                )
            current = selected_category["value"].requires_return
            stock.configure(state="normal")
            if current and (not stock.get().strip() or stock.get().strip() == "0"):
                stock.delete(0, "end")
                stock.insert(0, "1")

        if category_dropdown is not None:
            category_dropdown.configure(command=category_changed)
        if not perishable.get():
            toggle_expiration()
        if serial_enabled.get():
            toggle_serial()
        if category.requires_return and (not stock.get().strip() or stock.get().strip() == "0"):
            stock.delete(0, "end")
            stock.insert(0, "1")

        def choose_image():
            path = filedialog.askopenfilename(
                parent=modal, filetypes=[("Images", "*.png *.jpg *.jpeg")]
            )
            if path:
                image_path["value"] = path
                set_image_preview(path)

        def set_image_preview(path):
            if not path or not os.path.isfile(path):
                preview_label.configure(image=None, text="Image Preview")
                preview_label.image = None
                return
            try:
                source = Image.open(path)
                sw, sh = source.size
                ratio = min(190 / max(1, sw), 135 / max(1, sh))
                pw = max(1, int(sw * ratio))
                ph = max(1, int(sh * ratio))
                image_preview = ctk.CTkImage(light_image=source, dark_image=source, size=(pw, ph))
                preview_label.configure(image=image_preview, text="")
                preview_label.image = image_preview
            except (OSError, ValueError) as error:
                preview_label.configure(image=None, text="Unable to load image")
                preview_label.image = None
                messagebox.showwarning(
                    "Image Preview", f"Could not load the selected image: {error}", parent=modal
                )

        set_image_preview(image_path["value"])

        def save():
            try:
                current_category = selected_category["value"]
                stock_text = stock.get().strip()
                if not stock_text.isascii() or not stock_text.isdigit():
                    messagebox.showwarning(
                        "Invalid Stock", "Stock must contain whole numbers only.", parent=modal
                    )
                    return
                stock_value = int(stock_text)
                minimum_stock = 1 if current_category.requires_return else 0
                if not minimum_stock <= stock_value <= 500:
                    messagebox.showwarning(
                        "Invalid Stock",
                        f"Stock must be between {minimum_stock} and 500.",
                        parent=modal,
                    )
                    return
                name_value = name.get().strip()
                code_value = code.get().strip()
                serial_value = serial.get().strip() if serial_enabled.get() else ""
                if not name_value or not code_value:
                    messagebox.showwarning(
                        "Missing Information", "Item name and item code are required.", parent=modal
                    )
                    return
                if serial_enabled.get():
                    if not serial_value:
                        messagebox.showwarning(
                            "Missing Information",
                            "Serial number is required when serial tracking is enabled.",
                            parent=modal,
                        )
                        return
                    if len(serial_value) > 8 or not serial_value.isalnum():
                        messagebox.showwarning(
                            "Invalid Serial Number",
                            "Serial No. can only contain up to 8 letters or numbers.",
                            parent=modal,
                        )
                        return
                exclude_id = item_id if manage else 0
                if self.inventory_repo.exists_duplicate(
                    name_value, code_value, serial_value, exclude_id
                ):
                    messagebox.showwarning(
                        "Duplicate Item",
                        "Item name, item code, or serial number already exists.",
                        parent=modal,
                    )
                    return
                timestamp = datetime.now()
                entity = InventoryItem(
                    item_id,
                    current_category.category_id,
                    name_value,
                    code_value,
                    self._text_value(description).strip(),
                    stock_value,
                    serial_value,
                    self._date_value(expiration.get() if perishable.get() else ""),
                    timestamp,
                    item.added_date if item else timestamp,
                    unit.get(),
                    image_path["value"],
                    current_category.category_name,
                    current_category.requires_return,
                )
                if messagebox.askyesno("Confirm", "Save this inventory item?", parent=modal):
                    (
                        self.inventory_repo.update(entity)
                        if manage
                        else self.inventory_repo.add(entity)
                    )
                    modal.destroy()
                    self.load_inventory_cards()
            except (ValueError, Exception) as error:
                messagebox.showerror("Inventory Error", str(error), parent=modal)

        def delete_item():
            if not item or not messagebox.askyesno(
                "Delete Item", "Delete this inventory item?", parent=modal
            ):
                return
            try:
                self.inventory_repo.delete(item.item_id)
                modal.destroy()
                self.load_inventory_cards()
            except (ValueError, Exception) as error:
                messagebox.showerror("Inventory Error", str(error), parent=modal)

        buttons = ctk.CTkFrame(body, fg_color="transparent")
        buttons.pack(fill="x", pady=(16, 0))

        def cancel_item_form():
            if manage:
                modal.destroy()
                return
            if messagebox.askyesno("Cancel Item", "Would you like to cancel?", parent=modal):
                modal.destroy()
                self.select_category()

        ctk.CTkButton(
            buttons,
            text="Update" if manage else "Submit",
            width=110,
            height=36,
            command=save,
            fg_color=GREEN if manage else BLUE,
            corner_radius=8,
        ).pack(side="right", padx=(0, 6))
        if manage:
            ctk.CTkButton(
                buttons,
                text="Delete",
                width=110,
                height=36,
                command=delete_item,
                fg_color=RED,
                corner_radius=8,
            ).pack(side="right", padx=(0, 6))
        ctk.CTkButton(
            buttons,
            text="Cancel",
            width=110,
            height=36,
            command=cancel_item_form,
            fg_color=RED,
            corner_radius=8,
        ).pack(side="left")

    def show_details(self, item_id):
        item = self.inventory_repo.get_by_id(item_id)
        if not item:
            messagebox.showerror("Inventory", "Item could not be found.")
            return
        modal = ctk.CTkToplevel(self.app)
        modal.title("Item Details")
        modal.geometry("600x500")
        modal.configure(fg_color=MODAL_BG)
        modal.transient(self.app)
        modal.grab_set()
        modal.protocol("WM_DELETE_WINDOW", modal.destroy)
        ctk.CTkLabel(modal, text="Item Details", text_color=WHITE, font=MODAL_TITLE_FONT).pack(
            anchor="w", padx=24, pady=(20, 8))
        content = ctk.CTkFrame(modal, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        content.grid_columnconfigure(0, weight=1, minsize=250)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)
        preview = ctk.CTkFrame(content, fg_color=WHITE, corner_radius=8)
        preview.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        preview_label = ctk.CTkLabel(preview, text="Image Preview", text_color="black", font=MODAL_FONT)
        preview_label.pack(anchor="center", expand=True)
        if item.image_path and os.path.isfile(item.image_path):
            try:
                source = Image.open(item.image_path)
                sw, sh = source.size
                ratio = min(240 / max(1, sw), 280 / max(1, sh))
                pw = max(1, int(sw * ratio))
                ph = max(1, int(sh * ratio))
                image_preview = ctk.CTkImage(light_image=source, dark_image=source, size=(pw, ph))
                preview_label.configure(image=image_preview, text="")
                preview_label.image = image_preview
            except (OSError, ValueError):
                pass
        card = ctk.CTkFrame(
            content, fg_color=MODAL_BG, corner_radius=8, border_width=1, border_color="#334b80"
        )
        card.grid(row=0, column=1, sticky="nsew")
        details = ctk.CTkTextbox(card, corner_radius=8, fg_color=WHITE, text_color="black")
        details.pack(fill="both", expand=True, padx=14, pady=14)
        details.insert(
            "1.0",
            "\n".join(
                f"{key.replace('_', ' ').title()}: {value}"
                for key, value in item.to_dict().items()
            ),
        )
        details.configure(state="disabled")
        ctk.CTkButton(
            modal, text="Close", width=110, height=36, fg_color=BLUE, command=modal.destroy
        ).pack(anchor="e", padx=24, pady=(0, 18))

    def manage(self, item_id):
        item = self.inventory_repo.get_by_id(item_id)
        if item:
            self.item_form(item=item, manage=True)

    def load_categories_filter(self):
        try:
            categories = self.category_repo.get_all()
            values = ["All", "Available", "Out of Stock", "Expired"] + [
                category.category_name for category in categories
            ]
            self.filter_combo.configure(values=values)
            if self.filter_combo.get() not in values:
                self.filter_combo.set("All")
        except (ValueError, Exception):
            pass

    def refresh_inventory(self):
        self.load_categories_filter()
        self.load_inventory_cards()

    def load_inventory_cards(self):
        for widget in self.cards.winfo_children():
            widget.destroy()
        try:
            items = self.inventory_repo.get_all(search_term=self.search.get())
            filter_choice = self.filter_combo.get()
            if filter_choice == "Available":
                items = [item for item in items if item.stock > 0 and not item.is_expired]
            elif filter_choice == "Out of Stock":
                items = [item for item in items if item.stock <= 0]
            elif filter_choice == "Expired":
                items = [item for item in items if item.is_expired]
            elif filter_choice and filter_choice not in ("All", "All Categories"):
                items = [item for item in items if item.category_name == filter_choice]
        except (ValueError, Exception) as error:
            messagebox.showerror("Inventory Unavailable", str(error))
            return
        for index, item in enumerate(items):
            card = ctk.CTkFrame(
                self.cards, height=280, fg_color=WHITE, border_width=1, border_color="#d1d5db", corner_radius=8
            )
            card.grid(row=index // 3, column=index % 3, padx=10, pady=10, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)
            card.grid_rowconfigure(1, weight=1)

            name_frame = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0)
            name_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
            ctk.CTkLabel(
                name_frame,
                text=item.item_name,
                font=("Arial", 12, "bold"),
                text_color=TEXT_BLUE,
                anchor="center",
            ).pack(fill="x", padx=10, pady=(8, 4))
            if item.is_expired:
                stock_label_text = "Expired"
                stock_color = "#dc2626"
            elif item.stock <= 0:
                stock_label_text = "Out of Stock"
                stock_color = "#b91c1c"
            else:
                stock_label_text = f"Stock available: {item.stock}"
                stock_color = "#15803d"
            ctk.CTkLabel(
                name_frame,
                text=stock_label_text,
                font=("Arial", 10, "bold"),
                text_color=stock_color,
                anchor="center",
            ).pack(fill="x", padx=10, pady=(0, 6))
            ctk.CTkFrame(name_frame, height=1, fg_color="#d1d5db").pack(fill="x", padx=10)

            image_frame = ctk.CTkFrame(card, fg_color="#e5e7eb", corner_radius=6)
            image_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

            image_label = ctk.CTkLabel(
                image_frame, text="No image available", text_color="#6b7280", font=("Arial", 10)
            )
            image_label.place(relx=0.5, rely=0.5, anchor="center")
            if item.image_path and os.path.isfile(item.image_path):
                try:
                    source = Image.open(item.image_path)
                    img_w, img_h = source.size
                    init_ratio = min(150 / max(1, img_w), 120 / max(1, img_h))
                    init_w = max(1, int(img_w * init_ratio))
                    init_h = max(1, int(img_h * init_ratio))
                    card_image = ctk.CTkImage(
                        light_image=source, dark_image=source, size=(init_w, init_h)
                    )
                    image_label.configure(image=card_image, text="")
                    image_label.image = card_image

                    def on_v2_img_resize(event, src=source, lbl=image_label):
                        w = event.width
                        h = event.height
                        if w > 10 and h > 10:
                            sw, sh = src.size
                            ratio = min(w / sw, h / sh)
                            new_w = max(1, int(sw * ratio))
                            new_h = max(1, int(sh * ratio))
                            resized = ctk.CTkImage(light_image=src, dark_image=src, size=(new_w, new_h))
                            lbl.configure(image=resized, text="")
                            lbl.image = resized

                    image_frame.bind("<Configure>", on_v2_img_resize)
                except (OSError, ValueError):
                    pass

            btn_frame = ctk.CTkFrame(
                card, fg_color=WHITE, corner_radius=0, border_width=1, border_color="#d1d5db"
            )
            btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
            btn_frame.grid_columnconfigure(0, weight=1)
            btn_frame.grid_columnconfigure(1, weight=1)

            ctk.CTkButton(
                btn_frame,
                text="View Details",
                height=35,
                fg_color=BLUE,
                hover_color="#1e40af",
                corner_radius=6,
                font=("Arial", 10, "bold"),
                command=lambda item_id=item.item_id: self.show_details(item_id),
            ).grid(row=0, column=0, sticky="ew", padx=(8, 4), pady=8)
            ctk.CTkButton(
                btn_frame,
                text="Manage",
                height=35,
                fg_color="#86efac",
                text_color="black",
                hover_color="#4ade80",
                corner_radius=6,
                font=("Arial", 10, "bold"),
                command=lambda item_id=item.item_id: self.manage(item_id),
            ).grid(row=0, column=1, sticky="ew", padx=(4, 8), pady=8)


def create_inventory_tab_v2(parent_frame, app=None):
    return InventoryView(parent_frame, app=app)
