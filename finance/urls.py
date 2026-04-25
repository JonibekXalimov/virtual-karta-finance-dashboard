from django.urls import path

from .views import (
    CardCreateView,
    CardDeleteView,
    CardDetailView,
    CardExpenseCreateView,
    CardIncomeCreateView,
    CardListView,
    CardUpdateView,
    DashboardView,
    TransactionDeleteView,
    TransactionDetailView,
    TransactionHistoryView,
)

urlpatterns = [
    path("", DashboardView.as_view(), name="home"),
    path("cards/", CardListView.as_view(), name="card_list"),
    path("cards/add/", CardCreateView.as_view(), name="card_create"),
    path("cards/<int:pk>/", CardDetailView.as_view(), name="card_detail"),
    path("cards/<int:pk>/edit/", CardUpdateView.as_view(), name="card_update"),
    path("cards/<int:pk>/delete/", CardDeleteView.as_view(), name="card_delete"),
    path("cards/<int:card_pk>/income/add/", CardIncomeCreateView.as_view(), name="card_income_create"),
    path("cards/<int:card_pk>/expense/add/", CardExpenseCreateView.as_view(), name="card_expense_create"),
    path("transactions/", TransactionHistoryView.as_view(), name="transaction_list"),
    path("transactions/<int:pk>/", TransactionDetailView.as_view(), name="transaction_detail"),
    path("transactions/<int:pk>/delete/", TransactionDeleteView.as_view(), name="transaction_delete"),
]
