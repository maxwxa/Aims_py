import os
import subprocess
import sys
from datetime import date, datetime, timedelta
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image, ImageTk
from tkcalendar import DateEntry

from models.users import Session
from repositories import (
    InventoryRepository, CategoryRepository, RequestRepository, TransactionRepository,
    UserRepository,
)

DARK_BLUE = "#1c3b7a"
BG_BLUE = "#eef2ff"
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"
RED = "#ef4444"
MODAL_BG = "#0b1b42"
MODAL_FONT = ("Segoe UI", 12)
MODAL_TITLE_FONT = ("Segoe UI", 22, "bold")
UI_FONT = "Segoe UI"
CORNER_RADIUS = 8
GREEN = "#84cc16"
BLUE = "#1d4ed8"
PURPLE = "#9333ea"

ctk.set_appearance_mode("light")

app = ctk.CTk()
app.geometry("1000x650")
app.title("Academic Inventory Management System - User Dashboard")

icon_path = os.path.join(os.path.dirname(__file__), "assets", "Aims_plain_white.png")
if not os.path.exists(icon_path):
    icon_path = os.path.join(os.path.dirname(__file__), "Assets", "Aims_plain_white.png")
if os.path.exists(icon_path):
    try:
        app_icon = ImageTk.PhotoImage(Image.open(icon_path))
        app.wm_iconphoto(True, app_icon)
        app._app_icon = app_icon
    except Exception:
        pass
try:
    app.state("zoomed")
except Exception:
    pass
app.after(100, lambda: app.state("zoomed"))

if not Session.load():
    messagebox.showerror("Access Denied", "No active session found. Please log in.")
    app.destroy()
    subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "main.py")])
    sys.exit()

current_user = Session.load()

user_role = current_user.get("role", "").strip().lower()
if user_role not in {"user", "student"}:
    messagebox.showerror("Unauthorized", "You do not have user permissions.")
    Session.clear()
    app.destroy()
    subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "main.py")])
    sys.exit()

def load_my_requests():
    try:
        return RequestRepository().get_for_user(current_user["user_id"])
    except Exception as e:
        print(f"Error loading requests: {e}")
        return []

def load_notifications():
    try:
        return RequestRepository().get_notifications(current_user["user_id"])
    except Exception as e:
        print(f"Error loading notifications: {e}")
        return []


def load_user_info():
    try:
        row = UserRepository().get_by_id(current_user["user_id"])
        
        if row:
            gmail = row.get("gmail", current_user.get("gmail", "user@example.com"))
            username = gmail.split("@")[0]
            last_name = username.split(".")[-1].title() if "." in username else username.title()
            return {
                "user_id": row["user_id"],
                "gmail": gmail,
                "department": row.get("department", ""),
                "course": row.get("course", ""),
                "last_name": last_name
            }
    except Exception as e:
        print(f"Error loading user info: {e}")
    
    gmail = current_user.get("gmail", "user@example.com")
    username = gmail.split("@")[0]
    last_name = username.split(".")[-1].title() if "." in username else username.title()
    return {
        "user_id": current_user.get("user_id", 1),
        "gmail": gmail,
        "department": "",
        "course": "",
        "last_name": last_name
    }


