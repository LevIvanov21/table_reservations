from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.forms import BooleanField
from users.models import User


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "name", "password1", "password2",)


class UserProfileForm(StyleFormMixin, UserChangeForm):
    class Meta:
        model = User
        fields = ("email", "name", "first_name", "last_name", "description", "phone_number", "avatar", "tg_nick",
                  "tg_chat_id", "time_offset",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password"].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = int(self.cleaned_data["time_offset"])
        if -12 > cleaned_data or cleaned_data > 14:
            raise forms.ValidationError(f"Невозможное смещение часового пояса: {cleaned_data} часа")
        else:
            return self.cleaned_data
