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
    Staff,
    Manager,
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


@login_required(login_url="/accounts/login/")
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


@login_required(login_url="/accounts/login/")
def time_off_request_view(request):
    """
    Handles the time-off request process for an employee.

    This view allows an employee to submit a vacation request by filling out a form with
    the start date, end date, unpaid time, and overtime to be used during their vacation.

    The view performs several validation checks before submitting the request:
    - Ensures the user is an employee.
    - Checks if the entered date range is valid.
    - Ensures the user has enough available vacation time, overtime, or unpaid time.
    - Checks if the user has already requested or been approved for the selected vacation dates.

    If the validation passes, a vacation request is created in the database and a success message is shown.
    If validation fails, an appropriate error message is displayed, and the form is rendered again with the error.

    Parameters:
    - request: The HTTP request object that contains the POST data with the form submission.

    Returns:
    - A rendered time-off form if the request is a GET request or if validation fails.
    - On a successful form submission, the form is submitted, and a success message is displayed.

    Validation errors include:
    - Using too much unpaid time or overtime.
    - Overtime exceeding the saved overtime available to the employee.
    - Invalid date ranges.
    - Vacation hours exceeding the allowed vacation time.
    - Conflicts with already submitted or approved vacations.
    """
    user = request.user
    user1 = Staff.objects.get(user=user)
    if not user1.getIsEmployee():
        return redirect("employee")
    if request.method == "POST":
        dept = user1.dept
        vacation_used = user1.vacation_used
        saved_overtime = user1.overtime_hours
        allowed_hours = annual_vacation(user1)
        is_employee = user1.is_employee
        form = TimeOffForm(request.POST)
        start_month = int(request.POST["start_date_month"])
        start_day = int(request.POST["start_date_day"])
        start_year = int(request.POST["start_date_year"])
        end_month = int(request.POST["end_date_month"])
        end_day = int(request.POST["end_date_day"])
        end_year = int(request.POST["end_date_year"])
        unpaid_time = float(request.POST["unpaid_time"])
        overtime = float(request.POST["overtime"])
        start_date = datetime.date(start_year, start_month, start_day)
        end_date = datetime.date(end_year, end_month, end_day)
        vacation_hours = (
            vacation_days_used(start_date, end_date) - unpaid_time - overtime
        )
        vacations = Vacations.objects.filter(name=user1).filter(request_denied=False)
        if vacation_days_used(start_date, end_date) < unpaid_time + overtime:
            messages.error(
                request, "You have used either too much unpaid time or overtime."
            )
            form = TimeOffForm()
            return render(
                request,
                "timeoff.html",
                {"form": form, "is_employee": True},
            )
        if overtime > saved_overtime:
            messages.error(request, "You do not have engough overtime.")
            form = TimeOffForm()
            return render(
                request,
                "timeoff.html",
                {"form": form, "is_employee": True},
            )
        if not valid_date_range(start_date, end_date):
            messages.error(request, "Please enter a valid date range")
            form = TimeOffForm(request.POST)
            return render(request, "timeoff.html", {"form": form, "is_employee": True})
        if vacation_hours > allowed_hours:
            messages.error(
                request,
                "You do not have enough hours to \
            take this time off. You can take some as unpaid if you like.",
            )
            form = TimeOffForm()
            return render(
                request,
                "timeoff.html",
                {"form": form, "is_employee": True},
            )
        if only_apply_for_one_vacation_date(start_date, end_date, vacations):
            messages.error(
                request,
                "You have already either applied of been \
            approved for one of these dates. Please try again.",
            )
            form = TimeOffForm()
            return render(
                request,
                "timeoff.html",
                {"form": form, "is_employee": True},
            )
        else:
            Vacations.objects.create(
                name=user1,
                start_date=start_date,
                end_date=end_date,
                dept=dept,
                is_employee=is_employee,
                total_hours_away=vacation_hours,
                hours_unpaid=unpaid_time,
                overtime=overtime,
                request_submitted=True,
            )
            user1.overtime_hours = saved_overtime - overtime
            user1.save()
            messages.success(
                request,
                "Your vacation request was submitted successfully! If approved, this \
            vacation will use "
                + str(vacation_hours)
                + " of your availabe \
            vacation time hours.",
            )
    form = TimeOffForm()
    return render(request, "timeoff.html", {"form": form, "is_employee": True})