class UserDashboard:
    def __init__(self):
        self.user_info = load_user_info()
        self.requests = load_my_requests()
        self.notifications = load_notifications()       
        self.main_bg = ctk.CTkFrame(app, fg_color=BG_BLUE, corner_radius=8)
        self.main_bg.pack(fill="both", expand=True)     
        self._build_header()
        self._build_navigation()
        self._build_content_area()
        
        self.active_tab = "Home"
    
    def _build_header(self):
        """Build the header section with logo, greeting, and logout button."""
        header_frame = ctk.CTkFrame(self.main_bg, height=80, fg_color=DARK_BLUE, corner_radius=0)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)
        
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "Aims_plain_white.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(os.path.dirname(__file__), "Assets", "Aims_plain_white.png")
        try:
            if os.path.exists(logo_path):
                logo_img = ctk.CTkImage(light_image=Image.open(logo_path), size=(50, 50))
                ctk.CTkLabel(header_frame, image=logo_img, text="").place(x=20, y=15)
        except Exception:
            ctk.CTkLabel(header_frame, text="[LOGO]", text_color=WHITE, 
                        font=("Arial", 16, "bold")).place(x=20, y=25)
        
        last_name = self.user_info.get("last_name", "User")
        ctk.CTkLabel(header_frame, text=f"Hello, {last_name}", 
                    font=("Arial", 28, "bold"), text_color=WHITE).place(x=90, y=20)
        
        logout_btn = ctk.CTkButton(header_frame, text="Log out", width=100, height=35,
                                   fg_color=RED, hover_color="#dc2626", corner_radius=8,
                                   font=("Arial", 14, "bold"),
                                   command=self._show_logout_modal)
        logout_btn.pack(side="right", padx=20, pady=22)
        current_date_str = datetime.now().strftime("%A, %B %d, %Y")
        date_label = ctk.CTkLabel(header_frame, text=current_date_str, font=("Arial", 14, "bold"), text_color=WHITE)
        date_label.pack(side="right", padx=(0, 15), pady=22)
    
    def _build_navigation(self):
        """Build the pill-shaped navigation bar with centered buttons."""
        nav_frame = ctk.CTkFrame(self.main_bg, height=60, fg_color=WHITE, corner_radius=20,
                                 border_width=1, border_color="#d1d5db")
        nav_frame.pack(fill="x", padx=20, pady=15)
        nav_frame.pack_propagate(False)

        self.nav_buttons = {}
        tabs = ["Home", "Items", "History", "Profile"]
        
        nav_frame.grid_columnconfigure(0, weight=1)
        nav_frame.grid_columnconfigure(5, weight=1)
        buttons_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
        buttons_frame.grid(row=0, column=1, sticky="ew", pady=12)
        buttons_frame.grid_columnconfigure(tuple(range(len(tabs))), weight=1)

        for i, tab in enumerate(tabs):
            bg_color = DARK_BLUE if tab == "Home" else TEXT_BLUE
            btn = ctk.CTkButton(
                buttons_frame,
                text=tab,
                width=200,
                height=50,
                fg_color=bg_color,
                corner_radius=6,
                font=("Arial", 18, "bold"),
                command=lambda selected_tab=tab: self._show_tab(selected_tab),
            )
            btn.grid(row=0, column=i, padx=4, sticky="ew")
            self.nav_buttons[tab] = btn
    
    def _build_content_area(self):
        """Build the main content area with all tabs."""
        self.content_frames = {}
        self.content_frames["Home"] = self._create_home_tab()
        self.content_frames["Home"].pack(fill="both", expand=True, padx=20, pady=20)
        self.content_frames["Items"] = self._create_items_tab()
        for tab in ["History", "Profile"]:
            frame = self._create_history_tab() if tab == "History" else self._create_profile_tab()
            self.content_frames[tab] = frame
    
    def _create_home_tab(self):
        home_frame = ctk.CTkFrame(self.main_bg, fg_color=DARK_BLUE, corner_radius=8,
                                  border_width=1, border_color="#d1d5db")
    
        inner_frame = ctk.CTkFrame(home_frame, fg_color=BG_BLUE, corner_radius=8)
        inner_frame.pack(fill="both", expand=True, padx=2, pady=2)
        inner_frame.grid_columnconfigure(0, weight=5)
        inner_frame.grid_columnconfigure(1, weight=4)
        inner_frame.grid_rowconfigure(0, weight=1)
        
        items_panel = ctk.CTkFrame(inner_frame, fg_color=WHITE, corner_radius=8,
                                   border_width=1, border_color="#d1d5db")
        items_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        items_header = ctk.CTkFrame(items_panel, height=45, fg_color=DARK_BLUE, corner_radius=0)
        items_header.pack(fill="x", padx=0, pady=(0, 0))
        items_header.pack_propagate(False)
        
        ctk.CTkLabel(items_header, text="Track Items",
                     font=("Arial", 16, "bold"), text_color=WHITE).pack(
                         side="left", padx=15, pady=10
                     )
        
        items_toolbar = ctk.CTkFrame(items_header, fg_color="transparent")
        items_toolbar.pack(side="right", padx=15)
        
        self.items_refresh = ctk.CTkButton(items_toolbar, text="Refresh", width=70, height=30,
                                           corner_radius=6, fg_color=WHITE, text_color="black",
                                           command=self._load_items_cards)
        self.items_refresh.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(items_toolbar, text="Search:", 
                     font=("Arial", 12, "bold"), text_color=WHITE).pack(side="left", padx=(0, 4))
        self.items_search = ctk.CTkEntry(items_toolbar, width=130, height=30,
                                         corner_radius=6, fg_color=WHITE, text_color="black")
        self.items_search.pack(side="left", padx=(0, 0))
        self.items_search.bind("<KeyRelease>", lambda e: self._filter_items())
        
        self.items_scroll = ctk.CTkScrollableFrame(items_panel, fg_color=WHITE,
                                                   corner_radius=0)
        self.items_scroll.pack(fill="both", expand=True, padx=15, pady=15)
        self.items_scroll.grid_columnconfigure((0, 1), weight=1)
        
        self._load_items_cards()
        
        notif_panel = ctk.CTkFrame(inner_frame, fg_color=WHITE, corner_radius=8,
                                   border_width=1, border_color="#d1d5db")
        notif_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        notif_header = ctk.CTkFrame(notif_panel, height=45, fg_color=DARK_BLUE, corner_radius=0)
        notif_header.pack(fill="x", padx=0, pady=(0, 0))
        notif_header.pack_propagate(False)
        
        ctk.CTkLabel(notif_header, text="Notifications",
                     font=("Arial", 16, "bold"), text_color=WHITE).pack(
                         side="left", padx=15, pady=10
                     )
        
        notif_toolbar = ctk.CTkFrame(notif_header, fg_color="transparent")
        notif_toolbar.pack(side="right", padx=15)
        
        self.notif_refresh = ctk.CTkButton(notif_toolbar, text="Refresh", width=70, height=30,
                                           corner_radius=6, fg_color=WHITE, text_color="black",
                                           command=self._load_notifications_list)
        self.notif_refresh.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(notif_toolbar, text="Search:", 
                     font=("Arial", 12, "bold"), text_color=WHITE).pack(side="left", padx=(0, 4))
        self.notif_search = ctk.CTkEntry(notif_toolbar, width=130, height=30,
                                         corner_radius=6, fg_color=WHITE, text_color="black")
        self.notif_search.pack(side="left", padx=(0, 0))
        self.notif_search.bind("<KeyRelease>", lambda e: self._filter_notifications())
        
        self.notif_scroll = ctk.CTkScrollableFrame(
            notif_panel, fg_color=WHITE, corner_radius=0,
        )
        self.notif_scroll.pack(fill="both", expand=True, padx=15, pady=15)
        
        self._load_notifications_list()
        
        return home_frame
    
    def _create_items_tab(self):
        """Create the Items tab with Item Catalogue, filter, search, and grid layout."""
        self.inventory_repo = InventoryRepository()
        self.category_repo = CategoryRepository()
        
        items_frame = ctk.CTkFrame(self.main_bg, fg_color=DARK_BLUE, corner_radius=8,
                                   border_width=1, border_color="#d1d5db")
        inner_frame = ctk.CTkFrame(items_frame, fg_color=BG_BLUE, corner_radius=8)
        inner_frame.pack(fill="both", expand=True, padx=2, pady=2)
    
        catalogue_panel = ctk.CTkFrame(inner_frame, fg_color=WHITE, corner_radius=8,
                                       border_width=1, border_color="#d1d5db")
        catalogue_panel.pack(fill="both", expand=True, padx=10, pady=10)
        
        cat_header = ctk.CTkFrame(catalogue_panel, height=45, fg_color=DARK_BLUE, corner_radius=0)
        cat_header.pack(fill="x", padx=0, pady=(0, 0))
        cat_header.pack_propagate(False)
        
        ctk.CTkLabel(cat_header, text="Item Catalogue",
                     font=("Arial", 16, "bold"), text_color=WHITE).pack(
                         side="left", padx=15, pady=10
                     )
        
        controls_frame = ctk.CTkFrame(cat_header, fg_color="transparent")
        controls_frame.pack(side="right", padx=15)
        self.items_filter_label = ctk.CTkLabel(controls_frame, text="Filter:",
                                               font=("Arial", 12, "bold"), text_color=WHITE)
        self.items_filter_label.pack(side="left", padx=(0, 4))
        self.items_filter = ctk.CTkComboBox(controls_frame, width=130, height=30,
                                            corner_radius=6, fg_color=WHITE,
                                            text_color="black", button_color=WHITE,
                                            values=["All Categories"],
                                            state="readonly")
        self.items_filter.pack(side="left", padx=(0, 12))
        self.items_filter.set("All Categories")
        self.items_filter.bind("<<ComboboxSelected>>", lambda e: self._load_inventory_grid())
        self.items_cat_search_label = ctk.CTkLabel(controls_frame, text="Search:",
                                                   font=("Arial", 12, "bold"), text_color=WHITE)
        self.items_cat_search_label.pack(side="left", padx=(0, 4))
        self.items_cat_search = ctk.CTkEntry(controls_frame, width=130, height=30,
                                             corner_radius=6, fg_color=WHITE, text_color="black")
        self.items_cat_search.pack(side="left", padx=(0, 0))
        self.items_cat_search.bind("<KeyRelease>", lambda e: self._load_inventory_grid())
        ctk.CTkButton(
            controls_frame, text="Refresh", width=80, height=30,
            fg_color=WHITE, text_color=DARK_BLUE, hover_color="#dbeafe",
            corner_radius=6, command=self._refresh_dashboard,
        ).pack(side="left", padx=(8, 0))
        
        self.catalogue_container = ctk.CTkScrollableFrame(catalogue_panel, fg_color=BG_BLUE,
                                                          corner_radius=0)
        self.catalogue_container.pack(fill="both", expand=True, padx=15, pady=15)
        self.catalogue_container.grid_columnconfigure((0, 1, 2), weight=1)
        self._load_categories_filter()
        self._load_inventory_grid()
        
        return items_frame

    def _refresh_inventory(self):
        """Reload categories and inventory without changing the current filters."""
        self._load_categories_filter()
        self._load_inventory_grid()

    def _refresh_dashboard(self):
        """Reload inventory, request statuses, and notifications."""
        self.requests = load_my_requests()
        self.notifications = load_notifications()
        self._load_inventory_grid()
        self._load_items_cards()
        self._load_notifications_list()
    
    def _load_categories_filter(self):
        try:
            categories = self.category_repo.get_all()
            values = ["All Categories", "Available", "Out of Stock", "Expired"] + [cat.category_name for cat in categories]
            self.items_filter.configure(values=values)
        except Exception as e:
            print(f"Error loading categories: {e}")
    
    def _load_inventory_grid(self):
        for widget in self.catalogue_container.winfo_children():
            widget.destroy()
        
        search_term = self.items_cat_search.get()
        filter_category = self.items_filter.get()
        
        try:
            items = self.inventory_repo.get_all(search_term=search_term)
            
            if filter_category == "Available":
                items = [item for item in items if item.stock > 0 and not item.is_expired]
            elif filter_category == "Out of Stock":
                items = [item for item in items if item.stock <= 0]
            elif filter_category == "Expired":
                items = [item for item in items if item.is_expired]
            elif filter_category and filter_category != "All Categories":
                items = [item for item in items if item.category_name == filter_category]
        except Exception as e:
            messagebox.showerror("Inventory Unavailable",
                                f"Could not load inventory data: {e}")
            return
        
        for i, item in enumerate(items):
            row = i // 3
            col = i % 3
            
            card = self._create_inventory_card(self.catalogue_container, item)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
    
    def _create_inventory_card(self, parent, item):
        """Create a single inventory item card with proper structure and internal padding."""
        card = ctk.CTkFrame(parent, height=280, fg_color=WHITE, border_width=1,
                           border_color="#d1d5db", corner_radius=8)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)
        
        name_frame = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0)
        name_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        ctk.CTkLabel(name_frame, text=item.item_name,
                     font=("Arial", 12, "bold"), text_color=TEXT_BLUE,
                     anchor="center").pack(fill="x", padx=10, pady=(8, 4))
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
        # Bottom border line
        ctk.CTkFrame(name_frame, height=1, fg_color="#d1d5db").pack(fill="x", padx=10)
        image_frame = ctk.CTkFrame(card, fg_color="#e5e7eb", corner_radius=6)
        image_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        image_label = ctk.CTkLabel(image_frame, text="No image available",
                                   text_color="#6b7280", font=("Arial", 10))
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
        btn_frame = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0,
                                 border_width=1, border_color="#d1d5db")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        view_btn = ctk.CTkButton(btn_frame, text="View Details", height=35,
                                 fg_color=BLUE, hover_color="#1e40af", corner_radius=6,
                                 font=("Arial", 10, "bold"),
                                 command=lambda iid=item.item_id: self._show_view_details_modal(iid))
        view_btn.grid(row=0, column=0, sticky="ew", padx=(8, 4), pady=8)
        
        is_expired = item.is_expired
        is_out_of_stock = item.stock <= 0
        cannot_request = is_expired or is_out_of_stock
        btn_text = "Expired" if is_expired else ("Out of Stock" if is_out_of_stock else "Request")
        request_btn = ctk.CTkButton(btn_frame, text=btn_text, height=35,
                                    fg_color="#9ca3af" if cannot_request else "#22c55e",
                                    hover_color="#9ca3af" if cannot_request else "#16a34a",
                                    corner_radius=6,
                                    font=("Arial", 10, "bold"),
                                    command=lambda iid=item.item_id: self._show_item_request_modal(iid))
        request_btn.grid(row=0, column=1, sticky="ew", padx=(4, 8), pady=8)
        if cannot_request:
            request_btn.configure(state="disabled")
        
        return card
    
    def _create_placeholder_tab(self, tab_name):
        """Create a placeholder tab for History and Profile."""
        frame = ctk.CTkFrame(self.main_bg, fg_color=DARK_BLUE, corner_radius=8,
                             border_width=1, border_color="#d1d5db")
        
        inner = ctk.CTkFrame(frame, fg_color=BG_BLUE, corner_radius=8)
        inner.pack(fill="both", expand=True, padx=2, pady=2)
        
        ctk.CTkLabel(inner, text=f"{tab_name} Tab", font=("Arial", 24, "bold"),
                    text_color=TEXT_BLUE).pack(expand=True)
        ctk.CTkLabel(inner, text="Coming soon...", font=("Arial", 14),
                    text_color=TEXT_BLUE).pack(expand=True)
        
        return frame

    def _create_history_tab(self):
        frame = ctk.CTkFrame(self.main_bg, fg_color=DARK_BLUE, corner_radius=8,
                             border_width=1, border_color="#d1d5db")
        header_bar = ctk.CTkFrame(frame, height=45, fg_color=DARK_BLUE,
                                  corner_radius=8)
        header_bar.pack(fill="x", padx=20, pady=(20, 0))
        header_bar.pack_propagate(False)
        ctk.CTkLabel(header_bar, text="History", text_color=WHITE,
                     font=("Arial", 16, "bold")).pack(side="left", padx=15)
        toolbar = ctk.CTkFrame(header_bar, fg_color="transparent")
        toolbar.pack(side="right", padx=15)
        ctk.CTkLabel(toolbar, text="Search:", text_color=WHITE,
                     font=("Arial", 11, "bold")).pack(side="left", padx=5)
        history_search = ctk.CTkEntry(toolbar, width=150, height=30,
                                      corner_radius=6, fg_color=WHITE,
                                      text_color="black")
        history_search.pack(side="left", padx=5)
        scroll = ctk.CTkScrollableFrame(
            frame, fg_color=WHITE, corner_radius=8,
            border_width=1, border_color="#d1d5db",
        )
        scroll.pack(fill="both", expand=True, padx=20, pady=(6, 20))
        headers = [
            "Transaction ID", "Item Name", "Transaction Type", "Quantity",
            "Approved By", "Received By", "Date",
        ]
        column_widths = (2, 3, 3, 1, 2, 2, 3)
        header = ctk.CTkFrame(
            scroll, fg_color="#dbeafe", corner_radius=8,
            border_width=1, border_color="#d1d5db",
        )
        header.pack(fill="x", padx=10, pady=(0, 6))
        for index, title in enumerate(headers):
            ctk.CTkLabel(header, text=title, text_color=TEXT_BLUE,
                         font=("Arial", 11, "bold"), anchor="w").grid(
                             row=0, column=index, sticky="ew", padx=8, pady=10
                         )
        for index, width in enumerate(column_widths):
            header.grid_columnconfigure(index, weight=width, uniform="col")
        rows_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        rows_frame.pack(fill="both", expand=True, padx=10)
        for index, width in enumerate(column_widths):
            rows_frame.grid_columnconfigure(index, weight=width)

        rows = []

        def fetch_and_render_rows(*_args):
            nonlocal rows
            try:
                rows = TransactionRepository().get_user_history(current_user["user_id"])
            except Exception as error:
                messagebox.showerror("History Unavailable", str(error), parent=app)
                rows = []
            render_rows()

        def render_rows(*_args):
            for widget in rows_frame.winfo_children():
                widget.destroy()
            term = history_search.get().strip().lower()
            filtered_rows = [
                row for row in rows
                if not term or term in str(row.get("item_name", "")).lower()
                or term in str(row.get("transaction_type", "")).lower()
            ]
            for row_index, row in enumerate(filtered_rows):
                card = ctk.CTkFrame(
                    rows_frame, fg_color=WHITE, corner_radius=8,
                    border_width=1, border_color="#d1d5db",
                )
                card.grid(row=row_index, column=0, columnspan=len(headers),
                          sticky="ew", pady=5)
                date_value = row.get("transaction_date")
                date_text = date_value.strftime("%Y-%m-%d %H:%M") if date_value else ""
                is_cancelled = (
                    str(row.get("transaction_type", "")).strip().lower() == "cancelled"
                    or str(row.get("request_status", "")).strip().lower() == "cancelled"
                )
                received_by = "N/A" if is_cancelled else (row.get("requester_name") or row.get("confirmed_by_name") or "N/A")
                values = [
                    row.get("transaction_id", ""), row.get("item_name", ""),
                    row.get("transaction_type", ""), row.get("quantity", ""),
                    row.get("approved_by_name") or "N/A",
                    received_by,
                    date_text,
                ]
                for index, value in enumerate(values):
                    label = ctk.CTkLabel(
                        card, text=str(value), text_color=TEXT_BLUE,
                        font=("Arial", 11, "bold") if index == 1 else MODAL_FONT,
                        anchor="w",
                    )
                    label.grid(row=0, column=index, sticky="ew", padx=8, pady=8)
                    label.bind(
                        "<Button-1>",
                        lambda _event=None, transaction=row:
                        self._show_transaction_details_modal(transaction),
                    )
                for index, width in enumerate(column_widths):
                    card.grid_columnconfigure(index, weight=width, uniform="col")
                card.bind(
                    "<Button-1>",
                    lambda _event=None, transaction=row:
                    self._show_transaction_details_modal(transaction),
                )

        history_search.bind("<KeyRelease>", render_rows)
        ctk.CTkButton(
            toolbar, text="Search", width=70, height=30, corner_radius=6,
            fg_color=BLUE, hover_color="#1e40af", command=render_rows,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            toolbar, text="Refresh", width=80, height=30, corner_radius=6,
            fg_color=WHITE, text_color=DARK_BLUE, hover_color="#dbeafe",
            command=fetch_and_render_rows,
        ).pack(side="left", padx=5)
        fetch_and_render_rows()
        return frame

    def _show_transaction_details_modal(self, transaction):
        transaction_id = transaction.get("transaction_id")
        if transaction_id:
            try:
                full_details = TransactionRepository().get_details(transaction_id, mode="current")
                if not full_details:
                    full_details = TransactionRepository().get_details(transaction_id, mode="archived")
                if full_details:
                    transaction = full_details
            except Exception:
                pass

        modal = ctk.CTkToplevel(app)
        modal.title("Transaction Details")
        modal.geometry("600x560")
        modal.minsize(480, 400)
        modal.configure(fg_color=MODAL_BG)
        modal.transient(app)
        modal.grab_set()
        modal.protocol("WM_DELETE_WINDOW", modal.destroy)
        body = ctk.CTkScrollableFrame(modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=(24, 12))
        ctk.CTkLabel(
            body, text="Transaction Details", text_color=WHITE,
            font=MODAL_TITLE_FONT,
        ).pack(anchor="w", pady=(0, 12))

        date_value = transaction.get("transaction_date")
        date_text = date_value.strftime("%Y-%m-%d %H:%M") if hasattr(date_value, "strftime") else (date_value or "N/A")
        request_date = transaction.get("request_date")
        request_date_text = request_date.strftime("%Y-%m-%d %H:%M") if hasattr(request_date, "strftime") else (request_date or "N/A")
        due_date = transaction.get("due_date")
        due_date_text = due_date.strftime("%Y-%m-%d %H:%M") if hasattr(due_date, "strftime") else (due_date or "Not applicable")

        is_cancelled = (
            str(transaction.get("transaction_type", "")).strip().lower() == "cancelled"
            or str(transaction.get("request_status", "")).strip().lower() == "cancelled"
        )
        condition_label = "Cancellation Reason" if is_cancelled else "Condition Status"
        received_by = "N/A" if is_cancelled else (transaction.get("requester_name") or transaction.get("confirmed_by_name") or "N/A")

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
                body, text=f"{label}: {value}", text_color=WHITE,
                font=MODAL_FONT, anchor="w", justify="left",
            ).pack(fill="x", pady=3)

        ctk.CTkLabel(
            body, text="Item Description", text_color=WHITE, font=MODAL_FONT,
        ).pack(anchor="w", pady=(12, 2))
        ctk.CTkLabel(
            body, text=transaction.get("item_description") or "No description available.",
            text_color="#bfdbfe", font=MODAL_FONT, wraplength=500,
            anchor="w", justify="left",
        ).pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(
            body, text="Condition Notes", text_color=WHITE, font=MODAL_FONT,
        ).pack(anchor="w", pady=(8, 2))
        ctk.CTkLabel(
            body, text=transaction.get("condition_notes") or "No condition notes.",
            text_color="#bfdbfe", font=MODAL_FONT, wraplength=500,
            anchor="w", justify="left",
        ).pack(fill="x", pady=(0, 12))
        ctk.CTkButton(
            modal, text="Close", height=36, fg_color=RED,
            command=modal.destroy,
        ).pack(fill="x", padx=24, pady=(0, 20))

    def _create_profile_tab(self):
        frame = ctk.CTkFrame(self.main_bg, fg_color=DARK_BLUE, corner_radius=8,
                             border_width=1, border_color="#d1d5db")
        body = ctk.CTkScrollableFrame(frame, fg_color=BG_BLUE, corner_radius=8)
        body.pack(fill="both", expand=True, padx=20, pady=20)
        body.grid_columnconfigure((0, 1), weight=1, uniform="profile")
        try:
            profile = UserRepository().get_by_id(current_user["user_id"]) or {}
        except Exception as error:
            messagebox.showerror("Profile Unavailable", str(error), parent=app)
            profile = dict(current_user)

        left = ctk.CTkFrame(body, fg_color=WHITE, corner_radius=8,
                            border_width=1, border_color="#d1d5db")
        right = ctk.CTkFrame(body, fg_color=WHITE, corner_radius=8,
                             border_width=1, border_color="#d1d5db")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        ctk.CTkLabel(left, text="Account Information", text_color=TEXT_BLUE,
                     font=("Arial", 18, "bold")).pack(anchor="w", padx=20, pady=(18, 8))
        fields = [
            ("Account No.", profile.get("user_id", current_user.get("user_id", ""))),
            ("Account Role", profile.get("role", current_user.get("role", ""))),
            ("Email", profile.get("gmail", current_user.get("gmail", ""))),
            ("Account Status", "Active"),
            ("Account Created Date", profile.get("creationdate", "")),
        ]
        for label, value in fields:
            self._profile_entry(left, label, value)
        ctk.CTkButton(
            left, text="Change Password", height=36, fg_color=RED,
            corner_radius=6, command=lambda: PasswordModal(app, current_user["user_id"]),
        ).pack(fill="x", padx=20, pady=(12, 20))

        ctk.CTkLabel(right, text="Personal Information", text_color=TEXT_BLUE,
                     font=("Arial", 18, "bold")).pack(anchor="w", padx=20, pady=(18, 8))
        personal = [
            ("First Name", profile.get("first_name", "")),
            ("Middle Name", profile.get("middle_name", "")),
            ("Last Name", profile.get("last_name", "")),
            ("Contact No.", profile.get("contact_number", "")),
            ("Gender", profile.get("gender", "")),
            ("Student No.", profile.get("student_id", "")),
            ("Department", profile.get("department", "")),
            ("Course", profile.get("course", "")),
        ]
        for label, value in personal:
            self._profile_entry(right, label, value)
        ctk.CTkLabel(right, text="Address", text_color=TEXT_BLUE,
                     font=MODAL_FONT).pack(anchor="w", padx=20, pady=(6, 2))
        address = ctk.CTkTextbox(right, height=55, corner_radius=6,
                                 fg_color="#f3f4f6", text_color="black")
        address.pack(fill="x", padx=20, pady=(0, 18))
        address.insert("1.0", profile.get("address", ""))
        address.configure(state="disabled")
        return frame

    @staticmethod
    def _profile_entry(parent, label, value):
        ctk.CTkLabel(parent, text=label, text_color=TEXT_BLUE,
                     font=MODAL_FONT).pack(anchor="w", padx=20, pady=(4, 2))
        entry = ctk.CTkEntry(parent, height=30, corner_radius=6,
                             fg_color="#f3f4f6", text_color="black")
        entry.pack(fill="x", padx=20, pady=(0, 3))
        entry.insert(0, str(value or ""))
        entry.configure(state="disabled")
    
    def _load_items_cards(self):
        """Load and display item request cards."""
        # Clear existing cards
        for widget in self.items_scroll.winfo_children():
            widget.destroy()
        visible_requests = [
            req for req in self.requests
            if req.get("request_status") not in {"Returned", "Cancelled"}
        ]
        for i, req in enumerate(visible_requests):
            row = i // 2
            col = i % 2
            card = self._create_request_card(self.items_scroll, req)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
    
    def _create_request_card(self, parent, request):
        """Create a single request card with proper structure and internal padding."""
        card = ctk.CTkFrame(parent, height=280, fg_color=WHITE, corner_radius=8,
                           border_width=1, border_color="#d1d5db")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)
        name_frame = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0)
        name_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        ctk.CTkLabel(name_frame, text=request["item_name"],
                     font=("Arial", 12, "bold"), text_color=TEXT_BLUE,
                     anchor="center").pack(fill="x", padx=10, pady=(8, 8))
        ctk.CTkFrame(name_frame, height=1, fg_color="#d1d5db").pack(fill="x", padx=10)
        
        image_frame = ctk.CTkFrame(card, fg_color="#e5e7eb", corner_radius=6)
        image_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        image_label = ctk.CTkLabel(image_frame, text="No image available",
                                   text_color="#6b7280", font=("Arial", 10))
        image_label.place(relx=0.5, rely=0.5, anchor="center")
        
        image_path = request.get("image_path")
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

                def on_req_resize(event, src=source, lbl=image_label):
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

                image_frame.bind("<Configure>", on_req_resize)
            except (OSError, ValueError):
                pass

        status = request["request_status"]
        
        if status == "Pending":
            btn_frame = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0,
                                     border_width=1, border_color="#d1d5db")
            btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
            ctk.CTkButton(btn_frame, text="Cancel Request", height=35,
                         fg_color=RED, hover_color="#dc2626", corner_radius=6,
                         font=("Arial", 11, "bold"),
                         command=lambda rid=request["request_id"]: 
                                 self._show_cancel_modal(rid, request["item_name"], status))\
                         .pack(fill="x", padx=8, pady=8)
        
        elif status == "Approved":
            status_frame = ctk.CTkFrame(
                card, fg_color=WHITE, corner_radius=0,
                border_width=1, border_color="#d1d5db",
            )
            status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
            ctk.CTkLabel(status_frame, text="Waiting for admin to confirm receipt",
                        font=("Arial", 10, "bold"), text_color=TEXT_BLUE,
                        anchor="center").pack(fill="x", padx=8, pady=(6, 2))
            ctk.CTkButton(
                status_frame, text="Cancel Accepted Request", height=26,
                fg_color=RED, hover_color="#dc2626", corner_radius=6,
                font=("Arial", 10, "bold"),
                command=lambda rid=request["request_id"]: self._show_cancel_modal(
                    rid, request["item_name"], status
                ),
            ).pack(fill="x", padx=8, pady=(0, 6))

        elif status == "Active":
            btn_frame = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0,
                                     border_width=1, border_color="#d1d5db")
            btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
            ctk.CTkButton(btn_frame, text="Return", height=35,
                         fg_color=GREEN, hover_color="#65a30d", corner_radius=6,
                         font=("Arial", 11, "bold"),
                         command=lambda: self._show_return_modal(request))\
                         .pack(fill="x", padx=8, pady=8)

        elif status == "Return Requested":
            status_frame = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0)
            status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
            ctk.CTkLabel(status_frame, text="Return pending confirmation",
                        font=("Arial", 10, "bold"), text_color=TEXT_BLUE,
                        anchor="center").pack(fill="both", padx=8, pady=8)
        
        elif status == "Cancelled":
            status_frame = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0,
                                        border_width=1, border_color="#d1d5db")
            status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
            ctk.CTkLabel(status_frame, text="Request cancelled", font=("Arial", 10),
                        text_color=RED, anchor="center").pack(fill="both", expand=True, padx=8, pady=8)
        
        elif status == "Returned":
            status_frame = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0,
                                        border_width=1, border_color="#d1d5db")
            status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
            ctk.CTkLabel(status_frame, text="Already returned", font=("Arial", 10),
                        text_color="#6b7280", anchor="center").pack(fill="both", expand=True, padx=8, pady=8)
        return card
    
    def _load_notifications_list(self):
        """Load and display notifications list."""
        # Clear existing notifications
        for widget in self.notif_scroll.winfo_children():
            widget.destroy()
        
        for notif in self.notifications:
            self._create_notification_row(self.notif_scroll, notif)
    
    def _create_notification_row(self, parent, notification):
        is_unread = notification.get("notif_isread", 0) == 0

        card = ctk.CTkFrame(
            parent,
            fg_color=WHITE if is_unread else "#f9fafb",
            corner_radius=8,
            border_width=1,
            border_color="#93c5fd" if is_unread else "#d1d5db",
        )
        card.pack(fill="x", padx=8, pady=6)

        # Header area: Indicator, Date, Type
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(10, 4))
        
        if is_unread:
            indicator = ctk.CTkFrame(header, width=8, height=8, fg_color=BLUE, corner_radius=4)
            indicator.pack(side="left", padx=(0, 6))

        date_val = notification.get("notif_create")
        if isinstance(date_val, (datetime, date)):
            date_str = date_val.strftime("%Y-%m-%d %H:%M")
        else:
            date_str = str(date_val or "")

        date_label = ctk.CTkLabel(
            header,
            text=date_str,
            font=("Arial", 11, "bold") if is_unread else ("Arial", 11),
            text_color=TEXT_BLUE if is_unread else "#4b5563",
            anchor="w",
        )
        date_label.pack(side="left")

        notif_type = notification.get("notif_type", "")
        type_prefix = "From: " if notif_type == "Admin" else "Type: "
        type_label = ctk.CTkLabel(
            header,
            text=f"{type_prefix}{notif_type}",
            font=("Arial", 10, "italic"),
            text_color="#6b7280",
            anchor="e",
        )
        type_label.pack(side="right")
        ctk.CTkFrame(card, height=1, fg_color="#e5e7eb").pack(fill="x", padx=12, pady=(2, 6))
        msg_frame = ctk.CTkFrame(card, fg_color="transparent")
        msg_frame.pack(fill="x", expand=True, padx=12, pady=4)

        msg_label = ctk.CTkLabel(
            msg_frame,
            text=str(notification.get("notif_message", "")),
            text_color="black" if is_unread else "#374151",
            font=("Arial", 11),
            anchor="w",
            justify="left",
            wraplength=300,
        )
        msg_label.pack(fill="x", expand=True, anchor="w")

        def _update_wrap(event):
            new_wrap = max(80, event.width - 10)
            msg_label.configure(wraplength=new_wrap)

        msg_frame.bind("<Configure>", _update_wrap)

        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", padx=12, pady=(4, 10))

        if is_unread:
            mark_btn = ctk.CTkButton(
                footer,
                text="Mark as Read",
                width=100,
                height=28,
                font=("Arial", 10, "bold"),
                fg_color=BLUE,
                hover_color="#1e40af",
                corner_radius=6,
                command=lambda nid=notification["notif_id"]: self._mark_notification_read(nid),
            )
        else:
            mark_btn = ctk.CTkButton(
                footer,
                text="Read",
                width=80,
                height=28,
                font=("Arial", 10),
                fg_color="#e5e7eb",
                text_color="#6b7280",
                hover_color="#e5e7eb",
                corner_radius=6,
                state="disabled",
            )
        mark_btn.pack(side="right")

        return card
    
    def _filter_items(self):
        """Filter items based on search text."""
        search_term = self.items_search.get().lower()

        for widget in self.items_scroll.winfo_children():
            widget.destroy()
        
        filtered = [req for req in self.requests 
                   if (search_term in req["item_name"].lower() or 
                       search_term in req.get("item_code", "").lower()) and
                      req.get("request_status") not in {"Returned", "Cancelled"}]
        
        for i, req in enumerate(filtered):
            row = i // 2
            col = i % 2
            card = self._create_request_card(self.items_scroll, req)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
    
    def _filter_notifications(self):
        """Filter notifications based on search text."""
        search_term = self.notif_search.get().lower()
        
        for widget in self.notif_scroll.winfo_children():
            widget.destroy()
        
        filtered = [notif for notif in self.notifications 
                   if search_term in notif["notif_message"].lower() or
                      search_term in notif["notif_type"].lower()]
        
        for notif in filtered:
            self._create_notification_row(self.notif_scroll, notif)
    
    def _show_tab(self, selected_tab):
        """Switch between tabs."""
        for frame in self.content_frames.values():
            frame.pack_forget()

        if selected_tab == "Home":
            self.content_frames["Home"].pack(fill="both", expand=True, padx=20, pady=20)
        else:
            self.content_frames[selected_tab].pack(fill="both", expand=True, padx=20, pady=20)

        for tab, button in self.nav_buttons.items():
            button.configure(fg_color=DARK_BLUE if tab == selected_tab else TEXT_BLUE)
        
        self.active_tab = selected_tab
    
    def _show_logout_modal(self):
        """Show the logout confirmation modal."""
        LogoutConfirmationModal(app)
    
    def _show_cancel_modal(self, request_id, item_name, status="Pending"):
        """Show the cancel request confirmation modal."""
        CancelConfirmationModal(app, request_id, item_name, status)

    def _mark_notification_read(self, notification_id):
        try:
            RequestRepository().mark_notification_read(
                notification_id, current_user["user_id"]
            )
            self.notifications = load_notifications()
            self._load_notifications_list()
        except Exception as error:
            messagebox.showerror("Notification Error", str(error), parent=app)
    
    def _show_return_modal(self, request):
        ItemReturnModal(app, request)
    
    def _show_view_details_modal(self, item_id):
        try:
            item = self.inventory_repo.get_by_id(item_id)
            if item:
                ViewDetailsModal(app, item)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load item details: {e}")
    
    def _show_item_request_modal(self, item_id):
        try:
            item = self.inventory_repo.get_by_id(item_id)
            if not item:
                messagebox.showerror(
                    "Item Unavailable",
                    "This item could not be found in the inventory.",
                    parent=app,
                )
                return
            if item.is_expired:
                messagebox.showwarning(
                    "Item Expired",
                    f"'{item.item_name}' has expired and cannot be requested.",
                    parent=app,
                )
                return
            if item.stock <= 0:
                messagebox.showwarning(
                    "Out of Stock",
                    f"'{item.item_name}' is currently out of stock and cannot be requested.",
                    parent=app,
                )
                return
            if RequestRepository().has_active_request(
                current_user["user_id"], item_id
            ):
                messagebox.showwarning(
                    "Active Request",
                    "You already have an active request for this item.",
                    parent=app,
                )
                return
            if item.is_expiring_soon():
                exp_date = item.expiration_date
                exp_str = exp_date.strftime("%Y-%m-%d") if hasattr(exp_date, "strftime") else str(exp_date)[:10]
                if not messagebox.askyesno(
                    "Expiring Soon",
                    f"'{item.item_name}' is expiring soon on {exp_str}. Continue to request?",
                    parent=app,
                ):
                    return
            ItemRequestModal(app, item)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load item details: {e}")

