from django.urls import path

from .views import HomePageView, employee_info_view

from . import views


urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("employee/", views.employee_info_view, name="employee"),
]
