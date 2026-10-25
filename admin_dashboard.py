import os
import subprocess
import sys
from datetime import datetime
from tkinter import filedialog, ttk, messagebox

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import mysql.connector
from PIL import Image

from models.users import Session
from repositories import InventoryRepository, CategoryRepository
from models.inventory import InventoryItem, Category

app = ctk.CTk()
app.geometry("1000x650")
app.title("(Analytics) admin_dashboard.py")
app.resizable(False, False)
ctk.set_appearance_mode("light")

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

DARK_BLUE = "#1e3aa8"  
BG_BLUE = "#a5b4fc" 
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

# ==========================================
# HEADER
# ==========================================
header_frame = ctk.CTkFrame(main_bg, height=80, fg_color=DARK_BLUE, corner_radius=0)
header_frame.pack(fill="x", side="top")

# Logo
logo_path = r"C:\Users\maxwx\OneDrive\Documents\SDF04-Aims\Assets\Aims_plain_white.png"
try:
    if os.path.exists(logo_path):
        logo_img = ctk.CTkImage(light_image=Image.open(logo_path), size=(50, 50))
        ctk.CTkLabel(header_frame, image=logo_img, text="").place(x=20, y=15)
except Exception:
    ctk.CTkLabel(header_frame, text="[LOGO]", text_color=WHITE, font=("Arial", 16, "bold")).place(x=20, y=25)

ctk.CTkLabel(header_frame, text="Greetings, Admin", font=("Arial", 28, "bold"), text_color=WHITE).place(x=90, y=20)

def logout():
    confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to log out?")
    
    if confirm:
        Session.clear()
        app.destroy()
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "main.py")])

logout_btn = ctk.CTkButton(header_frame, text="Log out", width=100, height=35, fg_color=RED, hover_color="#dc2626", corner_radius=8, font=("Arial", 14, "bold"), command=logout)
logout_btn.place(x=870, y=22)

# ==========================================
# NAVIGATION BAR
# ==========================================
nav_frame = ctk.CTkFrame(main_bg, height=60, fg_color=WHITE, corner_radius=20)
nav_frame.pack(fill="x", padx=20, pady=15)

tabs = ["Analytics", "Inventory Managemt", "Request", "Transactions", "Accounts"]
nav_buttons = {}
for i, tab in enumerate(tabs):
    bg_color = DARK_BLUE if tab == "Analytics" else TEXT_BLUE
    btn = ctk.CTkButton(
        nav_frame,
        text=tab,
        width=160,
        height=35,
        fg_color=bg_color,
        corner_radius=15,
        font=("Arial", 12, "bold"),
        command=lambda selected_tab=tab: show_tab(selected_tab),
    )
    btn.place(x=20 + (i * 180), y=12)
    nav_buttons[tab] = btn

# ==========================================
# MAIN CONTENT AREA
# ==========================================
content_frame = ctk.CTkFrame(main_bg, fg_color=DARK_BLUE, corner_radius=15)
content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

ctk.CTkLabel(content_frame, text="Data Insights", font=("Arial", 18, "bold"), text_color=WHITE).place(x=20, y=10)
ctk.CTkButton(content_frame, text="Refresh", width=80, height=28, fg_color=WHITE, text_color=DARK_BLUE, corner_radius=15, font=("Arial", 12, "bold")).place(x=850, y=10)

inner_frame = ctk.CTkFrame(content_frame, fg_color=BG_BLUE, corner_radius=0)
inner_frame.pack(fill="both", expand=True, padx=2, pady=(45, 2))

chart_card = ctk.CTkFrame(inner_frame, width=460, fg_color=WHITE, corner_radius=15, border_width=1, border_color="#d1d5db")
chart_card.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
chart_card.pack_propagate(False)

ctk.CTkLabel(chart_card, text="System Analytics", font=("Arial", 16, "bold"), text_color=TEXT_BLUE).pack(pady=(10, 0))


fig = Figure(figsize=(5, 4), dpi=100)
fig.patch.set_facecolor('#ffffff')

ax1 = fig.add_subplot(211)

dept_labels = ['IT', 'Engineering', 'Business', 'Health']
dept_sizes = [45, 25, 20, 10]
wedges, texts, autotexts = ax1.pie(dept_sizes, labels=dept_labels, autopct='%1.1f%%', startangle=90, colors=['#3b82f6', '#8b5cf6', '#f59e0b', '#10b981'])
centre_circle = plt.Circle((0,0),0.60,fc='white')
fig.gca().add_artist(centre_circle)
ax1.set_title("Users by Department", fontsize=10, fontweight='bold', pad=5)

