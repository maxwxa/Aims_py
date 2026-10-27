import os
import subprocess
import sys
from datetime import datetime
from tkinter import messagebox, ttk
import customtkinter as ctk
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from models.account_validation import (
    validate_contact_number, validate_email, validate_password,
    validate_student_number,
)
from repositories import UserRepository

ctk.set_appearance_mode("light")
app = ctk.CTk()
app.geometry("900x550")
app.title("Academic Inventory Management System - Register")

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
CARD_GRAY = "#f3f4f6"
BORDER_GRAY = "#d1d5db"

department_data = {
    "College of Arts & Sciences": [
        "ABCom - Bachelor of Arts in Communication",
        "ABEng - Bachelor of Arts in English",
        "BSM - Bachelor of Science in Mathematics",
        "BSP - Bachelor of Science in Psychology"
    ],
    "College of Business & Accountancy": [
        "ABA - Associate in Business Administration",
        "BSAIS - Bachelor of Science in Accounting Information System",
        "BSA - Bachelor of Science in Accountancy",
        "BSMA - Bachelor of Science in Management Accounting",
        "BSREM - Bachelor of Science in Real Estate Management",
        "BSIA - Bachelor of Science in Internal Auditing",
        "BSLM - Bachelor of Science in Legal Management",
        "BSBA - Bachelor of Science in Business Administration"
    ],
    "College of Computer Studies": [
        "ACT - Associate in Computer Technology",
        "BSCS - Bachelor of Science in Computer Science",
        "BSIT - Bachelor of Science in Information Technology",
        "BSIS - Bachelor of Science in Information System"
    ],
    "College of Teacher Education": [
        "BECEd - Bachelor in Early Childhood Education",
        "BELEMEd - Bachelor in Elementary Education",
        "BSEd - Bachelor in Secondary Education",
        "BTVTEd - Bachelor in Technical Vocational Teacher Education",
        "CPT - Certificate in Teaching Program"
    ],
    "College of Criminology & Administration": [
        "BSC - Bachelor of Science in Criminology",
        "BSISM - Bachelor of Science in Industrial Security Management",
        "BPA - Bachelor in Public Administration"
    ],
    "College of Engineering": [
        "BSCE - Bachelor of Science in Computer Engineering",
        "BSELE - Bachelor of Science in Electronics Engineering"
    ],
    "College of Health Sciences": [
        "BSMedTech - Bachelor of Science in Medical Technology",
        "BSN - Bachelor of Science in Nursing",
        "BSRadTech - Bachelor of Science in Radiologic Technology",
        "DHWA - Diploma in Health Care & Wellness Associate"
    ],
    "International School of Hospitality & Tourism Management": [
        "BSHM - Bachelor of Science in Hospitality Management",
        "BSTM - Bachelor of Science in Tourism Management",
        "DHRM1 - Diploma in Hotel & Restaurant Management-1",
        "DHRM2 - Diploma in Hotel & Restaurant Management-2"
    ],
    "Senior High Department": [
        "ACADEMIC-TRACK",
        "TECH-PRO-TRACK"
    ]
}

main_bg = ctk.CTkFrame(app, fg_color=BLUE_BG, corner_radius=0)
main_bg.pack(fill="both", expand=True)

card_frame = ctk.CTkFrame(main_bg, width=1050, height=660, fg_color=CARD_GRAY, corner_radius=15)
card_frame.place(relx=0.5, rely=0.5, anchor="center")

ctk.CTkLabel(card_frame, text="Create Your Account", font=("Arial", 32, "bold"), text_color=TEXT_BLUE).place(relx=0.5, y=35, anchor="n")

form_frame = ctk.CTkFrame(card_frame, width=980, height=480, fg_color=CARD_GRAY, corner_radius=10, border_width=2, border_color="black")
form_frame.place(relx=0.5, y=95, anchor="n")

ctk.CTkFrame(form_frame, width=2, height=476, fg_color="black").place(x=280, y=2)

left_section = ctk.CTkFrame(form_frame, width=276, height=476, fg_color=CARD_GRAY, corner_radius=0)
left_section.place(x=2, y=2)

