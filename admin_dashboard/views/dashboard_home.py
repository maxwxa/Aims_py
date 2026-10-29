import os
from datetime import datetime
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from repositories import AnalyticsRepository
from admin_dashboard.components.report_modal import SummaryReportModal

BG_BLUE = "#eef2ff"
DARK_BLUE = "#1c3b7a"
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"


class DashboardHomeView(ctk.CTkScrollableFrame):
    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color=BG_BLUE, corner_radius=0)
        self.app = app or self.winfo_toplevel()
        self.repository = AnalyticsRepository()
        self.current_logs_data = []

        self._build_view()
        self.refresh()

    def _build_view(self):
        date_header = ctk.CTkFrame(self, fg_color="transparent")
        date_header.pack(fill="x", padx=20, pady=(15, 0))

        ctk.CTkButton(
            date_header,
            text="Summary Reports & Export",
            height=26,
            fg_color="#10b981",
            hover_color="#059669",
            text_color=WHITE,
            font=("Arial", 11, "bold"),
            command=lambda: SummaryReportModal(self.app),
        ).pack(side="right")

        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", padx=20, pady=(15, 10))
        for column in range(4):
            cards.grid_columnconfigure(column, weight=1)

        self.card_values = {}
        card_configs = (
            ("total_stock", "Total Items"),
            ("pending_requests", "Pending Requests"),
            ("active_users", "Active Users"),
            ("active_requests", "Active Requests"),
            ("out_of_stock_count", "Out of Stock Count"),
            ("expired_count", "Expired Items"),
            ("due_for_return_count", "Due for Return Count"),
            ("total_transactions", "Total Transactions"),
        )

        for index, (key, title) in enumerate(card_configs):
            row = index // 4
            column = index % 4
            card = ctk.CTkFrame(
                cards,
                fg_color=WHITE,
                corner_radius=8,
                border_width=1,
                border_color="#d1d5db",
            )
            card.grid(row=row, column=column, sticky="ew", padx=5, pady=(0 if row == 0 else 10))
            ctk.CTkLabel(
                card,
                text=title,
                text_color=TEXT_BLUE,
                font=("Arial", 12, "bold"),
            ).pack(anchor="w", padx=15, pady=(12, 2))
            value = ctk.CTkLabel(
                card,
                text="0",
                text_color=TEXT_BLUE,
                font=("Arial", 26, "bold"),
            )
            value.pack(anchor="w", padx=15, pady=(0, 12))
            self.card_values[key] = value

        charts = ctk.CTkFrame(self, fg_color="transparent")
        charts.pack(fill="x", padx=20, pady=10)
        charts.grid_columnconfigure((0, 1), weight=1)

        self.left_chart = ctk.CTkFrame(
            charts,
            fg_color=WHITE,
            corner_radius=8,
            border_width=1,
            border_color="#d1d5db",
            height=250,
        )
        self.right_chart = ctk.CTkFrame(
            charts,
            fg_color=WHITE,
            corner_radius=8,
            border_width=1,
            border_color="#d1d5db",
            height=250,
        )
        self.left_chart.pack_propagate(False)
        self.right_chart.pack_propagate(False)
        self.left_chart.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.right_chart.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        alerts = ctk.CTkFrame(self, fg_color="transparent")
        alerts.pack(fill="x", padx=20, pady=(0, 10))
        alerts.grid_columnconfigure((0, 1), weight=1)

        oos_frame = ctk.CTkFrame(
            alerts, fg_color=WHITE, corner_radius=8, border_width=1, border_color="#f87171"
        )
        oos_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        ctk.CTkLabel(
            oos_frame, text="Alerts", text_color="#dc2626", font=("Arial", 14, "bold")
        ).pack(pady=(10, 5))
        self.oos_list = ctk.CTkScrollableFrame(oos_frame, fg_color="transparent", height=140)
        self.oos_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        due_frame = ctk.CTkFrame(
            alerts, fg_color=WHITE, corner_radius=8, border_width=1, border_color="#fbbf24"
        )
        due_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        ctk.CTkLabel(
            due_frame, text="Items Due for Return", text_color="#d97706", font=("Arial", 14, "bold")
        ).pack(pady=(10, 5))
        self.due_list = ctk.CTkScrollableFrame(due_frame, fg_color="transparent", height=140)
        self.due_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        log_header = ctk.CTkFrame(self, height=38, fg_color="#1c3b7a", corner_radius=8)
        log_header.pack(fill="x", padx=20, pady=(10, 0))
        log_header.pack_propagate(False)

        ctk.CTkLabel(
            log_header, text="System Logs", text_color=WHITE, font=("Arial", 14, "bold")
        ).pack(side="left", padx=15)

        ctk.CTkButton(
            log_header,
            text="Refresh",
            width=80,
            height=26,
            fg_color=WHITE,
            text_color="#1c3b7a",
            command=self.refresh,
        ).pack(side="right", padx=(5, 10), pady=6)

        self.action_var = ctk.StringVar(value="All Actions")
        action_dropdown = ctk.CTkOptionMenu(
            log_header,
            variable=self.action_var,
            width=120,
            height=26,
            values=["All Actions", "INSERT", "UPDATE", "DELETE"],
            fg_color=WHITE,
            text_color="black",
            button_color="#d1d5db",
            command=lambda e: self.filter_logs(),
        )
        action_dropdown.pack(side="right", padx=5, pady=6)

        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            log_header,
            placeholder_text="Search logs...",
            textvariable=self.search_var,
            width=150,
            height=26,
            fg_color=WHITE,
            text_color="black",
        )
        search_entry.pack(side="right", padx=5, pady=6)
        search_entry.bind("<KeyRelease>", lambda e: self.filter_logs())

        self.logs = ctk.CTkScrollableFrame(self, fg_color=WHITE, corner_radius=8, height=250)
        self.logs.pack(fill="x", padx=20, pady=20)

    def filter_logs(self):
        for widget in self.logs.winfo_children():
            widget.destroy()

        headers = ("Log ID", "User", "Action", "Table", "ID", "Date/Time")
        for column, title in enumerate(headers):
            ctk.CTkLabel(
                self.logs, text=title, fg_color="#dbeafe", text_color=TEXT_BLUE, anchor="w"
            ).grid(row=0, column=column, sticky="ew", padx=1, pady=1)
            self.logs.grid_columnconfigure(column, weight=1, minsize=90)

        search_term = self.search_var.get().lower()
        active_action = self.action_var.get()

        row_index = 1
        for row in self.current_logs_data:
            log_id = str(row.get("log_id") or "")
            user = str(row.get("user") or row.get("user_id") or "")
            action = str(row.get("action") or "").upper()
            table = str(row.get("table_affected") or "")
            timestamp = str(row.get("timestamp") or "")

            target_id = str(row.get("item_id") or row.get("id") or "")
            target_name = str(row.get("item_name") or row.get("name") or "")
            desc = f"{target_id}" if target_id or target_name else str(row.get("description") or "")

            if active_action != "All Actions" and active_action != action:
                continue
            if search_term and search_term not in f"{log_id} {user} {action} {table} {desc} {timestamp}".lower():
                continue

            values = (log_id, user, action, table, desc, timestamp)
            for column, value in enumerate(values):
                ctk.CTkLabel(
                    self.logs, text=value, fg_color=WHITE, text_color="black", anchor="w"
                ).grid(row=row_index, column=column, sticky="ew", padx=1, pady=1)
            row_index += 1

    def refresh(self):
        try:
            stats = self.repository.get_summary_stats()
            for key, label in self.card_values.items():
                label.configure(text=str(stats.get(key, "0")))
            for widget in self.oos_list.winfo_children():
                widget.destroy()
            for widget in self.due_list.winfo_children():
                widget.destroy()

            oos_items = self.repository.get_out_of_stock_and_expired_items()
            due_items = self.repository.get_due_items()
            if not oos_items:
                ctk.CTkLabel(
                    self.oos_list, text="No items out of stock or expired.", text_color="gray"
                ).pack(pady=10)
            else:
                for item in oos_items:
                    card = ctk.CTkFrame(self.oos_list, fg_color="#f3f4f6", corner_radius=6)
                    card.pack(fill="x", pady=2, padx=2)

                    img_path = item.get("image_path")
                    ctk_img = None
                    if img_path and os.path.exists(img_path):
                        try:
                            ctk_img = ctk.CTkImage(
                                light_image=Image.open(img_path),
                                dark_image=Image.open(img_path),
                                size=(40, 40),
                            )
                        except Exception:
                            pass

                    img_label = ctk.CTkLabel(
                        card,
                        text="No Img" if not ctk_img else "",
                        image=ctk_img,
                        width=40,
                        height=40,
                        fg_color="#e5e7eb",
                        corner_radius=4,
                    )
                    img_label.pack(side="left", padx=5, pady=5)

                    details = ctk.CTkFrame(card, fg_color="transparent")
                    details.pack(side="left", fill="x", expand=True, padx=(5, 5))
                    ctk.CTkLabel(
                        details,
                        text=item.get("item_name", "Unknown"),
                        font=("Arial", 12, "bold"),
                        text_color="black",
                        anchor="w",
                    ).pack(fill="x")

                    status_reason = item.get("status_reason", "Out of Stock")
                    exp_date = item.get("expiration_date")
                    exp_str = f" | Exp: {str(exp_date)[:10]}" if exp_date else ""
                    ctk.CTkLabel(
                        details,
                        text=f"ID: {item.get('item_id', 'N/A')} | Stock: {item.get('stock', 0)}{exp_str}",
                        font=("Arial", 10),
                        text_color="gray",
                        anchor="w",
                    ).pack(fill="x")

                    tag_color = "#dc2626" if "Expired" in status_reason else "#b91c1c"
                    ctk.CTkLabel(
                        card,
                        text=status_reason,
                        font=("Arial", 10, "bold"),
                        text_color=tag_color,
                    ).pack(side="right", padx=10)

            if not due_items:
                ctk.CTkLabel(self.due_list, text="No items currently due.", text_color="gray").pack(
                    pady=10
                )
            else:
                for item in due_items:
                    card = ctk.CTkFrame(self.due_list, fg_color="#f3f4f6", corner_radius=6)
                    card.pack(fill="x", pady=2, padx=2)

                    img_path = item.get("image_path")
                    ctk_img = None
                    if img_path and os.path.exists(img_path):
                        try:
                            ctk_img = ctk.CTkImage(
                                light_image=Image.open(img_path),
                                dark_image=Image.open(img_path),
                                size=(40, 40),
                            )
                        except Exception:
                            pass

                    img_label = ctk.CTkLabel(
                        card,
                        text="No Img" if not ctk_img else "",
                        image=ctk_img,
                        width=40,
                        height=40,
                        fg_color="#e5e7eb",
                        corner_radius=4,
                    )
                    img_label.pack(side="left", padx=5, pady=5)

                    details = ctk.CTkFrame(card, fg_color="transparent")
                    details.pack(side="left", fill="x", expand=True, padx=(5, 5))
                    ctk.CTkLabel(
                        details,
                        text=item.get("item_name", "Unknown"),
                        font=("Arial", 12, "bold"),
                        text_color="black",
                        anchor="w",
                    ).pack(fill="x")
                    ctk.CTkLabel(
                        details,
                        text=f"Req ID: {item.get('request_id', 'N/A')} | Due: {item.get('due_date', 'Unknown')}",
                        font=("Arial", 10),
                        text_color="#d97706",
                        anchor="w",
                    ).pack(fill="x")

            top_items = self.repository.get_top_requested_items()
            category_data = self.repository.get_category_request_distribution()

            for widget in self.left_chart.winfo_children() + self.right_chart.winfo_children():
                widget.destroy()

            item_names = [row["item_name"] for row in top_items]
            item_counts = [row["request_count"] for row in top_items]
            figure1 = Figure(figsize=(4, 2.2), dpi=90)
            figure1.patch.set_alpha(0)
            axis1 = figure1.add_subplot(111)
            axis1.bar(item_names, item_counts, color="#1c3b7a")
            axis1.set_title("Top 5 Requested Items")
            axis1.tick_params(axis="x", rotation=25, labelsize=8)
            figure1.tight_layout()
            canvas1 = FigureCanvasTkAgg(figure1, master=self.left_chart)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

            labels = [row["category_name"] for row in category_data]
            counts = [row["request_count"] for row in category_data]
            figure2 = Figure(figsize=(4, 2.2), dpi=90)
            figure2.patch.set_alpha(0)
            axis2 = figure2.add_subplot(111)
            if counts:
                axis2.pie(counts, labels=labels, autopct="%1.1f%%")
            axis2.set_title("Most Requested Categories")
            figure2.tight_layout()
            canvas2 = FigureCanvasTkAgg(figure2, master=self.right_chart)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

            self.current_logs_data = self.repository.get_recent_logs()
            self.filter_logs()

        except Exception as error:
            messagebox.showerror("Analytics Unavailable", str(error))


def create_analytics_tab(parent_frame, app=None):
    return DashboardHomeView(parent_frame, app=app)
