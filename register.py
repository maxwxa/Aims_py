# Standard library imports
import os
import subprocess
import sys
from datetime import datetime
from tkinter import messagebox

# Third-party imports
import customtkinter as ctk
import mysql.connector
from PIL import Image
from tkcalendar import DateEntry

# Local application imports
from models.password_utils import hash_password

app = ctk.CTk()
app.geometry("900x550")
app.title("register.py")
app.resizable(False, False)
ctk.set_appearance_mode("light")

BLUE_BG = "#1e3a8a"
TEXT_BLUE = "#2563eb"
WHITE = "#ffffff"
CARD_GRAY = "#f3f4f6"
BORDER_GRAY = "#d1d5db"

# --- Department Data Dictionary ---
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

main_bg = ctk.CTkFrame(app, width=900, height=550, fg_color=BLUE_BG, corner_radius=0)
main_bg.pack(fill="both", expand=True)

card_frame = ctk.CTkFrame(main_bg, width=800, height=480, fg_color=CARD_GRAY, corner_radius=15)
card_frame.place(relx=0.5, rely=0.5, anchor="center")

ctk.CTkLabel(card_frame, text="Create Your Account", font=("Arial", 28, "bold"), text_color=TEXT_BLUE).place(relx=0.5, y=30, anchor="n")

form_frame = ctk.CTkFrame(card_frame, width=720, height=340, fg_color=CARD_GRAY, corner_radius=10, border_width=2, border_color="black")
form_frame.place(relx=0.5, y=80, anchor="n")

ctk.CTkFrame(form_frame, width=2, height=336, fg_color="black").place(x=220, y=2)

# ==========================================
# LEFT SECTION: Account Information
# ==========================================
left_section = ctk.CTkFrame(form_frame, width=216, height=336, fg_color=CARD_GRAY, corner_radius=0)
left_section.place(x=2, y=2)

ctk.CTkLabel(left_section, text="Account Information", font=("Arial", 14, "bold"), text_color=TEXT_BLUE).place(relx=0.5, y=10, anchor="n")

