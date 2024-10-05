from django.urls import resolve, reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.models import Q
import datetime

from .views import time_off_request_view

from .utils import (
    vacation_days_used,
    valid_date_range,
    annual_vacation,
    calculate_overtime_hours,
    vacation_conflict,
    only_apply_for_one_vacation_date,
    add_year,
    update_vacations,
)

from .models import (
    Division,
    Allowed_vacation,
    JobTitle,
    Manager,
    Dept,
    Staff,
    Owner,
    Vacations,
)


class EntryModelTest(TestCase):

    def setUp(self):
        User = get_user_model()
        User.objects.create(username="al", email="al@gmail.com", password="1234")
        User.objects.create(username="nancy", email="al@gmail.com", password="1234")
        div = Division.objects.create(name="Widget, Inc.")
        JobTitle.objects.create(title="Controller")
        JobTitle.objects.create(title="Accounting Clerk")
        Allowed_vacation.objects.create(years_employed=1, annual_vacation_hours=80)
        Allowed_vacation.objects.create(years_employed=3, annual_vacation_hours=120)
        Dept.objects.create(name="Accounting", division=div, staff_num=4, min_staff=2)
        Dept.objects.create(name="Purchasing", division=div, staff_num=4, min_staff=3)

    def test_division(self):
        entry = Division(name="Widget Inc.")
        self.assertEqual(str(entry), entry.name)

    def test_vacation_days(self):
        entry = Allowed_vacation(years_employed=1, annual_vacation_hours=80)
        self.assertEqual(entry.annual_vacation_hours, 80)
        self.assertEqual(entry.years_employed, 1)

    def test_vacation_days(self):
        User = get_user_model()
        entry = Allowed_vacation(years_employed=1, annual_vacation_hours=80)
        date = datetime.date(2022, 10, 20)
        user = User.objects.get(username="al")
        staff = Staff.objects.create(user=user, anniversary_date=date)
        today = datetime.date.today()
        vacations = Allowed_vacation.objects.all()
        vacation_qualify = int((today - user.staff.anniversary_date).days / 365)
        allowed_hours = 0
        for vacation in vacations:
            if vacation_qualify >= vacation.years_employed:
                allowed_hours = vacation.annual_vacation_hours
        self.assertEqual(vacation_qualify, entry.years_employed),
        self.assertEqual(allowed_hours, 80)
        self.assertEqual(staff.vacation_used, 0)

    def test_user_profile(self):
        User = get_user_model()
        user = User.objects.get(username="al")
        date = datetime.datetime(2020, 5, 17)
        staff = Staff.objects.create(user=user, anniversary_date=date)
        staff.anniversary_date = date
        self.assertEqual(user.username, "al")
        self.assertEqual(staff.anniversary_date, datetime.datetime(2020, 5, 17, 0, 0))

    def test_mangager(self):
        User = get_user_model()
        user = User.objects.get(username="al")
        user1 = user1 = Staff.objects.create(user=user, is_manager=True)
        dept = Dept.objects.get(name="Accounting")
        employee = user1.getIsEmployee()
        owner = user1.getIsOwner()
        manager = user1.getIsManager()
        manager1 = Manager(name=user1, dept=dept)
        self.assertEquals(employee, False)
        self.assertEquals(owner, False)
        self.assertEquals(manager, True)
        self.assertEqual(manager1.name.user.username, "al")
        self.assertEqual(manager1.dept.name, "Accounting")
        self.assertEqual(manager1.approve_expense, False)
        self.assertEqual(manager1.approve_any_staff, False)

    def test_employee(self):
        User = get_user_model()
        user = User.objects.get(username="al")
        user_id = user.id
        staff = Staff.objects.create(user=user)
        staff.is_employee = True
        employee = staff.getIsEmployee()
        owner = staff.getIsOwner()
        manager = staff.getIsManager()
        user1 = Staff.objects.get(user_id=user_id)
        user1.dept = Dept.objects.get(name="Accounting")
        user1.title = JobTitle.objects.get(title="Accounting Clerk")
        self.assertEquals(employee, True)
        self.assertEquals(owner, False)
        self.assertEquals(manager, False)
        self.assertEquals(user1.user.username, "al")
        self.assertEquals(user1.dept.name, "Accounting")
        self.assertEquals(user1.title.title, "Accounting Clerk")

    def test_conflicting_holidays(self):
        User = get_user_model()
        user = User.objects.get(username="nancy")
        user1 = Staff.objects.create(user=user)
        user1.dept = Dept.objects.get(name="Purchasing")
        dept = user1.dept
        start = datetime.date(2020, 1, 2)
        end = datetime.date(2020, 1, 4)
        start1 = datetime.date(2020, 1, 7)
        end1 = datetime.date(2020, 1, 10)
        Vacations.objects.create(name=user1, dept=dept, start_date=start, end_date=end)
        Vacations.objects.create(
            name=user1, dept=dept, start_date=start1, end_date=end1
        )
        request_start = datetime.date(2020, 1, 4)
        request_end = datetime.date(2020, 1, 8)
        vacations = Vacations.objects.filter(
            Q(start_date__lte=request_start) | Q(start_date__lte=request_end)
        )
        conflict = vacation_conflict(request_start, request_end, vacations, 1)
        self.assertEqual(
            conflict,
            [
                datetime.date(2020, 1, 4),
                datetime.date(2020, 1, 7),
                datetime.date(2020, 1, 8),
            ],
        )
        conflict = vacation_conflict(request_start, request_end, vacations, 2)
        self.assertEqual(conflict, [])

    def test_two_holidays_same_date(self):
        User = get_user_model()
        user = User.objects.get(username="nancy")
        user1 = Staff.objects.create(user=user)
        user1.dept = Dept.objects.get(name="Purchasing")
        dept = user1.dept
        start = datetime.date(2020, 1, 2)
        end = datetime.date(2020, 1, 4)
        Vacations.objects.create(name=user1, dept=dept, start_date=start, end_date=end)
        request_start = datetime.date(2020, 1, 4)
        request_end = datetime.date(2020, 1, 8)
        vacations = Vacations.objects.filter(name=user1)
        conflict = only_apply_for_one_vacation_date(
            request_start, request_end, vacations
        )
        self.assertEquals(conflict, True)

    #########################
    # Helper function tests #
    #########################
    def test_vacation_days(self):
        start = datetime.date(2019, 12, 23)
        end = datetime.date(2020, 1, 7)
        days = vacation_days_used(start, end)
        self.assertEquals(days, 96)

    def test_single_vacation_day(self):
        start = datetime.date(2019, 12, 1)
        end = datetime.date(2019, 12, 1)
        days = vacation_days_used(start, end)
        self.assertEquals(days, 8)

    def test_valid_vacation_date(self):
        start_date = datetime.date(2024, 12, 31)
        end_date = datetime.date(2025, 1, 5)
        is_valid = valid_date_range(start_date, end_date)
        self.assertEquals(is_valid, True)

    def test_get_employee_holiday_requests(self):
        User = get_user_model()
        user = User.objects.get(username="al")
        user1 = Staff.objects.create(user=user)
        start = datetime.date(2019, 12, 23)
        end = datetime.date(2019, 12, 27)
        Vacations.objects.create(name=user1, start_date=start, end_date=end)
        employee_vac = Vacations.objects.filter(name=user1).filter(
            request_submitted=True
        )
        self.assertEquals(employee_vac[0].start_date, start)

    def test_get_employee_holiday_requests_by_dept(self):
        User = get_user_model()
        user1 = User.objects.get(username="al")
        user2 = User.objects.get(username="nancy")
        staff1 = Staff.objects.create(user=user1)
        staff2 = Staff.objects.create(user=user2)
        staff1.dept = Dept.objects.get(name="Accounting")
        staff1.save()
        staff2.dept = Dept.objects.get(name="Purchasing")
        staff2.save()
        start = datetime.date(2019, 12, 23)
        end = datetime.date(2019, 12, 27)
        dept_name = staff2.dept
        Vacations.objects.create(
            name=staff1, dept=staff1.dept, start_date=start, end_date=end
        )
        Vacations.objects.create(
            name=staff2, dept=staff2.dept, start_date=start, end_date=end
        )
        employee_vac = Vacations.objects.filter(request_submitted=True).filter(
            dept=dept_name
        )
        self.assertEquals(employee_vac[0].name.user.username, "nancy")

    def test_overtime_time_and_a_half(self):
        ot_request = 4
        overtime = calculate_overtime_hours(ot_request)
        self.assertEquals(overtime, 6)

    def test_overtime_double_time(self):
        ot_request = 8
        overtime = calculate_overtime_hours(ot_request)
        self.assertEquals(overtime, 14)

    def test_update_anniversary_year(self):
        User = get_user_model()
        user = User.objects.get(username="nancy")
        staff = Staff.objects.create(
            user=user,
            vacation_used=35,
            anniversary_date=datetime.date(2019, 11, 1),
            update_on=datetime.date(2020, 11, 1),
        )
        staff.save()
        date = datetime.date(2020, 12, 7)
        update_vacations(staff, date)
        self.assertEquals(staff.vacation_used, 0)
        self.assertEquals(staff.update_on, datetime.date(2021, 11, 1))
        staff.vacation_used = 35
        staff.save()
        date = datetime.date(2020, 12, 23)
        update_vacations(staff, date)
        self.assertEquals(staff.vacation_used, 35)
