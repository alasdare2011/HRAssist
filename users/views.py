from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from .forms import UserSignupForm  # Ensure the form is imported from the users app
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


@user_passes_test(lambda u: u.is_staff)
def signup(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Generate token and encoded user ID for the password reset link
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # Create the password reset link
            reset_link = request.build_absolute_uri(
                reverse(
                    "password_reset_confirm", kwargs={"uidb64": uid, "token": token}
                )
            )
            # Trigger a password reset email
            subject = "Set your password"
            email_template_name = "registration/password_reset_email.html"
            context = {
                "email": user.email,
                "domain": request.get_host(),
                "site_name": "Your Site",
                "uid": uid,
                "user": user,
                "token": token,
                "protocol": "http",
                "reset_link": reset_link,
            }
            email_body = render_to_string(email_template_name, context)
            send_mail(subject, email_body, "your_email@example.com", [user.email])
            return redirect("home")  # Redirect after successful signup
    else:
        form = UserSignupForm()

    return render(request, "signup.html", {"form": form})
