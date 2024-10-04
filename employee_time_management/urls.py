from django.urls import path

from .views import HomePageView, employee_info_view

from . import views


urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("employee/", views.employee_info_view, name="employee"),
    path("hrinfo/", views.hr_info_view, name="hrinfo"),
    path("timeoff/", views.time_off_request_view, name="timeoff"),
    path("overtime/", views.overtime_request_view, name="overtime"),
]
