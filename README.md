# HRAssist

This is a Django application that helps managers handle overtime requests, time-off approvals, and sick day tracking for employees. Owners can also access department statistics to manage staffing levels effectively. The system integrates with Mailgun to send new employees a welcome message when their account is set up.

## Features

- **Overtime Requests**: Employees can submit overtime requests for approval.
- **Time Off Approvals**: Managers can review and approve or deny vacation requests.
- **Sick Day Tracking**: Managers can record and approve sick days.
- **Conflict Detection**: Automatically detects vacation date conflicts based on staffing levels.
- **Department Statistics**: Owners can view department-level stats to see which employees are present, on vacation, or sick, and receive alerts for any departments that are understaffed.
- **Email Notifications**: Automatically sends a welcome email to new employees via Mailgun when their account is set up.
- **Employee Self-Service**: Employees can log on to:
  - Check available overtime and vacation hours.
  - View their approved, unapproved, and denied vacation requests.
- **HR Account Management**: HR can:
  - Manage employee accounts via Django’s admin interface.
  - Approve new holiday hours on an employee's anniversary date.
  - Deduct any unpaid time off requests from payroll.
- **Automatic Vacation Calculation**: The program automatically calculates additional vacation hours based on the number of years an employee has worked for the company.
