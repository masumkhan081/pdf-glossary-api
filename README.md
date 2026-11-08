# PDF Glossary

A tool that helps readers upload a PDF and get a useful pre-reading glossary.

**Stack:** Django 5.2 · Django REST Framework · PostgreSQL · Next.js (frontend, planned)

---

## Quick Start (Windows PowerShell)

### 1. Activate the virtual environment

```powershell
Set-Location d:\0-STUDY\projects\pdf-glossary
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example and fill in your values:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set:

| Variable | Purpose | Example |
|---|---|---|
| `DJANGO_SECRET_KEY` | Cryptographic signing key | Pre-generated in `.env` |
| `DJANGO_DEBUG` | Enable debug mode | `True` for local dev |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames | `localhost,127.0.0.1` |
| `DATABASE_URL` | PostgreSQL connection string | See below |

#### Setting DATABASE_URL

Set your PostgreSQL connection string in `.env`:

```
# Supabase (Session Pooler)
DATABASE_URL=postgresql://postgres.vhxlznvlleaejuzeuzmv:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres

# Local PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/pdf_glossary
```

> **Note:** Connection URL options such as `sslmode=require` are supported and parsed automatically.

### 4. Run migrations

```powershell
python manage.py migrate
```

> Migrations require a working `DATABASE_URL`. Make sure you replace `[YOUR-PASSWORD]` with your actual password.

### 5. Start the development server

```powershell
python manage.py runserver
```

### 6. Verify the health endpoint

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health/
```

Expected output:

```
status
------
ok
```

> **Server liveness vs database readiness:** The health endpoint confirms the Django process is running. It does **not** verify the database connection. To confirm database readiness, run `python manage.py migrate --check`.

### 7. Run tests

```powershell
python manage.py test glossary --verbosity=2
```

Tests use `SimpleTestCase` and do not require a running database.

---

## Project Structure

```
pdf-glossary/
├── config/                  # Django project settings and root URL config
│   ├── settings.py          # Main settings (env-driven)
│   ├── urls.py              # Root URL routing
│   ├── wsgi.py
│   └── asgi.py
├── glossary/                # Main app
│   ├── services/
│   │   └── text_processing.py  # count_words() function
│   ├── views.py             # DRF API views (health endpoint)
│   ├── urls.py              # App URL routing
│   ├── models.py
│   ├── admin.py
│   └── tests.py
├── .env.example             # Template for environment variables
├── .gitignore
├── manage.py
└── requirements.txt
```
