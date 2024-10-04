from django.contrib import admin
from .models import (
    Division,
    Allowed_vacation,
    JobTitle,
    Dept,
    Staff,
    Manager,
    Owner,
    Vacations,
    Overtime,
    SickDays,
    LeaveOfAbsense,
)
from django.db.models.signals import post_delete
from django.dispatch import receiver


class DivisionAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


class AllowedVacationAdmin(admin.ModelAdmin):
    list_display = [
        "years_employed",
        "annual_vacation_hours",
    ]  # Fields to display in the list view
    search_fields = ["years_employed"]  # Enable search by years employed


class JobTitleAdmin(admin.ModelAdmin):
    list_display = ["title"]  # Display the title field in the list view
    search_fields = ["title"]  # Enable search by title


class DeptAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "division",
        "staff_num",
        "min_staff",
    ]  # Display fields in the list view
    search_fields = [
        "name",
        "division__name",
    ]  # Enable search by department name and division name
    list_filter = ["division"]  # Add a filter for divisions


class StaffAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "job_title",
        "dept",
        "anniversary_date",
        "vacation_used",
        "overtime_hours",
        "unpaid_time",
        "is_employee",
        "is_manager",
        "is_owner",
    ]  # Fields to display in the list view
    search_fields = [
        "user__username",
        "dept__name",
        "job_title__title",
    ]  # Enable search by user, department, and job title
    list_filter = [
        "dept",
        "job_title",
        "is_employee",
        "is_manager",
        "is_owner",
    ]  # Filters for the department, job title, and roles

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Check if the user is a manager
        if obj.is_manager:
            # If is_manager is checked, add the staff to the Manager model if not already present
            Manager.objects.get_or_create(name=obj, dept=obj.dept)
        else:
            # If is_manager is unchecked, remove the user from the Manager model if they exist
            Manager.objects.filter(name=obj).delete()

        # Check if the user is an owner
        if obj.is_owner:
            # If is_manager is checked, add the staff to the Manager model if not already present
            Owner.objects.get_or_create(name=obj)
        else:
            # If is_manager is unchecked, remove the user from the Manager model if they exist
            Owner.objects.filter(name=obj).delete()


class ManagerAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "dept",
        "approve_expense",
        "approve_any_staff",
    ]  # Fields to display in the list view
    search_fields = [
        "name__user__username",
        "dept__name",
    ]  # Enable search by manager's username and department name
    list_filter = [
        "approve_expense",
        "approve_any_staff",
    ]  # Filters for approval permissions


# Define the signal handler
@receiver(post_delete, sender=Manager)
def uncheck_is_manager(sender, instance, **kwargs):
    # Access the corresponding Staff object and uncheck is_manager
    staff = instance.name  # The 'name' field in Manager refers to the Staff instance
    if staff:
        staff.is_manager = False
        staff.save()  # Save the Staff object with is_manager unchecked


class OwnerAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "approve_expense",
        "approve_any_staff",
    ]  # Fields to display in the list view
    search_fields = ["name__user__username"]  # Enable search by owner's username
    list_filter = [
        "approve_expense",
        "approve_any_staff",
    ]  # Filters for approval permissions


# Define the signal handler for Owner
@receiver(post_delete, sender=Owner)
def uncheck_is_owner(sender, instance, **kwargs):
    staff = instance.name  # The 'name' field in Owner refers to the Staff instance
    if staff:
        staff.is_owner = False
        staff.save()  # Save the Staff object with is_owner unchecked


class VacationsAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "dept",
        "start_date",
        "end_date",
        "total_hours_away",
        "request_submitted",
        "request_approved",
        "request_denied",
        "approved_by",
    ]  # Fields to display in the list view
    search_fields = [
        "name__user__username",
        "dept__name",
        "approved_by__name__user__username",
    ]  # Enable search by staff name, department, and manager
    list_filter = [
        "dept",
        "is_employee",
        "request_approved",
        "request_denied",
    ]  # Add filters for department and approval status


class OvertimeAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "dept",
        "date",
        "ot_hours",
        "request_submitted",
        "request_approved",
        "request_denied",
        "approved_by",
    ]  # Fields to display in the list view
    search_fields = [
        "name__user__username",
        "dept__name",
        "approved_by__name__user__username",
    ]  # Enable search by staff name, department, and manager
    list_filter = [
        "dept",
        "request_approved",
        "request_denied",
    ]  # Add filters for department and approval status


class SickDaysAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "date",
        "dept",
        "total_hours_away",
        "hours_unpaid",
        "approved_by",
    ]  # Fields to display in the list view
    search_fields = [
        "name__user__username",
        "dept__name",
        "approved_by__name__user__username",
    ]  # Enable search by staff name, department, and manager
    list_filter = ["dept", "approved_by"]  # Add filters for department and manager


class LeaveOfAbsenseAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "date",
        "start_date",
        "end_date",
        "total_hours_away",
        "unpaid",
        "hours_unpaid",
        "approved_by",
    ]  # Fields to display in the list view
    search_fields = [
        "name__user__username",
        "approved_by__name__user__username",
    ]  # Enable search by staff name and manager
    list_filter = [
        "unpaid",
        "approved_by",
    ]  # Add filters for unpaid status and the manager who approved


admin.site.register(Division, DivisionAdmin)
admin.site.register(Allowed_vacation, AllowedVacationAdmin)
admin.site.register(JobTitle, JobTitleAdmin)
admin.site.register(Dept, DeptAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(Manager, ManagerAdmin)
admin.site.register(Owner, OwnerAdmin)
admin.site.register(Vacations, VacationsAdmin)
admin.site.register(Overtime, OvertimeAdmin)
admin.site.register(SickDays, SickDaysAdmin)
admin.site.register(LeaveOfAbsense, LeaveOfAbsenseAdmin)
