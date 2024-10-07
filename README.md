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

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/alasdare2011/HRAssist.git
2. Navigate to the project directory:
   ```bash
   cd hrassist
   
## Using Docker for Development

This project uses Docker containers to simplify development and setup.
1. Ensure Docker is installed and running on your machine.
2. Build and run the Docker containers:
   ```bash
   docker-compose up --build
3. The application should now be accessible at http://127.0.0.1:8000.
4. To run migrations inside the Docker container:
   ```bash
   docker-compose exec web python manage.py migrate
5. To create a superuser inside the Docker container:
   ```bash
   docker-compose exec web python manage.py createsuperuser

## Usage

- **Employees** can:
    - Submit overtime and vacation requests.
    - Log on to check their available overtime and vacation hours.
    - View their approved, unapproved, and denied vacation requests.
- **Managers** can approve or deny requests and track sick days.
- **Owners** can view department statistics, including:
    - Total staff, employees on vacation, employees sick, and staff present.
    - Alerts when departments are understaffed based on preset minimum staffing levels.
- **HR** can:
    - Manage employee accounts through Django’s admin interface.
    - Approve new holiday hours on an employee's anniversary date.
    - Deduct any unpaid time off requests from payroll.
- **Automatic Vacation Calculation**: The system automatically calculates additional vacation hours
   based on how many years an employee has worked for the company.
- **New Employee Notifications**: When a new employee is added to the system, an automated email is sent using Mailgun.

## Technologies

- **Django**: Backend framework.
- **Bootstrap**: Frontend styling for a responsive interface.
- **Crispy Forms**: Enhanced form handling.
- **PostgreSQL**: Recommended for database use (optional).
- **Mailgun**: For sending email notifications to new employees when their accounts are created.
- **Docker**: For containerized development.
