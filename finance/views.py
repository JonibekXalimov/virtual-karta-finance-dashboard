from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import CardForm, TransactionCreateForm
from .models import Transaction, VirtualCard


class UserCardsRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.cards.exists():
            messages.warning(request, "Avval kamida bitta karta yarating.")
            return redirect("card_create")
        return super().dispatch(request, *args, **kwargs)


class OwnedCardMixin(LoginRequiredMixin):
    def get_queryset(self):
        return self.request.user.cards.order_by("created_at")


class OwnedTransactionMixin(LoginRequiredMixin):
    def get_queryset(self):
        return self.request.user.transactions.select_related("card").order_by("-created_at")


class DashboardView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "finance/dashboard.html"
    context_object_name = "recent_transactions"

    def get_active_card(self):
        cards = self.request.user.cards.order_by("created_at")
        requested_card_id = self.request.GET.get("card")
        if requested_card_id and cards.filter(pk=requested_card_id).exists():
            return cards.get(pk=requested_card_id)
        return cards.first()

    def get_queryset(self):
        active_card = self.get_active_card()
        if not active_card:
            return Transaction.objects.none()
        return active_card.transactions.select_related("card").order_by("-created_at")[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cards = self.request.user.cards.order_by("created_at")
        primary_card = self.get_active_card()
        summary = primary_card.get_summary() if primary_card else {
            "income": Decimal("0.00"),
            "expense": Decimal("0.00"),
            "card_balance": Decimal("0.00"),
        }
        context["cards"] = cards
        context["primary_card"] = primary_card
        context["active_card_id"] = primary_card.pk if primary_card else None
        context["card_count"] = cards.count()
        context["total_income"] = summary["income"]
        context["total_expense"] = summary["expense"]
        context["total_balance"] = summary["card_balance"]
        return context


class CardListView(LoginRequiredMixin, ListView):
    model = VirtualCard
    template_name = "finance/card_list.html"
    context_object_name = "cards"

    def get_queryset(self):
        return self.request.user.cards.order_by("created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.request.user.get_finance_summary())
        return context


class CardDetailView(OwnedCardMixin, DetailView):
    model = VirtualCard
    template_name = "finance/card_detail.html"
    context_object_name = "card_object"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cards"] = self.request.user.cards.order_by("created_at")
        context["active_card_id"] = self.object.pk
        context["card_summary"] = self.object.get_summary()
        context["recent_transactions"] = self.object.transactions.order_by("-created_at")[:10]
        context["total_cards"] = self.request.user.cards.count()
        return context


class CardCreateView(LoginRequiredMixin, CreateView):
    model = VirtualCard
    form_class = CardForm
    template_name = "finance/card_form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Yangi karta yaratildi.")
        return response

    def get_success_url(self):
        return reverse("card_detail", kwargs={"pk": self.object.pk})


class CardUpdateView(OwnedCardMixin, UpdateView):
    model = VirtualCard
    form_class = CardForm
    template_name = "finance/card_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Karta ma'lumotlari yangilandi.")
        return response

    def get_success_url(self):
        return reverse("card_detail", kwargs={"pk": self.object.pk})


class CardDeleteView(OwnedCardMixin, DeleteView):
    model = VirtualCard
    template_name = "finance/card_confirm_delete.html"
    success_url = reverse_lazy("card_list")

    def form_valid(self, form):
        messages.success(self.request, "Karta va unga tegishli tranzaksiyalar o'chirildi.")
        return super().form_valid(form)


class TransactionCreateView(UserCardsRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionCreateForm
    template_name = "finance/transaction_form.html"
    transaction_type = None
    page_title = ""
    submit_label = ""
    selected_card = None

    def get_selected_card(self):
        if self.selected_card is not None:
            return self.selected_card
        self.selected_card = get_object_or_404(
            self.request.user.cards.order_by("created_at"),
            pk=self.kwargs["card_pk"],
        )
        return self.selected_card

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["selected_card"] = self.get_selected_card()
        return kwargs

    def get_success_url(self):
        return reverse("card_detail", kwargs={"pk": self.object.card.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["submit_label"] = self.submit_label
        context["transaction_type"] = self.transaction_type
        context["card_object"] = self.get_selected_card()
        return context

    def form_valid(self, form):
        card = form.cleaned_data["card"]
        amount = form.cleaned_data["amount"]
        if self.transaction_type == Transaction.TransactionType.EXPENSE and amount > card.current_balance:
            form.add_error("amount", "Kartada yetarli mablag' yo'q.")
            return self.form_invalid(form)

        form.instance.user = self.request.user
        form.instance.card = card
        form.instance.type = self.transaction_type
        response = super().form_valid(form)
        messages.success(self.request, "Tranzaksiya muvaffaqiyatli saqlandi.")
        return response


class IncomeCreateView(TransactionCreateView):
    transaction_type = Transaction.TransactionType.INCOME
    page_title = "Kirim qo'shish"
    submit_label = "Kirimni saqlash"


class ExpenseCreateView(TransactionCreateView):
    transaction_type = Transaction.TransactionType.EXPENSE
    page_title = "Chiqim qo'shish"
    submit_label = "Chiqimni saqlash"


class CardIncomeCreateView(IncomeCreateView):
    pass


class CardExpenseCreateView(ExpenseCreateView):
    pass


class TransactionHistoryView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "finance/transaction_list.html"
    context_object_name = "transactions"
    paginate_by = 15

    def get_queryset(self):
        queryset = self.request.user.transactions.select_related("card").order_by("-created_at")
        transaction_type = self.request.GET.get("type")
        valid_types = {choice[0] for choice in Transaction.TransactionType.choices}
        if transaction_type in valid_types:
            queryset = queryset.filter(type=transaction_type)
        card_id = self.request.GET.get("card")
        if card_id and self.request.user.cards.filter(pk=card_id).exists():
            queryset = queryset.filter(card_id=card_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_type"] = self.request.GET.get("type", "")
        context["selected_card"] = self.request.GET.get("card", "")
        context["transaction_types"] = Transaction.TransactionType.choices
        context["cards"] = self.request.user.cards.order_by("created_at")
        return context


class TransactionDetailView(OwnedTransactionMixin, DetailView):
    model = Transaction
    template_name = "finance/transaction_detail.html"
    context_object_name = "transaction"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next_url"] = self.request.GET.get("next", "")
        return context


class TransactionDeleteView(OwnedTransactionMixin, DeleteView):
    model = Transaction
    template_name = "finance/transaction_confirm_delete.html"
    success_url = reverse_lazy("transaction_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next_url"] = self.request.GET.get("next", "")
        return context

    def get_success_url(self):
        return self.request.POST.get("next") or self.request.GET.get("next") or str(self.success_url)

    def form_valid(self, form):
        messages.success(self.request, "Tranzaksiya o'chirildi.")
        return super().form_valid(form)
