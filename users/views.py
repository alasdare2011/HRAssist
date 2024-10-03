from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from .forms import UserSignupForm  # Ensure the form is imported from the users app


@user_passes_test(lambda u: u.is_staff)
def signup(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")  # Redirect after successful signup
    else:
        form = UserSignupForm()

    return render(request, "signup.html", {"form": form})
