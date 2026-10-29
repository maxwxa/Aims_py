import os
from datetime import datetime
import customtkinter as ctk
from PIL import Image
from user_dashboard.components.logout_modal import LogoutConfirmationModal

DARK_BLUE = "#1c3b7a"
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"
RED = "#ef4444"


class Sidebar(ctk.CTkFrame):
    """Header and Navigation bar component for User Dashboard."""

    def __init__(self, parent, user_info, on_tab_change, app=None):
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.app = app or self.winfo_toplevel()
        self.user_info = user_info or {}
        self.on_tab_change = on_tab_change
        self.tabs = ["Home", "Items", "History", "Profile"]
        self.nav_buttons = {}

        self._build_header()
        self._build_navigation()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, height=80, fg_color=DARK_BLUE, corner_radius=0)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        root_dir = os.path.dirname(os.path.dirname(__file__))
        logo_path = os.path.join(root_dir, "assets", "Aims_plain_white.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(root_dir, "Assets", "Aims_plain_white.png")
        try:
            if os.path.exists(logo_path):
                img = Image.open(logo_path)
                self.logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(50, 50))
                ctk.CTkLabel(header_frame, image=self.logo_img, text="").place(x=20, y=15)
        except Exception:
            ctk.CTkLabel(
                header_frame, text="[LOGO]", text_color=WHITE, font=("Arial", 16, "bold")
            ).place(x=20, y=25)

        name_parts = [
            self.user_info.get("last_name", "").strip(),
            self.user_info.get("first_name", "").strip(),
            self.user_info.get("middle_name", "").strip(),
        ]
        display_name = "Hello, " + ", ".join([part for part in name_parts if part])
        if not display_name:
            display_name = "User"

        ctk.CTkLabel(
            header_frame, text=display_name, font=("Arial", 28, "bold"), text_color=WHITE
        ).place(x=90, y=20)

        logout_btn = ctk.CTkButton(
            header_frame,
            text="Log out",
            width=100,
            height=35,
            fg_color=RED,
            hover_color="#dc2626",
            corner_radius=8,
            font=("Arial", 14, "bold"),
            command=self._logout,
        )
        logout_btn.pack(side="right", padx=20, pady=22)

        current_date_str = datetime.now().strftime("%A, %B %d, %Y")
        date_label = ctk.CTkLabel(
            header_frame, text=current_date_str, font=("Arial", 14, "bold"), text_color=WHITE
        )
        date_label.pack(side="right", padx=(0, 15), pady=22)

    def _build_navigation(self):
        nav_frame = ctk.CTkFrame(
            self,
            height=60,
            fg_color=WHITE,
            corner_radius=20,
            border_width=1,
            border_color="#d1d5db",
        )
        nav_frame.pack(fill="x", padx=20, pady=15)
        nav_frame.pack_propagate(False)

        nav_frame.grid_columnconfigure(0, weight=1)
        nav_frame.grid_columnconfigure(5, weight=1)
        buttons_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
        buttons_frame.grid(row=0, column=1, sticky="ew", pady=12)
        buttons_frame.grid_columnconfigure(tuple(range(len(self.tabs))), weight=1)

        for i, tab in enumerate(self.tabs):
            bg_color = DARK_BLUE if tab == "Home" else TEXT_BLUE
            btn = ctk.CTkButton(
                buttons_frame,
                text=tab,
                width=200,
                height=50,
                fg_color=bg_color,
                corner_radius=6,
                font=("Arial", 18, "bold"),
                command=lambda selected_tab=tab: self.on_tab_change(selected_tab),
            )
            btn.grid(row=0, column=i, padx=4, sticky="ew")
            self.nav_buttons[tab] = btn

    def set_active_tab(self, selected_tab):
        for tab, button in self.nav_buttons.items():
            button.configure(fg_color=DARK_BLUE if tab == selected_tab else TEXT_BLUE)

    def _logout(self):
        LogoutConfirmationModal(self.app)
