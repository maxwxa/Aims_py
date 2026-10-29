import os
import subprocess
import sys
from tkinter import messagebox, ttk
import customtkinter as ctk
from PIL import Image, ImageTk
from models.users import Session
from repositories import UserRepository
from admin_dashboard.sidebar import Sidebar
from admin_dashboard.views.dashboard_home import DashboardHomeView
from admin_dashboard.views.inventory_view import InventoryView
from admin_dashboard.views.requests_view import RequestsView
from admin_dashboard.views.transactions_view import TransactionsView
from admin_dashboard.views.users_view import UsersView

DARK_BLUE = "#1c3b7a"
BG_BLUE = "#eef2ff"
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"


class AdminDashboardApp:
    def __init__(self):
        ctk.set_appearance_mode("light")
        self.app = ctk.CTk()
        self.app.geometry("1920x1080")
        self.app.title("Academic Inventory Management System - Admin Dashboard")

        self._set_icon()
        self._set_window_state()
        self._check_session()
        self._load_user_info()
        self._configure_styles()
        self._build_ui()

    def _set_icon(self):
        root_dir = os.path.dirname(os.path.dirname(__file__))
        icon_path = os.path.join(root_dir, "assets", "Aims_plain_white.png")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(root_dir, "Assets", "Aims_plain_white.png")
        if os.path.exists(icon_path):
            try:
                app_icon = ImageTk.PhotoImage(Image.open(icon_path))
                self.app.wm_iconphoto(True, app_icon)
                self.app._app_icon = app_icon
            except Exception:
                pass

    def _set_window_state(self):
        try:
            self.app.state("zoomed")
        except Exception:
            pass
        self.app.after(100, lambda: self.app.state("zoomed"))

    def _check_session(self):
        root_dir = os.path.dirname(os.path.dirname(__file__))
        self.current_user = Session.load()
        if not self.current_user:
            messagebox.showerror("Access Denied", "No active session found. Please log in.")
            self.app.destroy()
            subprocess.Popen([sys.executable, os.path.join(root_dir, "main.py")])
            sys.exit()

        if self.current_user.get("role", "").lower() != "admin":
            messagebox.showerror("Unauthorized", "You do not have admin permissions.")
            Session.clear()
            self.app.destroy()
            subprocess.Popen([sys.executable, os.path.join(root_dir, "main.py")])
            sys.exit()

    def _load_user_info(self):
        try:
            row = UserRepository().get_by_id(self.current_user["user_id"])
            if row:
                gmail = row.get("gmail", self.current_user.get("gmail", "admin@example.com"))
                first_name = (row.get("first_name") or "").strip()
                middle_name = (row.get("middle_name") or "").strip()
                last_name = (row.get("last_name") or "").strip()
                self.user_info = {
                    "user_id": row["user_id"],
                    "gmail": gmail,
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "last_name": last_name,
                }
                return
        except Exception as e:
            print(f"Error loading user info: {e}")

        gmail = self.current_user.get("gmail", "admin@example.com")
        self.user_info = {
            "user_id": self.current_user.get("user_id", 1),
            "gmail": gmail,
            "first_name": "",
            "middle_name": "",
            "last_name": "",
        }

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background=WHITE,
            foreground="black",
            rowheight=25,
            fieldbackground=WHITE,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=BG_BLUE,
            foreground="black",
            font=("Arial", 10, "bold"),
        )
        style.map("Treeview", background=[("selected", "#dbeafe")])

    def _build_ui(self):
        self.main_bg = ctk.CTkFrame(self.app, fg_color=BG_BLUE, corner_radius=0)
        self.main_bg.pack(fill="both", expand=True)

        self.sidebar = Sidebar(
            self.main_bg,
            user_info=self.user_info,
            on_tab_change=self.show_tab,
            app=self.app,
        )
        self.sidebar.pack(fill="x", side="top")

        self.views = {
            "Analytics": DashboardHomeView(self.main_bg, app=self.app),
            "Inventory": InventoryView(self.main_bg, app=self.app),
            "Requests": RequestsView(self.main_bg, app=self.app),
            "Transactions": TransactionsView(self.main_bg, app=self.app),
            "Accounts": UsersView(self.main_bg, app=self.app),
        }

        for view in self.views.values():
            view.pack_forget()

        self.show_tab("Analytics")

    def show_tab(self, selected_tab):
        if selected_tab not in self.views:
            messagebox.showinfo(
                "Unavailable",
                f"The {selected_tab} section is not available yet.",
            )
            return

        for name, view in self.views.items():
            if name == selected_tab:
                view.pack(fill="both", expand=True, padx=20, pady=20)
            else:
                view.pack_forget()

        self.sidebar.set_active_tab(selected_tab)

    def run(self):
        self.app.mainloop()


def run_app():
    app = AdminDashboardApp()
    app.run()


if __name__ == "__main__":
    run_app()