ctk.CTkLabel(left_section, text="Email", font=("Arial", 11, "bold"), text_color="black").place(x=15, y=45)
email_entry = ctk.CTkEntry(left_section, width=180, height=30, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black")
email_entry.place(x=15, y=65)

ctk.CTkLabel(left_section, text="Password", font=("Arial", 11, "bold"), text_color="black").place(x=15, y=100)
password_entry = ctk.CTkEntry(left_section, width=180, height=30, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black", show="*")
password_entry.place(x=15, y=120)

def toggle_password():
    password_entry.configure(show="" if show_pass_var.get() == 1 else "*")

show_pass_var = ctk.IntVar()
ctk.CTkCheckBox(left_section, text="Show Password", variable=show_pass_var, command=toggle_password, font=("Arial", 11), checkbox_height=16, checkbox_width=16, border_color=BORDER_GRAY, fg_color=TEXT_BLUE, text_color="black").place(x=15, y=155)

logo_path = r"C:\Users\maxwx\OneDrive\Documents\SDF04-Aims\Assets\Aims_plain_black.png"
try:
    if os.path.exists(logo_path):
        logo_img_data = Image.open(logo_path)
        logo_image = ctk.CTkImage(light_image=logo_img_data, dark_image=logo_img_data, size=(120, 120))
        ctk.CTkLabel(left_section, image=logo_image, text="").place(relx=0.5, y=240, anchor="center")
    else:
        ctk.CTkLabel(left_section, text="[ A.I.M.S ]", text_color="gray", font=("Arial", 16, "bold")).place(relx=0.5, y=240, anchor="center")
except Exception as e:
    pass

# ==========================================
# RIGHT SECTION: Personal Information
# ==========================================
right_section = ctk.CTkFrame(form_frame, width=494, height=336, fg_color=CARD_GRAY, corner_radius=0)
right_section.place(x=224, y=2)

ctk.CTkLabel(right_section, text="Personal Information", font=("Arial", 14, "bold"), text_color=TEXT_BLUE).place(relx=0.5, y=10, anchor="n")

ctk.CTkLabel(right_section, text="First Name", font=("Arial", 11, "bold"), text_color="black").place(x=15, y=45)
fname_entry = ctk.CTkEntry(right_section, width=145, height=30, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black")
fname_entry.place(x=15, y=65)

ctk.CTkLabel(right_section, text="Middle Name (Optional)", font=("Arial", 11, "bold"), text_color="black").place(x=175, y=45)
mname_entry = ctk.CTkEntry(right_section, width=145, height=30, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black")
mname_entry.place(x=175, y=65)

ctk.CTkLabel(right_section, text="Last Name", font=("Arial", 11, "bold"), text_color="black").place(x=335, y=45)
lname_entry = ctk.CTkEntry(right_section, width=145, height=30, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black")
lname_entry.place(x=335, y=65)

ctk.CTkLabel(right_section, text="Contact No.", font=("Arial", 11, "bold"), text_color="black").place(x=15, y=100)
contact_entry = ctk.CTkEntry(right_section, width=145, height=30, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black")
contact_entry.place(x=15, y=120)

ctk.CTkLabel(right_section, text="Birthday", font=("Arial", 11, "bold"), text_color="black").place(x=175, y=100)

bday_frame = ctk.CTkFrame(
    right_section,
    width=145,
    height=30,
    fg_color=WHITE,
    corner_radius=8,
    border_width=1,
    border_color=BORDER_GRAY,
)
bday_frame.place(x=175, y=120)

bday_entry = DateEntry(
    bday_frame,
    background="#2563eb",
    foreground="white",
    borderwidth=0,              # Removes the native ttk border
    date_pattern="yyyy-mm-dd",
    state="readonly",
    font=("Arial", 11)
)
# Increase the x/y offset and reduce width/height slightly 
# so the sharp corners sit inside the frame's rounded edges
bday_entry.place(x=3, y=3, width=138, height=24)
ctk.CTkLabel(right_section, text="Gender", font=("Arial", 11, "bold"), text_color="black").place(x=335, y=100)
gender_combo = ctk.CTkComboBox(right_section, width=145, height=30, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black", button_color=BORDER_GRAY, button_hover_color="gray", values=["Male", "Female", "Other", "Prefer not to say"])
gender_combo.place(x=335, y=120)

ctk.CTkLabel(right_section, text="Student No.", font=("Arial", 11, "bold"), text_color="black").place(x=15, y=155)
student_no_entry = ctk.CTkEntry(right_section, width=145, height=30, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black")
student_no_entry.place(x=15, y=175)

def update_courses(choice):
    courses = department_data.get(choice, [])
    course_combo.configure(values=courses)
    if courses:
        course_combo.set(courses[0])
    else:
        course_combo.set("")

ctk.CTkLabel(right_section, text="Department", font=("Arial", 11, "bold"), text_color="black").place(x=175, y=155)
dept_combo = ctk.CTkComboBox(right_section, width=145, height=30, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black", button_color=BORDER_GRAY, button_hover_color="gray", values=list(department_data.keys()), command=update_courses)
dept_combo.place(x=175, y=175)

ctk.CTkLabel(right_section, text="Course", font=("Arial", 11, "bold"), text_color="black").place(x=335, y=155)
course_combo = ctk.CTkComboBox(right_section, width=145, height=30, corner_radius=8, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black", button_color=BORDER_GRAY, button_hover_color="gray", values=[])
course_combo.place(x=335, y=175)

ctk.CTkLabel(right_section, text="Address :", font=("Arial", 11, "bold"), text_color="black").place(x=15, y=210)
address_textbox = ctk.CTkTextbox(right_section, width=465, height=90, corner_radius=8, border_width=1, border_color=BORDER_GRAY, fg_color=WHITE, text_color="black")
address_textbox.place(x=15, y=230)


# ==========================================
# BUTTONS AND LOGIC
# ==========================================
def open_login():
    app.destroy()
    subprocess.Popen([sys.executable, "main.py"])

ctk.CTkButton(card_frame, text="Back to Login", width=120, height=35, fg_color=CARD_GRAY, text_color=TEXT_BLUE, border_color=TEXT_BLUE, border_width=1, hover_color="#eff6ff", corner_radius=8, font=("Arial", 12, "bold"), command=open_login).place(x=545, y=430)

def register_user():
    email = email_entry.get().strip().lower()
    password = password_entry.get()
    fname = fname_entry.get()
    mname = mname_entry.get()
    lname = lname_entry.get()
    contact = contact_entry.get()
    bday = bday_entry.get()
    gender = gender_combo.get()
    student_no = student_no_entry.get().strip().upper()
    dept = dept_combo.get()
    course = course_combo.get()
    address = address_textbox.get("1.0", "end-1c")

    if not email or not password or not fname or not lname or not student_no:
        messagebox.showwarning("Validation Error", "Email, Password, First Name, Last Name, and Student No. are required.")
        return

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="aims_db"
        )
        cursor = conn.cursor()

        # Compare normalized values so case and surrounding spaces cannot bypass
        # the duplicate checks.
        cursor.execute(
            "SELECT user_id FROM user_account WHERE LOWER(TRIM(gmail)) = %s",
            (email,),
        )
        if cursor.fetchone():
            messagebox.showerror("Registration Failed", "This email address is already registered.")
            cursor.close()
            conn.close()
            return

        cursor.execute(
            "SELECT personal_id FROM personal_info "
            "WHERE UPPER(TRIM(student_id)) = %s",
            (student_no,),
        )
        if cursor.fetchone():
            messagebox.showerror("Registration Failed", "This Student No. is already registered.")
            cursor.close()
            conn.close()
            return

        creation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        hashed_password = hash_password(password)
        
        user_sql = "INSERT INTO user_account (gmail, password_hash, role, creationdate) VALUES (%s, %s, %s, %s)"
        
        cursor.execute(user_sql, (email, hashed_password, "Student", creation_date))
        
        new_user_id = cursor.lastrowid
        
        info_sql = """
            INSERT INTO personal_info 
            (user_id, student_id, first_name, middle_name, last_name, birthday, contact_number, department, course, gender, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(info_sql, (new_user_id, student_no, fname, mname, lname, bday, contact, dept, course, gender, address))
        
        conn.commit()
        messagebox.showinfo("Success", "Account registered successfully! Returning to login.")
        open_login()
        
    except mysql.connector.Error as err:
        conn.rollback()
        print("\n=== DATABASE ERROR ===")
        print(f"Error Code: {err.errno}")
        print(f"SQLSTATE: {err.sqlstate}")
        print(f"Message: {err.msg}")
        print("======================\n")
        messagebox.showerror("Database Error", "Registration failed. Check console for details.")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

ctk.CTkButton(card_frame, text="Register", width=120, height=35, fg_color=TEXT_BLUE, hover_color="#1d4ed8", corner_radius=8, font=("Arial", 12, "bold"), command=register_user).place(x=675, y=430)

app.mainloop()