ax2 = fig.add_subplot(212)
# NOTE: Replace with -> cursor.execute("SELECT i.item_name, SUM(r.quantity) FROM item_requests r JOIN inventory_items i ON r.item_id = i.item_id GROUP BY i.item_name ORDER BY SUM(r.quantity) DESC LIMIT 3")
items = ['Arduino Uno', 'ESP32', 'Breadboard']
requests = [120, 95, 80]
ax2.bar(items, requests, color=['#1e3a8a', '#2563eb', '#60a5fa'])
ax2.set_title("Most Requested Items", fontsize=10, fontweight='bold', pad=5)
fig.tight_layout()

canvas = FigureCanvasTkAgg(fig, master=chart_card)
canvas.draw()
canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)


logs_card = ctk.CTkFrame(inner_frame, width=460, fg_color=WHITE, corner_radius=15, border_width=1, border_color="#d1d5db")
logs_card.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
logs_card.pack_propagate(False)

log_top = ctk.CTkFrame(logs_card, height=40, fg_color=DARK_BLUE, corner_radius=15)
log_top.pack(fill="x", padx=10, pady=10)

ctk.CTkLabel(log_top, text="Logs", font=("Arial", 16, "bold"), text_color=WHITE).place(x=15, y=5)
ctk.CTkButton(log_top, text="Refresh", width=70, height=25, fg_color=WHITE, text_color=DARK_BLUE, corner_radius=15).place(x=150, y=7)
ctk.CTkLabel(log_top, text="Search:", font=("Arial", 12, "bold"), text_color=WHITE).place(x=230, y=8)
ctk.CTkEntry(log_top, width=130, height=25, corner_radius=10, fg_color=WHITE, text_color="black").place(x=290, y=7)

style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", background=WHITE, foreground="black", rowheight=25, fieldbackground=WHITE, borderwidth=0)
style.configure("Treeview.Heading", background=BG_BLUE, foreground="black", font=('Arial', 10, 'bold'))
style.map('Treeview', background=[('selected', '#dbeafe')])

columns = ("log_no", "user_no", "action", "table", "record", "time")
tree_frame = ctk.CTkFrame(logs_card, fg_color=WHITE)
tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
tree.heading("log_no", text="Log No.")
tree.heading("user_no", text="User No.")
tree.heading("action", text="Action")
tree.heading("table", text="Table Affected")
tree.heading("record", text="Record ID")
tree.heading("time", text="Timestamp")

tree.column("log_no", width=60, anchor="center")
tree.column("user_no", width=70, anchor="center")
tree.column("action", width=120, anchor="w")
tree.column("table", width=100, anchor="center")
tree.column("record", width=70, anchor="center")
tree.column("time", width=130, anchor="center")

tree.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")