ctk.CTkLabel(left_section, text="Account Information", font=("Arial", 16, "bold"), text_color=TEXT_BLUE).place(relx=0.5, y=15, anchor="n")

ctk.CTkLabel(left_section, text="Email", font=("Arial", 12, "bold"), text_color="black").place(x=25, y=65)
email_entry = ctk.CTkEntry(left_section, width=225, height=35, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black")
email_entry.place(x=25, y=90)

ctk.CTkLabel(left_section, text="Password", font=("Arial", 12, "bold"), text_color="black").place(x=25, y=140)
password_entry = ctk.CTkEntry(left_section, width=225, height=35, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black", show="*")
password_entry.place(x=25, y=165)

def toggle_password():
    password_entry.configure(show="" if show_pass_var.get() == 1 else "*")

show_pass_var = ctk.IntVar()
ctk.CTkCheckBox(left_section, text="Show Password", variable=show_pass_var, command=toggle_password, font=("Arial", 12), checkbox_height=18, checkbox_width=18, border_color=BORDER_GRAY, fg_color=TEXT_BLUE, text_color="black").place(x=25, y=210)

logo_path = os.path.join(os.path.dirname(__file__), "assets", "Aims_plain_black.png")
if not os.path.exists(logo_path):
    logo_path = os.path.join(os.path.dirname(__file__), "Assets", "Aims_plain_black.png")
try:
    if os.path.exists(logo_path):
        logo_img_data = Image.open(logo_path)
        logo_image = ctk.CTkImage(light_image=logo_img_data, dark_image=logo_img_data, size=(150, 150))
        ctk.CTkLabel(left_section, image=logo_image, text="").place(relx=0.5, y=340, anchor="center")
    else:
        ctk.CTkLabel(left_section, text="[ A.I.M.S ]", text_color="gray", font=("Arial", 20, "bold")).place(relx=0.5, y=340, anchor="center")
except Exception as e:
    pass

right_section = ctk.CTkFrame(form_frame, width=694, height=476, fg_color=CARD_GRAY, corner_radius=0)
right_section.place(x=284, y=2)

ctk.CTkLabel(right_section, text="Personal Information", font=("Arial", 16, "bold"), text_color=TEXT_BLUE).place(relx=0.5, y=15, anchor="n")
ctk.CTkLabel(right_section, text="First Name", font=("Arial", 12, "bold"), text_color="black").place(x=25, y=65)
fname_entry = ctk.CTkEntry(right_section, width=200, height=35, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black")
fname_entry.place(x=25, y=90)

ctk.CTkLabel(right_section, text="Middle Name (Optional)", font=("Arial", 12, "bold"), text_color="black").place(x=245, y=65)
mname_entry = ctk.CTkEntry(right_section, width=200, height=35, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black")
mname_entry.place(x=245, y=90)

ctk.CTkLabel(right_section, text="Last Name", font=("Arial", 12, "bold"), text_color="black").place(x=465, y=65)
lname_entry = ctk.CTkEntry(right_section, width=200, height=35, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black")
lname_entry.place(x=465, y=90)

ctk.CTkLabel(right_section, text="Contact No.", font=("Arial", 12, "bold"), text_color="black").place(x=25, y=140)
contact_entry = ctk.CTkEntry(right_section, width=200, height=35, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black")
contact_entry.place(x=25, y=165)

ctk.CTkLabel(right_section, text="Birthday", font=("Arial", 12, "bold"), text_color="black").place(x=245, y=140)
bday_frame = ctk.CTkFrame(right_section, width=200, height=35, fg_color=WHITE, corner_radius=8, border_width=1, border_color=BORDER_GRAY)
bday_frame.place(x=245, y=165)

date_entry_style = ttk.Style(bday_frame)
date_entry_style.configure("Birthday.TEntry", padding=(8, 4), font=("Arial", 12))
bday_entry = DateEntry(bday_frame, background=WHITE, foreground="black", borderwidth=0, date_pattern="yyyy-mm-dd", state="readonly", font=("Arial", 12), style="Birthday.TEntry")
bday_entry.pack(fill="both", expand=True, padx=2, pady=2)

ctk.CTkLabel(right_section, text="Gender", font=("Arial", 12, "bold"), text_color="black").place(x=465, y=140)
gender_combo = ctk.CTkComboBox(right_section, width=200, height=35, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black", button_color=BORDER_GRAY, button_hover_color="gray", values=["Male", "Female", "Other", "Prefer not to say"], state="readonly")
gender_combo.place(x=465, y=165)

ctk.CTkLabel(right_section, text="Student No.", font=("Arial", 12, "bold"), text_color="black").place(x=25, y=215)
student_no_entry = ctk.CTkEntry(right_section, width=200, height=35, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black")
student_no_entry.place(x=25, y=240)

def update_courses(choice):
    courses = department_data.get(choice, [])
    course_combo.configure(values=courses)
    if courses:
        course_combo.set(courses[0])
    else:
        course_combo.set("")

ctk.CTkLabel(right_section, text="Department", font=("Arial", 12, "bold"), text_color="black").place(x=245, y=215)
dept_combo = ctk.CTkComboBox(right_section, width=200, height=35, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black", button_color=BORDER_GRAY, button_hover_color="gray", values=list(department_data.keys()), command=update_courses, state="readonly")
dept_combo.place(x=245, y=240)

ctk.CTkLabel(right_section, text="Course", font=("Arial", 12, "bold"), text_color="black").place(x=465, y=215)
course_combo = ctk.CTkComboBox(right_section, width=200, height=35, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black", button_color=BORDER_GRAY, button_hover_color="gray", values=[], state="readonly")
course_combo.place(x=465, y=240)

initial_dept = list(department_data.keys())[0]
dept_combo.set(initial_dept)
update_courses(initial_dept)

ctk.CTkLabel(right_section, text="Address :", font=("Arial", 12, "bold"), text_color="black").place(x=25, y=290)
address_textbox = ctk.CTkTextbox(right_section, width=640, height=130, corner_radius=8, border_width=1, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black")
address_textbox.place(x=25, y=315)

def open_login():
    app.destroy()
    subprocess.Popen([sys.executable, "main.py"])

def register_user():
    email = email_entry.get().strip().lower()
    password = password_entry.get()
    fname = fname_entry.get().strip()
    mname = mname_entry.get().strip()
    lname = lname_entry.get().strip()
    contact = contact_entry.get().strip()
    bday = bday_entry.get()
    gender = gender_combo.get()
    student_no = student_no_entry.get().strip().upper()
    dept = dept_combo.get()
    course = course_combo.get()
    address = address_textbox.get("1.0", "end-1c").strip()

    if not email or not password or not fname or not lname or not student_no or not course:
        messagebox.showwarning(
            "Validation Error",
            "Email, Password, First Name, Last Name, Student No., and Course are required.",
        )
        return
    try:
        validate_email(email)
        validate_student_number(student_no)
        validate_contact_number(contact)
        validate_password(password)
    except ValueError as error:
        messagebox.showerror("Validation Error", str(error))
        return

    account_data = {
        "gmail": email,
        "password": password,
        "role": "Student",
        "status": "Active",
    }
    personal_data = {
        "student_id": student_no,
        "first_name": fname,
        "middle_name": mname,
        "last_name": lname,
        "birthday": bday,
        "contact_number": contact,
        "department": dept,
        "course": course,
        "gender": gender,
        "address": address,
    }

    try:
        user_repo = UserRepository()
        user_repo.add_user(account_data, personal_data)
        messagebox.showinfo("Success", "Account registered successfully! Returning to login.")
        open_login()
    except ValueError as err:
        messagebox.showerror("Registration Failed", str(err))
    except Exception as err:
        messagebox.showerror("Database Connection Error", f"Registration failed due to database connection loss or error: {err}")

ctk.CTkButton(card_frame, text="Back to Login", width=140, height=40, fg_color=CARD_GRAY, text_color=TEXT_BLUE, border_color=TEXT_BLUE, border_width=1, hover_color="#eff6ff", corner_radius=8, font=("Arial", 14, "bold"), command=open_login).place(x=35, y=595)
ctk.CTkButton(card_frame, text="Register", width=140, height=40, fg_color=TEXT_BLUE, hover_color="#1d4ed8", corner_radius=8, font=("Arial", 14, "bold"), command=register_user).place(x=875, y=595)

app.mainloop()