class LogoutConfirmationModal:
    """Modal for confirming logout action."""
    
    def __init__(self, parent):
        self.modal = ctk.CTkToplevel(parent)
        self.modal.title("Confirm Logout")
        self.modal.geometry("350x200")
        self.modal.configure(fg_color=MODAL_BG)
        self.modal.transient(parent)
        self.modal.grab_set()
        self.modal.protocol("WM_DELETE_WINDOW", self.modal.destroy)
        
        self.modal.update_idletasks()
        x = (self.modal.winfo_screenwidth() // 2) - 200
        y = (self.modal.winfo_screenheight() // 2) - 150
        self.modal.geometry(f"+{x}+{y}")
        
        body = ctk.CTkFrame(self.modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=(24, 20))

        ctk.CTkLabel(body, text="Log Out", text_color=WHITE,
                    font=MODAL_TITLE_FONT).pack(anchor="w", pady=(0, 10))
        
        ctk.CTkLabel(body, text="Are you sure you want to log out?",
                    text_color="#bfdbfe", font=MODAL_FONT).pack(anchor="w", pady=(0, 20))
        
        actions = ctk.CTkFrame(body, fg_color="transparent")
        actions.pack(fill="x", pady=(20, 0))
        actions.grid_columnconfigure((0, 1), weight=1, uniform="action")
        
        ctk.CTkButton(actions, text="No", width=120, height=40,
                     command=self.modal.destroy,
                     fg_color=RED, corner_radius=8,
                     font=("Arial", 12, "bold"))\
                     .grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        ctk.CTkButton(actions, text="Yes", width=120, height=40,
                     command=self._confirm_logout,
                     fg_color=GREEN, corner_radius=8,
                     font=("Arial", 12, "bold"))\
                     .grid(row=0, column=1, sticky="ew", padx=(10, 0))
    
    def _confirm_logout(self):
        """Handle logout confirmation."""
        self.modal.destroy()
        Session.clear()
        app.destroy()
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "main.py")])

