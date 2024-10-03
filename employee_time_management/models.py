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
    years_employed = models.IntegerField()
    annual_vacation_hours = models.IntegerField()


class JobTitle(models.Model):
    title = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.title}"


class Dept(models.Model):
    name = models.CharField(max_length=64)
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
