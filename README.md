# VanaraFleetsOps — University Fleet Management System
North-Eastern University, Gombe

## Quick Setup (Local Development)

### 1. Prerequisites
- Python 3.10+
- MySQL 8.x running locally
- VS Code (recommended)

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create the MySQL database
Open MySQL Workbench or your MySQL client and run:
```sql
CREATE DATABASE vanara_fleets CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Configure database credentials
Open `VanaraFleetsOps/settings.py` and update the DATABASES block:
```python
'USER':     'your_mysql_username',
'PASSWORD': 'your_mysql_password',
```

### 6. Run migrations
```bash
python manage.py migrate
```

### 7. Create the first Super Admin account
```bash
python manage.py createsuperuser
```
When prompted, enter email, full name, and password.
Then open the Django shell and mark them as system admin:
```bash
python manage.py shell
>>> from accounts.models import User
>>> u = User.objects.get(email='your@email.com')
>>> u.is_system_admin = True
>>> u.save()
>>> exit()
```

### 8. Run the development server
```bash
python manage.py runserver
```
Visit: http://127.0.0.1:8000

---

## Project Structure
```
VanaraFleetsOps/        ← Django project config (settings, urls, wsgi)
accounts/               ← Department, Role, RoleModulePermission, User
vehicles/               ← Vehicle register
drivers/                ← Driver register
vendors/                ← Vendor register (fuel stations, mechanics)
coupons/                ← Fuel coupon issuance & lifecycle
fuel_logs/              ← Fuel transaction records (coupon redemption)
maintenance/            ← Maintenance & repair records
reports/                ← Report views (no models, queries other apps)
audit/                  ← Immutable audit log
templates/              ← Global HTML templates
static/                 ← CSS, JS, images
```

## Key Design Decisions
- No self-registration. All user accounts are created by Super Admin.
- Every user has one Role and one Department.
- Navbar items are rendered dynamically based on the user's role permissions.
- All data is manually entered — no real-time/sensor data collected.
- Odometer readings are NOT tracked anywhere in this system.
- Department scoping: users see only their department's data. Super Admin sees all.
