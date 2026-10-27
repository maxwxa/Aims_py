import os
import subprocess
import sys
import customtkinter as ctk
import mysql.connector

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime
from tkinter import filedialog, ttk, messagebox
from PIL import Image
from tkcalendar import DateEntry
from models.users import Session
from repositories import (
    InventoryRepository, CategoryRepository, RequestRepository, TransactionRepository,
    UserRepository, AnalyticsRepository,
)
from models.inventory import InventoryItem, Category
from models.account_validation import validate_new_account, validate_password

ctk.set_appearance_mode("light")
app = ctk.CTk()
app.geometry("1920x1080")
app.title("Academic Inventory Management System - Admin Dashboard")
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

if current_user.get("role", "").lower() != "admin":
    messagebox.showerror("Unauthorized", "You do not have admin permissions.")
    Session.clear()
    app.destroy()
    subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "main.py")])
    sys.exit()

DARK_BLUE = "#1c3b7a"
BG_BLUE = "#eef2ff"
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"
RED = "#ef4444"
MODAL_BG = "#0b1b42"
MODAL_FONT = ("Segoe UI", 12)
MODAL_TITLE_FONT = ("Segoe UI", 22, "bold")
GREEN = "#84cc16"
BLUE = "#1d4ed8"
PURPLE = "#9333ea"

main_bg = ctk.CTkFrame(app, fg_color=BG_BLUE, corner_radius=0)
main_bg.pack(fill="both", expand=True)

header_frame = ctk.CTkFrame(main_bg, height=70, fg_color=DARK_BLUE, corner_radius=0)
header_frame.pack(fill="x", side="top")

logo_path = r"C:\Users\maxwx\OneDrive\Documents\SDF04-Aims\Assets\Aims_plain_white.png"
try:
    if os.path.exists(logo_path):
        logo_img = ctk.CTkImage(light_image=Image.open(logo_path), size=(50, 50))
        ctk.CTkLabel(header_frame, image=logo_img, text="").place(x=20, y=15)
except Exception:
    ctk.CTkLabel(header_frame, text="[LOGO]", text_color=WHITE, font=("Arial", 16, "bold")).place(x=20, y=25)

ctk.CTkLabel(header_frame, text="Greetings, Admin", font=("Arial", 24, "bold"),
             text_color=WHITE).pack(side="left", padx=(90, 0), pady=16)

def logout():
    LogoutConfirmationModal(app)
logout_btn = ctk.CTkButton(header_frame, text="Log out", width=100, height=35, fg_color=RED, hover_color="#dc2626", corner_radius=8, font=("Arial", 14, "bold"), command=logout)
logout_btn.pack(side="right", padx=20, pady=17)
nav_frame = ctk.CTkFrame(main_bg, height=60, fg_color=WHITE, corner_radius=20)
nav_frame.pack(fill="x", padx=20, pady=15)
nav_frame.grid_columnconfigure(0, weight=1)
nav_frame.grid_columnconfigure(6, weight=1)
tabs = ["Analytics", "Inventory", "Requests", "Transactions", "Accounts"]
nav_buttons_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
nav_buttons_frame.grid(row=0, column=1, sticky="ew", pady=12)
nav_buttons_frame.grid_columnconfigure(tuple(range(len(tabs))), weight=1)

nav_buttons = {}
for i, tab in enumerate(tabs):
    bg_color = DARK_BLUE if tab == "Analytics" else TEXT_BLUE
    btn = ctk.CTkButton(
        nav_buttons_frame,
        text=tab,
        width=200,
        height=50,
        fg_color=bg_color,
        corner_radius=6,
        font=("Arial", 18, "bold"),
        command=lambda selected_tab=tab: show_tab(selected_tab),
    )
    btn.grid(row=0, column=i, padx=4, sticky="ew")
    nav_buttons[tab] = btn

def create_analytics_tab(parent_frame):
    repository = AnalyticsRepository()
    frame = ctk.CTkScrollableFrame(parent_frame, fg_color=BG_BLUE, corner_radius=0)
    frame.pack(fill="both", expand=True)
    
    # --- SUMMARY CARDS (2 Rows, 3 Columns) ---
    cards = ctk.CTkFrame(frame, fg_color="transparent")
    cards.pack(fill="x", padx=20, pady=(20, 10))
    for column in range(3):
        cards.grid_columnconfigure(column, weight=1)

    card_values = {}
    card_configs = (
        ("total_stock", "Total Items"),
        ("pending_requests", "Pending Requests"),
        ("active_users", "Active Users"),
        ("active_requests", "Active Requests"), 
        ("out_of_stock_count", "Out of Stock Count"),
        ("due_for_return_count", "Due for Return Count")
    )
    
    for index, (key, title) in enumerate(card_configs):
        row = index // 3
        column = index % 3
        card = ctk.CTkFrame(cards, fg_color=WHITE, corner_radius=8,
                            border_width=1, border_color="#d1d5db")
        card.grid(row=row, column=column, sticky="ew", padx=5, pady=(0 if row == 0 else 10))
        ctk.CTkLabel(card, text=title, text_color=TEXT_BLUE,
                     font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(12, 2))
        value = ctk.CTkLabel(card, text="0", text_color=TEXT_BLUE,
                             font=("Arial", 26, "bold"))
        value.pack(anchor="w", padx=15, pady=(0, 12))
        card_values[key] = value

    charts = ctk.CTkFrame(frame, fg_color="transparent")
    charts.pack(fill="x", padx=20, pady=10)
    charts.grid_columnconfigure((0, 1), weight=1)
    
    left_chart = ctk.CTkFrame(charts, fg_color=WHITE, corner_radius=8,
                              border_width=1, border_color="#d1d5db", height=250)
    right_chart = ctk.CTkFrame(charts, fg_color=WHITE, corner_radius=8,
                               border_width=1, border_color="#d1d5db", height=250)
    left_chart.pack_propagate(False)
    right_chart.pack_propagate(False)
    left_chart.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
    right_chart.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

    alerts = ctk.CTkFrame(frame, fg_color="transparent")
    alerts.pack(fill="x", padx=20, pady=(0, 10))
    alerts.grid_columnconfigure((0, 1), weight=1)
    
    oos_frame = ctk.CTkFrame(alerts, fg_color=WHITE, corner_radius=8, border_width=1, border_color="#f87171")
    oos_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
    ctk.CTkLabel(oos_frame, text="Out of Stock Items", text_color="#dc2626", font=("Arial", 14, "bold")).pack(pady=(10, 5))
    oos_list = ctk.CTkScrollableFrame(oos_frame, fg_color="transparent", height=120)
    oos_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    due_frame = ctk.CTkFrame(alerts, fg_color=WHITE, corner_radius=8, border_width=1, border_color="#fbbf24")
    due_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
    ctk.CTkLabel(due_frame, text="Items Due for Return", text_color="#d97706", font=("Arial", 14, "bold")).pack(pady=(10, 5))
    due_list = ctk.CTkScrollableFrame(due_frame, fg_color="transparent", height=120)
    due_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    log_header = ctk.CTkFrame(frame, height=38, fg_color="#1c3b7a", corner_radius=8)
    log_header.pack(fill="x", padx=20, pady=(10, 0))
    log_header.pack_propagate(False)
    
    ctk.CTkLabel(log_header, text="Recent System Activity", text_color=WHITE,
                 font=("Arial", 14, "bold")).pack(side="left", padx=15)
                 
    ctk.CTkButton(log_header, text="Refresh", width=80, height=26,
                  fg_color=WHITE, text_color="#1c3b7a", command=lambda: refresh()).pack(
        side="right", padx=(5, 10), pady=6)
        
    action_var = ctk.StringVar(value="All Actions")
    action_dropdown = ctk.CTkOptionMenu(log_header, variable=action_var, width=120, height=26,
                                        values=["All Actions", "INSERT", "UPDATE", "DELETE"],
                                        fg_color=WHITE, text_color="black", button_color="#d1d5db",
                                        command=lambda e: filter_logs())
    action_dropdown.pack(side="right", padx=5, pady=6)
    
    search_var = ctk.StringVar()
    search_entry = ctk.CTkEntry(log_header, placeholder_text="Search logs...", 
                                textvariable=search_var, width=150, height=26,
                                fg_color=WHITE, text_color="black")
    search_entry.pack(side="right", padx=5, pady=6)
    search_entry.bind("<KeyRelease>", lambda e: filter_logs())

    logs = ctk.CTkScrollableFrame(frame, fg_color=WHITE, corner_radius=8, height=250)
    logs.pack(fill="x", padx=20, pady=20)

    current_logs_data = []

    def filter_logs():
        for widget in logs.winfo_children():
            widget.destroy()
            
        headers = ("Log ID", "User", "Action", "Table", "ID", "Date/Time")
        for column, title in enumerate(headers):
            ctk.CTkLabel(logs, text=title, fg_color="#dbeafe",
                         text_color=TEXT_BLUE, anchor="w").grid(
                row=0, column=column, sticky="ew", padx=1, pady=1)
            logs.grid_columnconfigure(column, weight=1, minsize=90)
            
        search_term = search_var.get().lower()
        active_action = action_var.get()
        
        row_index = 1
        for row in current_logs_data:
            log_id = str(row.get("log_id") or "")
            user = str(row.get("user") or row.get("user_id") or "")
            action = str(row.get("action") or "").upper()
            table = str(row.get("table_affected") or "")
            timestamp = str(row.get("timestamp") or "")
            
            target_id = str(row.get("item_id") or row.get("id") or "")
            target_name = str(row.get("item_name") or row.get("name") or "")
            desc = f"{target_id}" if target_id or target_name else str(row.get("description") or "")
            
            if active_action != "All Actions" and active_action != action: continue
            if search_term and search_term not in f"{log_id} {user} {action} {table} {desc} {timestamp}".lower(): continue
                
            values = (log_id, user, action, table, desc, timestamp)
            for column, value in enumerate(values):
                ctk.CTkLabel(logs, text=value, fg_color=WHITE, text_color="black", anchor="w").grid(
                    row=row_index, column=column, sticky="ew", padx=1, pady=1)
            row_index += 1

    def refresh():
        nonlocal current_logs_data
        try:
            stats = repository.get_summary_stats()
            for key, label in card_values.items():
                label.configure(text=str(stats.get(key, "0")))
            for widget in oos_list.winfo_children(): widget.destroy()
            for widget in due_list.winfo_children(): widget.destroy()
            
            oos_items = repository.get_out_of_stock_items() 
            due_items = repository.get_due_items()
            if not oos_items:
                ctk.CTkLabel(oos_list, text="No items out of stock.", text_color="gray").pack(pady=10)
            else:
                for item in oos_items:
                    card = ctk.CTkFrame(oos_list, fg_color="#f3f4f6", corner_radius=6)
                    card.pack(fill="x", pady=2, padx=2)
                    
                    img_path = item.get("image_path") # Update key to match your DB column
                    ctk_img = None
                    if img_path and os.path.exists(img_path):
                        try:
                            ctk_img = ctk.CTkImage(light_image=Image.open(img_path), size=(40, 40))
                        except Exception:
                            pass
                            
                    img_label = ctk.CTkLabel(card, text="No Img" if not ctk_img else "", image=ctk_img, 
                                             width=40, height=40, fg_color="#e5e7eb", corner_radius=4)
                    img_label.pack(side="left", padx=5, pady=5)
                    
                    details = ctk.CTkFrame(card, fg_color="transparent")
                    details.pack(side="left", fill="x", expand=True, padx=(5, 5))
                    ctk.CTkLabel(details, text=item.get("item_name", "Unknown"), font=("Arial", 12, "bold"), text_color="black", anchor="w").pack(fill="x")
                    ctk.CTkLabel(details, text=f"ID: {item.get('item_id', 'N/A')} | Stock: {item.get('stock', 0)}", font=("Arial", 10), text_color="gray", anchor="w").pack(fill="x")

            if not due_items:
                ctk.CTkLabel(due_list, text="No items currently due.", text_color="gray").pack(pady=10)
            else:
                for item in due_items:
                    card = ctk.CTkFrame(due_list, fg_color="#f3f4f6", corner_radius=6)
                    card.pack(fill="x", pady=2, padx=2)
                    
                    img_path = item.get("image_path")
                    ctk_img = None
                    if img_path and os.path.exists(img_path):
                        try:
                            ctk_img = ctk.CTkImage(light_image=Image.open(img_path), size=(40, 40))
                        except Exception:
                            pass
                            
                    img_label = ctk.CTkLabel(card, text="No Img" if not ctk_img else "", image=ctk_img, 
                                             width=40, height=40, fg_color="#e5e7eb", corner_radius=4)
                    img_label.pack(side="left", padx=5, pady=5)
                    
                    details = ctk.CTkFrame(card, fg_color="transparent")
                    details.pack(side="left", fill="x", expand=True, padx=(5, 5))
                    ctk.CTkLabel(details, text=item.get("item_name", "Unknown"), font=("Arial", 12, "bold"), text_color="black", anchor="w").pack(fill="x")
                    ctk.CTkLabel(details, text=f"Req ID: {item.get('request_id', 'N/A')} | Due: {item.get('due_date', 'Unknown')}", font=("Arial", 10), text_color="#d97706", anchor="w").pack(fill="x")

            top_items = repository.get_top_requested_items()
            category_data = repository.get_category_request_distribution()
            
            for widget in left_chart.winfo_children() + right_chart.winfo_children():
                widget.destroy()
                
            item_names = [row["item_name"] for row in top_items]
            item_counts = [row["request_count"] for row in top_items]
            figure1 = Figure(figsize=(4, 2.2), dpi=90)
            figure1.patch.set_alpha(0)
            axis1 = figure1.add_subplot(111)
            axis1.bar(item_names, item_counts, color="#1c3b7a")
            axis1.set_title("Most Requested Items")
            axis1.tick_params(axis="x", rotation=25, labelsize=8)
            figure1.tight_layout()
            canvas1 = FigureCanvasTkAgg(figure1, master=left_chart)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
            
            labels = [row["category_name"] for row in category_data]
            counts = [row["request_count"] for row in category_data]
            figure2 = Figure(figsize=(4, 2.2), dpi=90)
            figure2.patch.set_alpha(0)
            axis2 = figure2.add_subplot(111)
            if counts:
                axis2.pie(counts, labels=labels, autopct="%1.1f%%")
            axis2.set_title("Most Requested Categories")
            figure2.tight_layout()
            canvas2 = FigureCanvasTkAgg(figure2, master=right_chart)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
            
            # 4. Logs
            current_logs_data = repository.get_recent_logs()
            filter_logs()
            
        except (ValueError, mysql.connector.Error) as error:
            messagebox.showerror("Analytics Unavailable", str(error))
            
    refresh()
    return frame

