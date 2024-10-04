from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import datetime
from django.db.models import Q
from django.contrib.auth import get_user_model

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

User = get_user_model()  # Reference the custom user model


class HomePageView(TemplateView):
    template_name = "home.html"


@login_required(login_url="/accounts/login/")
def employee_info_view(request):
    """
    View to display employee information including vacation details, overtime, and role-specific information.

    This view retrieves and displays the user's information (such as manager, owner, and employee status),
    their vacation and overtime hours, and their submitted, approved, and denied holidays. It calculates
    the total available hours (vacation + overtime - used vacation) for the user and provides this data
    to the template for rendering.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - HttpResponse: Renders the 'employee_time_mgmt/employeeInfo.html' template with the following context:
        - full_name: The full name of the user.
        - allowed_hours: Total vacation hours available to the user.
        - vacation_used: The number of vacation hours the user has already used.
        - overtime: The total overtime hours the user has.
        - total_hours_available: The total number of vacation and overtime hours available to the user.
        - submitted_holidays: Holidays that have been submitted but not yet approved or denied.
        - approved_holidays: Holidays that have been approved.
        - denied_holidays: Holidays that have been denied.
        - is_manager: Boolean indicating whether the user is a manager.
        - is_owner: Boolean indicating whether the user is an owner.
        - is_employee: Boolean indicating whether the user is an employee.
        - is_super: Boolean indicating whether the user is a superuser.
    """
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


def hr_info_view(request):
    """
    View to display human resource information for staff, including attendance, vacation, overtime,
    and unpaid time statistics, as well as functionality for updating vacation details or clearing unpaid time.

    This view first checks if the user is a manager or an employee. If true, it redirects them to the employee view.
    For HR users (owners or superusers), it compiles various staff-related statistics, including:
    - Staff whose vacation or other stats need to be updated.
    - Staff with unpaid time.
    - Daily attendance of each staff member, including vacation, sick, or present status.
    - Overall statistics for each staff member, including vacation used, overtime hours, unpaid time,
      and total sick days taken (calculated as 8 hours per sick day).

    If the method is POST, the function handles two actions:
    1. Updating vacation details for selected staff.
    2. Resetting unpaid time for selected staff.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - HttpResponse: Renders the 'employee_time_mgmt/hrInfo.html' template with the following context:
        - unpaid_hours: List of staff members with unpaid hours.
        - update_staff: List of staff members whose details need to be updated (based on date).
        - staff_stats: List of staff members' statistics including first name, last name, vacation used,
          overtime hours, unpaid time, and total sick days.
        - daily_attendance: List of staff attendance for the day (Vacation, Sick, or Present).
        - is_owner: Boolean indicating if the user is an owner.
        - is_super: Boolean indicating if the user is a superuser.
    """
    user = request.user
    user_id = user.id
    today = datetime.date.today()
    user1 = Staff.objects.get(user_id=user_id)
    is_owner = user1.getIsOwner()
    is_super = user.is_superuser
    is_manager = user1.getIsManager()
    is_employee = user1.getIsEmployee()
    if is_manager or is_employee:
        return redirect("employee")

    staff = Staff.objects.all()
    update_staff = []
    for s in staff:
        if datetime.date.today() >= s.update_on:
            update_staff.append(s)

    unpaid_hours = []
    for s in staff:
        if s.unpaid_time > 0:
            unpaid_hours.append(s)

    daily_attendance = []

    for s in staff:
        employee = []
        employee.append(s)
        vacation = (
            Vacations.objects.filter(name=s)
            .filter(request_approved=True)
            .filter(
                Q(start_date__lte=datetime.date.today())
                & Q(end_date__gte=datetime.date.today())
            )
        )
        if vacation.count() > 0:
            employee.append("Vacation")
        elif (
            SickDays.objects.filter(name=s).filter(date=datetime.date.today()).count()
            > 0
        ):
            employee.append("Sick")
        else:
            employee.append("Present")
        daily_attendance.append(employee)

    staff_stats = []
    for s in staff:
        staff1 = []
        staff1.append(s.user.first_name)
        staff1.append(s.user.last_name)
        staff1.append(s.vacation_used)
        staff1.append(s.overtime_hours)
        staff1.append(s.unpaid_time)
        staff1.append(SickDays.objects.filter(name=s).count() * 8)
        staff_stats.append(staff1)

    if request.method == "POST":
        if "update" in request.POST:
            dict_post = request.POST.dict()
            staff1 = dict_post["Staff"].split(" ", 1)[0]
            user = User.objects.get(username=staff1)  # Use custom user model
            staff = Staff.objects.get(user=user)
            update_vacations(staff, datetime.date.today())
        else:
            dict_post = request.POST.dict()
            staff1 = dict_post["Staff"].split(" ", 1)[0]
            user = User.objects.get(username=staff1)
            staff = Staff.objects.get(user=user)
            staff.unpaid_time = 0
            staff.save()

        return HttpResponseRedirect(request.path_info)

    context = {
        "unpaid_hours": unpaid_hours,
        "update_staff": update_staff,
        "staff_stats": staff_stats,
        "daily_attendance": daily_attendance,
        "is_owner": is_owner,
        "is_super": is_super,
    }
    return render(request, "hrInfo.html", context)
