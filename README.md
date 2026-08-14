# Ecommerce API

A backend API for an ecommerce platform, built as a learning project to understand JWT authentication, relational data modeling, and third-party service integration (Stripe) in Python.

## Features

- **JWT Authentication** — signup, login, and password hashing with bcrypt
- **Products** — full CRUD, public browsing/search, admin-only create/update/delete
- **Shopping Cart** — add, update, and remove items, with automatic quantity merging for duplicate products
- **Checkout & Payments** — Stripe integration for real payment processing (test mode)
- **Role-based access control** — regular users vs. admin users, enforced via reusable auth dependencies

## Tech Stack

- **FastAPI** — web framework
- **SQLAlchemy** — ORM
- **SQLite** — database (dev)
- **python-jose** — JWT creation/decoding
- **bcrypt** — password hashing
- **Stripe** — payment processing
- **Pydantic** — request/response validation

## Data Model

```
User ──< Product (created_by)
User ──< Cart ──< CartItem >── Product
User ──< Order ──< OrderItem >── Product
```

- A `User` can be a regular user or an admin (`is_admin`)
- Each `User` has exactly one `Cart`
- A `Cart` holds many `CartItem` rows, each referencing a `Product` and a quantity
- Checkout converts a `Cart` into an `Order`, with `OrderItem` rows storing a frozen `price_at_purchase` so historical orders stay accurate even if product prices change later

## Getting Started

### 1. Clone and set up a virtual environment

```bash
git clone https://github.com/rudra485/ecommerce-api.git
cd ecommerce-api
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```
SECRET_KEY=your-long-random-secret-string
STRIPE_SECRET_KEY=sk_test_your_stripe_test_key
```

Get a free Stripe test key from the [Stripe dashboard](https://dashboard.stripe.com/test/apikeys) — no business verification needed for test mode.

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

Visit **http://127.0.0.1:8000/docs** for the interactive Swagger UI — every endpoint can be tested directly from the browser.

### 5. (Optional) Promote a user to admin

Admin access can't be granted through the API by design — it's set directly in the database:

```bash
python make_admin.py
```

Edit the email inside the script first to match the user you want to promote.

## API Overview

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/auth/signup` | Public | Create a new user account |
| POST | `/auth/login` | Public | Log in, receive a JWT access token |
| GET | `/products/` | Public | List/search products |
| GET | `/products/{id}` | Public | Get a single product |
| POST | `/products/` | Admin only | Create a product |
| PUT | `/products/{id}` | Admin only | Update a product |
| DELETE | `/products/{id}` | Admin only | Delete a product |
| GET | `/cart/` | Authenticated | View your cart |
| POST | `/cart/items` | Authenticated | Add an item to your cart |
| PUT | `/cart/items/{id}` | Authenticated | Update item quantity |
| DELETE | `/cart/items/{id}` | Authenticated | Remove an item |
| POST | `/orders/checkout` | Authenticated | Convert cart into an order, create a Stripe PaymentIntent |
| POST | `/orders/webhook` | Stripe only | Confirms payment and marks an order as paid |

## What This Project Demonstrates

- Password hashing and JWT-based authentication, including a chained dependency system for protecting and admin-gating routes
- A relational data model with foreign keys, one-to-one and one-to-many relationships, and join tables
- Defense-in-depth validation (database constraints backing up application-level checks)
- Real third-party API integration (Stripe) including the security reasoning behind webhook-based payment confirmation

## Possible Next Steps

- Alembic migrations instead of `create_all()`
- Refresh tokens
- Order history endpoint
- PostgreSQL in place of SQLite
- Automated tests with pytest
