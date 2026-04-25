from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm

from .models import CustomUser


class StyledFormMixin:
    input_class = "form-control form-control-lg"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css_class = self.input_class
            if isinstance(field.widget, forms.CheckboxInput):
                css_class = "form-check-input"

            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {css_class}".strip()
            field.widget.attrs.setdefault("placeholder", field.label)
            if name == "password":
                field.widget.attrs["autocomplete"] = "current-password"
            elif name in {"password1", "password2"}:
                field.widget.attrs["autocomplete"] = "new-password"


class CustomAuthenticationForm(StyledFormMixin, AuthenticationForm):
    pass


class CustomUserCreationForm(StyledFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
        )


class CustomUserChangeForm(StyledFormMixin, UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "is_active",
            "is_staff",
        )
