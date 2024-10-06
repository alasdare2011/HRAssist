from employee_time_management.models import Staff


def staff_context(request):
    if request.user.is_authenticated:
        try:
            staff = Staff.objects.get(user=request.user)
            return {
                "is_employee": staff.is_employee,
                "is_manager": staff.is_manager,
                "is_owner": staff.is_owner,
                "is_super": request.user.is_superuser,
            }
        except Staff.DoesNotExist:
            return {}
    return {}
