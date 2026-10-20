import os
import subprocess
import sys
from tkinter import ttk, messagebox

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import mysql.connector
from PIL import Image

from models.users import Session

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
for i, tab in enumerate(tabs):
    bg_color = DARK_BLUE if tab == "Analytics" else TEXT_BLUE
    btn = ctk.CTkButton(nav_frame, text=tab, width=160, height=35, fg_color=bg_color, corner_radius=15, font=("Arial", 12, "bold"))
    btn.place(x=20 + (i * 180), y=12)

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

app.mainloop()