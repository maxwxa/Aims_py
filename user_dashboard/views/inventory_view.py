import os
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image
from models.users import Session
from repositories import (
    ACCOUNT_DISABLED_MESSAGE,
    InventoryRepository,
    CategoryRepository,
    RequestRepository,
)
from user_dashboard.components.details_modal import ViewDetailsModal
from user_dashboard.components.request_modal import ItemRequestModal

DARK_BLUE = "#1c3b7a"
BG_BLUE = "#eef2ff"
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"
BLUE = "#1d4ed8"


class InventoryView(ctk.CTkFrame):
    """Items / Catalogue View for User Dashboard."""

    def __init__(self, parent, app=None, on_data_changed=None):
        super().__init__(
            parent, fg_color=DARK_BLUE, corner_radius=8, border_width=1, border_color="#d1d5db"
        )
        self.app = app or self.winfo_toplevel()
        self.on_data_changed = on_data_changed
        self.inventory_repo = InventoryRepository()
        self.category_repo = CategoryRepository()
        self.current_page = 1
        self.items_per_page = 25
        self._build_view()
        self.load_categories_filter()
        self.load_inventory_grid()

    def _build_view(self):
        inner_frame = ctk.CTkFrame(self, fg_color=BG_BLUE, corner_radius=8)
        inner_frame.pack(fill="both", expand=True, padx=2, pady=2)

        catalogue_panel = ctk.CTkFrame(
            inner_frame, fg_color=WHITE, corner_radius=8, border_width=1, border_color="#d1d5db"
        )
        catalogue_panel.pack(fill="both", expand=True, padx=10, pady=10)

        cat_header = ctk.CTkFrame(catalogue_panel, height=45, fg_color=DARK_BLUE, corner_radius=0)
        cat_header.pack(fill="x", padx=0, pady=(0, 0))
        cat_header.pack_propagate(False)

        ctk.CTkLabel(
            cat_header, text="Item Catalogue", font=("Arial", 16, "bold"), text_color=WHITE
        ).pack(side="left", padx=15, pady=10)

        controls_frame = ctk.CTkFrame(cat_header, fg_color="transparent")
        controls_frame.pack(side="right", padx=15)
        self.items_filter_label = ctk.CTkLabel(
            controls_frame, text="Filter:", font=("Arial", 12, "bold"), text_color=WHITE
        )
        self.items_filter_label.pack(side="left", padx=(0, 4))
        self.items_filter = ctk.CTkComboBox(
            controls_frame,
            width=130,
            height=30,
            corner_radius=6,
            fg_color=WHITE,
            text_color="black",
            button_color=WHITE,
            values=["All Categories"],
            state="readonly",
        )
        self.items_filter.pack(side="left", padx=(0, 12))
        self.items_filter.set("All Categories")
        self.items_cat_search_label = ctk.CTkLabel(
            controls_frame, text="Search:", font=("Arial", 12, "bold"), text_color=WHITE
        )
        self.items_cat_search_label.pack(side="left", padx=(0, 4))
        self.items_cat_search = ctk.CTkEntry(
            controls_frame, width=130, height=30, corner_radius=6, fg_color=WHITE, text_color="black"
        )
        self.items_cat_search.pack(side="left", padx=(0, 0))
        self.items_cat_search.bind("<KeyRelease>", lambda e: self.load_inventory_grid())

        ctk.CTkButton(
            controls_frame,
            text="Refresh",
            width=80,
            height=30,
            fg_color=WHITE,
            text_color=DARK_BLUE,
            hover_color="#dbeafe",
            corner_radius=6,
            command=self.refresh_dashboard,
        ).pack(side="left", padx=(8, 0))

        self.catalogue_container = ctk.CTkScrollableFrame(
            catalogue_panel, fg_color=BG_BLUE, corner_radius=0
        )

        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pagination_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.btn_prev = ctk.CTkButton(self.pagination_frame, text="<< Previous", width=100, 
                                      fg_color=BLUE, command=self.prev_page)
        self.btn_prev.pack(side="left")
        
        self.lbl_page = ctk.CTkLabel(self.pagination_frame, text="Page 1 of 1", font=("Arial", 14, "bold"), text_color=WHITE)
        self.lbl_page.pack(side="left", expand=True)
        
        self.btn_next = ctk.CTkButton(self.pagination_frame, text="Next >>", width=100, 
                                      fg_color=BLUE, command=self.next_page)
        self.btn_next.pack(side="right")

        self.catalogue_container.pack(fill="both", expand=True, padx=15, pady=15)
        self.catalogue_container.grid_columnconfigure((0, 1, 2), weight=1)



    def refresh_inventory(self):
        self.load_categories_filter()
        self.load_inventory_grid()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_inventory_grid()

    def next_page(self):
        self.current_page += 1
        self.load_inventory_grid() 

    def refresh_dashboard(self):
        self.load_categories_filter()
        self.load_inventory_grid()
        if self.on_data_changed:
            self.on_data_changed()

    def load_categories_filter(self):
        try:
            categories = self.category_repo.get_all()
            
            values = ["All Categories"] + [cat.category_name for cat in categories]
            
            self.items_filter.configure(values=values)
            
        except Exception as e:
            print(f"Error loading categories: {e}")

    def load_inventory_grid(self):
        for widget in self.catalogue_container.winfo_children():
            widget.destroy()
        search_term = self.items_cat_search.get()
        filter_category = self.items_filter.get()

        try:
            items = self.inventory_repo.get_all(search_term=search_term)

            items = [item for item in items if not item.is_expired]

            if filter_category and filter_category != "All Categories":
                items = [item for item in items if item.category_name == filter_category]
                
        except Exception as e:
            messagebox.showerror("Inventory Unavailable", f"Could not load inventory data: {e}")
            return

        total_items = len(items)
        total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > total_pages:
            self.current_page = 1
            
        self.lbl_page.configure(text=f"Page {self.current_page} of {total_pages} (Total: {total_items})")
        self.btn_prev.configure(state="normal" if self.current_page > 1 else "disabled")
        self.btn_next.configure(state="normal" if self.current_page < total_pages else "disabled")

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        display_items = items[start_idx:end_idx]

        for i, item in enumerate(display_items):
            row = i // 3
            col = i % 3

            card = self.create_inventory_card(self.catalogue_container, item)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

    def create_inventory_card(self, parent, item):
        card = ctk.CTkFrame(
            parent,
            height=280,
            fg_color=WHITE,
            border_width=1,
            border_color="#d1d5db",
            corner_radius=8,
        )
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

        image_path = item.image_path
        if image_path and os.path.isfile(image_path):
            try:
                source = Image.open(image_path)
                img_w, img_h = source.size
                init_ratio = min(150 / max(1, img_w), 120 / max(1, img_h))
                init_w = max(1, int(img_w * init_ratio))
                init_h = max(1, int(img_h * init_ratio))
                card_image = ctk.CTkImage(light_image=source, dark_image=source, size=(init_w, init_h))
                image_label.configure(image=card_image, text="")
                image_label.image = card_image

                def on_resize(event, src=source, lbl=image_label):
                    w = event.width
                    h = event.height
                    if w > 10 and h > 10:
                        sw, sh = src.size
                        ratio = min(w / sw, h / sh)
                        new_w = max(1, int(sw * ratio))
                        new_h = max(1, int(sh * ratio))
                        resized_img = ctk.CTkImage(light_image=src, dark_image=src, size=(new_w, new_h))
                        lbl.configure(image=resized_img, text="")
                        lbl.image = resized_img

                image_frame.bind("<Configure>", on_resize)
            except (OSError, ValueError):
                pass

        btn_frame = ctk.CTkFrame(
            card, fg_color=WHITE, corner_radius=0, border_width=1, border_color="#d1d5db"
        )
        btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        view_btn = ctk.CTkButton(
            btn_frame,
            text="View Details",
            height=35,
            fg_color=BLUE,
            hover_color="#1e40af",
            corner_radius=6,
            font=("Arial", 10, "bold"),
            command=lambda iid=item.item_id: self.show_view_details_modal(iid),
        )
        view_btn.grid(row=0, column=0, sticky="ew", padx=(8, 4), pady=8)

        is_expired = item.is_expired
        is_out_of_stock = item.stock <= 0
        cannot_request = is_expired or is_out_of_stock
        btn_text = "Expired" if is_expired else ("Out of Stock" if is_out_of_stock else "Request")
        request_btn = ctk.CTkButton(
            btn_frame,
            text=btn_text,
            height=35,
            fg_color="#9ca3af" if cannot_request else "#22c55e",
            hover_color="#9ca3af" if cannot_request else "#16a34a",
            corner_radius=6,
            font=("Arial", 10, "bold"),
            command=lambda iid=item.item_id: self.show_item_request_modal(iid),
        )
        request_btn.grid(row=0, column=1, sticky="ew", padx=(4, 8), pady=8)
        if cannot_request:
            request_btn.configure(state="disabled")

        return card

    def show_view_details_modal(self, item_id):
        try:
            item = self.inventory_repo.get_by_id(item_id)
            if item:
                ViewDetailsModal(self.app, item)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load item details: {e}", parent=self.app)

    def show_item_request_modal(self, item_id):
        try:
            item = self.inventory_repo.get_by_id(item_id)
            if not item:
                messagebox.showerror(
                    "Item Unavailable",
                    "This item could not be found in the inventory.",
                    parent=self.app,
                )
                return
            if item.is_expired:
                messagebox.showwarning(
                    "Item Expired",
                    f"'{item.item_name}' has expired and cannot be requested.",
                    parent=self.app,
                )
                return
            if item.stock <= 0:
                messagebox.showwarning(
                    "Out of Stock",
                    f"'{item.item_name}' is currently out of stock and cannot be requested.",
                    parent=self.app,
                )
                return
            current_user = Session.load() or {}
            user_id = current_user.get("user_id", 1)
            request_repo = RequestRepository()
            try:
                request_repo.process_overdue_returns()
            except Exception:
                pass
            if request_repo.is_account_disabled(user_id):
                messagebox.showwarning(
                    "Account Disabled",
                    ACCOUNT_DISABLED_MESSAGE,
                    parent=self.app,
                )
                return
            if request_repo.has_overdue_unreturned_items(user_id):
                messagebox.showwarning(
                    "Overdue Item",
                    "You have an overdue item to return. Return it before requesting again.",
                    parent=self.app,
                )
                return
            if request_repo.has_active_request(
                user_id, item_id
            ):
                messagebox.showwarning(
                    "Active Request",
                    "You already have an active request for this item.",
                    parent=self.app,
                )
                return
            if item.is_expiring_soon():
                exp_date = item.expiration_date
                exp_str = (
                    exp_date.strftime("%Y-%m-%d")
                    if hasattr(exp_date, "strftime")
                    else str(exp_date)[:10]
                )
                if not messagebox.askyesno(
                    "Expiring Soon",
                    f"'{item.item_name}' is expiring soon on {exp_str}. Continue to request?",
                    parent=self.app,
                ):
                    return
            ItemRequestModal(self.app, item, on_requested=self.refresh_dashboard)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load item details: {e}", parent=self.app)
