from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import datetime


def one_year_from_today():
    date = datetime.date.today()
    return date.replace(year=date.year + 1)


class Division(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"{self.name}"


class Allowed_vacation(models.Model):
    years_employed = models.IntegerField(unique=True)
    annual_vacation_hours = models.IntegerField()


class JobTitle(models.Model):
    title = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"{self.title}"


class Dept(models.Model):
    name = models.CharField(max_length=64, unique=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    staff_num = models.IntegerField(default=1)
    min_staff = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.name}"


class Staff(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    anniversary_date = models.DateField(
        auto_now=False,
        auto_now_add=False,
        default=datetime.date.today,
        null=True,
        blank=True,
    )
    update_on = models.DateField(default=one_year_from_today)
    updated_hours = models.BooleanField(default=True)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE, null=True, blank=True)
    job_title = models.ForeignKey(
        JobTitle, on_delete=models.CASCADE, null=True, blank=True
    )
    vacation_used = models.FloatField(default=0)
    overtime_hours = models.FloatField(default=0)
    unpaid_time = models.FloatField(default=0)
    is_employee = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} ({self.job_title}) in {self.dept} department"

    def getIsEmployee(self):
        return self.is_employee

    def getIsManager(self):
        return self.is_manager

    def getIsOwner(self):
        return self.is_owner


class Manager(models.Model):
    name = models.OneToOneField(Staff, on_delete=models.CASCADE)
    dept = models.OneToOneField(Dept, on_delete=models.CASCADE, null=True, blank=True)
    approve_expense = models.BooleanField(default=False)
    approve_any_staff = models.BooleanField(default=False)


class Owner(models.Model):
    name = models.ForeignKey(Staff, on_delete=models.CASCADE)
    approve_expense = models.BooleanField(default=True)
    approve_any_staff = models.BooleanField(default=True)


class Vacations(models.Model):
    name = models.ForeignKey(Staff, on_delete=models.CASCADE)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE, blank=True, null=True)
    start_date = models.DateField(auto_now=False, auto_now_add=False)
    end_date = models.DateField(auto_now=False, auto_now_add=False)
    is_employee = models.BooleanField(default=True)
    total_hours_away = models.FloatField(default=0)
    hours_unpaid = models.FloatField(default=0)
    overtime = models.FloatField(default=0)
    request_submitted = models.BooleanField(default=True)
    request_approved = models.BooleanField(default=False)
    request_denied = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        Manager, on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return f"{self.name} {self.start_date} to {self.end_date}"


class Overtime(models.Model):
    name = models.ForeignKey(Staff, on_delete=models.CASCADE)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField(auto_now=False, auto_now_add=False)
    ot_hours = models.FloatField(default=0)
    is_employee = models.BooleanField(default=True)
    request_submitted = models.BooleanField(default=True)
    request_approved = models.BooleanField(default=False)
    request_denied = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        Manager, on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return (
            f"{self.name.user.first_name} {self.name.user.last_name} requests "
            + f"{self.ot_hours} hours of overtime on {self.date}"
        )


class SickDays(models.Model):
    name = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField(auto_now=False, auto_now_add=False)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE, blank=True, null=True)
    total_hours_away = models.FloatField()
    hours_unpaid = models.FloatField(default=0)
    approved_by = models.ForeignKey(Manager, on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            "name",
            "date",
        )


class LeaveOfAbsense(models.Model):
    name = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField(auto_now=False, auto_now_add=False)
    start_date = models.DateField(auto_now=False, auto_now_add=False)
    end_date = models.DateField(auto_now=False, auto_now_add=False)
    total_hours_away = models.IntegerField()
    unpaid = models.BooleanField()
    hours_unpaid = models.FloatField(default=0)
    approved_by = models.ForeignKey(Manager, on_delete=models.CASCADE)
