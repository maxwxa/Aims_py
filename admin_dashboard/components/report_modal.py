import csv
from datetime import datetime
from tkinter import filedialog, ttk, messagebox
import customtkinter as ctk
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
from repositories import (
    InventoryRepository, RequestRepository, TransactionRepository, AnalyticsRepository
)

DARK_BLUE = "#1c3b7a"
MODAL_BG = "#0b1b42"
WHITE = "#ffffff"
TEXT_BLUE = "#1e3a8a"
BLUE = "#1d4ed8"


class SummaryReportModal:
    def __init__(self, parent):
        self.modal = ctk.CTkToplevel(parent)
        self.modal.title("Summary Reports & Exports")
        self.modal.geometry("980x680")
        self.modal.minsize(800, 500)
        self.modal.configure(fg_color=MODAL_BG)
        self.modal.transient(parent)
        self.modal.grab_set()

        self.report_headers = []
        self.report_data = []
        self.report_title = ""

        top_bar = ctk.CTkFrame(self.modal, fg_color=DARK_BLUE, height=60, corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        ctk.CTkLabel(
            top_bar, text="Generate Summary Reports", font=("Arial", 20, "bold"), text_color=WHITE
        ).pack(side="left", padx=20, pady=15)

        controls_frame = ctk.CTkFrame(self.modal, fg_color=WHITE, corner_radius=8)
        controls_frame.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            controls_frame, text="Report Type:", font=("Arial", 12, "bold"), text_color=TEXT_BLUE
        ).pack(side="left", padx=(15, 5), pady=12)

        self.report_type_combo = ctk.CTkComboBox(
            controls_frame,
            width=280,
            values=[
                "Inventory Summary",
                "Out of Stock & Expired Items",
                "Items Due for Return",
                "Item Requests Summary",
                "Transactions Summary",
                "System Activity Logs"
            ],
            fg_color=WHITE,
            text_color="black",
            button_color="#d1d5db",
            state="readonly",
        )
        self.report_type_combo.pack(side="left", padx=5, pady=12)
        self.report_type_combo.set("Inventory Summary")

        ctk.CTkButton(
            controls_frame,
            text="Generate Report",
            fg_color=BLUE,
            hover_color="#1e40af",
            font=("Arial", 12, "bold"),
            command=self.generate_report,
        ).pack(side="left", padx=10, pady=12)

        ctk.CTkButton(
            controls_frame,
            text="Export to CSV",
            fg_color="#16a34a",
            hover_color="#15803d",
            font=("Arial", 12, "bold"),
            command=self.export_csv,
        ).pack(side="right", padx=(5, 15), pady=12)

        ctk.CTkButton(
            controls_frame,
            text="Export to PDF",
            fg_color="#dc2626",
            hover_color="#b91c1c",
            font=("Arial", 12, "bold"),
            command=self.export_pdf,
        ).pack(side="right", padx=5, pady=12)

        self.stats_label = ctk.CTkLabel(
            self.modal,
            text="Select a report type and click 'Generate Report' to view summary details.",
            font=("Arial", 13, "bold"),
            text_color="#bfdbfe",
            anchor="w",
        )
        self.stats_label.pack(fill="x", padx=25, pady=(0, 5))

        table_frame = ctk.CTkFrame(self.modal, fg_color=WHITE, corner_radius=8)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        self.tree = ttk.Treeview(table_frame, show="headings", selectmode="browse")
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        self.generate_report()

    def generate_report(self):
        report_type = self.report_type_combo.get()
        self.report_title = report_type
        self.report_headers = []
        self.report_data = []

        try:
            if report_type == "Inventory Summary":
                items = InventoryRepository().get_all()
                self.report_headers = ["Item ID", "Item Name", "Code", "Category", "Stock", "Unit", "Added Date"]
                total_stock = 0
                for item in items:
                    total_stock += item.stock
                    self.report_data.append([
                        str(item.item_id),
                        item.item_name,
                        item.item_code or "N/A",
                        item.category_name or "N/A",
                        str(item.stock),
                        item.unit or "pcs",
                        str(item.added_date or "N/A")[:10]
                    ])
                self.stats_label.configure(
                    text=f"Report: {report_type} | Total Items: {len(items)} | Total Combined Stock: {total_stock}"
                )
            elif report_type == "Out of Stock & Expired Items":
                items = InventoryRepository().get_all()
                target_items = [item for item in items if item.stock <= 0 or item.is_expired]
                self.report_headers = ["Item ID", "Item Name", "Code", "Category", "Stock", "Expiration Date", "Status"]
                for item in target_items:
                    self.report_data.append([
                        str(item.item_id),
                        item.item_name,
                        item.item_code or "N/A",
                        item.category_name or "N/A",
                        str(item.stock),
                        str(item.expiration_date or "N/A")[:10],
                        item.status_label
                    ])
                self.stats_label.configure(
                    text=f"Report: {report_type} | Total Out-of-Stock & Expired Items: {len(target_items)}"
                )
            elif report_type == "Items Due for Return":
                due_items = AnalyticsRepository().get_due_items()
                self.report_headers = ["Request ID", "Item ID", "Item Name", "Due Date"]
                for item in due_items:
                    self.report_data.append([
                        str(item.get("request_id", "N/A")),
                        str(item.get("item_id", "N/A")),
                        item.get("item_name", "N/A"),
                        str(item.get("due_date", "N/A"))[:10]
                    ])
                self.stats_label.configure(
                    text=f"Report: {report_type} | Items Due/Overdue for Return: {len(due_items)}"
                )
            elif report_type == "Item Requests Summary":
                requests = RequestRepository().get_all()
                self.report_headers = ["Req ID", "Requester", "Student No", "Item Name", "Qty", "Status", "Request Date", "Due Date"]
                counts = {}
                for req in requests:
                    status = req.get("request_status", "Pending")
                    counts[status] = counts.get(status, 0) + 1
                    self.report_data.append([
                        str(req.get("request_id", "")),
                        req.get("requester_name", "N/A"),
                        req.get("student_id", "N/A"),
                        req.get("item_name", "N/A"),
                        str(req.get("quantity", 1)),
                        status,
                        str(req.get("request_date", "N/A"))[:16],
                        str(req.get("due_date", "N/A"))[:10]
                    ])
                summary_status = ", ".join(f"{k}: {v}" for k, v in counts.items())
                self.stats_label.configure(
                    text=f"Report: {report_type} | Total Requests: {len(requests)} ({summary_status})"
                )
            elif report_type == "Transactions Summary":
                transactions = TransactionRepository().get_all(mode="current")
                self.report_headers = ["Track No.", "Req ID", "Type", "Item Name", "Qty", "Approved By", "Received By", "Date/Time"]
                for trx in transactions:
                    is_cancelled = (
                        str(trx.get("transaction_type", "")).strip().lower() == "cancelled"
                        or str(trx.get("request_status", "")).strip().lower() == "cancelled"
                    )
                    received_by = "N/A" if is_cancelled else (trx.get("requester_name") or trx.get("confirmed_by_name") or "N/A")
                    self.report_data.append([
                        f"TRX-{trx.get('transaction_id', '')}",
                        f"REQ-{trx.get('request_id', '')}",
                        str(trx.get("transaction_type", "N/A")),
                        str(trx.get("item_name", "N/A")),
                        str(trx.get("quantity", 0)),
                        str(trx.get("approved_by_name") or "N/A"),
                        received_by,
                        str(trx.get("transaction_date", "N/A"))[:16]
                    ])
                self.stats_label.configure(
                    text=f"Report: {report_type} | Total Current Transactions: {len(transactions)}"
                )
            elif report_type == "System Activity Logs":
                logs = AnalyticsRepository().get_recent_logs(limit=100)
                self.report_headers = ["Log ID", "User", "Action", "Table Affected", "Record ID", "Timestamp"]
                for log in logs:
                    self.report_data.append([
                        str(log.get("log_id", "")),
                        str(log.get("user", "System")),
                        str(log.get("action", "")),
                        str(log.get("table_affected", "")),
                        str(log.get("item_id", "")),
                        str(log.get("timestamp", ""))[:19]
                    ])
                self.stats_label.configure(
                    text=f"Report: {report_type} | Recent Log Entries: {len(logs)}"
                )
        except Exception as error:
            messagebox.showerror("Report Error", f"Failed to generate report: {error}", parent=self.modal)
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.tree["columns"] = self.report_headers
        for header in self.report_headers:
            self.tree.heading(header, text=header)
            self.tree.column(header, width=120, anchor="center")

        for row in self.report_data:
            self.tree.insert("", "end", values=row)

    def export_csv(self):
        if not self.report_data:
            messagebox.showwarning("No Data", "There is no report data to export.", parent=self.modal)
            return
        filename = filedialog.asksaveasfilename(
            parent=self.modal,
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv"), ("All files", "*.*")],
            initialfile=f"{self.report_title.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        if not filename:
            return
        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([self.report_title])
                writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                writer.writerow([])
                writer.writerow(self.report_headers)
                writer.writerows(self.report_data)
            messagebox.showinfo("Export Success", f"Report successfully exported to:\n{filename}", parent=self.modal)
        except Exception as error:
            messagebox.showerror("Export Error", f"Failed to export CSV: {error}", parent=self.modal)

    def export_pdf(self):
        if not self.report_data:
            messagebox.showwarning("No Data", "There is no report data to export.", parent=self.modal)
            return
        filename = filedialog.asksaveasfilename(
            parent=self.modal,
            defaultextension=".pdf",
            filetypes=[("PDF file", "*.pdf"), ("All files", "*.*")],
            initialfile=f"{self.report_title.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        if not filename:
            return
        try:
            with PdfPages(filename) as pdf:
                rows_per_page = 25
                total_rows = len(self.report_data)
                num_pages = max(1, (total_rows + rows_per_page - 1) // rows_per_page)

                for page_num in range(num_pages):
                    start_idx = page_num * rows_per_page
                    end_idx = min(start_idx + rows_per_page, total_rows)
                    page_data = self.report_data[start_idx:end_idx]

                    fig = Figure(figsize=(11, 8.5))
                    ax = fig.add_subplot(111)
                    ax.axis("off")

                    fig.suptitle(
                        f"Academic Inventory Management System\n{self.report_title}",
                        fontsize=14, fontweight="bold", y=0.96
                    )

                    gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ax.text(
                        0.0, 1.02,
                        f"Generated: {gen_time}   |   Page {page_num + 1} of {num_pages}",
                        transform=ax.transAxes, fontsize=9, color="#555555"
                    )

                    table = ax.table(
                        cellText=page_data,
                        colLabels=self.report_headers,
                        loc="center",
                        cellLoc="center"
                    )
                    table.auto_set_font_size(False)
                    table.set_fontsize(8)
                    table.scale(1.0, 1.4)

                    for (r, c), cell in table.get_celld().items():
                        if r == 0:
                            cell.set_facecolor("#1c3b7a")
                            cell.get_text().set_color("white")
                            cell.get_text().set_weight("bold")
                        elif r % 2 == 0:
                            cell.set_facecolor("#f3f4f6")
                        else:
                            cell.set_facecolor("white")

                    pdf.savefig(fig, bbox_inches="tight")
            messagebox.showinfo("Export Success", f"Report successfully exported to:\n{filename}", parent=self.modal)
        except Exception as error:
            messagebox.showerror("Export Error", f"Failed to export PDF: {error}", parent=self.modal)
