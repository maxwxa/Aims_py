import os
import subprocess
import sys
from tkinter import TclError, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
from models.password_utils import verify_password
from models.users import Session
from repositories import UserRepository

ctk.set_appearance_mode("light")

app = ctk.CTk()

def destroy_login_window() -> None:
    try:
        if app.winfo_exists():
            app.destroy()
    except TclError:
        pass

app.geometry("900x550")
app.title("Academic Inventory Management System - Login")

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

BLUE_BG = "#1e3a8a"
TEXT_BLUE = "#2563eb"
WHITE = "#ffffff"
BG_GRAY = "#f3f4f6"

left_frame = ctk.CTkFrame(app, fg_color=BLUE_BG, corner_radius=0)
left_frame.pack(side="left", fill="both", expand=True)
right_frame = ctk.CTkFrame(app, fg_color=BG_GRAY, corner_radius=0)
right_frame.pack(side="right", fill="both", expand=True)

left_content = ctk.CTkFrame(left_frame, fg_color="transparent")
left_content.place(relx=0.5, rely=0.5, anchor="center")

logo_path = os.path.join(os.path.dirname(__file__), "assets", "Aims_plain_white.png")
if not os.path.exists(logo_path):
    logo_path = os.path.join(os.path.dirname(__file__), "Assets", "Aims_plain_white.png")
try:
    if os.path.exists(logo_path):
        logo_img_data = Image.open(logo_path)
        logo_image = ctk.CTkImage(light_image=logo_img_data, dark_image=logo_img_data, size=(260, 260))
        logo_label = ctk.CTkLabel(left_content, image=logo_image, text="")
        logo_label.pack(pady=(0, 15))
    else:
        logo_label = ctk.CTkLabel(left_content, text="[ A.I.M.S LOGO ]", text_color=WHITE, font=("Arial", 20, "bold"))
        logo_label.pack(pady=(0, 15))
except Exception as e:
    pass

ctk.CTkLabel(left_content, text="A.I.M.S", font=("Arial", 56, "bold"), text_color=WHITE).pack(pady=(0, 5))
ctk.CTkLabel(left_content, text="Academic Inventory\nManagement System", font=("Arial", 42, "bold"), text_color=WHITE, justify="center").pack()

card_frame = ctk.CTkFrame(right_frame, width=440, height=440, fg_color=WHITE, corner_radius=15, border_width=1, border_color="#e5e7eb")
card_frame.place(relx=0.5, rely=0.5, anchor="center")

ctk.CTkLabel(card_frame, text="Login", font=("Arial", 32, "bold"), text_color=TEXT_BLUE).place(relx=0.5, y=35, anchor="n")

ctk.CTkLabel(card_frame, text="Email", font=("Arial", 12, "bold"), text_color="black").place(x=25, y=95)
email_entry = ctk.CTkEntry(card_frame, width=390, height=40, corner_radius=8, border_color="#d1d5db", fg_color=WHITE, text_color="black")
email_entry.place(x=25, y=120)

ctk.CTkLabel(card_frame, text="Password", font=("Arial", 12, "bold"), text_color="black").place(x=25, y=175)
password_entry = ctk.CTkEntry(card_frame, width=390, height=40, corner_radius=8, border_color="#d1d5db", fg_color=WHITE, text_color="black", show="*")
password_entry.place(x=25, y=200)

