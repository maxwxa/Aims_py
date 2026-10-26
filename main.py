import os
import subprocess
import sys
from tkinter import TclError, messagebox

import customtkinter as ctk
import mysql.connector
from PIL import Image

from models.password_utils import verify_password
from models.users import Session

app = ctk.CTk()

def destroy_login_window() -> None:
    try:
        if app.winfo_exists():
            app.destroy()
    except TclError:
        pass

app.geometry("900x550")
app.title("Academic Inventory Management System - Login")
app.resizable(False, False)
ctk.set_appearance_mode("light")

BLUE_BG = "#1e3a8a"
TEXT_BLUE = "#2563eb"
WHITE = "#ffffff"
BG_GRAY = "#f3f4f6"

left_frame = ctk.CTkFrame(app, width=450, height=550, fg_color=BLUE_BG, corner_radius=0)
left_frame.pack(side="left", fill="both", expand=True)
right_frame = ctk.CTkFrame(app, width=450, height=550, fg_color=BG_GRAY, corner_radius=0)
right_frame.pack(side="right", fill="both", expand=True)

logo_path = r"C:\Users\maxwx\OneDrive\Documents\SDF04-Aims\Assets\Aims_plain_white.png"
try:
    if os.path.exists(logo_path):
        logo_img_data = Image.open(logo_path)
        logo_image = ctk.CTkImage(light_image=logo_img_data, dark_image=logo_img_data, size=(160, 160))
        logo_label = ctk.CTkLabel(left_frame, image=logo_image, text="")
        logo_label.pack(pady=(120, 15))
    else:
        logo_label = ctk.CTkLabel(left_frame, text="[ A.I.M.S LOGO ]", text_color=WHITE, font=("Arial", 20, "bold"))
        logo_label.pack(pady=(120, 15))
except Exception as e:
    print(f"Error loading image: {e}")

ctk.CTkLabel(left_frame, text="A.I.M.S", font=("Arial", 36, "bold"), text_color=WHITE).pack(pady=(0, 5))
ctk.CTkLabel(left_frame, text="Academic Inventory\nManagement System", font=("Arial", 22, "bold"), text_color=WHITE, justify="center").pack()

card_frame = ctk.CTkFrame(right_frame, width=340, height=440, fg_color=WHITE, corner_radius=15, border_width=1, border_color="#e5e7eb")
card_frame.place(relx=0.5, rely=0.5, anchor="center")

ctk.CTkLabel(card_frame, text="Login", font=("Arial", 28, "bold"), text_color=TEXT_BLUE).place(relx=0.5, y=35, anchor="n")

ctk.CTkLabel(card_frame, text="Email", font=("Arial", 12, "bold"), text_color="black").place(x=25, y=95)
email_entry = ctk.CTkEntry(card_frame, width=290, height=40, corner_radius=8, border_color="#d1d5db", fg_color=WHITE, text_color="black")
email_entry.place(x=25, y=120)

ctk.CTkLabel(card_frame, text="Password", font=("Arial", 12, "bold"), text_color="black").place(x=25, y=175)
password_entry = ctk.CTkEntry(card_frame, width=290, height=40, corner_radius=8, border_color="#d1d5db", fg_color=WHITE, text_color="black", show="*")
password_entry.place(x=25, y=200)

def authenticate_user():
    email = email_entry.get()
    password = password_entry.get()
    
    if not email or not password:
        messagebox.showwarning("Validation Error", "Please fill in both email and password.")
        return

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="aims_db"
        )
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT user_id, gmail, password_hash, role FROM user_account WHERE gmail = %s", (email,))
        user = cursor.fetchone()
        
        if user:
            if verify_password(password, user['password_hash']):
                Session.save(user['user_id'], user['gmail'], user['role'])
                
                messagebox.showinfo("Login Success", f"Welcome! Logged in as: {user['role']}")
                
                dashboard_name = (
                    "admin_dashboard.py"
                    if user['role'].lower() == "admin"
                    else "user_dashboard.py"
                )
                dashboard_path = os.path.join(os.path.dirname(__file__), dashboard_name)
                if not os.path.isfile(dashboard_path):
                    Session.clear()
                    messagebox.showerror(
                        "Dashboard Unavailable",
                        f"The dashboard for the {user['role']} role is not available yet.",
                    )
                    return

                subprocess.Popen(
                    [sys.executable, dashboard_path],
                    cwd=os.path.dirname(__file__),
                )
                destroy_login_window()
                sys.exit()
            else:
                messagebox.showerror("Login Failed", "Incorrect password.")
        else:
            messagebox.showerror("Login Failed", "Account not found. Please register.")
            
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Connection failed: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def toggle_password():
    password_entry.configure(show="" if show_pass_var.get() == 1 else "*")

show_pass_var = ctk.IntVar()
ctk.CTkCheckBox(card_frame, text="Show Password?", variable=show_pass_var, command=toggle_password, font=("Arial", 11), checkbox_height=18, checkbox_width=18, border_color="#d1d5db", fg_color=TEXT_BLUE, text_color="black").place(x=25, y=250)

ctk.CTkButton(card_frame, text="Login", width=290, height=40, fg_color=TEXT_BLUE, hover_color="#1d4ed8", corner_radius=8, font=("Arial", 14, "bold"), command=authenticate_user).place(x=25, y=295)

ctk.CTkFrame(card_frame, width=290, height=2, fg_color="#e5e7eb").place(x=25, y=355)

def open_register():
    destroy_login_window()
    subprocess.Popen([sys.executable, "register.py"]) 

ctk.CTkButton(card_frame, text="Register", width=290, height=40, fg_color=WHITE, text_color=TEXT_BLUE, border_color=TEXT_BLUE, border_width=2, hover_color="#eff6ff", corner_radius=8, font=("Arial", 14, "bold"), command=open_register).place(x=25, y=375)

app.mainloop()
destroy_login_window()