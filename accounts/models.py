from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Sum
from decimal import Decimal


phone_validator = RegexValidator(
    regex=r"^\+?\d{9,15}$",
    message="Phone number must contain 9 to 15 digits and may start with '+'.",
)


class CustomUser(AbstractUser):
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    phone = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        validators=[phone_validator],
        help_text="Enter phone number in international format.",
    )

    class Meta:
        verbose_name = "Custom user"
        verbose_name_plural = "Custom users"
        ordering = ("username",)

    def __str__(self):
        return self.get_full_name() or self.username

    def ensure_card(self):
        from finance.models import VirtualCard

        card = self.cards.order_by("created_at").first()
        if card:
            return card
        return VirtualCard.objects.create(user=self, name="Asosiy karta")

    def get_finance_summary(self):
        summary = self.cards.aggregate(
            total_income=Sum("total_income"),
            total_expense=Sum("total_expense"),
            total_balance=Sum("balance"),
        )
        income = summary["total_income"] or Decimal("0.00")
        expense = summary["total_expense"] or Decimal("0.00")
        balance = summary["total_balance"] or Decimal("0.00")
        return {
            "income": income,
            "expense": expense,
            "balance": balance,
            "card_count": self.cards.count(),
        }