class CancelConfirmationModal:
    """Modal for confirming request cancellation."""
    
    def __init__(self, parent, request_id, item_name, status="Pending"):
        self.request_id = request_id
        self.item_name = item_name
        self.status = status
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
        
        ctk.CTkLabel(body, text="Cancel Request", text_color=WHITE,
                    font=MODAL_TITLE_FONT).pack(anchor="w", pady=(0, 10))
        
        ctk.CTkLabel(body, text=f"Are you sure you want to cancel your request for '{self.item_name}'?",
                    text_color="#bfdbfe", font=MODAL_FONT, wraplength=380)\
                    .pack(anchor="w", pady=(0, 20))
        if self.status == "Approved":
            ctk.CTkLabel(
                body, text="Cancellation reason (required):",
                text_color=WHITE, font=MODAL_FONT,
            ).pack(anchor="w", pady=(0, 4))
            self.reason = ctk.CTkTextbox(
                body, height=75, corner_radius=6,
                fg_color=WHITE, text_color="black",
            )
            self.reason.pack(fill="x", pady=(0, 10))
        
        actions = ctk.CTkFrame(body, fg_color="transparent")
        actions.pack(fill="x", pady=(20, 0))
        actions.grid_columnconfigure((0, 1), weight=1, uniform="action")
        
        ctk.CTkButton(actions, text="No", width=120, height=40,
                     command=self.modal.destroy,
                     fg_color=TEXT_BLUE, corner_radius=8,
                     font=("Arial", 12, "bold"))\
                     .grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        ctk.CTkButton(actions, text="Yes, Cancel", width=120, height=40,
                     command=self._confirm_cancel,
                     fg_color=RED, corner_radius=8,
                     font=("Arial", 12, "bold"))\
                     .grid(row=0, column=1, sticky="ew", padx=(10, 0))
    
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
            messagebox.showinfo("Cancelled", f"Your request for '{self.item_name}' has been cancelled.")
            self.modal.destroy()
            dashboard.requests = load_my_requests()
            dashboard.notifications = load_notifications()
            dashboard._load_items_cards()
            dashboard._load_notifications_list()
        except (ValueError, Exception) as error:
            messagebox.showerror("Request Error", str(error), parent=self.modal)


