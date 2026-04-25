from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView

from .forms import CustomAuthenticationForm, CustomUserCreationForm
from .models import CustomUser


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.user.ensure_card()
        return response


class SignUpView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = "accounts/profile.html"
    context_object_name = "profile_user"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cards = self.request.user.cards.order_by("created_at")
        summary = self.request.user.get_finance_summary()
        context["cards"] = cards
        context["total_income"] = summary["income"]
        context["total_expense"] = summary["expense"]
        context["total_balance"] = summary["balance"]
        context["card_count"] = summary["card_count"]
        return context