@login_required(login_url="/accounts/login/")
def overtime_request_view(request):
    """
    Handles the overtime request process for an employee.

    This view allows an employee to submit an overtime request by filling out a form with
    the date and the number of overtime hours to be requested.

    The view performs several validation checks before submitting the request:
    - Ensures the user is an employee.
    - Checks if the entered overtime date is valid (not in the future).
    - Ensures the employee has not already applied for overtime on the same date.

    If the validation passes, the overtime request is created in the database, and a success message is shown.
    If validation fails, an appropriate error message is displayed, and the form is rendered again with the error.

    Parameters:
    - request: The HTTP request object that contains the POST data with the form submission.

    Returns:
    - A rendered overtime request form if the request is a GET request or if validation fails.
    - On a successful form submission, the form is submitted, and a success message is displayed.

    Validation errors include:
    - Submitting an overtime request for a future date.
    - Submitting multiple overtime requests for the same date.
    """
    user = request.user
    user_id = user.id
    today = datetime.date.today()
    user1 = Staff.objects.get(user_id=user_id)
    if not user1.getIsEmployee():
        return redirect("employee")
    if request.method == "POST":
        dept = user1.dept
        form = TimeOffForm(request.POST)
        month = int(request.POST["ot_date_month"])
        day = int(request.POST["ot_date_day"])
        year = int(request.POST["ot_date_year"])
        hours_ot = int(request.POST["hours"])
        ot_date = datetime.date(year, month, day)
        count = Overtime.objects.filter(name=user1).filter(date=ot_date).count()
        if ot_date > today:
            messages.error(request, "Please enter a valid date.")
            form = ApplyForOT()
            return render(
                request, "ot_requests.html", {"form": form, "is_employee": True}
            )
        elif count > 0:
            messages.error(request, "You already applied for overtime on this date.")
            form = ApplyForOT()
            return render(
                request,
                "ot_requests.html",
                {"form": form, "is_employee": True},
            )
        else:
            overtime = calculate_overtime_hours(hours_ot)
            Overtime.objects.create(
                name=user1, dept=dept, date=ot_date, ot_hours=overtime
            )
            messages.success(
                request,
                "Your overtime request was submitted successfully. If approved, you \
            will receive "
                + str(overtime)
                + " hours of banked time off.",
            )
    form = ApplyForOT()
    return render(
        request,
        "ot_requests.html",
        {"form": form, "is_employee": True},
    )


@login_required(login_url="/accounts/login/")
def manager_approve_time_off_view(request):
    """
    Handles the time-off approval process for managers.

    This view allows a manager to review and approve or deny time-off requests submitted by employees in their department.
    The view displays unapproved vacation requests and checks for scheduling conflicts with already approved vacations.

    The view performs several tasks:
    - Ensures the user is a manager. If not, they are redirected to the employee page.
    - Retrieves the staff in the manager's department and calculates the maximum number of employees that can be on vacation at once.
    - Retrieves unapproved vacation requests and checks for conflicts with approved vacations.
    - Allows the manager to approve or deny vacation requests. If a request is denied, the employee's overtime is returned to them.

    Parameters:
    - request: The HTTP request object that contains the POST data with the form submission.

    Returns:
    - A rendered vacation approval form with a list of unapproved vacations and vacation conflicts.
    - After a POST request, it redirects back to the same page to display the updated list of unapproved vacations.

    Actions:
    - Approving a vacation: Marks the vacation as approved and updates the employee's vacation and unpaid time.
    - Denying a vacation: Marks the vacation as denied and restores any overtime hours the employee had requested to use.

    Validation errors include:
    - None in this view, but the logic ensures that only managers can access the vacation approval process.
    """
    user = request.user
    user_id = user.id
    user1 = Staff.objects.get(user_id=user_id)
    is_manager = user1.getIsManager()
    if not is_manager:
        return redirect("employee")
    dept = user1.dept
    staff = Staff.objects.filter(dept=dept).filter(is_employee=True)
    total_staff = staff.count()
    min_staff = dept.min_staff
    max_staff_off = total_staff - min_staff
    unapproved_vacations = (
        Vacations.objects.filter(dept=dept)
        .filter(request_submitted=True)
        .filter(is_employee=True)
        .filter(request_approved=False)
        .filter(request_denied=False)
        .order_by("name")
    )
    approved_vacations = (
        Vacations.objects.filter(dept=dept)
        .filter(request_submitted=True)
        .filter(is_employee=True)
        .filter(request_approved=True)
    )
    vacations_with_conflicts = list_of_conflicing_dates(
        unapproved_vacations, approved_vacations, max_staff_off
    )
    if request.method == "POST":
        vacation = request.POST.dict()
        vacation_keys = list(vacation.keys())
        vacation_id = vacation_keys[1]
        if vacation_id.startswith("Deny"):
            vacation_id = vacation_id.split(" ", 1)[1]
            approved_vacation = Vacations.objects.get(id=vacation_id)
            approved_vacation.request_denied = True
            approved_vacation.save()
            overtime = approved_vacation.overtime
            staff = approved_vacation.name
            staff.overtime_hours = staff.overtime_hours + overtime
            staff.save()
            return HttpResponseRedirect(request.path_info)
        else:
            approved_vacation = Vacations.objects.get(id=vacation_id)
            staff = approved_vacation.name
            hours_away = approved_vacation.total_hours_away
            unpaid_time = approved_vacation.hours_unpaid
            staff.vacation_used = hours_away
            staff.save()
            staff.unpaid_time = staff.unpaid_time + unpaid_time
            staff.save()
            approved_vacation.request_approved = True
            approved_vacation.save()
            unapproved_vacations = (
                Vacations.objects.filter(dept=dept)
                .filter(request_submitted=True)
                .filter(is_employee=True)
                .filter(request_approved=False)
                .filter(request_denied=False)
                .order_by("name")
            )
            return HttpResponseRedirect(request.path_info)
    context = {
        "unapproved_vacations": unapproved_vacations,
        "vacations_with_conflicts": vacations_with_conflicts,
        "is_manager": is_manager,
    }
    return render(request, "approveTimeOff.html", context)