class ItemReturnModal:
    """Modal for returning an item."""
    
    def __init__(self, parent, request):
        self.request = request
        
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
        
        ctk.CTkLabel(left_frame, text="Return Item", text_color=TEXT_BLUE, # Assuming TEXT_BLUE is defined
                    font=("Arial", 20, "bold")).pack(anchor="w", pady=(0, 15))
        
        image_bg = ctk.CTkFrame(left_frame, fg_color="#f3f4f6", corner_radius=10, width=220, height=220)
        image_bg.pack(pady=(0, 15))
        image_bg.pack_propagate(False)
        
        image_label = ctk.CTkLabel(image_bg, text="No image", text_color="gray", font=("Arial", 12))
        image_label.pack(expand=True)
        
        image_path = request.get("image_path")
        if image_path and os.path.isfile(image_path):
            try:
                source = Image.open(image_path)
                return_image = ctk.CTkImage(light_image=source, dark_image=source, size=(200, 200))
                image_label.configure(image=return_image, text="")
                image_label.image = return_image
            except (OSError, ValueError):
                pass

        item_name = request.get("item_name", "N/A")
        item_code = request.get("item_code", "N/A")
        
        ctk.CTkLabel(left_frame, text=item_name, text_color=TEXT_BLUE, 
                     font=("Arial", 14, "bold"), wraplength=200).pack()
        ctk.CTkLabel(left_frame, text=f"Code: {item_code}", text_color="gray", 
                     font=("Arial", 12)).pack()

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
            ("Request Status", request.get("request_status", "N/A"))
        ]
        
        if item:
            details.extend([
                ("Serial No.", item.serial_no or "N/A"),
                ("Added Date", item.added_date or "N/A"),
            ])

        for idx, (label_text, value) in enumerate(details):
            ctk.CTkLabel(right_frame, text=label_text, text_color=TEXT_BLUE, 
                         font=("Arial", 12)).grid(row=idx, column=0, sticky="w", pady=5)
            
            entry = ctk.CTkEntry(right_frame, fg_color="#f9fafb", text_color="black", 
                                 border_color="#d1d5db", height=30)
            entry.grid(row=idx, column=1, sticky="ew", pady=5, padx=(10, 0))
            entry.insert(0, str(value))
            entry.configure(state="readonly")
            
        desc_idx = len(details)
        ctk.CTkLabel(right_frame, text="Description", text_color=TEXT_BLUE, 
                     font=("Arial", 12)).grid(row=desc_idx, column=0, sticky="nw", pady=(10, 5))
        
        desc_box = ctk.CTkTextbox(right_frame, height=60, fg_color="#f9fafb", 
                                  text_color="black", border_color="#d1d5db", border_width=1)
        desc_box.grid(row=desc_idx, column=1, sticky="ew", pady=(10, 5), padx=(10, 0))
        desc_text = (item.description if item else request.get("item_description", "")) or "No description available."
        desc_box.insert("1.0", desc_text)
        desc_box.configure(state="disabled")

        ctk.CTkLabel(right_frame, 
                     text="Return this item to the admin. The admin will inspect its condition.", 
                     text_color="gray", font=("Arial", 11, "italic")).grid(row=desc_idx+1, column=1, sticky="w", pady=(5, 10), padx=(10, 0))

        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.grid(row=desc_idx+2, column=1, sticky="e", pady=(20, 0), padx=(10, 0))

        ctk.CTkButton(btn_frame, text="Cancel", width=100, height=35,
                      command=self.modal.destroy, fg_color=RED, 
                      hover_color="#dc2626", font=("Arial", 12, "bold")).pack(side="left", padx=(0, 10))
                      
        ctk.CTkButton(btn_frame, text="Initiate Return", width=130, height=35,
                      command=self._confirm_return, fg_color=GREEN, 
                      hover_color="#16a34a", font=("Arial", 12, "bold")).pack(side="left")

    @staticmethod
    def _readonly_field(parent, label, value, multiline=False):
        ctk.CTkLabel(parent, text=label, text_color=TEXT_BLUE,
                     font=MODAL_FONT).pack(anchor="w", pady=(6, 2))
        if multiline:
            field = ctk.CTkTextbox(parent, height=65, corner_radius=8,
                                   fg_color=WHITE, text_color="black")
            field.pack(fill="x", pady=(0, 6))
            field.insert("1.0", str(value))
        else:
            field = ctk.CTkEntry(parent, corner_radius=8,
                                 fg_color=WHITE, text_color="black")
            field.pack(fill="x", pady=(0, 6))
            field.insert(0, str(value))
        field.configure(state="disabled")
    
    def _confirm_return(self):
        """Notify the admin that the item is ready to be returned."""
        if not messagebox.askyesno("Confirm Return", 
                                   f"Confirm return of '{self.request['item_name']}'?",
                                   parent=self.modal):
            return
        
        try:
            changed = RequestRepository().request_return(self.request["request_id"])
            if not changed:
                raise ValueError("The return request could not be submitted.")
            messagebox.showinfo("Success", f"Return initiated for '{self.request['item_name']}'.")
            self.modal.destroy()
            dashboard.requests = load_my_requests()
            dashboard._load_items_cards()
        except (ValueError, Exception) as error:
            messagebox.showerror("Return Error", str(error), parent=self.modal)


