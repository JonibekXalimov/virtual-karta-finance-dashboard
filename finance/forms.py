from django import forms

from .models import Transaction, VirtualCard


class StyledFinanceFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} form-control form-control-lg".strip()


class CardForm(StyledFinanceFormMixin, forms.ModelForm):
    class Meta:
        model = VirtualCard
        fields = ("name",)
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Masalan Asosiy karta",
                }
            ),
        }


class TransactionCreateForm(StyledFinanceFormMixin, forms.ModelForm):
    def __init__(self, *args, user=None, selected_card=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["card"].queryset = user.cards.order_by("created_at") if user else VirtualCard.objects.none()
        self.fields["card"].initial = selected_card
        self.fields["card"].queryset = self.fields["card"].queryset.filter(pk=selected_card.pk)
        self.fields["card"].widget = forms.HiddenInput()

    class Meta:
        model = Transaction
        fields = ("card", "amount", "note")
        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0.01",
                    "placeholder": "Masalan 150000",
                }
            ),
            "note": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Izoh (ixtiyoriy)",
                }
            ),
        }
