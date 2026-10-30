import os
from datetime import date, datetime
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image
from models.users import Session
from repositories import RequestRepository
from user_dashboard.components.cancel_modal import CancelConfirmationModal
from user_dashboard.components.return_modal import ItemReturnModal

DARK_BLUE = "#1c3b7a"
BG_BLUE = "#eef2ff"
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"
RED = "#ef4444"
BLUE = "#1d4ed8"
GREEN = "#84cc16"


class DashboardHomeView(ctk.CTkFrame):
    def __init__(self, parent, app=None, on_data_changed=None):
        super().__init__(parent, fg_color=DARK_BLUE, corner_radius=8, border_width=1, border_color="#d1d5db")
        self.app = app or self.winfo_toplevel()
        self.on_data_changed = on_data_changed
        self.requests = []
        self.notifications = []

        self._build_view()
        self.refresh()

    def _build_view(self):
        inner_frame = ctk.CTkFrame(self, fg_color=BG_BLUE, corner_radius=8)
        inner_frame.pack(fill="both", expand=True, padx=2, pady=2)
        inner_frame.grid_columnconfigure(0, weight=5)
        inner_frame.grid_columnconfigure(1, weight=4)
        inner_frame.grid_rowconfigure(0, weight=1)

        # Track Items Panel
        items_panel = ctk.CTkFrame(
            inner_frame, fg_color=WHITE, corner_radius=8, border_width=1, border_color="#d1d5db"
        )
        items_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        items_header = ctk.CTkFrame(items_panel, height=45, fg_color=DARK_BLUE, corner_radius=0)
        items_header.pack(fill="x", padx=0, pady=(0, 0))
        items_header.pack_propagate(False)

        ctk.CTkLabel(
            items_header, text="Track Items", font=("Arial", 16, "bold"), text_color=WHITE
        ).pack(side="left", padx=15, pady=10)

        items_toolbar = ctk.CTkFrame(items_header, fg_color="transparent")
        items_toolbar.pack(side="right", padx=15)

        self.items_refresh = ctk.CTkButton(
            items_toolbar,
            text="Refresh",
            width=70,
            height=30,
            corner_radius=6,
            fg_color=WHITE,
            text_color="black",
            command=self.load_items_cards,
        )
        self.items_refresh.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            items_toolbar, text="Search:", font=("Arial", 12, "bold"), text_color=WHITE
        ).pack(side="left", padx=(0, 4))
        self.items_search = ctk.CTkEntry(
            items_toolbar, width=130, height=30, corner_radius=6, fg_color=WHITE, text_color="black"
        )
        self.items_search.pack(side="left", padx=(0, 0))
        self.items_search.bind("<KeyRelease>", lambda e: self.filter_items())

        self.items_scroll = ctk.CTkScrollableFrame(items_panel, fg_color=WHITE, corner_radius=0)
        self.items_scroll.pack(fill="both", expand=True, padx=15, pady=15)
        self.items_scroll.grid_columnconfigure((0, 1), weight=1)

        # Notifications Panel
        notif_panel = ctk.CTkFrame(
            inner_frame, fg_color=WHITE, corner_radius=8, border_width=1, border_color="#d1d5db"
        )
        notif_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

        notif_header = ctk.CTkFrame(notif_panel, height=45, fg_color=DARK_BLUE, corner_radius=0)
        notif_header.pack(fill="x", padx=0, pady=(0, 0))
        notif_header.pack_propagate(False)

        ctk.CTkLabel(
            notif_header, text="Notifications", font=("Arial", 16, "bold"), text_color=WHITE
        ).pack(side="left", padx=15, pady=10)

        notif_toolbar = ctk.CTkFrame(notif_header, fg_color="transparent")
        notif_toolbar.pack(side="right", padx=15)

        self.notif_refresh = ctk.CTkButton(
            notif_toolbar,
            text="Refresh",
            width=70,
            height=30,
            corner_radius=6,
            fg_color=WHITE,
            text_color="black",
            command=self.load_notifications_list,
        )
        self.notif_refresh.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            notif_toolbar, text="Search:", font=("Arial", 12, "bold"), text_color=WHITE
        ).pack(side="left", padx=(0, 4))
        self.notif_search = ctk.CTkEntry(
            notif_toolbar, width=130, height=30, corner_radius=6, fg_color=WHITE, text_color="black"
        )
        self.notif_search.pack(side="left", padx=(0, 0))
        self.notif_search.bind("<KeyRelease>", lambda e: self.filter_notifications())

        self.notif_scroll = ctk.CTkScrollableFrame(notif_panel, fg_color=WHITE, corner_radius=0)
        self.notif_scroll.pack(fill="both", expand=True, padx=15, pady=15)

    def refresh(self):
        current_user = Session.load() or {}
        user_id = current_user.get("user_id", 1)
        try:
            self.requests = RequestRepository().get_for_user(user_id)
        except Exception as e:
            print(f"Error loading requests: {e}")
            self.requests = []

        try:
            self.notifications = RequestRepository().get_notifications(user_id)
        except Exception as e:
            print(f"Error loading notifications: {e}")
            self.notifications = []

        self.load_items_cards()
        self.load_notifications_list()
        if self.on_data_changed:
            self.on_data_changed()

    def load_items_cards(self):
        for widget in self.items_scroll.winfo_children():
            widget.destroy()
        visible_requests = [
            req for req in self.requests
            if req.get("request_status") not in {"Returned", "Cancelled"}
        ]
        for i, req in enumerate(visible_requests):
            row = i // 2
            col = i % 2
            card = self.create_request_card(self.items_scroll, req)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

    def create_request_card(self, parent, request):
        card = ctk.CTkFrame(
            parent, height=280, fg_color=WHITE, corner_radius=8, border_width=1, border_color="#d1d5db"
        )
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)
        name_frame = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0)
        name_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        ctk.CTkLabel(
            name_frame,
            text=request["item_name"],
            font=("Arial", 12, "bold"),
            text_color=TEXT_BLUE,
            anchor="center",
        ).pack(fill="x", padx=10, pady=(8, 8))
        ctk.CTkFrame(name_frame, height=1, fg_color="#d1d5db").pack(fill="x", padx=10)

        image_frame = ctk.CTkFrame(card, fg_color="#e5e7eb", corner_radius=6)
        image_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        image_label = ctk.CTkLabel(
            image_frame, text="No image available", text_color="#6b7280", font=("Arial", 10)
        )
        image_label.place(relx=0.5, rely=0.5, anchor="center")

        image_path = request.get("image_path")
        if image_path and os.path.isfile(image_path):
            try:
                source = Image.open(image_path)
                img_w, img_h = source.size
                init_ratio = min(150 / max(1, img_w), 120 / max(1, img_h))
                init_w = max(1, int(img_w * init_ratio))
                init_h = max(1, int(img_h * init_ratio))
                card_image = ctk.CTkImage(light_image=source, dark_image=source, size=(init_w, init_h))
                image_label.configure(image=card_image, text="")
                image_label.image = card_image

                def on_req_resize(event, src=source, lbl=image_label):
                    w = event.width
                    h = event.height
                    if w > 10 and h > 10:
                        sw, sh = src.size
                        ratio = min(w / sw, h / sh)
                        new_w = max(1, int(sw * ratio))
                        new_h = max(1, int(sh * ratio))
                        resized_img = ctk.CTkImage(light_image=src, dark_image=src, size=(new_w, new_h))
                        lbl.configure(image=resized_img, text="")
                        lbl.image = resized_img

                image_frame.bind("<Configure>", on_req_resize)
            except (OSError, ValueError):
                pass

        status = request["request_status"]

        if status == "Pending":
            btn_frame = ctk.CTkFrame(
                card, fg_color=WHITE, corner_radius=0, border_width=1, border_color="#d1d5db"
            )
            btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
            ctk.CTkButton(
                btn_frame,
                text="Cancel Request",
                height=35,
                fg_color=RED,
                hover_color="#dc2626",
                corner_radius=6,
                font=("Arial", 11, "bold"),
                command=lambda rid=request["request_id"]: self.show_cancel_modal(
                    rid, request["item_name"], status
                ),
            ).pack(fill="x", padx=8, pady=8)

        elif status == "Approved":
            status_frame = ctk.CTkFrame(
                card, fg_color=WHITE, corner_radius=0, border_width=1, border_color="#d1d5db"
            )
            status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
            ctk.CTkLabel(
                status_frame,
                text="Waiting for admin to confirm receipt",
                font=("Arial", 10, "bold"),
                text_color=TEXT_BLUE,
                anchor="center",
            ).pack(fill="x", padx=8, pady=(6, 2))
            ctk.CTkButton(
                status_frame,
                text="Cancel Accepted Request",
                height=26,
                fg_color=RED,
                hover_color="#dc2626",
                corner_radius=6,
                font=("Arial", 10, "bold"),
                command=lambda rid=request["request_id"]: self.show_cancel_modal(
                    rid, request["item_name"], status
                ),
            ).pack(fill="x", padx=8, pady=(0, 6))

        elif status == "Active":
            btn_frame = ctk.CTkFrame(
                card, fg_color=WHITE, corner_radius=0, border_width=1, border_color="#d1d5db"
            )
            btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
            ctk.CTkButton(
                btn_frame,
                text="Return",
                height=35,
                fg_color=GREEN,
                hover_color="#65a30d",
                corner_radius=6,
                font=("Arial", 11, "bold"),
                command=lambda: self.show_return_modal(request),
            ).pack(fill="x", padx=8, pady=8)

        elif status == "Return Requested":
            status_frame = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0)
            status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
            ctk.CTkLabel(
                status_frame,
                text="Return pending confirmation",
                font=("Arial", 10, "bold"),
                text_color=TEXT_BLUE,
                anchor="center",
            ).pack(fill="both", padx=8, pady=8)

        elif status == "Cancelled":
            status_frame = ctk.CTkFrame(
                card, fg_color=WHITE, corner_radius=0, border_width=1, border_color="#d1d5db"
            )
            status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
            ctk.CTkLabel(
                status_frame,
                text="Request cancelled",
                font=("Arial", 10),
                text_color=RED,
                anchor="center",
            ).pack(fill="both", expand=True, padx=8, pady=8)

        elif status == "Returned":
            status_frame = ctk.CTkFrame(
                card, fg_color=WHITE, corner_radius=0, border_width=1, border_color="#d1d5db"
            )
            status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
            ctk.CTkLabel(
                status_frame,
                text="Already returned",
                font=("Arial", 10),
                text_color="#6b7280",
                anchor="center",
            ).pack(fill="both", expand=True, padx=8, pady=8)

        return card

    def load_notifications_list(self):
        for widget in self.notif_scroll.winfo_children():
            widget.destroy()

        for notif in self.notifications:
            self.create_notification_row(self.notif_scroll, notif)

    def create_notification_row(self, parent, notification):
        is_unread = notification.get("notif_isread", 0) == 0

        card = ctk.CTkFrame(
            parent,
            fg_color=WHITE if is_unread else "#f9fafb",
            corner_radius=8,
            border_width=1,
            border_color="#93c5fd" if is_unread else "#d1d5db",
        )
        card.pack(fill="x", padx=8, pady=6)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(10, 4))

        if is_unread:
            indicator = ctk.CTkFrame(header, width=8, height=8, fg_color=BLUE, corner_radius=4)
            indicator.pack(side="left", padx=(0, 6))

        date_val = notification.get("notif_create")
        if isinstance(date_val, (datetime, date)):
            date_str = date_val.strftime("%Y-%m-%d %H:%M")
        else:
            date_str = str(date_val or "")

        date_label = ctk.CTkLabel(
            header,
            text=date_str,
            font=("Arial", 11, "bold") if is_unread else ("Arial", 11),
            text_color=TEXT_BLUE if is_unread else "#4b5563",
            anchor="w",
        )
        date_label.pack(side="left")

        notif_type = notification.get("notif_type", "")
        if str(notif_type).strip().lower() == "overdue":
            notif_type = "System"
        type_prefix = "From: " if notif_type == "Admin" else "Type: "
        type_label = ctk.CTkLabel(
            header,
            text=f"{type_prefix}{notif_type}",
            font=("Arial", 10, "italic"),
            text_color="#6b7280",
            anchor="e",
        )
        type_label.pack(side="right")
        ctk.CTkFrame(card, height=1, fg_color="#e5e7eb").pack(fill="x", padx=12, pady=(2, 6))
        msg_frame = ctk.CTkFrame(card, fg_color="transparent")
        msg_frame.pack(fill="x", expand=True, padx=12, pady=4)

        message = str(notification.get("notif_message", "")).strip()
        line_guess = max(2, message.count("\n") + 1, (len(message) // 42) + 1)
        msg_height = min(140, max(64, line_guess * 22))
        msg_box = ctk.CTkTextbox(
            msg_frame,
            height=msg_height,
            fg_color="transparent",
            text_color="black" if is_unread else "#374151",
            font=("Arial", 11),
            wrap="word",
            activate_scrollbars=True,
            border_width=0,
        )
        msg_box.pack(fill="x", expand=True)
        msg_box.insert("1.0", message)
        msg_box.configure(state="disabled")

        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", padx=12, pady=(4, 10))

        if is_unread:
            mark_btn = ctk.CTkButton(
                footer,
                text="Mark as Read",
                width=100,
                height=28,
                font=("Arial", 10, "bold"),
                fg_color=BLUE,
                hover_color="#1e40af",
                corner_radius=6,
                command=lambda nid=notification["notif_id"]: self.mark_notification_read(nid),
            )
        else:
            mark_btn = ctk.CTkButton(
                footer,
                text="Read",
                width=80,
                height=28,
                font=("Arial", 10),
                fg_color="#e5e7eb",
                text_color="#6b7280",
                hover_color="#e5e7eb",
                corner_radius=6,
                state="disabled",
            )
        mark_btn.pack(side="right")

        return card

    def filter_items(self):
        search_term = self.items_search.get().lower()

        for widget in self.items_scroll.winfo_children():
            widget.destroy()

        filtered = [
            req
            for req in self.requests
            if (
                search_term in req["item_name"].lower()
                or search_term in req.get("item_code", "").lower()
            )
            and req.get("request_status") not in {"Returned", "Cancelled"}
        ]

        for i, req in enumerate(filtered):
            row = i // 2
            col = i % 2
            card = self.create_request_card(self.items_scroll, req)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

    def filter_notifications(self):
        search_term = self.notif_search.get().lower()

        for widget in self.notif_scroll.winfo_children():
            widget.destroy()

        filtered = [
            notif
            for notif in self.notifications
            if search_term in notif["notif_message"].lower()
            or search_term in notif["notif_type"].lower()
        ]

        for notif in filtered:
            self.create_notification_row(self.notif_scroll, notif)

    def mark_notification_read(self, notification_id):
        current_user = Session.load() or {}
        try:
            RequestRepository().mark_notification_read(
                notification_id, current_user.get("user_id", 1)
            )
            self.refresh()
        except Exception as error:
            messagebox.showerror("Notification Error", str(error), parent=self.app)

    def show_cancel_modal(self, request_id, item_name, status="Pending"):
        CancelConfirmationModal(self.app, request_id, item_name, status, on_cancelled=self.refresh)

    def show_return_modal(self, request):
        ItemReturnModal(self.app, request, on_returned=self.refresh)
