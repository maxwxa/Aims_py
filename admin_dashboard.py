import customtkinter as ctk
from tkinter import ttk, messagebox
from PIL import Image
import os
import subprocess
import sys
import mysql.connector
import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

app = ctk.CTk()
app.geometry("1000x650")
app.title("(Analytics) admin_dashboard.py")
app.resizable(False, False)
ctk.set_appearance_mode("light")

session_path = "session.json"

if not os.path.exists(session_path):
    messagebox.showerror("Access Denied", "No active session found. Please log in.")
    app.destroy()
    subprocess.Popen([sys.executable, "login.py"])
    sys.exit()

# Read the session file
try:
    with open(session_path, "r") as f:
        current_user = json.load(f)
except json.JSONDecodeError:
    current_user = {}

# Verify the user actually has Admin privileges
if current_user.get("role", "").lower() != "admin":
    messagebox.showerror("Unauthorized", "You do not have admin permissions.")
    if os.path.exists(session_path):
        os.remove(session_path) # Destroy invalid session
    app.destroy()
    subprocess.Popen([sys.executable, "login.py"])
    sys.exit()

# --- Colors ---
DARK_BLUE = "#1e3aa8"    # Header & Active tabs
BG_BLUE = "#a5b4fc"      # Main background
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"
RED = "#ef4444"

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
    app.destroy()
    subprocess.Popen([sys.executable, "login.py"])

logout_btn = ctk.CTkButton(header_frame, text="Log out", width=100, height=35, fg_color=RED, hover_color="#dc2626", corner_radius=8, font=("Arial", 14, "bold"), command=logout)
logout_btn.place(x=870, y=22)

# ==========================================
# NAVIGATION BAR
# ==========================================
nav_frame = ctk.CTkFrame(main_bg, height=60, fg_color=WHITE, corner_radius=20)
nav_frame.pack(fill="x", padx=20, pady=15)

tabs = ["Analytics", "Inventory Managemt", "Request", "Transactions", "Accounts"]
for i, tab in enumerate(tabs):
    bg_color = DARK_BLUE if tab == "Analytics" else TEXT_BLUE
    btn = ctk.CTkButton(nav_frame, text=tab, width=160, height=35, fg_color=bg_color, corner_radius=15, font=("Arial", 12, "bold"))
    btn.place(x=20 + (i * 180), y=12)

# ==========================================
# MAIN CONTENT AREA
# ==========================================
content_frame = ctk.CTkFrame(main_bg, fg_color=DARK_BLUE, corner_radius=15)
content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

# Content Header
ctk.CTkLabel(content_frame, text="Data Insights", font=("Arial", 18, "bold"), text_color=WHITE).place(x=20, y=10)
ctk.CTkButton(content_frame, text="Refresh", width=80, height=28, fg_color=WHITE, text_color=DARK_BLUE, corner_radius=15, font=("Arial", 12, "bold")).place(x=850, y=10)

# Inner Split Container
inner_frame = ctk.CTkFrame(content_frame, fg_color=BG_BLUE, corner_radius=0)
inner_frame.pack(fill="both", expand=True, padx=2, pady=(45, 2))

# --- LEFT PANEL: CHARTS ---
chart_card = ctk.CTkFrame(inner_frame, width=460, fg_color=WHITE, corner_radius=15, border_width=1, border_color="#d1d5db")
chart_card.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
chart_card.pack_propagate(False)

ctk.CTkLabel(chart_card, text="System Analytics", font=("Arial", 16, "bold"), text_color=TEXT_BLUE).pack(pady=(10, 0))

# Matplotlib Figure integration
fig = Figure(figsize=(5, 4), dpi=100)
fig.patch.set_facecolor('#ffffff')

# Subplot 1: Users by Department (Donut Chart)
ax1 = fig.add_subplot(211)
# NOTE: Replace with -> cursor.execute("SELECT department, COUNT(*) FROM personal_info GROUP BY department")
dept_labels = ['IT', 'Engineering', 'Business', 'Health']
dept_sizes = [45, 25, 20, 10]
wedges, texts, autotexts = ax1.pie(dept_sizes, labels=dept_labels, autopct='%1.1f%%', startangle=90, colors=['#3b82f6', '#8b5cf6', '#f59e0b', '#10b981'])
centre_circle = plt.Circle((0,0),0.60,fc='white')
fig.gca().add_artist(centre_circle)
ax1.set_title("Users by Department", fontsize=10, fontweight='bold', pad=5)

# Subplot 2: Most Requested Items (Bar Chart)
ax2 = fig.add_subplot(212)
# NOTE: Replace with -> cursor.execute("SELECT i.item_name, SUM(r.quantity) FROM item_requests r JOIN inventory_items i ON r.item_id = i.item_id GROUP BY i.item_name ORDER BY SUM(r.quantity) DESC LIMIT 3")
items = ['Arduino Uno', 'ESP32', 'Breadboard']
requests = [120, 95, 80]
ax2.bar(items, requests, color=['#1e3a8a', '#2563eb', '#60a5fa'])
ax2.set_title("Most Requested Items", fontsize=10, fontweight='bold', pad=5)
fig.tight_layout()

# Embed the chart into the Tkinter window
canvas = FigureCanvasTkAgg(fig, master=chart_card)
canvas.draw()
canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)


# --- RIGHT PANEL: LOGS TABLE ---
logs_card = ctk.CTkFrame(inner_frame, width=460, fg_color=WHITE, corner_radius=15, border_width=1, border_color="#d1d5db")
logs_card.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
logs_card.pack_propagate(False)

# Logs Header
log_top = ctk.CTkFrame(logs_card, height=40, fg_color=DARK_BLUE, corner_radius=15)
log_top.pack(fill="x", padx=10, pady=10)

ctk.CTkLabel(log_top, text="Logs", font=("Arial", 16, "bold"), text_color=WHITE).place(x=15, y=5)
ctk.CTkButton(log_top, text="Refresh", width=70, height=25, fg_color=WHITE, text_color=DARK_BLUE, corner_radius=15).place(x=150, y=7)
ctk.CTkLabel(log_top, text="Search:", font=("Arial", 12, "bold"), text_color=WHITE).place(x=230, y=8)
ctk.CTkEntry(log_top, width=130, height=25, corner_radius=10, fg_color=WHITE, text_color="black").place(x=290, y=7)

# Treeview (Table) Styling
style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", background=WHITE, foreground="black", rowheight=25, fieldbackground=WHITE, borderwidth=0)
style.configure("Treeview.Heading", background=BG_BLUE, foreground="black", font=('Arial', 10, 'bold'))
style.map('Treeview', background=[('selected', '#dbeafe')])

# Treeview Setup
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

# Dummy Data (Replace with: SELECT * FROM logs ORDER BY timestamp DESC)
dummy_logs = [
    (1, 101, "User Registered", "user_account", 101, "2026-10-18 10:05"),
    (2, 105, "Item Requested", "item_requests", 42, "2026-10-18 11:30"),
    (3, 2, "Stock Updated", "inventory_items", 15, "2026-10-18 14:15"),
]
for log in dummy_logs:
    tree.insert("", "end", values=log)

tree.pack(side="left", fill="both", expand=True)

# Scrollbar for Table
scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

def logout():
    # Completely destroy the session file
    if os.path.exists(session_path):
        os.remove(session_path)
        
    app.destroy()
    subprocess.Popen([sys.executable, "login.py"])

app.mainloop()