class PasswordModal:
    def __init__(self, parent, user_id):
        self.user_id = user_id
        self.modal = ctk.CTkToplevel(parent)
        self.modal.title("Change Password")
        self.modal.geometry("350x400")
        self.modal.configure(fg_color=MODAL_BG)
        self.modal.transient(parent)
        self.modal.grab_set()
        body = ctk.CTkFrame(self.modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=24)
        ctk.CTkLabel(body, text="Change Password", text_color=WHITE,
                     font=MODAL_TITLE_FONT).pack(anchor="w", pady=(0, 12))
        self.old = self._entry(body, "Old Password")
        self.new = self._entry(body, "New Password")
        self.confirm = self._entry(body, "Re-enter New Password")
        self.show_password = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            body,
            text="Show password",
            variable=self.show_password,
            command=self._toggle_password_visibility,
            text_color=WHITE,
            fg_color=BLUE,
            hover_color="#1e40af",
            corner_radius=4,
        ).pack(anchor="w", pady=(10, 0))
        ctk.CTkButton(body, text="SAVE", height=38, fg_color=GREEN,
                      text_color="black", corner_radius=6,
                      command=self.save).pack(fill="x", pady=(14, 0))

    def _entry(self, parent, label):
        ctk.CTkLabel(parent, text=label, text_color=TEXT_BLUE,
                     font=MODAL_FONT).pack(anchor="w", pady=(5, 2))
        entry = ctk.CTkEntry(parent, show="*", corner_radius=6,
                             fg_color=WHITE, text_color="black")
        entry.pack(fill="x")
        return entry

    def _toggle_password_visibility(self):
        show = "" if self.show_password.get() else "*"
        for entry in (self.old, self.new, self.confirm):
            entry.configure(show=show)

    def save(self):
        old, new, confirm = self.old.get(), self.new.get(), self.confirm.get()
        try:
            repository = UserRepository()
            if not repository.verify_password(self.user_id, old):
                raise ValueError("The old password is incorrect.")
            if new != confirm:
                raise ValueError("The new passwords do not match.")
            repository.change_password(self.user_id, new)
            self.modal.destroy()
            messagebox.showinfo("Password Updated", "Your password was changed.", parent=app)
        except (ValueError, Exception) as error:
            messagebox.showerror("Password Error", str(error), parent=self.modal)


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
        
        card = ctk.CTkFrame(self.modal, width=740, height=400,
                            fg_color=WHITE, corner_radius=8,
                            border_width=1, border_color="#d1d5db")
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(card, text="Item Details", text_color=TEXT_BLUE,
                     font=MODAL_TITLE_FONT).pack(anchor="w", padx=20, pady=(14, 8))
        
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
        image_label = ctk.CTkLabel(image_frame, text="No image", text_color="black",
                                   font=("Arial", 10))
        image_label.pack(expand=True)
        
        image_path = item.image_path
        if image_path and os.path.isfile(image_path):
            try:
                source = Image.open(image_path)
                detail_image = ctk.CTkImage(light_image=source, dark_image=source, size=(170, 120))
                image_label.configure(image=detail_image, text="")
                image_label.image = detail_image
            except (OSError, ValueError):
                pass

        ctk.CTkLabel(left, text=item.item_name, text_color=TEXT_BLUE,
                     font=("Arial", 13, "bold"), wraplength=200) \
            .grid(row=1, column=0, padx=10, pady=(2, 2))
        ctk.CTkLabel(left, text=f"Code: {item.item_code}",
                     text_color="#4b5563", font=("Arial", 11)) \
            .grid(row=2, column=0, padx=10, pady=(0, 10))

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
            fields_frame, "Description",
            item.description or "No description available.",
            multiline=True, row=field_row, columnspan=2,
        )
        field_row += 1
        
        if item.expiration_date:
            exp_str = str(item.expiration_date)[:10]
            if item.is_expired:
                exp_str += " (Expired)"
            elif item.is_expiring_soon():
                exp_str += " (Expiring Soon)"
            self._readonly_field(fields_frame, "Expiration Date", exp_str,
                                 row=field_row)
            field_row += 1
        
        if item.serial_no:
            self._readonly_field(fields_frame, "Serial No.", item.serial_no,
                                 row=field_row)
        
        close_btn = ctk.CTkButton(right, text="Close", width=100, height=32,
                                  command=self.modal.destroy,
                                  fg_color=BLUE, hover_color="#1e40af", corner_radius=6,
                                  font=("Arial", 12, "bold"))
        close_btn.pack(anchor="se", pady=(6, 0))

    @staticmethod
    def _readonly_field(parent, label, value, multiline=False, row=0,
                        columnspan=1):
        if isinstance(parent, ctk.CTkScrollableFrame):
            field_parent = getattr(parent, "_readonly_grid", None)
            if field_parent is None:
                field_parent = ctk.CTkFrame(parent, fg_color="transparent")
                field_parent.pack(fill="x")
                field_parent.grid_columnconfigure(0, weight=1)
                field_parent.grid_columnconfigure(1, weight=2)
                parent._readonly_grid = field_parent
            parent = field_parent
        ctk.CTkLabel(parent, text=label, text_color=TEXT_BLUE,
                     font=MODAL_FONT).grid(
                         row=row, column=0, columnspan=columnspan,
                         sticky="w", pady=(2, 1),
                     )
        if multiline:
            field = ctk.CTkTextbox(parent, height=55, corner_radius=CORNER_RADIUS,
                                   fg_color="#f3f4f6", text_color="black")
            field.grid(row=row, column=1, columnspan=columnspan,
                       sticky="ew", padx=(8, 0), pady=(2, 5))
            field.insert("1.0", str(value))
            field.configure(state="disabled")
        else:
            field = ctk.CTkEntry(parent, height=30, corner_radius=6,
                                 fg_color="#f3f4f6", text_color="black")
            field.grid(row=row, column=1, sticky="ew", padx=(8, 10), pady=(2, 5))
            field.insert(0, str(value or ""))
            field.configure(state="disabled")


