import datetime
from .models import Allowed_vacation


# returns number of vacation hours used excluding weekends
# This program does not account for stat holidays
def vacation_days_used(start_date, end_date):

    if start_date == end_date:
        return 8

    delta = end_date - start_date
    days_off = []
    for i in range(delta.days + 1):
        days_off.append(start_date + datetime.timedelta(days=i))

    holidays = []
    for days in days_off:
        if days.weekday() <= 4:
            holidays.append(days)

    return len(holidays) * 8


# ensures that a valid date range is given
def valid_date_range(start_date, end_date):
    today = datetime.date.today()
    if start_date > end_date:
        return False
    if start_date < today or end_date < today:
        return False
    return True


# calculates the number of vacation hours an employee is allowed
def annual_vacation(user):
    vacations = Allowed_vacation.objects.all()
    today = datetime.date.today()
    anniversary_date = user.anniversary_date
    vacation_qualify = int((today - anniversary_date).days / 365)
    allowed_hours = 0
    for vacation in vacations:
        if vacation_qualify >= vacation.years_employed:
            allowed_hours = vacation.annual_vacation_hours
    return allowed_hours


# calculates overtime employee is entitled to
def calculate_overtime_hours(hours):

    total_hours = hours + 8
    if total_hours <= 12:
        ot_hours = hours * 1.5
    else:
        double_time = total_hours - 12
        ot_hours = 1.5 * 4 + double_time * 2
    return ot_hours


# This function returns all the conflicting dates an
# unapproved vacation has with all approved vacations
def vacation_conflict(start, end, vacations, max_staff_off):
    start = start
    end = end

    delta = end - start
    dict1 = {}
    for i in range(delta.days + 1):
        day = start + datetime.timedelta(days=i)
        dict1[day] = 0

    for vacation in vacations:
        start = vacation.start_date
        end = vacation.end_date
        delta = end - start

        list1 = []
        for i in range(delta.days + 1):
            day = start + datetime.timedelta(days=i)
            list1.append(day)

        for item in list1:
            if item in dict1:
                dict1[item] += 1

    conflicts = [k for k, v in dict1.items() if int(v) >= max_staff_off]

    return conflicts


# returns a list of tuples of vaction request and its conflicting
# date with approved holidays
def list_of_conflicing_dates(requested_vacations, approved_vacations, max_staff_off):
    request_with_conflicts = []
    if len(requested_vacations) == 0:
        return []

    for requested_vacation in requested_vacations:
        vacation = requested_vacation
        start = vacation.start_date
        end = vacation.end_date

        conflicts = vacation_conflict(start, end, approved_vacations, max_staff_off)
        request_with_conflicts.append((requested_vacation, conflicts))

    return request_with_conflicts


def only_apply_for_one_vacation_date(start, end, vacations):
    start = start
    end = end

    delta = end - start
    dict1 = {}
    for i in range(delta.days + 1):
        day = start + datetime.timedelta(days=i)
        dict1[day] = 0

    for vacation in vacations:
        start1 = vacation.start_date
        end1 = vacation.end_date
        delta = end1 - start1

        list1 = []
        for i in range(delta.days + 1):
            day = start1 + datetime.timedelta(days=i)
            list1.append(day)

        for item in list1:
            if item in dict1:
                dict1[item] += 1

    return 1 in dict1.values()


def add_year(date):
    return date.replace(year=date.year + 1)


# updates a employees holidays on their anniversary year
def update_vacations(staff, date):
    if date >= staff.update_on and staff.updated_hours == True:
        staff.updated_hours = False
        staff.save()

    if date >= staff.update_on and staff.updated_hours == False:
        staff.update_on = add_year(staff.update_on)
        staff.save()
        staff.vacation_used = 0
        staff.save()
        staff.updated_hours == True
        staff.save()
    return