content_frame = create_analytics_tab(main_bg)

style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", background=WHITE, foreground="black", rowheight=25, fieldbackground=WHITE, borderwidth=0)
style.configure("Treeview.Heading", background=BG_BLUE, foreground="black", font=('Arial', 10, 'bold'))
style.map('Treeview', background=[('selected', '#dbeafe')])


def create_inventory_tab(parent_frame):
    inventory_repo = InventoryRepository()
    
    inventory_frame = ctk.CTkFrame(parent_frame, fg_color="#a5b4fc", corner_radius=0)
    inventory_frame.pack(fill="both", expand=True)

    header_frame = ctk.CTkFrame(inventory_frame, fg_color="#1e3a8a", height=45, corner_radius=8)
    header_frame.pack(fill="x", padx=20, pady=(20, 0))
    header_frame.pack_propagate(False)

    ctk.CTkLabel(header_frame, text="Items Catalogue", font=("Arial", 14, "bold"), text_color="white").pack(side="left", padx=15)

    search_entry = ctk.CTkEntry(header_frame, width=150, height=30, corner_radius=6, fg_color="white", text_color="black")
    search_entry.pack(side="right", padx=(5, 15), pady=8)
    ctk.CTkLabel(header_frame, text="Search :", font=("Arial", 12, "bold"), text_color="white").pack(side="right", padx=5)

    filter_combo = ctk.CTkComboBox(header_frame, width=120, height=30, corner_radius=6, fg_color="white", text_color="black", button_color="white", values=["All", "Available", "Requested"])
    filter_combo.pack(side="right", padx=(5, 15), pady=8)
    ctk.CTkLabel(header_frame, text="Filter :", font=("Arial", 12, "bold"), text_color="white").pack(side="right", padx=5)

    catalogue_container = ctk.CTkScrollableFrame(inventory_frame, fg_color="white", corner_radius=8)
    catalogue_container.pack(fill="both", expand=True, padx=20, pady=20)
    catalogue_container.grid_columnconfigure((0, 1, 2), weight=1)

    def load_inventory_cards(search_term="", filter_status="All"):
        for widget in catalogue_container.winfo_children():
            widget.destroy()

        try:
            items = inventory_repo.get_all(search_term=search_term, filter_status=filter_status)
        except mysql.connector.Error as error:
            messagebox.showerror(
                "Inventory Unavailable",
                f"Could not load inventory data: {error}",
            )
            return

        for i, item in enumerate(items):
            row = i // 3
            col = i % 3

            card = ctk.CTkFrame(catalogue_container, fg_color="white", border_width=2, border_color="black", corner_radius=0)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(card, text=item.item_name, font=("Arial", 12, "bold"), text_color="black").grid(row=0, column=0, pady=(5, 5))
            
            ctk.CTkFrame(card, height=2, fg_color="black").grid(row=1, column=0, sticky="ew")

            image_frame = ctk.CTkFrame(card, height=120, fg_color="#e5e7eb", corner_radius=0)
            image_frame.grid(row=2, column=0, sticky="nsew")
            
            stock_text = f"Stock: {item.stock}"
            ctk.CTkLabel(image_frame, text=stock_text, font=("Arial", 12, "bold"), text_color="black").place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkFrame(card, height=2, fg_color="black").grid(row=3, column=0, sticky="ew")

            btn_frame = ctk.CTkFrame(card, fg_color="transparent", corner_radius=0)
            btn_frame.grid(row=4, column=0, sticky="ew")
            btn_frame.grid_columnconfigure((0, 1), weight=1)

            view_btn = ctk.CTkButton(btn_frame, text="View Details", fg_color="#1e3a8a", corner_radius=0, command=lambda id=item.item_id: view_details(id))
            view_btn.grid(row=0, column=0, sticky="ew", padx=(0, 1))

            manage_btn = ctk.CTkButton(btn_frame, text="Manage", fg_color="#86efac", text_color="black", hover_color="#4ade80", corner_radius=0, command=lambda id=item.item_id: manage_item(id))
            manage_btn.grid(row=0, column=1, sticky="ew")

    def refresh_data():
        load_inventory_cards(search_term=search_entry.get(), filter_status=filter_combo.get())

    refresh_btn = ctk.CTkButton(header_frame, text="Refresh", width=80, height=30, corner_radius=6, fg_color="white", text_color="black", hover_color="#f3f4f6", font=("Arial", 12, "bold"), command=refresh_data)
    refresh_btn.pack(side="right", padx=(10, 15), pady=8)

    load_inventory_cards()

    bottom_controls = ctk.CTkFrame(inventory_frame, fg_color="transparent")
    bottom_controls.pack(fill="x", padx=20, pady=(0, 20))

    add_btn = ctk.CTkButton(bottom_controls, text="ADD", width=100, height=35, fg_color="#86efac", text_color="black", hover_color="#4ade80", font=("Arial", 14, "bold"), border_width=2, border_color="black", corner_radius=8)
    add_btn.pack(side="left")

    def view_details(item_id):
        print(f"Opening details modal for item ID: {item_id}")

    def manage_item(item_id):
        print(f"Opening manage modal for item ID: {item_id}")
    return inventory_frame


