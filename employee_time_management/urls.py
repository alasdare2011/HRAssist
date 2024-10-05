from django.urls import path

from . import views


urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("employee/", views.employee_info_view, name="employee"),
    path("hrinfo/", views.hr_info_view, name="hrinfo"),
    path("timeoff/", views.time_off_request_view, name="timeoff"),
    path("overtime/", views.overtime_request_view, name="overtime"),
    path(
        "approve_timeoff/", views.manager_approve_time_off_view, name="approve_timeoff"
    ),
]