def show_loading_screen(user, dashboard_path):
    left_frame.pack_forget()
    right_frame.pack_forget()

    loading_frame = ctk.CTkFrame(app, fg_color=BLUE_BG, corner_radius=0)
    loading_frame.pack(fill="both", expand=True)

    loading_center = ctk.CTkFrame(loading_frame, fg_color="transparent")
    loading_center.place(relx=0.5, rely=0.5, anchor="center")

    if os.path.exists(logo_path):
        try:
            load_logo_img = Image.open(logo_path)
            load_logo = ctk.CTkImage(light_image=load_logo_img, dark_image=load_logo_img, size=(220, 220))
            ctk.CTkLabel(loading_center, image=load_logo, text="").pack(pady=(0, 20))
        except Exception:
            ctk.CTkLabel(loading_center, text="A.I.M.S", font=("Arial", 40, "bold"), text_color=WHITE).pack(pady=(0, 20))
    else:
        ctk.CTkLabel(loading_center, text="A.I.M.S", font=("Arial", 40, "bold"), text_color=WHITE).pack(pady=(0, 20))

    ctk.CTkLabel(
        loading_center,
        text="Loading Dashboard...",
        font=("Arial", 22, "bold"),
        text_color=WHITE,
    ).pack(pady=(0, 10))

    status_label = ctk.CTkLabel(
        loading_center,
        text="Initializing components...",
        font=("Arial", 13),
        text_color="#93c5fd",
    )
    status_label.pack(pady=(0, 20))

    progress_bar = ctk.CTkProgressBar(
        loading_center,
        width=400,
        height=16,
        corner_radius=8,
        fg_color="#172554",
        progress_color="#60a5fa",
    )
    progress_bar.pack(pady=(0, 10))
    progress_bar.set(0.0)

    stages = [
        (0.20, "Authenticating session...", 250),
        (0.45, "Loading user profile & permissions...", 300),
        (0.70, "Fetching inventory & requests...", 350),
        (0.90, "Preparing dashboard interface...", 250),
        (1.00, "Ready! Launching dashboard...", 200),
    ]

    def run_stage(index):
        if index < len(stages):
            prog, msg, delay = stages[index]
            progress_bar.set(prog)
            status_label.configure(text=msg)
            app.after(delay, lambda: run_stage(index + 1))
        else:
            subprocess.Popen(
                [sys.executable, dashboard_path],
                cwd=os.path.dirname(__file__),
            )
            destroy_login_window()
            sys.exit()

    app.after(100, lambda: run_stage(0))


def authenticate_user():
    email = email_entry.get().strip()
    password = password_entry.get()
    
    if not email or not password:
        messagebox.showwarning("Validation Error", "Please fill in both email and password.")
        return

    try:
        user_repo = UserRepository()
        user = user_repo.get_by_email(email)
        
        if user:
            if verify_password(password, user['password_hash']):
                Session.save(user['user_id'], user['gmail'], user['role'])
                
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

                show_loading_screen(user, dashboard_path)
            else:
                messagebox.showerror("Login Failed", "Incorrect password.")
        else:
            messagebox.showerror("Login Failed", "Account not found. Please register.")
            
    except Exception as err:
        messagebox.showerror("Database Connection Error", f"Database connection was lost or unavailable: {err}")

def toggle_password():
    password_entry.configure(show="" if show_pass_var.get() == 1 else "*")

show_pass_var = ctk.IntVar()
ctk.CTkCheckBox(card_frame, text="Show Password?", variable=show_pass_var, command=toggle_password, font=("Arial", 11), checkbox_height=18, checkbox_width=18, border_color="#d1d5db", fg_color=TEXT_BLUE, text_color="black").place(x=25, y=250)

ctk.CTkButton(card_frame, text="Login", width=390, height=40, fg_color=TEXT_BLUE, hover_color="#1d4ed8", corner_radius=8, font=("Arial", 14, "bold"), command=authenticate_user).place(x=25, y=295)

ctk.CTkFrame(card_frame, width=290, height=2, fg_color="#e5e7eb").place(x=25, y=355)

def open_register():
    destroy_login_window()
    subprocess.Popen([sys.executable, "register.py"]) 

ctk.CTkButton(card_frame, text="Register", width=390, height=40, fg_color=WHITE, text_color=TEXT_BLUE, border_color=TEXT_BLUE, border_width=2, hover_color="#eff6ff", corner_radius=8, font=("Arial", 14, "bold"), command=open_register).place(x=25, y=375)

app.mainloop()
destroy_login_window()