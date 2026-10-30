from tkinter import messagebox
import customtkinter as ctk
from repositories import UserRepository
from admin_dashboard.components.user_modals import AccountEditor, AdminPasswordModal

BG_BLUE = "#eef2ff"
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"
GREEN = "#84cc16"
PURPLE = "#9333ea"
RED = "#ef4444"


class UsersView(ctk.CTkFrame):
    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color=BG_BLUE, corner_radius=0)
        self.app = app or self.winfo_toplevel()
        self.repository = UserRepository()
        self.state = {"mode": "current", "selected": None, "widgets": []}
        self.current_page = 1
        self.items_per_page = 50
        self._build_view()
        self.update_actions()
        self.load_rows()

    def _build_view(self):
        header = ctk.CTkFrame(self, height=45, fg_color="#1c3b7a", corner_radius=8)
        header.pack(fill="x", padx=20, pady=(20, 0))
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="Accounts", text_color=WHITE, font=("Arial", 16, "bold")).pack(
            side="left", padx=15
        )

        self.toggle = ctk.CTkButton(
            header,
            text="ARCHIVE",
            width=90,
            height=30,
            fg_color="#779adf",
            corner_radius=6,
            command=self.switch,
        )
        self.toggle.pack(side="left", padx=10)

        toolbar = ctk.CTkFrame(header, fg_color="transparent")
        toolbar.pack(side="right", padx=20)
        self.search = ctk.CTkEntry(
            toolbar,
            width=160,
            height=30,
            fg_color=WHITE,
            text_color="black",
            corner_radius=6,
            placeholder_text="Search",
        )
        self.search.pack(side="left", padx=5)
        self.search.bind("<KeyRelease>", lambda _event=None: self.load_rows())

        refresh_button = ctk.CTkButton(
            toolbar,
            text="Refresh",
            width=80,
            height=30,
            fg_color=WHITE,
            text_color="#1c3b7a",
            hover_color="#e5e7eb",
            corner_radius=6,
            command=self.refresh,
        )
        refresh_button.pack(side="left", padx=5)

        self.header_frame = ctk.CTkFrame(self, fg_color="#dbeafe", corner_radius=8)
        self.header_frame.pack(fill="x", padx=20, pady=(20, 0))

        self.table = ctk.CTkScrollableFrame(self, fg_color=WHITE, corner_radius=8)
        self.table.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.actions = ctk.CTkFrame(self, fg_color="transparent")
        self.actions.pack(fill="x", padx=20, pady=(0, 20))

        self.current_buttons = [
            ctk.CTkButton(
                self.actions,
                text="CREATE",
                fg_color=GREEN,
                text_color="black",
                corner_radius=6,
                command=lambda: AccountEditor(self.app, self.repository, on_changed=self.refresh),
            ),
            ctk.CTkButton(
                self.actions,
                text="UPDATE",
                fg_color="#f59e0b",
                text_color="black",
                corner_radius=6,
                command=self.edit,
            ),
            ctk.CTkButton(
                self.actions,
                text="CHANGE PASSWORD",
                fg_color=PURPLE,
                corner_radius=6,
                command=self.reset,
            ),
            ctk.CTkButton(
                self.actions,
                text="ARCHIVE",
                fg_color=RED,
                corner_radius=6,
                command=self.archive,
            ),
        ]
        self.restore_button = ctk.CTkButton(
            self.actions,
            text="RESTORE",
            fg_color=GREEN,
            text_color="black",
            corner_radius=6,
            command=lambda: self.move(self.repository.restore_user),
        )
        self.delete_button = ctk.CTkButton(
            self.actions,
            text="DELETE",
            fg_color=RED,
            corner_radius=6,
            command=lambda: self.move(self.repository.delete_archived),
        )
        
        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pagination_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.btn_prev = ctk.CTkButton(self.pagination_frame, text="<< Previous", width=100, fg_color="#1d4ed8", command=self.prev_page)
        self.btn_prev.pack(side="left")
        
        self.lbl_page = ctk.CTkLabel(self.pagination_frame, text="Page 1 of 1", font=("Arial", 14, "bold"), text_color="#1e3a8a")
        self.lbl_page.pack(side="left", expand=True)
        
        self.btn_next = ctk.CTkButton(self.pagination_frame, text="Next >>", width=100, fg_color="#1d4ed8", command=self.next_page)
        self.btn_next.pack(side="right")

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_rows()

    def next_page(self):
        self.current_page += 1
        self.load_rows()

    @staticmethod
    def configure_columns(container, count):
        for column in range(count):
            container.grid_columnconfigure(column, weight=1, uniform="col", minsize=0)

    def select(self, row, widgets):
        for widget in self.state["widgets"]:
            widget.configure(fg_color=WHITE)
        self.state["selected"], self.state["widgets"] = row, widgets
        for widget in widgets:
            widget.configure(fg_color="#bfdbfe")

    def load_rows(self):
        for widget in self.table.winfo_children():
            widget.destroy()
        self.state["selected"], self.state["widgets"] = None, []
        archived = self.state["mode"] == "archived"
        headers = (
            [
                "Acc_Archive No.",
                "Account No.",
                "Student ID",
                "Email",
                "Status",
                "Role",
                "Date/Time",
            ]
            if archived
            else ["Account No.", "Student ID", "Email", "Status", "Role", "Date/Time"]
        )
        for widget in self.header_frame.winfo_children():
            widget.destroy()
        self.configure_columns(self.header_frame, len(headers))
        for column, title in enumerate(headers):
            ctk.CTkLabel(
                self.header_frame,
                text=title,
                fg_color="#dbeafe",
                text_color=TEXT_BLUE,
                font=("Arial", 11, "bold"),
                anchor="w",
            ).grid(row=0, column=column, sticky="nsew", padx=1, pady=6)
        self.configure_columns(self.table, len(headers))
        try:
            rows = self.repository.get_all_accounts(self.state["mode"])
        except (ValueError, Exception) as error:
            messagebox.showerror("Accounts Unavailable", str(error), parent=self.app)
            return

        term = self.search.get().strip().lower()
        
        filtered_rows = []
        for row in rows:
            values = (
                [
                    row.get("account_archive_id"),
                    row.get("account_id"),
                    row.get("student_id"),
                    row.get("gmail"),
                    row.get("account_status"),
                    row.get("role"),
                    row.get("creationdate"),
                ]
                if archived
                else [
                    row.get("account_id"),
                    row.get("student_id"),
                    row.get("gmail"),
                    row.get("account_status"),
                    row.get("role"),
                    row.get("creationdate"),
                ]
            )
            if term and term not in " ".join(str(value or "") for value in values).lower():
                continue
            filtered_rows.append((row, values))

        total_items = len(filtered_rows)
        total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > total_pages:
            self.current_page = 1
            
        self.lbl_page.configure(text=f"Page {self.current_page} of {total_pages} (Total: {total_items})")
        self.btn_prev.configure(state="normal" if self.current_page > 1 else "disabled")
        self.btn_next.configure(state="normal" if self.current_page < total_pages else "disabled")

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        display_items = filtered_rows[start_idx:end_idx]

        for row_index, (row, values) in enumerate(display_items, 1):
            widgets = []
            for column, value in enumerate(values):
                label = ctk.CTkLabel(
                    self.table, text=str(value or ""), fg_color=WHITE, text_color="black", anchor="w"
                )
                label.grid(row=row_index, column=column, sticky="ew", padx=1, pady=1)
                label.bind(
                    "<Button-1>",
                    lambda _event=None, item=row, cells=widgets: self.select(item, cells),
                )
                widgets.append(label)

    def selected(self):
        if self.state["selected"] is None:
            messagebox.showwarning("Select Account", "Select an account first.", parent=self.app)
        return self.state["selected"]

    def refresh(self):
        self.load_rows()

    def switch(self):
        self.state["mode"] = "archived" if self.state["mode"] == "current" else "current"
        self.toggle.configure(text="CURRENT" if self.state["mode"] == "archived" else "ARCHIVE")
        self.update_actions()
        self.load_rows()

    def edit(self):
        account = self.selected()
        if account:
            AccountEditor(self.app, self.repository, account, self.refresh)

    def reset(self):
        account = self.selected()
        if account:
            AdminPasswordModal(self.app, self.repository, account, self.refresh)

    def archive(self):
        account = self.selected()
        if account and messagebox.askyesno(
            "Archive Account", "Archive this account?", parent=self.app
        ):
            try:
                self.repository.archive_user(account["account_id"])
                self.refresh()
            except (ValueError, Exception) as error:
                messagebox.showerror("Archive Account", str(error), parent=self.app)

    def move(self, action):
        account = self.selected()
        if account and messagebox.askyesno(
            "Confirm Action ", "Are you sure you want to perform this action?", parent=self.app
        ):
            try:
                if not action(account.get("account_archive_id")):
                    raise ValueError("The archived account could not be found.")
                self.refresh()
            except (ValueError, Exception) as error:
                messagebox.showerror("Delete Account", str(error), parent=self.app)

    def update_actions(self):
        for button in self.current_buttons + [self.restore_button, self.delete_button]:
            button.pack_forget()
        if self.state["mode"] == "current":
            for button in self.current_buttons:
                button.pack(side="left", padx=4)
        else:
            self.restore_button.pack(side="right")
            self.delete_button.pack(side="right", padx=(0, 8))


def create_accounts_tab(parent_frame, app=None):
    return UsersView(parent_frame, app=app)