@login_required(login_url="/accounts/login/")
def manager_approve_overtime_view(request):
    """
    Handles the overtime approval process for managers.

    This view allows a manager to review and approve or deny overtime requests submitted by employees in their department.
    The view displays unapproved overtime requests and allows the manager to either approve or deny each request.

    The view performs several tasks:
    - Ensures the user is a manager. If not, they are redirected to the employee page.
    - Retrieves the staff in the manager's department and displays unapproved overtime requests.
    - Allows the manager to approve or deny overtime requests. If a request is denied, no overtime hours are added to the employee's balance.

    Parameters:
    - request: The HTTP request object that contains the POST data with the form submission.

    Returns:
    - A rendered overtime approval form with a list of unapproved overtime requests.
    - After a POST request, it redirects back to the same page to display the updated list of unapproved overtime requests.

    Actions:
    - Approving overtime: Marks the overtime as approved and adds the requested overtime hours to the employee's balance.
    - Denying overtime: Marks the overtime as denied, and no overtime hours are added to the employee's balance.

    Validation errors include:
    - None in this view, but the logic ensures that only managers can access the overtime approval process.
    """
    user = request.user
    user_id = user.id
    user1 = Staff.objects.get(user_id=user_id)
    is_manager = user1.getIsManager()
    if not is_manager:
        return redirect("employee")
    dept = user1.dept
    staff = Staff.objects.filter(dept=dept).filter(is_employee=True)
    unapproved_overtime = (
        Overtime.objects.filter(dept=dept)
        .filter(request_submitted=True)
        .filter(is_employee=True)
        .filter(request_approved=False)
        .filter(request_denied=False)
        .order_by("name")
    )
    if request.method == "POST":
        overtime = request.POST.dict()
        overtime_keys = list(overtime.keys())
        overtime_id = overtime_keys[1]
        if overtime_id.startswith("Deny"):
            overtime_id = overtime_id.split(" ", 1)[1]
            approved_overtime = Overtime.objects.get(id=overtime_id)
            approved_overtime.request_denied = True
            approved_overtime.save()
            unapproved_overtime = (
                Overtime.objects.filter(dept=dept)
                .filter(request_submitted=True)
                .filter(is_employee=True)
                .filter(request_approved=False)
                .filter(request_denied=False)
                .order_by("name")
            )
            return HttpResponseRedirect(request.path_info)
        else:
            approved_overtime = Overtime.objects.get(id=overtime_id)
            staff = approved_overtime.name
            ot_hours = approved_overtime.ot_hours
            staff.overtime_hours = staff.overtime_hours + ot_hours
            staff.save()
            approved_overtime.request_approved = True
            approved_overtime.save()
            unapproved_overtime = (
                Overtime.objects.filter(dept=dept)
                .filter(request_submitted=True)
                .filter(is_employee=True)
                .filter(request_approved=False)
                .filter(request_denied=False)
                .order_by("name")
            )
            return HttpResponseRedirect(request.path_info)

    context = {"unapproved_overtime": unapproved_overtime, "is_manager": is_manager}
    return render(request, "approveOT.html", context)


