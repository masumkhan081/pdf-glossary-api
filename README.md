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

> Migrations require a working `DATABASE_URL`.

### 5. Start the development server

```powershell
python manage.py runserver
```

---

## API Endpoints

### 1. Health Probe (`GET /api/v1/health/`)

Confirms that the Django server process is up and running.

```powershell
Invoke-RestMethod -Uri http://localhost:8000/api/v1/health/ -Method Get
```

Expected response:

```json
{
  "status": "ok"
}
```

> **Server liveness vs database readiness:** The health endpoint is a pure process liveness probe and does **not** query the database.

---

### 2. Text Analysis (`POST /api/v1/analyse-text/`)

Accepts a JSON payload containing raw text and returns total word count, unique word count, and frequency-sorted word counts.

> **Security Note:** This endpoint currently allows public access (`AllowAny`) as an unauthenticated local-development prototype. Any public deployment must add authentication, rate-limiting, and resource-abuse protection.

#### Request Format
- **Method:** `POST`
- **Content-Type:** `application/json`
- **Body:**
  ```json
  {
    "text": "Freedom, freedom! Books inspire."
  }
  ```

#### Response Format (`200 OK`)
Words are sorted by descending frequency count, then alphabetically ascending for ties:
```json
{
  "total_words": 4,
  "unique_words": 3,
  "words": [
    {"word": "freedom", "count": 2},
    {"word": "books", "count": 1},
    {"word": "inspire", "count": 1}
  ]
}
```

#### Input Limits & Validation
- **JSON Object:** Payload must be a JSON object containing the key `"text"`.
- **Strict String Type:** Non-string types (numbers, booleans, null, lists, objects) are rejected rather than coerced.
- **Non-Empty:** Missing, empty, or whitespace-only inputs are rejected with `HTTP 400`.
- **Character Limit:** Maximum 20,000 characters (the untrimmed input length is checked before trimming). Inputs exceeding 20,000 characters return `HTTP 400`.
- **No Words Error:** If the text contains no valid English words after filtering out numbers and underscores, returns `HTTP 400` with a text-field error (`"No valid words found in the submitted text."`).
- **HTTP Methods & Headers:** Malformed JSON returns `HTTP 400`, non-JSON content types return `HTTP 415`, and non-POST methods return `HTTP 405`.

#### Tokenizer Behavior & Limitations
- **English-Only:** Extracts ASCII alphabetic words (`a-z`) and normalises case.
- **Contractions:** Allows internal apostrophes for contractions (e.g. `"isn't"`, `"o'clock"`). Normalises curly apostrophes (`’`, `‘`) to straight apostrophes (`'`).
- **Separators:** Hyphens (`-`), en-dashes (`–`), and em-dashes (`—`) are treated as word separators (e.g. `"well-being"` → `"well"`, `"being"`).
- **Exclusions:** Entire digit-containing or underscore-containing tokens are excluded rather than partially extracting words from them (e.g. `"123 ___ abc123 some_variable"` → `{}`).
- **Limitations:** This is a basic English tokenizer. It does **not** perform stemming, lemmatization, stopword filtering, rarity ranking, or multilingual tokenisation.

#### PowerShell Examples

**Success Example:**
```powershell
$body = @{ text = "Freedom, freedom! Books inspire." } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/api/v1/analyse-text/ -Method Post -ContentType "application/json" -Body $body
```

**Invalid Input Example (Non-string type):**
```powershell
$body = @{ text = 123 } | ConvertTo-Json
try {
    Invoke-RestMethod -Uri http://localhost:8000/api/v1/analyse-text/ -Method Post -ContentType "application/json" -Body $body
} catch {
    $_.ErrorDetails.Message
}
```

**Invalid Input Example (No valid words):**
```powershell
$body = @{ text = "123 ___ abc123 some_variable" } | ConvertTo-Json
try {
    Invoke-RestMethod -Uri http://localhost:8000/api/v1/analyse-text/ -Method Post -ContentType "application/json" -Body $body
} catch {
    $_.ErrorDetails.Message
}
```

---

## Running Tests

```powershell
python manage.py test glossary --verbosity=2
```

Tests run with Django's test runner using `SimpleTestCase` without touching or requiring the database.

---

## Project Structure

```
pdf-glossary/
├── config/                  # Django project settings and root URL config
│   ├── settings.py          # Main settings (env-driven)
│   ├── urls.py              # Root URL routing (/admin/ and /api/v1/)
│   ├── wsgi.py
│   └── asgi.py
├── glossary/                # Main app
│   ├── services/
│   │   ├── __init__.py
│   │   └── text_processing.py  # English tokenizer & analyse_text service
│   ├── serializers.py       # Strict input validation serializer
│   ├── views.py             # DRF views: health & analyse_text_view
│   ├── urls.py              # App URL routing (health/ and analyse-text/)
│   ├── models.py
│   ├── admin.py
│   └── tests.py             # Unit & integration test suite (32 tests)
├── .env.example             # Template for environment variables
├── .gitignore
├── manage.py
└── requirements.txt
```
