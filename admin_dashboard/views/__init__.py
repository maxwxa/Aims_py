from .dashboard_home import DashboardHomeView, create_analytics_tab
from .inventory_view import InventoryView, create_inventory_tab_v2
from .requests_view import RequestsView, create_requests_tab
from .transactions_view import TransactionsView, create_transactions_tab
from .users_view import UsersView, create_accounts_tab

__all__ = [
    "DashboardHomeView",
    "create_analytics_tab",
    "InventoryView",
    "create_inventory_tab_v2",
    "RequestsView",
    "create_requests_tab",
    "TransactionsView",
    "create_transactions_tab",
    "UsersView",
    "create_accounts_tab",
]
