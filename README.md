# 💰 Personal Expense Tracker with Shared Expenses & Budget Insights

A full-stack Django web application for tracking personal and shared expenses, managing budgets, and getting spending insights.

---

## ✨ Features

- **User Authentication** — Register/Login with preferred currency
- **Expense Management** — Add, edit, delete, filter, search, paginate expenses
- **Budget Management** — Set monthly budgets per category with alerts
- **Dashboard** — Summary cards, category-wise spending, insights
- **Shared Expenses** — Split bills equally or manually among multiple users
- **Settlement System** — Partial payments, UPI simulation, history
- **Export** — Download expenses as CSV

---

## 🛠️ COMPLETE SETUP GUIDE (Step by Step)

---

### STEP 1 — Install Python

1. Download Python 3.10+ from https://www.python.org/downloads/
2. During installation on Windows, **check "Add Python to PATH"**
3. Verify:
   ```
   python --version
   ```

---

### STEP 2 — Install PostgreSQL

#### On Windows:
1. Download from https://www.postgresql.org/download/windows/
2. Run the installer (use default settings)
3. Set a **password** for the `postgres` user (remember this!)
4. Default port: `5432` — leave as is
5. After install, open **pgAdmin** (installed with PostgreSQL)

#### On macOS:
```bash
brew install postgresql@15
brew services start postgresql@15
```

#### On Ubuntu/Linux:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

---

### STEP 3 — Create the Database

#### Using pgAdmin (Windows — GUI method):
1. Open **pgAdmin 4** from Start Menu
2. Connect to your local server (enter your postgres password)
3. Right-click **Databases** → **Create** → **Database**
4. Name it: `expense_tracker_db`
5. Click **Save**

#### Using Terminal/Command Line (all platforms):

**Windows** — Open Command Prompt or PowerShell:
```cmd
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
```

**macOS/Linux:**
```bash
sudo -u postgres psql
```

Once inside the `psql` shell, run these commands:
```sql
CREATE DATABASE expense_tracker_db;
CREATE USER expense_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE expense_tracker_db TO expense_user;
\q
```

> ⚠️ Remember your database name, username, and password — you'll need them in Step 6.

---

### STEP 4 — Download & Extract the Project

1. Download the ZIP file
2. Extract it to a folder, e.g., `C:\Projects\expense_tracker\` or `~/projects/expense_tracker/`
3. Open a terminal/command prompt in that folder

---

### STEP 5 — Create a Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal line.

---

### STEP 6 — Configure Environment Variables

1. Copy the example file:
   ```bash
   # Windows:
   copy .env.example .env

   # macOS/Linux:
   cp .env.example .env
   ```

2. Open `.env` in any text editor (Notepad, VS Code, etc.) and fill in your values:

   ```
   SECRET_KEY=any-long-random-string-here-make-it-50-chars
   DEBUG=True
   DB_NAME=expense_tracker_db
   DB_USER=postgres
   DB_PASSWORD=your_postgres_password_here
   DB_HOST=localhost
   DB_PORT=5432
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

   > **DB_USER**: Use `postgres` (the default superuser) or `expense_user` if you created one in Step 3.
   > **DB_PASSWORD**: The password you set during PostgreSQL installation.

---

### STEP 7 — Install Python Dependencies

Make sure your virtual environment is active, then:

```bash
pip install -r requirements.txt
```

This installs Django, psycopg2 (PostgreSQL adapter), and other packages. May take 1–2 minutes.

---

### STEP 8 — Run Database Migrations

This creates all the tables in your PostgreSQL database:

```bash
python manage.py migrate
```

Expected output: a list of `OK` messages for each migration.

---

### STEP 9 — (Optional) Load Sample Data

Load demo users and sample expenses to explore the app immediately:

```bash
python manage.py load_sample_data
```

This creates:
- **alice@example.com** / `demo1234` — with expenses and budgets
- **bob@example.com** / `demo1234` — a participant in shared expenses

---

### STEP 10 — Create an Admin Account (Optional)

```bash
python manage.py createsuperuser
```

Follow prompts to set email and password. Access admin at http://127.0.0.1:8000/admin/

---

### STEP 11 — Run the Server

```bash
python manage.py runserver
```

Open your browser and go to: **http://127.0.0.1:8000**

You'll be redirected to the login page. Register a new account or use the demo accounts.

---

## 🔍 Troubleshooting

### "could not connect to server" (PostgreSQL not running)

**Windows:** Open Services → Find `postgresql-x64-15` → Start it
Or: `net start postgresql-x64-15`

**macOS:** `brew services start postgresql@15`

**Linux:** `sudo systemctl start postgresql`

---

### "password authentication failed"

- Double-check your `.env` file — `DB_PASSWORD` must match your PostgreSQL password
- If you forgot your postgres password, reset it:
  ```bash
  sudo -u postgres psql
  ALTER USER postgres PASSWORD 'newpassword';
  ```

---

### "database expense_tracker_db does not exist"

Run Step 3 again to create the database.

---

### "No module named 'psycopg2'"

Make sure your virtual environment is active and run:
```bash
pip install psycopg2-binary
```

---

### Port 8000 already in use

Use a different port:
```bash
python manage.py runserver 8080
```
Then open http://127.0.0.1:8080

---

## 📁 Project Structure

```
expense_tracker/
├── manage.py
├── requirements.txt
├── .env.example
├── .env                  ← You create this
│
├── expense_tracker/      ← Django project config
│   ├── settings.py
│   └── urls.py
│
├── accounts/             ← User auth (register, login)
├── expenses/             ← Personal expense management + dashboard
├── budgets/              ← Monthly budget management
├── shared_expenses/      ← Shared bills & settlements
│
└── templates/            ← All HTML templates
    ├── base.html
    ├── accounts/
    ├── expenses/
    ├── budgets/
    └── shared_expenses/
```

---

## 🌐 Application Pages

| URL | Page |
|-----|------|
| `/` | Redirects to Dashboard |
| `/accounts/register/` | Register |
| `/accounts/login/` | Login |
| `/dashboard/` | Main Dashboard |
| `/dashboard/expenses/` | Expense List |
| `/dashboard/expenses/add/` | Add Expense |
| `/budgets/` | Budget Management |
| `/shared/` | Shared Expenses |
| `/admin/` | Django Admin |

---

## 💡 Quick Tips

- Use **Export CSV** in the sidebar to download all your expenses
- Set budgets before adding expenses to get alerts
- For shared expenses, all users must be registered first
- The **UPI Pay** button simulates a payment (no real money involved)
