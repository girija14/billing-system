# Billing System

A production-ready billing system built with **FastAPI**, **SQLAlchemy**, and **SQLite** (easily switchable to **PostgreSQL**).

## Features

- **Product Management** – Full CRUD for products (name, product ID, stock, price, tax %)
- **Billing Page (Page 1)** – Dynamic product rows, shop denomination counts, cash payment input
- **Bill Generation (Page 2)** – Calculates totals, taxes, rounded-down net price, balance, and optimal change denomination
- **Async Invoice Email** – Sends invoice to customer email in the background using FastAPI `BackgroundTasks`
- **Purchase History** – Search by customer email, view all past purchases, drill into line-item details

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x |
| Database | SQLite (default) / PostgreSQL |
| Templating | Jinja2 |
| Server | Uvicorn |

## Project Structure

```
billing_system/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app & startup
│   ├── config.py                # Environment configuration
│   ├── database.py              # Engine, session, Base
│   ├── models.py                # SQLAlchemy models
│   ├── routes/
│   │   ├── products.py          # Product CRUD routes
│   │   ├── billing.py           # Billing page routes
│   │   └── history.py           # Purchase history routes
│   ├── services/
│   │   ├── billing_service.py   # Bill processing logic
│   │   ├── email_service.py     # Invoice email sender
│   │   └── denomination_service.py  # Change calculation (greedy)
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── billing/
│   │   ├── products/
│   │   └── history/
│   └── static/
│       ├── css/style.css
│       └── js/billing.js
├── seed_data.py                 # Database seeder
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup & Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd billing_system
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Copy the example env file:

```bash
cp .env.example .env       # macOS/Linux
copy .env.example .env      # Windows
```

**SQLite (default – no extra setup):**
```
DATABASE_URL=sqlite:///./billing.db
```

**PostgreSQL:**
```
DATABASE_URL=postgresql://username:password@localhost:5432/billing_db
```
> Create the PostgreSQL database first: `createdb billing_db`

**Email (optional):**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
```
> If SMTP is not configured, invoices are logged to the console instead.

### 5. Seed the database

```bash
python seed_data.py
```

This creates 8 sample products and initialises shop denominations (500, 50, 20, 10, 5, 2, 1).

### 6. Run the application

```bash
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000** in your browser.

## Usage

| URL | Page |
|-----|------|
| `/` | Redirects to Billing |
| `/billing/` | **Billing Page 1** – create a new bill |
| `/products/` | **Product CRUD** – add / edit / delete products |
| `/history/` | **Purchase History** – search by email |

### Billing Workflow

1. Enter customer email
2. Add products with quantities (click **Add New** for more rows)
3. Review / update shop denomination counts
4. Enter cash paid by customer
5. Click **Generate Bill** → Page 2 shows the complete bill with balance denomination
6. Invoice is sent to the customer email in the background

## Assumptions

1. **Denominations**: 500, 50, 20, 10, 5, 2, 1 (Indian Rupee denominations)
2. The denomination counts on the billing page reflect the shop's current register state
3. After giving change, the shop's denomination inventory is reduced accordingly
4. Product stock is deducted upon bill generation
5. Net price is **rounded down** (floor) to the nearest integer for cash transactions
6. Balance change is calculated using a **greedy algorithm** (largest denomination first)
7. If SMTP is not configured, invoice details are logged to console (no email sent)

## API Documentation

FastAPI auto-generates interactive API docs:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
