from decimal import Decimal
import random
import string

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F


STARTING_CARD_BALANCE = Decimal("0.00")


def generate_card_number():
    return "".join(random.choices(string.digits, k=16))


class VirtualCard(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cards",
    )
    name = models.CharField(max_length=100, default="Asosiy karta")
    card_number = models.CharField(max_length=16, unique=True, blank=True)
    starting_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=STARTING_CARD_BALANCE,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=STARTING_CARD_BALANCE,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    total_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    total_expense = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.card_number:
            card_number = generate_card_number()
            while VirtualCard.objects.filter(card_number=card_number).exists():
                card_number = generate_card_number()
            self.card_number = card_number
        if self._state.adding and self.balance == STARTING_CARD_BALANCE:
            self.balance = self.starting_balance
        super().save(*args, **kwargs)

    @property
    def masked_number(self):
        return f"**** **** **** {self.card_number[-4:]}"

    def get_summary(self):
        return {
            "income": self.total_income,
            "expense": self.total_expense,
            "card_balance": self.balance,
        }

    @property
    def current_balance(self):
        return self.balance


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        INCOME = "income", "Kirim"
        EXPENSE = "expense", "Chiqim"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    card = models.ForeignKey(
        VirtualCard,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    type = models.CharField(max_length=20, choices=TransactionType.choices)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user.username} - {self.get_type_display()} - {self.amount}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if not is_new:
            return

        if self.type == self.TransactionType.INCOME:
            VirtualCard.objects.filter(pk=self.card_id).update(
                total_income=F("total_income") + self.amount,
                balance=F("balance") + self.amount,
            )
        else:
            VirtualCard.objects.filter(pk=self.card_id).update(
                total_expense=F("total_expense") + self.amount,
                balance=F("balance") - self.amount,
            )
        self.card.refresh_from_db(fields=["balance", "total_income", "total_expense"])
