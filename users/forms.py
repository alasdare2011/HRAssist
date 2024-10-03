from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = get_user_model()
        fields = ("email", "username")


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = get_user_model()
        fields = ("email", "username")


class UserSignupForm(UserCreationForm):
    is_staff = forms.BooleanField(
        required=False, help_text="Check if the user is staff."
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ["username", "email", "is_staff", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = self.cleaned_data[
            "is_staff"
        ]  # Set the is_staff field based on form input
        if commit:
            user.save()
        return user