def create_inventory_tab(parent_frame):
    inventory_repo = InventoryRepository()
    
    inventory_frame = ctk.CTkFrame(parent_frame, fg_color="#a5b4fc", corner_radius=0)
    inventory_frame.pack(fill="both", expand=True)

    header_frame = ctk.CTkFrame(inventory_frame, fg_color="#1e3a8a", height=45, corner_radius=8)
    header_frame.pack(fill="x", padx=20, pady=(20, 0))
    header_frame.pack_propagate(False)

    ctk.CTkLabel(header_frame, text="Items Catalogue", font=("Arial", 14, "bold"), text_color="white").pack(side="left", padx=15)

    search_entry = ctk.CTkEntry(header_frame, width=150, height=28, corner_radius=15, fg_color="white", text_color="black")
    search_entry.pack(side="right", padx=(5, 15), pady=8)
    ctk.CTkLabel(header_frame, text="Search :", font=("Arial", 12, "bold"), text_color="white").pack(side="right", padx=5)

    filter_combo = ctk.CTkComboBox(header_frame, width=120, height=28, corner_radius=15, fg_color="white", text_color="black", button_color="white", values=["All", "Available", "Requested"])
    filter_combo.pack(side="right", padx=(5, 15), pady=8)
    ctk.CTkLabel(header_frame, text="Filter :", font=("Arial", 12, "bold"), text_color="white").pack(side="right", padx=5)

    catalogue_container = ctk.CTkScrollableFrame(inventory_frame, fg_color="white", corner_radius=8)
    catalogue_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
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

    refresh_btn = ctk.CTkButton(header_frame, text="Refresh", width=80, height=28, corner_radius=15, fg_color="white", text_color="black", hover_color="#f3f4f6", font=("Arial", 12, "bold"), command=refresh_data)
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
    search = ctk.CTkEntry(header, width=150, fg_color=WHITE, text_color="black")
    search.pack(side="right", padx=15, pady=8)
    ctk.CTkLabel(header, text="Search:", text_color=WHITE).pack(side="right")
    cards = ctk.CTkScrollableFrame(inventory_frame, fg_color=WHITE, corner_radius=8)
    cards.pack(fill="both", expand=True, padx=20, pady=(0, 20))
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
        modal.geometry("430x480")
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
        modal.geometry("430x480")
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
        modal.geometry("520x480")
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
        modal.geometry("380x660")
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
            if current:
                stock.delete(0, "end")
                stock.insert(0, "1")
                stock.configure(state="disabled")

        if category_dropdown is not None:
            category_dropdown.configure(command=category_changed)
        if not perishable.get():
            toggle_expiration()
        if serial_enabled.get():
            toggle_serial()
        if category.requires_return:
            stock.delete(0, "end")
            stock.insert(0, "1")
            stock.configure(state="disabled")

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
                stock_value = 1 if current_category.requires_return else int(stock_text)
                if not 0 <= stock_value <= (1 if current_category.requires_return else 500):
                    messagebox.showwarning(
                        "Invalid Stock",
                        "Stock must be between 0 and 500.",
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
        modal.geometry("500x650")
        modal.configure(fg_color=MODAL_BG)
        modal.transient(app)
        ctk.CTkLabel(
            modal, text="Item Details", text_color=WHITE, font=MODAL_TITLE_FONT
        ).pack(anchor="w", padx=24, pady=(22, 6))
        preview = ctk.CTkFrame(modal, width=300, height=300, fg_color=WHITE,
                               corner_radius=8)
        preview.pack(pady=(0, 14))
        preview.pack_propagate(False)
        preview_label = ctk.CTkLabel(
            preview, text="Image Preview", text_color="black", font=MODAL_FONT
        )
        preview_label.pack(pady=(10, 10), anchor="center", expand=True)
        if item.image_path and os.path.isfile(item.image_path):
            try:
                source = Image.open(item.image_path)
                image_preview = ctk.CTkImage(
                    light_image=source, dark_image=source, size=(270, 270)
                )
                preview_label.configure(image=image_preview, text="")
                preview_label.image = image_preview
            except (OSError, ValueError):
                pass
        card = ctk.CTkFrame(modal, fg_color=MODAL_BG, corner_radius=8,
                            border_width=1, border_color="#334b80")
        card.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        ctk.CTkLabel(card, text=f"Category: {item.category_name}",
                     text_color=WHITE, font=MODAL_FONT).pack(anchor="w", padx=18, pady=(8, 4))
        ctk.CTkLabel(card, text=f"Item ID: {item.item_id}",
                     text_color=WHITE, font=MODAL_FONT).pack(anchor="w", padx=18, pady=(0, 8))
        details = ctk.CTkTextbox(card, height=150, corner_radius=8,
                                 fg_color=WHITE, text_color="black")
        details.pack(fill="both", expand=True, padx=18, pady=(0, 12))
        details.insert("1.0", "\n".join(
            f"{key.replace('_', ' ').title()}: {value}"
            for key, value in item.to_dict().items()
        ))
        details.configure(state="disabled")
        btn_frame = ctk.CTkFrame(modal, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(0, 18))

    def manage(item_id):
        item = inventory_repo.get_by_id(item_id)
        if item:
            item_form(item=item, manage=True)

    def load_inventory_cards():
        for widget in cards.winfo_children():
            widget.destroy()
        try:
            items = inventory_repo.get_all(search_term=search.get())
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
    ctk.CTkButton(header, text="Refresh", width=80, command=load_inventory_cards).pack(
        side="right", padx=10, pady=8)
    load_inventory_cards()
    return inventory_frame

inventory_frame = create_inventory_tab_v2(main_bg)
inventory_frame.pack_forget()

def show_tab(selected_tab):
    if selected_tab == "Analytics":
        inventory_frame.pack_forget()
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    elif selected_tab == "Inventory Managemt":
        content_frame.pack_forget()
        inventory_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    else:
        messagebox.showinfo(
            "Unavailable",
            f"The {selected_tab} section is not available yet.",
        )
        return

    for tab, button in nav_buttons.items():
        button.configure(fg_color=DARK_BLUE if tab == selected_tab else TEXT_BLUE)


app.mainloop()