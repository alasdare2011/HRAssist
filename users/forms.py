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


class UserSignupForm(forms.ModelForm):
    is_staff = forms.BooleanField(
        required=False, help_text="Check if the user is staff."
    )
    first_name = forms.CharField(max_length=30, required=True, help_text="First name")
    last_name = forms.CharField(max_length=30, required=True, help_text="Last name")

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ["username", "email", "first_name", "last_name", "is_staff"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = self.cleaned_data[
            "is_staff"
        ]  # Set the is_staff field based on form input
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.set_unusable_password()  # User will need to reset their password
        if commit:
            user.save()
        return user