def create_inventory_tab_v2(parent_frame):
    inventory_repo = InventoryRepository()
    category_repo = CategoryRepository()
    inventory_frame = ctk.CTkFrame(parent_frame, fg_color=BG_BLUE, corner_radius=0)
    inventory_frame.pack(fill="both", expand=True)
    header = ctk.CTkFrame(inventory_frame, fg_color=DARK_BLUE, height=45, corner_radius=8)
    header.pack(fill="x", padx=20, pady=(20, 0))
    header.pack_propagate(False)
    ctk.CTkLabel(header, text="Items Catalogue", font=("Arial", 14, "bold"),
                 text_color=WHITE).pack(side="left", padx=15)
    toolbar = ctk.CTkFrame(header, fg_color="transparent")
    toolbar.pack(side="right", padx=20)
    refresh_button = ctk.CTkButton(
        toolbar, text="Refresh", width=80, height=30, fg_color=WHITE,
        text_color="#1c3b7a", hover_color="#e5e7eb", corner_radius=6,
        command=lambda: refresh_inventory(),
    )
    refresh_button.pack(side="left", padx=5)
    filter_combo = ctk.CTkComboBox(
        toolbar, width=120, height=30, values=["All"],
        fg_color=WHITE, text_color="black", button_color=WHITE, corner_radius=6,
        command=lambda _val=None: load_inventory_cards(),
    )
    filter_combo.set("All")
    filter_combo.pack(side="left", padx=5)
    filter_combo.bind("<<ComboboxSelected>>", lambda _event=None: load_inventory_cards())
    search = ctk.CTkEntry(
        toolbar, width=150, height=30, fg_color=WHITE, text_color="black",
        corner_radius=6, placeholder_text="Search",
    )
    search.pack(side="left", padx=5)
    search.bind("<KeyRelease>", lambda _event=None: load_inventory_cards())
    cards = ctk.CTkScrollableFrame(inventory_frame, fg_color=WHITE, corner_radius=8)
    cards.pack(fill="both", expand=True, padx=20, pady=20)
    cards.grid_columnconfigure((0, 1, 2), weight=1)

    def value_text(value):
        return "" if value is None else str(value)

    def modal_text(parent, label, value="", height=36, readonly=False):
        ctk.CTkLabel(parent, text=label, text_color=WHITE,
                     font=MODAL_FONT).pack(anchor="w", pady=(5, 2))
        widget = (
            ctk.CTkTextbox(parent, height=height, corner_radius=8)
            if height > 36 else ctk.CTkEntry(parent, corner_radius=8)
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

    def modal_heading(parent, title, subtitle=""):
        ctk.CTkLabel(
            parent, text=title, text_color=WHITE, font=MODAL_TITLE_FONT
        ).pack(anchor="w", pady=(0, 2))
        if subtitle:
            ctk.CTkLabel(
                parent, text=subtitle, text_color="#bfdbfe", font=("Segoe UI", 10)
            ).pack(anchor="w", pady=(0, 14))

    def text_value(widget):
        return widget.get("1.0", "end-1c") if isinstance(widget, ctk.CTkTextbox) else widget.get()

    def date_value(raw):
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

    def create_category(parent, on_created):
        modal = ctk.CTkToplevel(parent)
        modal.title("Create Category")
        modal.geometry("400x450")
        modal.configure(fg_color=MODAL_BG)
        modal.transient(parent)
        modal.grab_set()
        modal.protocol("WM_DELETE_WINDOW", lambda: None)
        body = ctk.CTkFrame(modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=(24, 20))
        modal_heading(body, "Create Category", "Add a category for inventory items.")
        name = modal_text(body, "Category Name")
        description = modal_text(body, "Category Description", height=90)
        requires = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(body, text="Requires return", variable=requires,
                        text_color=WHITE, font=MODAL_FONT,
                        checkbox_width=20, checkbox_height=20).pack(anchor="w", pady=(10, 0))

        def save():
            category_name = name.get().strip()
            if not category_name:
                messagebox.showwarning("Validation", "Category name is required.", parent=modal)
                return
            try:
                category_repo.add(Category(0, category_name,
                                            text_value(description).strip(), requires.get()))
                modal.destroy()
                on_created(category_name)
            except (ValueError, mysql.connector.Error) as error:
                messagebox.showerror("Category Error", str(error), parent=modal)

        actions = ctk.CTkFrame(body, fg_color="transparent")
        actions.pack(fill="x", pady=18)
        ctk.CTkButton(actions, text="Cancel", width=100, height=36, command=modal.destroy,
                      fg_color=RED, corner_radius=8).pack(side="left", padx=(0, 5))
        ctk.CTkButton(actions, text="Create", width=100, height=36, command=save,
                      fg_color=GREEN, corner_radius=8).pack(side="right", padx=(5, 0))

    def edit_category(parent, category, on_updated):
        modal = ctk.CTkToplevel(parent)
        modal.title("Edit Category")
        modal.geometry("400x450")
        modal.configure(fg_color=MODAL_BG)
        modal.transient(parent)
        modal.grab_set()
        modal.protocol("WM_DELETE_WINDOW", lambda: None)
        body = ctk.CTkFrame(modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=(24, 20))
        modal_heading(body, "Edit Category", "Update the category details.")
        name = modal_text(body, "Category Name", category.category_name)
        description = modal_text(
            body, "Category Description", category.category_desc, height=90
        )
        requires = ctk.BooleanVar(value=category.requires_return)
        ctk.CTkCheckBox(
            body, text="Requires return", variable=requires,
            text_color=WHITE, font=MODAL_FONT,
            checkbox_width=20, checkbox_height=20,
        ).pack(anchor="w", pady=(10, 0))

        def save():
            category_name = name.get().strip()
            if not category_name:
                messagebox.showwarning(
                    "Validation", "Category name is required.", parent=modal
                )
                return
            if not messagebox.askyesno(
                "Update Category",
                "Would you like to update this category?",
                parent=modal,
            ):
                return
            try:
                category_repo.update(Category(
                    category.category_id, category_name,
                    text_value(description).strip(), requires.get(),
                ))
                modal.destroy()
                on_updated(category_name)
            except (ValueError, mysql.connector.Error) as error:
                messagebox.showerror("Category Error", str(error), parent=modal)

        actions = ctk.CTkFrame(body, fg_color="transparent")
        actions.pack(fill="x", pady=18)
        ctk.CTkButton(
            actions, text="Cancel", width=100, height=36,
            command=modal.destroy, fg_color=RED, corner_radius=8,
        ).pack(side="left", padx=(0, 5))
        ctk.CTkButton(
            actions, text="Save", width=100, height=36,
            command=save, fg_color=GREEN, corner_radius=8,
        ).pack(side="right", padx=(5, 0))

    def select_category():
        modal = ctk.CTkToplevel(app)
        modal.title("Select Category")
        modal.geometry("500x480")
        modal.configure(fg_color=MODAL_BG)
        modal.transient(app)
        modal.grab_set()
        modal.protocol("WM_DELETE_WINDOW", lambda: None)
        body = ctk.CTkFrame(modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=(24, 20))
        modal_heading(body, "Select Category", "Choose the category for the new item.")
        selected = {"category": None}
        dropdown = ctk.CTkComboBox(body, values=[], corner_radius=8,
                                   font=MODAL_FONT, dropdown_font=MODAL_FONT,
                                   fg_color=WHITE, text_color="black",
                                   button_color=WHITE, dropdown_fg_color=WHITE)
        ctk.CTkLabel(body, text="Category Name", text_color=WHITE,
                     font=MODAL_FONT).pack(anchor="w", pady=(0, 4))
        dropdown.pack(fill="x", pady=(0, 8))
        description = ctk.CTkTextbox(body, height=90, corner_radius=8,
                                     fg_color=WHITE, text_color="black")
        ctk.CTkLabel(body, text="Description", text_color=WHITE,
                     font=MODAL_FONT).pack(anchor="w", pady=(0, 4))
        description.pack(fill="x", pady=(0, 8))
        description.configure(state="disabled")
        return_label = ctk.CTkLabel(body, text="Requires return: -",
                                     text_color=WHITE, font=MODAL_FONT)
        return_label.pack(anchor="w", pady=(0, 8))
        def refresh(selected_name="", clear_selection=False):
            try:
                categories = category_repo.get_all()
            except (ValueError, mysql.connector.Error) as error:
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
            return_label.configure(text="Requires return: " +
                                   ("Yes" if category and category.requires_return else "No"))

        def edit_selected():
            category = selected["category"]
            if category is None:
                messagebox.showwarning(
                    "Edit Category", "Choose a valid category first.", parent=modal
                )
                return
            edit_category(modal, category, refresh)

        def delete_selected():
            category = selected["category"]
            if category is None:
                messagebox.showwarning(
                    "Delete Category", "Choose a valid category first.", parent=modal
                )
                return
            try:
                if category_repo.has_inventory_items(category.category_id):
                    messagebox.showwarning(
                        "Delete Category",
                        "This category cannot be deleted because inventory items "
                        "are assigned to it.",
                        parent=modal,
                    )
                    return
            except mysql.connector.Error as error:
                messagebox.showerror("Category Error", str(error), parent=modal)
                return
            if not messagebox.askyesno(
                "Delete Category",
                "Are you sure you want to delete this category?",
                parent=modal,
            ):
                return
            try:
                category_repo.delete(category.category_id)
                refresh(clear_selection=True)
            except (ValueError, mysql.connector.Error) as error:
                messagebox.showerror("Category Error", str(error), parent=modal)

        def changed(display):
            refresh(display)

        dropdown.configure(command=changed)
        refresh()

        def proceed():
            if selected["category"] is None:
                messagebox.showwarning("Select Category", "Choose a valid category first.",
                                       parent=modal)
                return
            modal.destroy()
            item_form(category=selected["category"])

        category_actions = ctk.CTkFrame(body, fg_color="transparent")
        category_actions.pack(fill="x", pady=(18, 8))
        category_actions.grid_columnconfigure((0, 1, 2), weight=1, uniform="category_action")
        ctk.CTkButton(
            category_actions, text="Create New Category", height=36,
            command=lambda: create_category(modal, refresh),
            fg_color=PURPLE, corner_radius=8,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ctk.CTkButton(
            category_actions, text="Edit Category", height=36,
            command=edit_selected, fg_color="#f59e0b", corner_radius=8,
        ).grid(row=0, column=1, sticky="ew", padx=4)
        ctk.CTkButton(
            category_actions, text="Delete Category", height=36,
            command=delete_selected, fg_color=RED, corner_radius=8,
        ).grid(row=0, column=2, sticky="ew", padx=(4, 0))

        actions = ctk.CTkFrame(body, fg_color="transparent")
        actions.pack(fill="x", pady=(0, 18))
        actions.grid_columnconfigure((0, 1), weight=1, uniform="navigation_action")
        ctk.CTkButton(
            actions, text="Cancel", height=36, command=modal.destroy,
            fg_color=RED, corner_radius=8,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ctk.CTkButton(
            actions, text="Proceed", height=36, command=proceed,
            fg_color=GREEN, corner_radius=8,
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0))

    def item_form(item=None, category=None, manage=False):
        category = category or next((c for c in category_repo.get_all()
                                     if c.category_id == item.category_id), None)
        if category is None:
            messagebox.showerror("Category Error", "The item's category no longer exists.")
            return
        modal = ctk.CTkToplevel(app)
        modal.title("Manage" if manage else "Item Information")
        modal.geometry("400x600")
        modal.configure(fg_color=MODAL_BG)
        modal.transient(app)
        modal.grab_set()
        body = ctk.CTkScrollableFrame(modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=(24, 20))
        modal_heading(
            body, "Manage" if manage else "Item Information",
            "Update the item details below." if manage else "Add a new inventory item.",
        )
        now = datetime.now()
        item_id = item.item_id if item else inventory_repo.next_id()
        top = ctk.CTkFrame(body, fg_color="transparent")
        top.pack(fill="x", pady=(0, 10))
        selected_category = {"value": category}
        category_dropdown = None
        category_name_label = None
        preview_column = ctk.CTkFrame(top, fg_color="transparent", width=220)
        preview_column.pack(anchor="center")
        preview = ctk.CTkFrame(preview_column, width=220, height=180, fg_color=WHITE,
                               corner_radius=8)
        preview.pack()
        preview.pack_propagate(False)
        preview_label = ctk.CTkLabel(
            preview, text="Image Preview", text_color="black", font=MODAL_FONT
        )
        preview_label.pack(pady=(10, 10), anchor="center", expand=True)
        ctk.CTkButton(
            preview, text="Select Image", command=lambda: choose_image(),
            fg_color=BLUE, corner_radius=8,
        ).pack(fill="x", padx=10, pady=(0, 10), anchor="center")
        ctk.CTkLabel(preview_column, text=f"Item ID: {item_id}", text_color=WHITE,
                     font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(8, 4))
        if manage:
            ctk.CTkLabel(preview_column, text="Category", text_color=WHITE,
                         font=MODAL_FONT).pack(anchor="w", pady=(0, 4))
            category_dropdown = ctk.CTkComboBox(
                preview_column,
                values=[f"{c.category_id} - {c.category_name}" for c in category_repo.get_all()],
                corner_radius=8, font=MODAL_FONT, dropdown_font=MODAL_FONT,
                fg_color=WHITE, text_color="black",
                button_color=WHITE, dropdown_fg_color=WHITE,
            )
            category_dropdown.pack(fill="x", pady=(0, 6))
            category_dropdown.set(f"{category.category_id} - {category.category_name}")
            category_name_label = ctk.CTkLabel(
                preview_column, text=f"Category Name: {category.category_name}",
                text_color=WHITE, font=MODAL_FONT,
            )
            category_name_label.pack(anchor="w", pady=(0, 6))
        else:
            ctk.CTkLabel(preview_column, text=f"Category: {category.category_id} - "
                         f"{category.category_name}", text_color=WHITE,
                         font=MODAL_FONT).pack(anchor="w", pady=(0, 6))
        name = modal_text(body, "Item Name", value_text(item.item_name if item else ""))
        code = modal_text(body, "Item Code", value_text(item.item_code if item else ""))
        description = modal_text(body, "Description",
                                 value_text(item.description if item else ""), height=70)
        stock = modal_text(body, "Stock", value_text(item.stock if item else 1))
        serial_frame = ctk.CTkFrame(body, fg_color="transparent")
        serial = modal_text(
            serial_frame, "Serial No.", value_text(item.serial_no if item else "")
        )
        serial_enabled = ctk.BooleanVar(value=bool(item and item.serial_no))
        serial_row = ctk.CTkFrame(body, fg_color="transparent")
        serial_row.pack(fill="x", pady=(8, 0))
        ctk.CTkCheckBox(
            serial_row, text="Serial No.", variable=serial_enabled,
            text_color=WHITE, font=MODAL_FONT, checkbox_width=20,
            checkbox_height=20,
        ).pack(anchor="w")
        unit = ctk.CTkComboBox(body, values=["pcs", "box", "set", "unit"],
                               corner_radius=8, font=MODAL_FONT,
                               dropdown_font=MODAL_FONT,
                               fg_color=WHITE, text_color="black",
                               button_color=WHITE, dropdown_fg_color=WHITE)
        ctk.CTkLabel(body, text="Unit", text_color=WHITE,
                     font=MODAL_FONT).pack(anchor="w", pady=(0, 4))
        unit.pack(fill="x", pady=(0, 6))
        unit.set(value_text(item.unit if item else "pcs") or "pcs")
        expiration_frame = ctk.CTkFrame(body, fg_color="transparent")
        expiration = modal_text(
            expiration_frame, "Expiration Date (YYYY-MM-DD)",
            value_text(item.expiration_date if item else ""),
        )
        perishable = ctk.BooleanVar(value=bool(item and item.expiration_date))
        perishable_row = ctk.CTkFrame(body, fg_color="transparent")
        perishable_row.pack(fill="x", pady=(8, 0))
        ctk.CTkCheckBox(
            perishable_row, text="Perishable Item", variable=perishable,
            text_color=WHITE, font=MODAL_FONT, checkbox_width=20,
            checkbox_height=20,
        ).pack(anchor="w")
        expiration_frame.pack(fill="x", before=perishable_row)
        image_path = {"value": value_text(item.image_path if item else "")}

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
                c for c in category_repo.get_all() if c.category_id == category_id
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
            path = filedialog.askopenfilename(parent=modal,
                                              filetypes=[("Images", "*.png *.jpg *.jpeg")])
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
                image_preview = ctk.CTkImage(
                    light_image=source, dark_image=source, size=(190, 135)
                )
                preview_label.configure(image=image_preview, text="")
                preview_label.image = image_preview
            except (OSError, ValueError) as error:
                preview_label.configure(image=None, text="Unable to load image")
                preview_label.image = None
                messagebox.showwarning(
                    "Image Preview", f"Could not load the selected image: {error}",
                    parent=modal,
                )

        set_image_preview(image_path["value"])

        def save():
            try:
                current_category = selected_category["value"]
                stock_text = stock.get().strip()
                if not stock_text.isascii() or not stock_text.isdigit():
                    messagebox.showwarning(
                        "Invalid Stock",
                        "Stock must contain whole numbers only.",
                        parent=modal,
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
                        "Missing Information",
                        "Item name and item code are required.",
                        parent=modal,
                    )
                    return
                exclude_id = item_id if manage else 0
                if inventory_repo.exists_duplicate(
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
                    item_id, current_category.category_id, name_value, code_value,
                    text_value(description).strip(), stock_value, serial_value,
                    date_value(expiration.get() if perishable.get() else ""), timestamp,
                    item.added_date if item else timestamp, unit.get(), image_path["value"],
                    current_category.category_name, current_category.requires_return,
                )
                if messagebox.askyesno("Confirm", "Save this inventory item?", parent=modal):
                    (inventory_repo.update(entity) if manage else inventory_repo.add(entity))
                    modal.destroy()
                    load_inventory_cards()
            except (ValueError, mysql.connector.Error) as error:
                messagebox.showerror("Inventory Error", str(error), parent=modal)

        def delete_item():
            if not item or not messagebox.askyesno(
                "Delete Item", "Delete this inventory item?", parent=modal
            ):
                return
            try:
                inventory_repo.delete(item.item_id)
                modal.destroy()
                load_inventory_cards()
            except (ValueError, mysql.connector.Error) as error:
                messagebox.showerror("Inventory Error", str(error), parent=modal)

        buttons = ctk.CTkFrame(body, fg_color="transparent")
        buttons.pack(fill="x", pady=(16, 0))

        def cancel_item_form():
            if manage:
                modal.destroy()
                return
            if messagebox.askyesno(
                "Cancel Item",
                "Would you like to cancel?",
                parent=modal,
            ):
                modal.destroy()
                select_category()

        ctk.CTkButton(buttons, text="Update" if manage else "Submit", width=110, height=36, command=save,
                      fg_color=GREEN if manage else BLUE,
                      corner_radius=8).pack(side="right", padx=(0, 6))
        if manage:
            ctk.CTkButton(buttons, text="Delete", width=110, height=36, command=lambda: delete_item(),
                          fg_color=RED, corner_radius=8).pack(side="right", padx=(0, 6))
        ctk.CTkButton(buttons, text="Cancel", width=110, height=36, command=cancel_item_form,
                      fg_color=RED, corner_radius=8).pack(side="left")

    def show_details(item_id):
        item = inventory_repo.get_by_id(item_id)
        if not item:
            messagebox.showerror("Inventory", "Item could not be found.")
            return
        modal = ctk.CTkToplevel(app)
        modal.title("Item Details")
        modal.geometry("600x500")
        modal.configure(fg_color=MODAL_BG)
        modal.transient(app)
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
            preview, text="Image Preview", text_color="black", font=MODAL_FONT
        )
        preview_label.pack(anchor="center", expand=True)
        if item.image_path and os.path.isfile(item.image_path):
            try:
                source = Image.open(item.image_path)
                image_preview = ctk.CTkImage(
                    light_image=source, dark_image=source, size=(240, 280)
                )
                preview_label.configure(image=image_preview, text="")
                preview_label.image = image_preview
            except (OSError, ValueError):
                pass
        card = ctk.CTkFrame(content, fg_color=MODAL_BG, corner_radius=8,
                            border_width=1, border_color="#334b80")
        card.grid(row=0, column=1, sticky="nsew")
        details = ctk.CTkTextbox(card, corner_radius=8,
                                 fg_color=WHITE, text_color="black")
        details.pack(fill="both", expand=True, padx=14, pady=14)
        details.insert("1.0", "\n".join(
            f"{key.replace('_', ' ').title()}: {value}"
            for key, value in item.to_dict().items()
        ))
        details.configure(state="disabled")
        ctk.CTkButton(
            modal, text="Close", width=110, height=36, fg_color=BLUE,
            command=modal.destroy,
        ).pack(anchor="e", padx=24, pady=(0, 18))

    def manage(item_id):
        item = inventory_repo.get_by_id(item_id)
        if item:
            item_form(item=item, manage=True)

    def load_categories_filter():
        try:
            categories = category_repo.get_all()
            values = ["All"] + [category.category_name for category in categories]
            filter_combo.configure(values=values)
            if filter_combo.get() not in values:
                filter_combo.set("All")
        except (ValueError, mysql.connector.Error):
            pass

    def refresh_inventory():
        load_categories_filter()
        load_inventory_cards()

    def load_inventory_cards():
        for widget in cards.winfo_children():
            widget.destroy()
        try:
            items = inventory_repo.get_all(search_term=search.get())
            filter_category = filter_combo.get()
            if filter_category and filter_category not in ("All", "All Categories"):
                items = [item for item in items if item.category_name == filter_category]
        except (ValueError, mysql.connector.Error) as error:
            messagebox.showerror("Inventory Unavailable", str(error))
            return
        for index, item in enumerate(items):
            card = ctk.CTkFrame(cards, fg_color=WHITE, border_width=2, border_color="black")
            card.grid(row=index // 3, column=index % 3, padx=10, pady=10, sticky="nsew")
            ctk.CTkLabel(card, text=item.item_name, text_color="black",
                         font=("Arial", 12, "bold")).pack(pady=8)
            image_frame = ctk.CTkFrame(card, width=150, height=120,
                                       fg_color="#e5e7eb", corner_radius=8)
            image_frame.pack(fill="x", padx=8)
            image_frame.pack_propagate(False)
            image_label = ctk.CTkLabel(image_frame, text="No image",
                                       text_color="black")
            image_label.pack(expand=True)
            if item.image_path and os.path.isfile(item.image_path):
                try:
                    source = Image.open(item.image_path)
                    card_image = ctk.CTkImage(
                        light_image=source, dark_image=source, size=(150, 120)
                    )
                    image_label.configure(image=card_image, text="")
                    image_label.image = card_image
                except (OSError, ValueError):
                    pass
            ctk.CTkLabel(card, text=f"Stock: {item.stock}", text_color="black").pack()
            ctk.CTkButton(card, text="View Details",
                          command=lambda item_id=item.item_id: show_details(item_id)).pack(
                              fill="x", padx=8, pady=(8, 2))
            ctk.CTkButton(card, text="Manage", fg_color="#86efac", text_color="black",
                          command=lambda item_id=item.item_id: manage(item_id)).pack(
                              fill="x", padx=8, pady=(2, 8))

    ctk.CTkButton(inventory_frame, text="ADD", width=100, command=select_category,
                  fg_color="#86efac", text_color="black").pack(anchor="w", padx=20, pady=(0, 20))
    load_categories_filter()
    load_inventory_cards()
    return inventory_frame

inventory_frame = create_inventory_tab_v2(main_bg)
inventory_frame.pack_forget()


def create_requests_tab(parent_frame):
    request_repo = RequestRepository()
    requests_frame = ctk.CTkFrame(parent_frame, fg_color=BG_BLUE, corner_radius=0)
    requests_frame.pack(fill="both", expand=True)

    header = ctk.CTkFrame(requests_frame, height=45, fg_color="#1c3b7a", corner_radius=8)
    header.pack(fill="x", padx=20, pady=(20, 0))
    header.pack_propagate(False)
    ctk.CTkLabel(header, text="Requests", font=("Arial", 16, "bold"),
                 text_color=WHITE).pack(side="left", padx=15)

    toolbar_frame = ctk.CTkFrame(header, fg_color="transparent")
    toolbar_frame.pack(side="right", padx=20)
    refresh_button = ctk.CTkButton(
        toolbar_frame, text="Refresh", width=80, height=30, fg_color=WHITE,
        text_color="#1c3b7a", hover_color="#e5e7eb", corner_radius=6,
    )
    refresh_button.pack(side="left", padx=5)
    filter_combo = ctk.CTkComboBox(
        toolbar_frame, width=120, height=30, values=["All", "Pending", "Approved",
                                                 "Active"],
        fg_color=WHITE, text_color="black", button_color=WHITE, corner_radius=6,
    )
    filter_combo.set("All")
    filter_combo.pack(side="left", padx=5)
    search_entry = ctk.CTkEntry(
        toolbar_frame, width=150, height=30, fg_color=WHITE, text_color="black",
        corner_radius=6, placeholder_text="Search",
    )
    search_entry.pack(side="left", padx=5)
    column_specs = (
        (0, 1, 100), (1, 2, 150), (2, 1, 100), (3, 1, 110),
        (4, 2, 180), (5, 1, 140), (6, 1, 130),
    )
    header_frame = ctk.CTkFrame(
        requests_frame, fg_color="#dbeafe", corner_radius=8,
        border_width=1, border_color="#d1d5db",
    )
    header_frame.pack(fill="x", padx=20, pady=(20, 0))
    for column, weight, minsize in column_specs:
        header_frame.grid_columnconfigure(column, weight=weight, minsize=minsize)
    headings = ["Request No.", "Request By", "Code", "Status",
                "Request Details", "Date/Time", "Item Details"]
    for column, heading in enumerate(headings):
        ctk.CTkLabel(
            header_frame, text=heading, fg_color="#dbeafe", text_color=TEXT_BLUE,
            font=("Arial", 11, "bold"), anchor="w",
        ).grid(row=0, column=column, sticky="ew", padx=8, pady=8)

    table = ctk.CTkScrollableFrame(
        requests_frame, fg_color=WHITE, corner_radius=8,
        border_width=1, border_color="#d1d5db",
    )
    table.pack(fill="both", expand=True, padx=20, pady=(6, 20))
    for column, weight, minsize in column_specs:
        table.grid_columnconfigure(column, weight=weight, minsize=minsize)

    selected = {"request": None, "rows": []}

    def show_request_item_details(item_id):
        item = InventoryRepository().get_by_id(item_id)
        if not item:
            messagebox.showerror("Inventory", "Item could not be found.", parent=app)
            return
        modal = ctk.CTkToplevel(app)
        modal.title("Item Details")
        modal.geometry("800x710")
        modal.configure(fg_color=MODAL_BG)
        modal.transient(app)
        modal.grab_set()
        modal.protocol("WM_DELETE_WINDOW", modal.destroy)
        ctk.CTkLabel(
            modal, text="Item Details", text_color=WHITE,
            font=MODAL_TITLE_FONT,
        ).pack(anchor="w", padx=24, pady=(20, 8))
        content = ctk.CTkFrame(modal, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        content.grid_columnconfigure(0, weight=1, minsize=250)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)
        preview = ctk.CTkFrame(content, fg_color=WHITE, corner_radius=8)
        preview.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        preview_label = ctk.CTkLabel(
            preview, text="No image", text_color="black", font=MODAL_FONT,
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
            ("Item ID", item.item_id), ("Item Name", item.item_name),
            ("Item Code", item.item_code), ("Category", item.category_name),
            ("Stock", item.stock), ("Serial No.", item.serial_no or "N/A"),
            ("Added Date", item.added_date or "N/A"),
            ("Updated Date", item.updated_date or "N/A"),
        )):
            _modal_field(details, label, str(value), disabled=True)
        ctk.CTkButton(
            modal, text="Close", width=110, height=36, fg_color=BLUE,
            command=modal.destroy,
        ).pack(anchor="e", padx=24, pady=(0, 18))

    def select_request(request, row_widgets):
        if selected["rows"]:
            for widget in selected["rows"]:
                widget.configure(fg_color=WHITE)
        selected["request"] = request
        selected["rows"] = row_widgets
        for widget in row_widgets:
            widget.configure(fg_color="#bfdbfe")

    def display_requests():
        for widget in table.winfo_children():
            widget.destroy()
        selected["request"] = None
        selected["rows"] = []
        try:
            rows = request_repo.get_all()
        except mysql.connector.Error as error:
            messagebox.showerror("Requests Unavailable", str(error), parent=app)
            return

        filter_value = filter_combo.get()
        search_value = search_entry.get().strip().lower()
        row_number = 1
        for request in rows:
            searchable = " ".join(
                str(request.get(key, "") or "")
                for key in ("request_id", "requester_name", "gmail", "item_code",
                            "item_name", "request_status")
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
                    table, text=str(value), fg_color=WHITE, text_color="black",
                    anchor="w", wraplength=180,
                )
                label.grid(row=row_number, column=column, sticky="ew", padx=3, pady=3)
                label.bind(
                    "<Button-1>",
                    lambda _event=None, item=request, widgets=row_widgets:
                    select_request(item, widgets),
                )
                row_widgets.append(label)
            details_button = ctk.CTkButton(
                table, text="View Item Details", width=120, height=26,
                fg_color=BLUE, hover_color="#254b91", corner_radius=6,
                command=lambda item_id=request["item_id"]:
                show_request_item_details(item_id),
            )
            details_button.grid(row=row_number, column=6, sticky="ew", padx=3, pady=3)
            row_number += 1

    def require_selection():
        if selected["request"] is None:
            messagebox.showwarning("Select Request", "Select a request first.", parent=app)
            return None
        return selected["request"]

    def manage_selected():
        request = require_selection()
        if request:
            RequestModal(app, request, request_repo, display_requests)

    def notify_selected():
        request = require_selection()
        if request:
            NotifyModal(app, request, request_repo)

    refresh_button.configure(command=display_requests)
    filter_combo.configure(command=lambda _value=None: display_requests())
    search_entry.bind("<KeyRelease>", lambda _event=None: display_requests())

    controls = ctk.CTkFrame(requests_frame, fg_color="transparent")
    controls.pack(fill="x", padx=20, pady=(0, 20))
    ctk.CTkButton(
        controls, text="MANAGE REQUEST", height=36, fg_color=GREEN,
        text_color="black", hover_color="#65a30d", corner_radius=6,
        command=manage_selected,
    ).pack(side="left", padx=(0, 10))
    ctk.CTkButton(
        controls, text="NOTIFY", height=36, fg_color="#f59e0b",
        text_color="black", hover_color="#d97706", corner_radius=6,
        command=notify_selected,
    ).pack(side="left")

    display_requests()
    return requests_frame


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
        self.status = ctk.CTkComboBox(
            details, values=["Pending", "Approved", "Cancelled", "Returned"],
            fg_color=WHITE, text_color="black", button_color=WHITE, corner_radius=8,
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
        try:
            self.request["quantity"] = int(self.quantity.get())
            new_status = self.status.get()
            if new_status == "Cancelled" and self.request.get("request_status") != "Cancelled":
                self._show_cancel_modal()
                return
            self.request["request_status"] = new_status
            self.repository.update(self.request)
            self.on_changed()
            messagebox.showinfo("Request Updated", "Request details were updated.", parent=self.modal)
        except (ValueError, mysql.connector.Error) as error:
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
                    parent=app,
                )
            except (ValueError, mysql.connector.Error) as error:
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
        except (ValueError, mysql.connector.Error) as error:
            messagebox.showerror("Request Error", str(error), parent=self.modal)

    def approve(self):
        if not messagebox.askyesno("Confirm Request", "Approve this request?", parent=self.modal):
            return
        try:
            self.repository.approve(self.request["request_id"])
            self.modal.destroy()
            self.on_changed()
        except mysql.connector.Error as error:
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
            if status == "Pending":
                changed = self.repository.approve(self.request["request_id"])
            elif status == "Approved":
                changed = self.repository.confirm_pickup(
                    self.request["request_id"],
                    current_user["user_id"],
                    self.request["item_id"],
                    int(self.request["quantity"]),
                )
            else:
                changed = False
            if not changed:
                raise ValueError("The request could not be updated.")
            self.modal.destroy()
            self.on_changed()
        except (ValueError, mysql.connector.Error) as error:
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
            corner_radius=8,
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
                changed = self.repository.confirm_return(
                    self.request["request_id"],
                    current_user["user_id"],
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
            except (ValueError, mysql.connector.Error) as error:
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
            messagebox.showinfo("Notification Sent", "The notification was sent.", parent=app)
        except (ValueError, mysql.connector.Error) as error:
            messagebox.showerror("Notification Error", str(error), parent=self.modal)


requests_frame = create_requests_tab(main_bg)
requests_frame.pack_forget()


def create_transactions_tab(parent_frame):
    repository = TransactionRepository()
    frame = ctk.CTkFrame(parent_frame, fg_color=BG_BLUE, corner_radius=0)
    frame.pack(fill="both", expand=True)
    state = {"mode": "current", "selected": None, "widgets": []}

    header = ctk.CTkFrame(frame, height=45, fg_color="#1c3b7a", corner_radius=8)
    header.pack(fill="x", padx=20, pady=(20, 0))
    header.pack_propagate(False)
    ctk.CTkLabel(header, text="Transactions", text_color=WHITE,
                 font=("Arial", 16, "bold")).pack(side="left", padx=15)

    def refresh():
        load_rows()

    toggle = ctk.CTkButton(header, text="ARCHIVE", width=90, height=30,
                           fg_color="#507ace", hover_color="#254b91",
                           corner_radius=6, command=lambda: switch_mode())
    toggle.pack(side="left", padx=10)
    toolbar = ctk.CTkFrame(header, fg_color="transparent")
    toolbar.pack(side="right", padx=20)
    ctk.CTkButton(toolbar, text="Refresh", width=80, height=30, fg_color=WHITE,
                  text_color="#1c3b7a", corner_radius=6,
                  command=refresh).pack(side="left", padx=5)
    filter_combo = ctk.CTkComboBox(toolbar, width=120, height=30,
                                   values=["All", "Cancelled", "Returned"],
                                   fg_color=WHITE, text_color="black",
                                   button_color=WHITE, corner_radius=6)
    filter_combo.set("All")
    filter_combo.pack(side="left", padx=5)
    search = ctk.CTkEntry(toolbar, width=150, height=30, fg_color=WHITE,
                          text_color="black", corner_radius=6, placeholder_text="Search")
    search.pack(side="left", padx=5)

    table = ctk.CTkScrollableFrame(frame, fg_color=WHITE, corner_radius=8)
    table.pack(fill="both", expand=True, padx=20, pady=20)
    widths = [100, 130, 250, 130, 150, 150, 150]
    for index, width in enumerate(widths):
        table.grid_columnconfigure(index, weight=1 if index == 2 else 0, minsize=width)
    for index, title in enumerate(
        ["Track No.", "Requested Item No.", "Transaction Details",
         "Request Status", "Approved By", "Received By", "Date/Time"]
    ):
        ctk.CTkLabel(table, text=title, fg_color="#dbeafe", text_color=TEXT_BLUE,
                     font=("Arial", 11, "bold"), anchor="w").grid(
                         row=0, column=index, sticky="ew", padx=1, pady=1
                     )

    def select(row, widgets):
        for widget in state["widgets"]:
            widget.configure(fg_color=WHITE)
        state["selected"] = row
        state["widgets"] = widgets
        for widget in widgets:
            widget.configure(fg_color="#bfdbfe")

    def load_rows():
        for widget in table.winfo_children():
            if int(widget.grid_info().get("row", 0)) > 0:
                widget.destroy()
        state["selected"] = None
        state["widgets"] = []
        try:
            rows = repository.get_all(state["mode"])
        except (ValueError, mysql.connector.Error) as error:
            messagebox.showerror("Transactions Unavailable", str(error), parent=app)
            return
        filter_value = filter_combo.get()
        term = search.get().strip().lower()
        row_index = 1
        for row in rows:
            text = " ".join(str(value or "") for value in row.values()).lower()
            if filter_value != "All" and row.get("transaction_type") != filter_value:
                continue
            if term and term not in text:
                continue
            date_value = row.get("transaction_date")
            is_cancelled = (
                str(row.get("transaction_type", "")).strip().lower() == "cancelled"
                or str(row.get("request_status", "")).strip().lower() == "cancelled"
            )
            received_by = "N/A" if is_cancelled else (row.get("requester_name") or row.get("confirmed_by_name") or "N/A")
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
                label = ctk.CTkLabel(table, text=str(value), fg_color=WHITE,
                                     text_color="black", anchor="w", wraplength=240)
                label.grid(row=row_index, column=column, sticky="ew", padx=1, pady=1)
                label.bind("<Button-1>",
                           lambda _event=None, item=row, cells=widgets: select(item, cells))
                label.bind(
                    "<Double-Button-1>",
                    lambda _event=None, item=row: show_transaction_details(item),
                )
                widgets.append(label)
            row_index += 1

    def show_transaction_details(row):
        try:
            transaction = repository.get_details(
                row["transaction_id"], state["mode"]
            )
        except (ValueError, mysql.connector.Error) as error:
            messagebox.showerror("Transaction Details Unavailable", str(error), parent=app)
            return
        if transaction is None:
            messagebox.showerror(
                "Transaction Details Unavailable",
                "The selected transaction could not be found.",
                parent=app,
            )
            return

        modal = ctk.CTkToplevel(app)
        modal.title("Transaction Details")
        modal.geometry("680x720")
        modal.minsize(520, 500)
        modal.configure(fg_color=MODAL_BG)
        modal.transient(app)
        modal.grab_set()

        body = ctk.CTkScrollableFrame(modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=(24, 12))

        ctk.CTkLabel(
            body, text="Transaction Details", text_color=WHITE,
            font=MODAL_TITLE_FONT,
        ).pack(anchor="w", pady=(0, 12))

        def add_section(title, fields):
            ctk.CTkLabel(
                body, text=title, text_color="#93c5fd", font=("Arial", 14, "bold"),
            ).pack(anchor="w", pady=(10, 4))
            for label, key in fields:
                value = key(transaction) if callable(key) else transaction.get(key)
                if value is None or value == "":
                    value = "N/A"
                ctk.CTkLabel(
                    body, text=f"{label}: {value}", text_color=WHITE,
                    font=MODAL_FONT, anchor="w", justify="left", wraplength=590,
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
        if state["mode"] == "archived":
            add_section(
                "Archive",
                [("Archived Date", "archived_date"), ("Archive Reason", "archive_reason")],
            )

        ctk.CTkButton(
            modal, text="Close", height=36, fg_color=RED,
            command=modal.destroy,
        ).pack(fill="x", padx=24, pady=(0, 20))

    def require_selected():
        if state["selected"] is None:
            messagebox.showwarning("Select Transaction", "Select a transaction first.", parent=app)
        return state["selected"]

    def confirm_action(title, message, action):
        row = require_selected()
        if row is None or not messagebox.askyesno(title, message, parent=app):
            return
        try:
            if not action(row["transaction_id"]):
                raise ValueError("The transaction could not be updated.")
            load_rows()
        except (ValueError, mysql.connector.Error) as error:
            messagebox.showerror("Transaction Error", str(error), parent=app)

    def switch_mode():
        state["mode"] = "archived" if state["mode"] == "current" else "current"
        toggle.configure(text="CURRENT" if state["mode"] == "archived" else "ARCHIVE")
        load_rows()
        update_actions()

    actions = ctk.CTkFrame(frame, fg_color="transparent")
    actions.pack(fill="x", padx=20, pady=(0, 20))
    current_button = ctk.CTkButton(
        actions, text="ARCHIVED", height=36, fg_color=GREEN, text_color="black",
        corner_radius=6, command=lambda: confirm_action(
            "Archive Transaction", "Archive this transaction?", repository.archiveTransaction
        ),
    )
    restore_button = ctk.CTkButton(
        actions, text="RESTORE", height=36, fg_color=GREEN, text_color="black",
        corner_radius=6, command=lambda: confirm_action(
            "Restore Transaction", "Restore this transaction?", repository.restoreTransaction
        ),
    )
    delete_button = ctk.CTkButton(
        actions, text="DELETE", height=36, fg_color=RED, corner_radius=6,
        command=lambda: confirm_action(
            "Delete Transaction", "Delete this archived transaction?", repository.delete
        ),
    )

    def update_actions():
        for button in (current_button, restore_button, delete_button):
            button.pack_forget()
        if state["mode"] == "current":
            current_button.pack(side="left")
        else:
            delete_button.pack(side="right", padx=(10, 0))
            restore_button.pack(side="right")

    filter_combo.configure(command=lambda _value=None: load_rows())
    search.bind("<KeyRelease>", lambda _event=None: load_rows())
    update_actions()
    load_rows()
    return frame


transactions_frame = create_transactions_tab(main_bg)
transactions_frame.pack_forget()

class AccountEditor:
    department_data = {
        "College of Arts & Sciences": [
            "ABCom - Bachelor of Arts in Communication",
            "ABEng - Bachelor of Arts in English",
            "BSM - Bachelor of Science in Mathematics",
            "BSP - Bachelor of Science in Psychology",
        ],
        "College of Business & Accountancy": [
            "ABA - Associate in Business Administration",
            "BSAIS - Bachelor of Science in Accounting Information System",
            "BSA - Bachelor of Science in Accountancy",
            "BSMA - Bachelor of Science in Management Accounting",
            "BSREM - Bachelor of Science in Real Estate Management",
            "BSIA - Bachelor of Science in Internal Auditing",
            "BSLM - Bachelor of Science in Legal Management",
            "BSBA - Bachelor of Science in Business Administration",
        ],
        "College of Computer Studies": [
            "ACT - Associate in Computer Technology",
            "BSCS - Bachelor of Science in Computer Science",
            "BSIT - Bachelor of Science in Information Technology",
            "BSIS - Bachelor of Science in Information System",
        ],
        "College of Teacher Education": [
            "BECEd - Bachelor in Early Childhood Education",
            "BELEMEd - Bachelor in Elementary Education",
            "BSEd - Bachelor in Secondary Education",
            "BTVTEd - Bachelor in Technical Vocational Teacher Education",
            "CPT - Certificate in Teaching Program",
        ],
        "College of Criminology & Administration": [
            "BSC - Bachelor of Science in Criminology",
            "BSISM - Bachelor of Science in Industrial Security Management",
            "BPA - Bachelor in Public Administration",
        ],
        "College of Engineering": [
            "BSCE - Bachelor of Science in Computer Engineering",
            "BSELE - Bachelor of Science in Electronics Engineering",
        ],
        "College of Health Sciences": [
            "BSMedTech - Bachelor of Science in Medical Technology",
            "BSN - Bachelor of Science in Nursing",
            "BSRadTech - Bachelor of Science in Radiologic Technology",
            "DHWA - Diploma in Health Care & Wellness Associate",
        ],
        "International School of Hospitality & Tourism Management": [
            "BSHM - Bachelor of Science in Hospitality Management",
            "BSTM - Bachelor of Science in Tourism Management",
            "DHRM1 - Diploma in Hotel & Restaurant Management-1",
            "DHRM2 - Diploma in Hotel & Restaurant Management-2",
        ],
        "Senior High Department": ["ACADEMIC-TRACK", "TECH-PRO-TRACK"],
    }

    def __init__(self, parent, repository, account=None, on_changed=None):
        self.repository = repository
        self.account = account
        self.on_changed = on_changed or (lambda: None)
        details = {}
        if account is not None:
            details = repository.get_by_id(account["account_id"]) or {}
        self.modal = ctk.CTkToplevel(parent)
        self.modal.title("Create Account" if account is None else "Update Account")
        self.modal.geometry("700x700")
        self.modal.configure(fg_color="#1e3a8a")
        self.modal.transient(parent)
        self.modal.grab_set()
        card = ctk.CTkFrame(
            self.modal, fg_color=WHITE, corner_radius=15,
            border_width=1, border_color="#d1d5db",
        )
        card.pack(fill="both", expand=True, padx=24, pady=24)
        card.grid_columnconfigure(0, weight=1, uniform="account")
        card.grid_columnconfigure(1, weight=0)
        card.grid_columnconfigure(2, weight=2, uniform="account")
        card.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(
            card, text=self.modal.title(), text_color=TEXT_BLUE,
            font=("Arial", 24, "bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=28, pady=(20, 8))

        left = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0)
        left.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=(28, 20), pady=(0, 24))
        right = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0)
        right.grid(row=1, column=2, rowspan=2, sticky="nsew", padx=(20, 28), pady=(0, 24))
        ctk.CTkFrame(card, width=2, fg_color="#d1d5db").grid(
            row=1, column=1, rowspan=2, sticky="ns", pady=(0, 24)
        )
        left.grid_columnconfigure(0, weight=1)
        right.grid_columnconfigure((0, 1), weight=1, uniform="personal")

        ctk.CTkLabel(
            left, text="Account Information", text_color=TEXT_BLUE,
            font=("Arial", 15, "bold"),
        ).pack(anchor="w", padx=4, pady=(0, 8))
        left_form = ctk.CTkFrame(left, fg_color=WHITE, corner_radius=0)
        left_form.pack(fill="x")
        left_form.grid_columnconfigure(0, weight=1)
        left_row = 0
        if account is not None:
            ctk.CTkLabel(
                left_form, text="Account ID", text_color=TEXT_BLUE,
            ).grid(row=left_row * 2, column=0, sticky="w", padx=4, pady=(4, 2))
            account_id_entry = ctk.CTkEntry(
                left_form, corner_radius=8, fg_color="#e5e7eb",
                text_color="#374151",
            )
            account_id_entry.grid(
                row=left_row * 2 + 1, column=0, sticky="ew",
                padx=4, pady=(0, 8),
            )
            account_id_entry.insert(0, str(account["account_id"]))
            account_id_entry.configure(state="disabled")
            left_row += 1
        self.email = self._entry(
            left_form, "Email", details.get("gmail", ""), left_row
        )
        left_row += 1
        self.password = self._entry(
            left_form, "Password" if account is None else "Password (optional)",
            "", left_row, masked=True,
        )
        self.show_password = ctk.CTkCheckBox(
            left_form, text="Show Password", text_color=TEXT_BLUE,
            command=self.toggle_password_visibility,
        )
        self.show_password.grid(
            row=left_row * 2 + 2, column=0, sticky="w", padx=4, pady=(0, 6)
        )
        left_row += 2
        self.role = self._combo(
            left_form, "Role", ["Admin", "Student"],
            details.get("role", "Student"),
            left_row,
        )
        left_row += 1
        self.status = self._combo(
            left_form, "Status", ["Active", "Inactive"],
            details.get("status", (account or {}).get("account_status", "Active")),
            left_row,
        )

        ctk.CTkLabel(
            right, text="Personal Information", text_color=TEXT_BLUE,
            font=("Arial", 15, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        self.personal_entries = {}
        for row, fields in enumerate(
            (
                (("first_name", "First Name"), ("middle_name", "Middle Name")),
                (("last_name", "Last Name"), ("contact_number", "Contact No.")),
                (("student_id", "Student No."),),
            ),
            1,
        ):
            for column, (key, label) in enumerate(fields):
                self.personal_entries[key] = self._entry(
                    right, label, details.get(key, ""), row, column
                )
            if len(fields) == 1:
                self.personal_entries[key].grid_configure(columnspan=2)
        self.birthday = self._date_entry(right, "Birthday", details.get("birthday"), 4)
        self.gender = self._combo(
            right, "Gender", ["Male", "Female", "Other"],
            details.get("gender", ""), 4, 1,
        )
        self.department = self._combo(
            right, "Department", list(self.department_data.keys()),
            details.get("department", ""), 5, 0,
            command=self.update_courses,
        )
        self.course = self._combo(
            right, "Course", self.department_data.get(details.get("department", ""), []),
            details.get("course", ""), 5, 1,
        )
        self.address = self._textbox(right, "Address", details.get("address", ""), 6)
        ctk.CTkButton(
            card, text="Create" if account is None else "Update", width=130,
            height=38, fg_color=GREEN, text_color="black", corner_radius=8,
            command=self.save,
        ).grid(row=3, column=2, sticky="e", padx=28, pady=(0, 20))

    @staticmethod
    def _entry(parent, label, value="", row=0, column=0, masked=False):
        ctk.CTkLabel(parent, text=label, text_color=TEXT_BLUE).grid(
            row=row * 2, column=column, sticky="w", padx=4, pady=(4, 2)
        )
        entry = ctk.CTkEntry(
            parent, corner_radius=8, fg_color="#f3f4f6",
            text_color="black", show="*" if masked else "",
        )
        entry.grid(row=row * 2 + 1, column=column, sticky="ew", padx=4, pady=(0, 6))
        entry.insert(0, value)
        return entry

    @staticmethod
    def _combo(parent, label, values, value, row=0, column=0, command=None):
        ctk.CTkLabel(parent, text=label, text_color=TEXT_BLUE).grid(
            row=row * 2, column=column, sticky="w", padx=4, pady=(4, 2)
        )
        combo = ctk.CTkComboBox(
            parent, values=values, corner_radius=8, fg_color="#f3f4f6",
            text_color="black", button_color="#d1d5db", command=command,
        )
        combo.grid(row=row * 2 + 1, column=column, sticky="ew", padx=4, pady=(0, 6))
        combo.set(value)
        return combo

    @staticmethod
    def _date_entry(parent, label, value, row):
        ctk.CTkLabel(parent, text=label, text_color=TEXT_BLUE).grid(
            row=row * 2, column=0, sticky="w", padx=4, pady=(4, 2)
        )
        date_entry = DateEntry(
            parent, date_pattern="yyyy-mm-dd", width=16,
            background="#1e3a8a", foreground="white",
            borderwidth=1, relief="solid",
        )
        date_entry.grid(row=row * 2 + 1, column=0, sticky="ew", padx=4, pady=(0, 6))
        date_entry.delete(0, "end")
        if value:
            try:
                date_entry.set_date(value)
            except (TypeError, ValueError):
                date_entry.insert(0, str(value)[:10])
        return date_entry

    @staticmethod
    def _textbox(parent, label, value="", row=0):
        ctk.CTkLabel(parent, text=label, text_color=TEXT_BLUE).grid(
            row=row * 2, column=0, columnspan=2, sticky="w", padx=4, pady=(4, 2)
        )
        textbox = ctk.CTkTextbox(
            parent, height=75, corner_radius=8,
            fg_color="#f3f4f6", text_color="black",
        )
        textbox.grid(
            row=row * 2 + 1, column=0, columnspan=2,
            sticky="nsew", padx=4, pady=(0, 6),
        )
        textbox.insert("1.0", value or "")
        return textbox

    def update_courses(self, department=None):
        selected = department or self.department.get()
        courses = self.department_data.get(selected, [])
        self.course.configure(values=courses)
        if self.course.get() not in courses:
            self.course.set(courses[0] if courses else "")

    def toggle_password_visibility(self):
        show = "" if self.show_password.get() else "*"
        self.password.configure(show=show)

    def save(self):
        if not messagebox.askyesno(
            "Confirm Account Creation",
            "Are you sure you want to create this account?",
            parent=self.modal,
        ):
            return
        try:
            account_data = {
                "gmail": self.email.get(),
                "password": self.password.get(),
                "role": self.role.get(),
                "status": self.status.get(),
            }
            personal_data = {
                key: entry.get() for key, entry in self.personal_entries.items()
            }
            personal_data["birthday"] = self.birthday.get_date()
            personal_data["gender"] = self.gender.get()
            personal_data["department"] = self.department.get()
            personal_data["course"] = self.course.get()
            personal_data["address"] = self.address.get("1.0", "end-1c")
            if self.account is None:
                validate_new_account(account_data, personal_data)
                self.repository.add_user(account_data, personal_data)
            else:
                if account_data["password"].strip():
                    validate_password(account_data["password"])
                self.repository.update_user(
                    self.account["account_id"], account_data, personal_data
                )
            self.modal.destroy()
            self.on_changed()
        except (ValueError, mysql.connector.Error) as error:
            messagebox.showerror("Account Error", str(error), parent=self.modal)

class AdminPasswordModal:
    def __init__(self, parent, repository, account, on_changed=None):
        self.repository = repository
        self.account = account
        self.on_changed = on_changed or (lambda: None)
        self.modal = ctk.CTkToplevel(parent)
        self.modal.title("Change Password")
        self.modal.geometry("400x300")
        self.modal.configure(fg_color=MODAL_BG)
        self.modal.transient(parent)
        self.modal.grab_set()
        body = ctk.CTkFrame(self.modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=24)
        ctk.CTkLabel(body, text="Change Password", text_color=WHITE,
                     font=MODAL_TITLE_FONT).pack(anchor="w", pady=(0, 10))
        ctk.CTkLabel(body, text="New Password", text_color=WHITE).pack(anchor="w")
        self.password = ctk.CTkEntry(body, show="*", corner_radius=6,
                                     fg_color=WHITE, text_color="black")
        self.password.pack(fill="x", pady=(2, 12))
        ctk.CTkLabel(body, text="Re-enter Password", text_color=WHITE).pack(
            anchor="w"
        )
        self.confirm_password = ctk.CTkEntry(
            body, show="*", corner_radius=6, fg_color=WHITE, text_color="black"
        )
        self.confirm_password.pack(fill="x", pady=(2, 8))
        self.show_password = ctk.CTkCheckBox(
            body, text="Show Password", text_color=WHITE,
            command=self.toggle_password_visibility,
        )
        self.show_password.pack(anchor="w", pady=(0, 12))
        ctk.CTkButton(body, text="SAVE", height=36, fg_color=PURPLE,
                      corner_radius=6, command=self.save).pack(fill="x")

    def toggle_password_visibility(self):
        show = "" if self.show_password.get() else "*"
        self.password.configure(show=show)
        self.confirm_password.configure(show=show)

    def save(self):
        if not messagebox.askyesno(
            "Confirm Changes",
            "Are you sure you want to save these changes?",
            parent=self.modal,
        ):
            return
        try:
            if self.password.get() != self.confirm_password.get():
                raise ValueError("The passwords do not match.")
            validate_password(self.password.get())
            self.repository.change_password(self.account["account_id"], self.password.get())
            self.modal.destroy()
            self.on_changed()
        except (ValueError, mysql.connector.Error) as error:
            messagebox.showerror("Password Error", str(error), parent=self.modal)

def create_accounts_tab(parent_frame):
    repository = UserRepository()
    frame = ctk.CTkFrame(parent_frame, fg_color=BG_BLUE, corner_radius=0)
    frame.pack(fill="both", expand=True)
    state = {"mode": "current", "selected": None, "widgets": []}
    header = ctk.CTkFrame(frame, height=45, fg_color="#1c3b7a", corner_radius=8)
    header.pack(fill="x", padx=20, pady=(20, 0))
    header.pack_propagate(False)
    ctk.CTkLabel(header, text="Accounts", text_color=WHITE,
                 font=("Arial", 16, "bold")).pack(side="left", padx=15)
    toggle = ctk.CTkButton(header, text="ARCHIVE", width=90, height=30,
                           fg_color="#779adf", corner_radius=6)
    toggle.pack(side="left", padx=10)
    toolbar = ctk.CTkFrame(header, fg_color="transparent")
    toolbar.pack(side="right", padx=20)
    search = ctk.CTkEntry(toolbar, width=160, height=30, fg_color=WHITE,
                          text_color="black", corner_radius=6, placeholder_text="Search")
    search.pack(side="left", padx=5)
    refresh_button = ctk.CTkButton(
        toolbar, text="Refresh", width=80, height=30,
        fg_color=WHITE, text_color="#1c3b7a", hover_color="#e5e7eb",
        corner_radius=6, command=lambda: refresh(),
    )
    refresh_button.pack(side="left", padx=5)
    header_frame = ctk.CTkFrame(frame, fg_color="#dbeafe", corner_radius=8)
    header_frame.pack(fill="x", padx=20, pady=(20, 0))
    table = ctk.CTkScrollableFrame(frame, fg_color=WHITE, corner_radius=8)
    table.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def configure_columns(container, count):
        for column in range(count):
            container.grid_columnconfigure(
                column, weight=1, uniform="col", minsize=0
            )

    def select(row, widgets):
        for widget in state["widgets"]:
            widget.configure(fg_color=WHITE)
        state["selected"], state["widgets"] = row, widgets
        for widget in widgets:
            widget.configure(fg_color="#bfdbfe")

    def load_rows():
        for widget in table.winfo_children():
            widget.destroy()
        state["selected"], state["widgets"] = None, []
        archived = state["mode"] == "archived"
        headers = (
            ["Acc_Archive No.", "Account No.", "Student ID", "Email",
             "Status", "Role", "Date/Time"]
            if archived else
            ["Account No.", "Student ID", "Email", "Status", "Role", "Date/Time"]
        )
        for widget in header_frame.winfo_children():
            widget.destroy()
        configure_columns(header_frame, len(headers))
        for column, title in enumerate(headers):
            ctk.CTkLabel(header_frame, text=title, fg_color="#dbeafe", text_color=TEXT_BLUE,
                         font=("Arial", 11, "bold"), anchor="w").grid(
                             row=0, column=column, sticky="nsew", padx=1, pady=6)
        configure_columns(table, len(headers))
        try:
            rows = repository.get_all_accounts(state["mode"])
        except (ValueError, mysql.connector.Error) as error:
            messagebox.showerror("Accounts Unavailable", str(error), parent=app)
            return
        term = search.get().strip().lower()
        for row_index, row in enumerate(rows, 1):
            values = (
                [row.get("account_archive_id"), row.get("account_id"),
                 row.get("student_id"), row.get("gmail"), row.get("account_status"),
                 row.get("role"), row.get("creationdate")]
                if archived else
                [row.get("account_id"), row.get("student_id"), row.get("gmail"),
                 row.get("account_status"), row.get("role"), row.get("creationdate")]
            )
            if term and term not in " ".join(str(value or "") for value in values).lower():
                continue
            widgets = []
            for column, value in enumerate(values):
                label = ctk.CTkLabel(table, text=str(value or ""), fg_color=WHITE,
                                     text_color="black", anchor="w")
                label.grid(row=row_index, column=column, sticky="ew", padx=1, pady=1)
                label.bind("<Button-1>",
                           lambda _event=None, item=row, cells=widgets: select(item, cells))
                widgets.append(label)

    def selected():
        if state["selected"] is None:
            messagebox.showwarning("Select Account", "Select an account first.", parent=app)
        return state["selected"]

    def refresh():
        load_rows()

    def switch():
        state["mode"] = "archived" if state["mode"] == "current" else "current"
        toggle.configure(text="CURRENT" if state["mode"] == "archived" else "ARCHIVE")
        update_actions()
        load_rows()

    toggle.configure(command=switch)
    search.bind("<KeyRelease>", lambda _event=None: load_rows())
    actions = ctk.CTkFrame(frame, fg_color="transparent")
    actions.pack(fill="x", padx=20, pady=(0, 20))
    current = [
        ctk.CTkButton(actions, text="CREATE", fg_color=GREEN, text_color="black",
                      corner_radius=6, command=lambda: AccountEditor(app, repository, on_changed=refresh)),
        ctk.CTkButton(actions, text="UPDATE", fg_color="#f59e0b", text_color="black",
                      corner_radius=6, command=lambda: edit()),
        ctk.CTkButton(actions, text="CHANGE PASSWORD", fg_color=PURPLE,
                      corner_radius=6, command=lambda: reset()),
        ctk.CTkButton(actions, text="ARCHIVE", fg_color=RED, corner_radius=6,
                      command=lambda: archive()),
    ]
    restore = ctk.CTkButton(actions, text="RESTORE", fg_color=GREEN, text_color="black",
                            corner_radius=6, command=lambda: move(repository.restore_user))
    delete = ctk.CTkButton(actions, text="DELETE", fg_color=RED, corner_radius=6,
                           command=lambda: move(repository.delete_archived))

    def edit():
        account = selected()
        if account:
            AccountEditor(app, repository, account, refresh)

    def reset():
        account = selected()
        if account:
            AdminPasswordModal(app, repository, account, refresh)

    def archive():
        account = selected()
        if account and messagebox.askyesno("Archive Account", "Archive this account?", parent=app):
            try:
                repository.archive_user(account["account_id"])
                refresh()
            except (ValueError, mysql.connector.Error) as error:
                messagebox.showerror("Archive Account", str(error), parent=app)

    def move(action):
        account = selected()
        if account and messagebox.askyesno("Confirm Action ", "Are you sure you want to perform this action?", parent=app):
            try:
                if not action(account.get("account_archive_id")):
                    raise ValueError("The archived account could not be found.")
                refresh()
            except (ValueError, mysql.connector.Error) as error:
                messagebox.showerror("Delete Account", str(error), parent=app)

    def update_actions():
        for button in current + [restore, delete]:
            button.pack_forget()
        if state["mode"] == "current":
            for button in current:
                button.pack(side="left", padx=4)
        else:
            restore.pack(side="right")
            delete.pack(side="right", padx=(0, 8))

    update_actions()
    load_rows()
    return frame


accounts_frame = create_accounts_tab(main_bg)
accounts_frame.pack_forget()

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
        x = (self.modal.winfo_screenwidth() // 2) - 175
        y = (self.modal.winfo_screenheight() // 2) - 100
        self.modal.geometry(f"+{x}+{y}")

        body = ctk.CTkFrame(self.modal, fg_color=MODAL_BG)
        body.pack(fill="both", expand=True, padx=24, pady=(24, 20))

        ctk.CTkLabel(
            body,
            text="Log Out",
            text_color=WHITE,
            font=MODAL_TITLE_FONT,
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(
            body,
            text="Are you sure you want to log out?",
            text_color="#bfdbfe",
            font=MODAL_FONT,
        ).pack(anchor="w", pady=(0, 20))

        actions = ctk.CTkFrame(body, fg_color="transparent")
        actions.pack(fill="x", pady=(20, 0))
        actions.grid_columnconfigure((0, 1), weight=1, uniform="action")

        ctk.CTkButton(
            actions,
            text="No",
            width=120,
            height=40,
            command=self.modal.destroy,
            fg_color=RED,
            hover_color="#dc2626",
            corner_radius=8,
            font=("Arial", 12, "bold"),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkButton(
            actions,
            text="Yes",
            width=120,
            height=40,
            command=self._confirm_logout,
            fg_color=GREEN,
            hover_color="#65a30d",
            text_color="black",
            corner_radius=8,
            font=("Arial", 12, "bold"),
        ).grid(row=0, column=1, sticky="ew", padx=(10, 0))

    def _confirm_logout(self):
        self.modal.destroy()
        Session.clear()
        app.destroy()
        subprocess.Popen([
            sys.executable,
            os.path.join(os.path.dirname(__file__), "main.py"),
        ])

def show_tab(selected_tab):
    if selected_tab == "Analytics":
        inventory_frame.pack_forget()
        requests_frame.pack_forget()
        transactions_frame.pack_forget()
        accounts_frame.pack_forget()
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
    elif selected_tab == "Inventory":
        content_frame.pack_forget()
        requests_frame.pack_forget()
        transactions_frame.pack_forget()
        accounts_frame.pack_forget()
        inventory_frame.pack(fill="both", expand=True, padx=20, pady=20)
    elif selected_tab == "Requests":
        content_frame.pack_forget()
        inventory_frame.pack_forget()
        transactions_frame.pack_forget()
        accounts_frame.pack_forget()
        requests_frame.pack(fill="both", expand=True, padx=20, pady=20)
    elif selected_tab == "Transactions":
        content_frame.pack_forget()
        inventory_frame.pack_forget()
        requests_frame.pack_forget()
        accounts_frame.pack_forget()
        transactions_frame.pack(fill="both", expand=True, padx=20, pady=20)
    elif selected_tab == "Accounts":
        content_frame.pack_forget()
        inventory_frame.pack_forget()
        requests_frame.pack_forget()
        transactions_frame.pack_forget()
        accounts_frame.pack(fill="both", expand=True, padx=20, pady=20)
    else:
        messagebox.showinfo(
            "Unavailable",
            f"The {selected_tab} section is not available yet.",
        )
        return

    for tab, button in nav_buttons.items():
        button.configure(fg_color=DARK_BLUE if tab == selected_tab else TEXT_BLUE)

app.mainloop()