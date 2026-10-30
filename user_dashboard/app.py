import os
import subprocess
import sys
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
from models.users import Session
from repositories import RequestRepository, UserRepository
from user_dashboard.sidebar import Sidebar
from user_dashboard.views.dashboard_home import DashboardHomeView
from user_dashboard.views.inventory_view import InventoryView
from user_dashboard.views.history_view import HistoryView
from user_dashboard.views.profile_view import ProfileView

DARK_BLUE = "#1c3b7a"
BG_BLUE = "#eef2ff"
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"


class UserDashboardApp:
    def __init__(self):
        ctk.set_appearance_mode("light")
        self.app = ctk.CTk()
        self.app.geometry("1000x650")
        self.app.title("Academic Inventory Management System - User Dashboard")

        self._set_icon()
        self._set_window_state()
        self._check_session()
        self._load_user_info()
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

        user_role = self.current_user.get("role", "").strip().lower()
        if user_role not in {"user", "student"}:
            messagebox.showerror("Unauthorized", "You do not have user permissions.")
            Session.clear()
            self.app.destroy()
            subprocess.Popen([sys.executable, os.path.join(root_dir, "main.py")])
            sys.exit()

        try:
            RequestRepository().process_overdue_returns()
        except Exception:
            pass

    def _load_user_info(self):
        try:
            row = UserRepository().get_by_id(self.current_user["user_id"])
            if row:
                gmail = row.get("gmail", self.current_user.get("gmail", "user@example.com"))
                first_name = (row.get("first_name") or "").strip()
                middle_name = (row.get("middle_name") or "").strip()
                last_name = (row.get("last_name") or "").strip()
                if not last_name and not first_name:
                    username = gmail.split("@")[0]
                    last_name = username.split(".")[-1].title() if "." in username else username.title()

                self.user_info = {
                    "user_id": row["user_id"],
                    "gmail": gmail,
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "last_name": last_name,
                    "department": row.get("department", ""),
                    "course": row.get("course", ""),
                }
                return
        except Exception as e:
            print(f"Error loading user info: {e}")

        gmail = self.current_user.get("gmail", "user@example.com")
        username = gmail.split("@")[0]
        last_name = username.split(".")[-1].title() if "." in username else username.title()
        self.user_info = {
            "user_id": self.current_user.get("user_id", 1),
            "gmail": gmail,
            "first_name": "",
            "middle_name": "",
            "last_name": last_name,
            "department": "",
            "course": "",
        }

    def _build_ui(self):
        self.main_bg = ctk.CTkFrame(self.app, fg_color=BG_BLUE, corner_radius=8)
        self.main_bg.pack(fill="both", expand=True)

        self.sidebar = Sidebar(
            self.main_bg,
            user_info=self.user_info,
            on_tab_change=self.show_tab,
            app=self.app,
        )
        self.sidebar.pack(fill="x", side="top")

        self.home_view = DashboardHomeView(
            self.main_bg, app=self.app, on_data_changed=self._on_home_data_changed
        )
        self.inventory_view = InventoryView(
            self.main_bg, app=self.app, on_data_changed=self._on_inventory_data_changed
        )
        self.history_view = HistoryView(self.main_bg, app=self.app)
        self.profile_view = ProfileView(self.main_bg, app=self.app)

        self.views = {
            "Home": self.home_view,
            "Items": self.inventory_view,
            "History": self.history_view,
            "Profile": self.profile_view,
        }

        for view in self.views.values():
            view.pack_forget()

        self.show_tab("Home")

    def _on_home_data_changed(self):
        if hasattr(self, "inventory_view"):
            self.inventory_view.refresh_inventory()

    def _on_inventory_data_changed(self):
        if hasattr(self, "home_view"):
            self.home_view.refresh()
        if hasattr(self, "history_view"):
            self.history_view.fetch_and_render_rows()

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
    app = UserDashboardApp()
    app.run()


if __name__ == "__main__":
    run_app()