@login_required(login_url="/accounts/login/")
def manager_sick_days_view(request):
    """
    Handles the sick day approval process for managers.

    This view allows a manager to approve sick days for employees in their department.
    The manager selects an employee and enters the date for which the sick day is being requested.

    The view performs several tasks:
    - Ensures the user is a manager. If not, they are redirected to the employee page.
    - Retrieves the list of employees in the manager's department.
    - Allows the manager to submit a sick day request for an employee. If the request is valid, the sick day is recorded, and the employee is marked as being away for 8 hours.

    Parameters:
    - request: The HTTP request object that contains the POST data with the form submission.

    Returns:
    - A rendered sick day approval form listing employees in the manager's department.
    - After a POST request, it either approves the sick day and displays a success message or shows an error message if the sick day for the selected date has already been approved.

    Actions:
    - Approving a sick day: Marks the employee as being away for 8 hours on the requested sick day.
    - Preventing duplicate sick day requests: Ensures that an employee cannot be approved for the same sick day more than once.

    Validation errors include:
    - Preventing duplicate sick day approvals for the same employee on the same date.
    """
    user = request.user
    user_id = user.id
    user1 = Staff.objects.get(user_id=user_id)
    is_manager = user1.getIsManager()
    if not is_manager:
        return redirect("employee")
    manager = Manager.objects.get(name=user1)
    dept = user1.dept
    staff = Staff.objects.filter(dept=dept).filter(is_employee=True)
    if request.method == "POST":
        date = request.POST["sickday"]
        date_list = date.split("-")
        dict_post = request.POST.dict()
        staff1 = dict_post["Staff"].split(" ", 1)[0]
        sick_staff1 = User.objects.get(username=staff1)
        sick_staff = Staff.objects.get(user=sick_staff1)
        dept = sick_staff.dept
        sick_day_date = datetime.date(
            int(date_list[0]), int(date_list[1]), int(date_list[2])
        )
        count = (
            SickDays.objects.filter(name=sick_staff).filter(date=sick_day_date).count()
        )
        if count == 0:
            SickDays.objects.create(
                name=sick_staff,
                date=sick_day_date,
                dept=dept,
                total_hours_away=8,
                approved_by=manager,
            )
            messages.success(request, "Sick Day is approved.")
            context = {"staff": staff}
            return render(request, "approveSickDay.html", context)
        else:
            messages.error(
                request, "Sick day for this employee already approved for this date."
            )
    context = {"staff": staff, "is_manager": is_manager}
    return render(request, "approveSickDay.html", context)


@login_required(login_url="/accounts/login/")
def deptstats_view(request):
    """
    Displays department statistics for the company owner.

    This view provides an overview of the current staffing situation for each department,
    excluding Human Resources. It shows the total number of staff, the number of staff on vacation,
    the number of staff on sick leave, and how many staff are present. It also flags if the
    present staff is below the department's minimum required staff level.

    The view performs several tasks:
    - Ensures the user is the company owner. If not, they are redirected to the employee page.
    - Retrieves all departments except Human Resources.
    - Calculates various statistics for each department, including total staff, vacations, sick days,
      and whether the department is understaffed.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - A rendered department statistics page displaying the following for each department:
      total staff, vacations, sick days, present staff, and whether the department is understaffed.

    Statistics calculated:
    - Total staff: The number of employees in the department.
    - Vacations: The number of employees on vacation today.
    - Sick days: The number of employees on sick leave today.
    - Present staff: The number of employees present at work (not on vacation or sick leave).
    - Understaffed: A flag indicating whether the present staff is below the minimum required staff.
    """
    user = request.user
    user_id = user.id
    today = datetime.date.today()
    user1 = Staff.objects.get(user_id=user_id)
    is_owner = user1.getIsOwner()
    if not is_owner:
        return redirect("employee")
    depts = Dept.objects.all().exclude(name="Human Resources")
    deptstats = []
    for dept in depts:
        deptinfo = []
        deptinfo.append(dept)
        total_staff = Staff.objects.filter(dept=dept).filter(is_employee=True).count()
        deptinfo.append(total_staff)
        vacations = (
            Vacations.objects.filter(dept=dept)
            .filter(request_approved=True)
            .filter(
                Q(start_date__lte=datetime.date.today())
                & Q(end_date__gte=datetime.date.today())
            )
            .count()
        )
        deptinfo.append(vacations)
        sickdays = (
            SickDays.objects.filter(dept=dept)
            .filter(date=datetime.date.today())
            .count()
        )
        deptinfo.append(sickdays)
        staff_present = total_staff - vacations - sickdays
        deptinfo.append(staff_present)
        if staff_present < dept.min_staff:
            deptinfo.append("Yes")
        else:
            deptinfo.append("No")
        deptstats.append(deptinfo)

    context = {"deptstats": deptstats, "is_owner": is_owner}
    return render(request, "deptstats.html", context)