class ItemRequestModal:
    """Modal for requesting an item — compact two-column card layout."""
    def __init__(self, parent, item):
        self.item = item
        
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
        
        card = ctk.CTkFrame(self.modal, width=740, height=400,
                            fg_color=WHITE, corner_radius=8,
                            border_width=1, border_color="#d1d5db")
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(card, text="Item Request", text_color=TEXT_BLUE,
                     font=MODAL_TITLE_FONT).pack(anchor="w", padx=20, pady=(14, 8))
        
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
        image_label = ctk.CTkLabel(image_frame, text="No image", text_color="black",
                                   font=("Arial", 10))
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
        
        ctk.CTkLabel(left, text=item.item_name, text_color=TEXT_BLUE,
                     font=("Arial", 13, "bold"), wraplength=200) \
            .grid(row=1, column=0, padx=10, pady=(2, 2))
        ctk.CTkLabel(left, text=f"Code: {item.item_code}",
                     text_color="#4b5563", font=("Arial", 11)) \
            .grid(row=2, column=0, padx=10, pady=(0, 10))
        
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
            fields_frame, "Description",
            item.description or "No description available.",
            multiline=True, row=field_row, columnspan=2,
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

        ctk.CTkLabel(right, text="Quantity", text_color=TEXT_BLUE,
                     font=MODAL_FONT).pack(anchor="w", pady=(4, 1))
        validate_quantity = self.modal.register(self._validate_quantity)
        self.quantity_entry = ctk.CTkEntry(
            right, height=30, corner_radius=6, fg_color="#f3f4f6",
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
                right, text="Due Date", text_color=TEXT_BLUE, font=MODAL_FONT,
            ).pack(anchor="w", pady=(4, 1))
            today = date.today()
            self.due_date_entry = DateEntry(
                right,
                width=18,
                date_pattern="yyyy-mm-dd",
                background=TEXT_BLUE,
                foreground=WHITE,
                borderwidth=1,
            )
            self.due_date_entry.pack(fill="x", pady=(0, 6))
            self.due_date_entry.set_date(today + timedelta(days=30))

            def release_modal_grab(_event=None):
                if self.modal.grab_current() == str(self.modal):
                    self.modal.grab_release()

            def restore_modal_grab(_event=None):
                if self.modal.winfo_exists():
                    self.modal.grab_set()
                    self.modal.focus_set()

            self.due_date_entry.bind(
                "<Button-1>", release_modal_grab, add="+"
            )
            self.due_date_entry.bind(
                "<<DateEntrySelected>>", restore_modal_grab, add="+"
            )

        ctk.CTkLabel(right, text="Unit/Serial No.", text_color=TEXT_BLUE,
                     font=MODAL_FONT).pack(anchor="w", pady=(4, 1))
        
        unit_options = []
        if item.unit:
            unit_values = [u.strip() for u in item.unit.split(",") if u.strip()]
            unit_options.extend(unit_values)
        if not unit_options:
            unit_options = ["Any"]
        
        self.unit_combo = ctk.CTkComboBox(
            right, height=30, corner_radius=6,
            fg_color="#f3f4f6", text_color="black",
            button_color=WHITE,
            values=unit_options if unit_options else ["Any"],
            state="readonly")
        self.unit_combo.pack(fill="x", pady=(0, 6))
        self.unit_combo.set(unit_options[0])
        
        actions = ctk.CTkFrame(right, fg_color="transparent")
        actions.pack(fill="x", pady=(6, 0))
        actions.grid_columnconfigure((0, 1), weight=1)
        
        send_btn = ctk.CTkButton(actions, text="SEND REQUEST", height=34,
                                 command=self._send_request,
                                 fg_color="#22c55e", hover_color="#16a34a", corner_radius=6,
                                 font=("Arial", 13, "bold"))
        send_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        
        ctk.CTkButton(
            actions, text="Cancel", height=34,
            command=self.modal.destroy, fg_color=RED, hover_color="#dc2626",
            corner_radius=6, font=("Arial", 12, "bold"),
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0))

    @staticmethod
    def _validate_quantity(proposed):
        return proposed == "" or (proposed.isdigit() and len(proposed) <= 2)
    
    def _send_request(self):
        qty_str = self.quantity_entry.get().strip()
        try:
            quantity = int(qty_str)
            if quantity <= 0:
                messagebox.showerror("Invalid Quantity", "Quantity must be a positive integer.",
                                     parent=self.modal)
                return
        except ValueError:
            messagebox.showerror("Invalid Quantity", "Quantity must contain digits only.",
                                 parent=self.modal)
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
            exp_str = exp_date.strftime("%Y-%m-%d") if hasattr(exp_date, "strftime") else str(exp_date)[:10]
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
            due_date = self.due_date_entry.get_date()
            today = date.today()
            if due_date < today or due_date > today + timedelta(days=90):
                messagebox.showwarning(
                    "Invalid Due Date",
                    "Items can only be borrowed for up to 3 months.",
                    parent=self.modal,
                )
                return
        if category in {"assets", "asset"}:
            if quantity != 1:
                messagebox.showerror(
                    "Invalid Quantity", "Assets can only be requested in a quantity of 1.",
                    parent=self.modal,
                )
                return
        elif category in {"consumables", "consumable"}:
            limit = 5 if unit == "pcs" else 1 if unit in {"box", "set", "unit"} else None
            if limit is None:
                messagebox.showerror(
                    "Invalid Unit", "Select pcs, box, set, or unit for consumables.",
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
        if not messagebox.askyesno("Confirm Request",
                                   f"Request {quantity} unit(s) of '{self.item.item_name}'?",
                                   parent=self.modal):
            return
        try:
            RequestRepository().add_request(
                self.item.item_id, current_user["user_id"], quantity, due_date
            )
            
            messagebox.showinfo("Success",
                              f"Request for '{self.item.item_name}' has been submitted.")
            self.modal.destroy()
            
            dashboard.requests = load_my_requests()
            dashboard._load_items_cards()
            
        except (ValueError, Exception) as e:
            messagebox.showerror("Error", f"Failed to submit request: {e}",
                               parent=self.modal)
dashboard = UserDashboard()
app.mainloop()
