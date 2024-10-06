import datetime
from .models import Allowed_vacation


def vacation_days_used(start_date, end_date):
    """
    Calculates the total vacation hours used between two dates.

    This function determines the number of working days (Monday to Friday) between the given start
    and end dates and returns the total number of vacation hours used. Each working day counts as 8 hours.

    The function performs the following tasks:
    - If the start and end dates are the same, it returns 8 hours.
    - Calculates the total number of days between the start and end dates.
    - Filters out weekends (Saturday and Sunday) to count only working days.
    - Multiplies the number of working days by 8 to return the total vacation hours.

    Parameters:
    - start_date: The start date of the vacation.
    - end_date: The end date of the vacation.

    Returns:
    - The total number of vacation hours used, with each working day counting as 8 hours.
    """

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


def valid_date_range(start_date, end_date):
    """
    Validates whether a given date range is valid.

    This function checks if the start and end dates form a valid range. A valid date range must satisfy the following conditions:
    - The start date must not be after the end date.
    - Both the start and end dates must be today or in the future.

    The function performs the following checks:
    - Ensures the start date is not later than the end date.
    - Ensures both the start and end dates are not in the past.

    Parameters:
    - start_date: The beginning of the date range.
    - end_date: The end of the date range.

    Returns:
    - True if the date range is valid.
    - False if the date range is invalid.
    """

    today = datetime.date.today()
    if start_date > end_date:
        return False
    if start_date < today or end_date < today:
        return False
    return True


def annual_vacation(user):
    """
    Calculates the annual vacation hours a user is entitled to based on their years of employment.

    This function determines how many vacation hours a user qualifies for by checking the number of years they have been employed.
    The function compares the user's employment anniversary date with the current date to calculate the total years employed.
    It then matches this with the allowed vacation hours for each year of employment from the `Allowed_vacation` model.

    The function performs the following tasks:
    - Calculates the number of years the user has been employed by comparing today's date with their anniversary date.
    - Iterates through all available vacation allowances and determines the maximum vacation hours the user qualifies for based on their years of service.

    Parameters:
    - user: The user for whom the vacation hours are being calculated.

    Returns:
    - The number of vacation hours the user is entitled to for the current year.
    """

    vacations = Allowed_vacation.objects.all()
    today = datetime.date.today()
    anniversary_date = user.anniversary_date
    vacation_qualify = int((today - anniversary_date).days / 365)
    allowed_hours = 0
    for vacation in vacations:
        if vacation_qualify >= vacation.years_employed:
            allowed_hours = vacation.annual_vacation_hours
    return allowed_hours


def calculate_overtime_hours(hours):
    """
    Calculates the overtime hours based on the total number of hours worked.

    This function calculates the overtime pay rate based on the number of hours worked beyond 8 hours in a day.
    It applies 1.5x the normal rate for hours worked up to 12 hours, and 2x the normal rate for any hours worked beyond 12 hours.

    The function performs the following tasks:
    - Adds 8 hours to the provided hours to account for a standard workday.
    - If the total hours worked are 12 or less, it calculates overtime at 1.5x the regular rate.
    - If the total hours exceed 12, it calculates the first 4 overtime hours at 1.5x the regular rate and any additional hours at 2x the regular rate.

    Parameters:
    - hours: The number of hours worked beyond the standard 8-hour workday.

    Returns:
    - The calculated overtime hours, applying the appropriate rate for regular overtime and double-time.
    """

    total_hours = hours + 8
    if total_hours <= 12:
        ot_hours = hours * 1.5
    else:
        double_time = total_hours - 12
        ot_hours = 1.5 * 4 + double_time * 2
    return ot_hours


def vacation_conflict(start, end, vacations, max_staff_off):
    """
    Checks for conflicts in vacation requests based on maximum allowable staff off.

    This function determines if there are any date conflicts in vacation requests by checking the number of employees
    scheduled to be off during a given period. It compares the requested vacation dates against existing vacation dates
    to see if the number of staff off on any day exceeds the maximum allowable staff off for the department.

    The function performs the following tasks:
    - Iterates over the range of days in the requested vacation period and initializes a count for each day.
    - Iterates over the existing vacations and increments the count for each day an employee is already scheduled off.
    - Identifies and returns a list of dates where the number of staff off exceeds the allowable limit.

    Parameters:
    - start: The start date of the requested vacation.
    - end: The end date of the requested vacation.
    - vacations: A queryset of existing vacation requests.
    - max_staff_off: The maximum number of staff allowed to be off on any given day.

    Returns:
    - A list of dates where the number of vacation requests exceeds the maximum allowable staff off.
    """

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


def list_of_conflicing_dates(requested_vacations, approved_vacations, max_staff_off):
    """
    Identifies conflicting dates between requested and approved vacations.

    This function checks each requested vacation against the list of approved vacations to determine if there are any conflicts,
    based on the maximum number of staff allowed to be off on the same day. It identifies any dates during the requested vacation period
    where the number of approved vacations would exceed the limit of staff off.

    The function performs the following tasks:
    - Iterates over each requested vacation.
    - Uses the `vacation_conflict` function to compare the requested vacation dates with the approved vacations.
    - Collects a list of dates where conflicts occur and associates them with the respective vacation request.

    Parameters:
    - requested_vacations: A queryset of vacation requests awaiting approval.
    - approved_vacations: A queryset of already approved vacation requests.
    - max_staff_off: The maximum number of staff allowed to be off on any given day.

    Returns:
    - A list of tuples, where each tuple contains a requested vacation and a list of conflicting dates.
    """

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
    """
    Ensures an employee can only apply for one vacation on a given date.

    This function checks if an employee has already applied for a vacation on any date within a requested vacation period.
    It compares the requested vacation dates against existing vacations to see if there is overlap, preventing the employee
    from applying for multiple vacations on the same date.

    The function performs the following tasks:
    - Iterates over the range of days in the requested vacation period and initializes a count for each day.
    - Iterates over the employee's existing vacation dates and increments the count for any overlapping days.
    - Returns True if the employee has already applied for a vacation on any date within the requested period.

    Parameters:
    - start: The start date of the requested vacation.
    - end: The end date of the requested vacation.
    - vacations: A queryset of the employee's existing vacation requests.

    Returns:
    - True if the employee has already applied for a vacation on any of the requested dates.
    - False if there are no conflicts with existing vacation requests.
    """

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


def update_vacations(staff, date):
    """
    Updates the vacation hours for staff based on the anniversary date.

    This function checks if a staff member's vacation hours need to be reset based on their annual update date.
    If the current date matches or exceeds the staff member's `update_on` date, the vacation usage is reset for the new year,
    and the staff member's `update_on` date is incremented by one year.

    The function performs the following tasks:
    - If the current date is on or after the `update_on` date and vacation hours have already been updated, it marks `updated_hours` as False.
    - If the current date is on or after the `update_on` date and vacation hours have not yet been updated, it increments the `update_on` date by one year,
      resets the vacation usage to zero, and marks `updated_hours` as True.

    Parameters:
    - staff: The staff member whose vacation hours are being updated.
    - date: The current date, used to check if the vacation update is due.

    Returns:
    - None. The function updates the staff member's record in the database directly.
    """

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
