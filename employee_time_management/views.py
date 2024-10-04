from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import datetime
from django.db.models import Q

from .forms import TimeOffForm, ApplyForOT

from .utils import (
    vacation_days_used,
    valid_date_range,
    annual_vacation,
    calculate_overtime_hours,
    list_of_conflicing_dates,
    only_apply_for_one_vacation_date,
    update_vacations,
    add_year,
)

from .models import (
    Division,
    Allowed_vacation,
    Staff,
    JobTitle,
    Manager,
    Owner,
    Dept,
    Vacations,
    SickDays,
    Overtime,
)


class HomePageView(TemplateView):
    template_name = "home.html"


@login_required(login_url="/accounts/login/")
def employee_info_view(request):

    user = request.user
    user_id = user.id
    user1 = Staff.objects.get(user_id=user_id)
    is_manager = user1.getIsManager()
    is_owner = user1.getIsOwner()
    is_employee = user1.getIsEmployee()
    is_super = user.is_superuser
    full_name = user.get_full_name()
    vacation_used = user1.vacation_used
    overtime = user1.overtime_hours
    allowed_hours = annual_vacation(user1)
    total_hours_available = allowed_hours + overtime - vacation_used
    submitted_holidays = (
        Vacations.objects.filter(name=user1)
        .filter(request_submitted=True)
        .filter(request_approved=False)
        .filter(request_denied=False)
    )
    approved_holidays = (
        Vacations.objects.filter(name=user1)
        .filter(request_submitted=True)
        .filter(request_approved=True)
        .filter(request_denied=False)
    )
    denied_holidays = Vacations.objects.filter(name=user1).filter(request_denied=True)
    context = {
        "full_name": full_name,
        "allowed_hours": allowed_hours,
        "vacation_used": vacation_used,
        "overtime": overtime,
        "total_hours_available": total_hours_available,
        "submitted_holidays": submitted_holidays,
        "approved_holidays": approved_holidays,
        "denied_holidays": denied_holidays,
        "is_manager": is_manager,
        "is_owner": is_owner,
        "is_employee": is_employee,
        "is_super": is_super,
    }
    return render(request, "employeeInfo.html", context)
