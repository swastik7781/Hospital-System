# 🏥 Utkal Hospital & Medical Research Centre
### Enterprise Hospital & Clinic Management System (EHR / HMIS)

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel%20Production-0D9488.svg?style=for-the-badge&logo=vercel)](https://utkalhospital.vercel.app/)
[![API Docs](https://img.shields.io/badge/Swagger%20UI-Live%20Documentation-009688.svg?style=for-the-badge&logo=fastapi)](https://utkalhospital.vercel.app/docs)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0%20(async)-D71F00.svg)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1.svg?logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D.svg?logo=redis)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-5.3+-37814A.svg?logo=celery)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose%20Ready-2496ED.svg?logo=docker)](https://www.docker.com/)

A modern, production-grade Electronic Health Record (EHR) and Hospital Information Management System (HMIS) built for **Utkal Hospital & Medical Research Centre** (Niladri Vihar, Chandrasekharpur, Bhubaneswar, Odisha).

The platform features an asynchronous **FastAPI** backend, **SQLAlchemy 2.0 (async)** ORM, **PostgreSQL 16 / SQLite** storage, **Redis 7** caching, **Celery** background task automation, and a zero-framework responsive Single Page Application (SPA) styled with an enterprise medical aesthetic (Deep Teal `#0D9488`, slate typography, and clean card surfaces).

---

## 🌐 Live Production Links

| Resource | URL | Description |
| :--- | :--- | :--- |
| 🏥 **Web Portal** | [https://utkalhospital.vercel.app/](https://utkalhospital.vercel.app/) | Interactive Hospital Management Portal with 1-Click Role Switcher |
| 📖 **OpenAPI Docs** | [https://utkalhospital.vercel.app/docs](https://utkalhospital.vercel.app/docs) | Interactive Swagger UI API documentation and testing workbench |
| 📚 **ReDoc** | [https://utkalhospital.vercel.app/redoc](https://utkalhospital.vercel.app/redoc) | Clean, searchable reference documentation |
| 🩺 **System Health** | [https://utkalhospital.vercel.app/health](https://utkalhospital.vercel.app/health) | Real-time service uptime, versioning, and environment check |
| 🐙 **GitHub Repository** | [swastik7781/Hospital-System](https://github.com/swastik7781/Hospital-System.git) | Source code, automated tests, and deployment configurations |

---

## 📐 Architecture & System Workflow

```
+---------------------------------------------------------------------------------------------------+
|                                      CLIENT LAYER (SPA)                                           |
|     👑 Medical Superintendent  |  🩺 Doctors  |  📋 Receptionists  |  🧑‍🦽 Registered Patients        |
|     * 1-Click Login Gate       * Clinical EHR  * POS Billing (₹)    * PDF Prescription Download   |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
                                   HTTP / HTTPS / JSON (RESTful)
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                     FASTAPI ASGI GATEWAY                                          |
|  * PathNormalizationMiddleware (Vercel Serverless URL routing)                                    |
|  * CORS Security Middleware                                                                       |
|  * SlowAPI Rate Limiting (Memory / Redis)                                                         |
|  * Global Exception Handler with Structured Error JSON                                            |
|  * JWT Bearer Authentication & Strict Role-Based Access Control (RBAC)                            |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
         +----------------------------------------+---------------------------------------+
         |                                        |                                       |
         v                                        v                                       v
+------------------------+              +-------------------+                   +-------------------+
|     ROUTER MODULES     |              |   DOMAIN SERVICES |                   | BACKGROUND TASKS  |
|  - Auth & Security     |              |  - Slot Conflict  |                   |  - Celery Worker  |
|  - Patient Records     |              |  - 5% GST Calc    |                   |  - Celery Beat    |
|  - Doctor Schedules    | <----------> |  - FIFO Pharmacy  | <---------------> |  - 24h Reminders  |
|  - Appointments        |              |  - ReportLab PDF  |                   |  - Expiry Alerts  |
|  - Prescriptions       |              +-------------------+                   +---------+---------+
|  - Lab & Radiology     |                                                                |
|  - Billing & Invoices  |                                                                |
|  - Pharmacy Inventory  |                                                                |
|  - Analytics Dashboard |                                                                |
+-----------+------------+                                                                |
            |                                                                             |
            v                                                                             v
+---------------------------------------------------+                           +-------------------+
|             DATABASE ACCESS LAYER                 |                           |    REDIS BROKER   |
|   - SQLAlchemy 2.0 Async Session Pool             |                           |  - Queue Broker   |
|   - Lazy Schema Initialization (Serverless Safe)  |                           |  - Result Backend |
|   - Alembic Database Migrations                   |                           +-------------------+
+-------------------------+-------------------------+
                          |
                          v
+---------------------------------------------------+
|               PERSISTENCE ENGINES                 |
|  - PostgreSQL 16 (Render Cloud / Docker Compose)  |
|  - SQLite + aiosqlite (Local Dev / Vercel /tmp)   |
+---------------------------------------------------+
```

---

## 🛠️ Complete Technology Stack

### Backend & Core Framework
- **Python 3.11+**: Modern, typed Python runtime with `asyncio`.
- **FastAPI 0.110+**: High-performance ASGI framework with Pydantic v2 data validation and automatic OpenAPI/Swagger generation.
- **Uvicorn 0.28+**: Fast ASGI server with uvloop and httptools.
- **SlowAPI**: Token-bucket and sliding-window rate limiting (20/min on auth, 120/min standard) with Redis or in-memory fallback.

### Database & ORM
- **SQLAlchemy 2.0 (Async)**: Modern declarative mapping using `AsyncSession`, `select()`, and asynchronous connection pooling.
- **Alembic 1.13+**: Database schema migration and version control.
- **asyncpg 0.29+**: High-performance asynchronous driver for PostgreSQL.
- **aiosqlite 0.20+**: Asynchronous SQLite driver for local zero-config testing and Vercel serverless execution.
- **PostgreSQL 16**: Production-grade relational database for Render and Docker deployments.

### Authentication & Cryptography
- **python-jose 3.3+**: Cryptographic signing and decoding of JSON Web Tokens (Access + Refresh tokens).
- **Passlib & bcrypt 4.0.1**: Salted password hashing with built-in runtime compatibility monkey-patching for modern Python environments.
- **RBAC Dependency Guards**: FastAPI dependencies enforcing role constraints (`Admin`, `Doctor`, `Receptionist`, `Patient`).

### Background Automation & Caching
- **Redis 7**: High-speed message broker and caching layer.
- **Celery 5.3+**: Distributed asynchronous task execution (PDF compilation, notification dispatches).
- **Celery Beat**: Periodic task scheduler for automated 24-hour appointment reminders and 30-day medicine batch expiration monitors.

### Document Generation & Media
- **ReportLab 4.1+**: Vector graphics and PDF generation engine producing branded medical prescription letterheads.

### Frontend Application
- **Vanilla ES6+ JavaScript**: Lightweight, reactive Single Page Application with modular state management and zero build-step dependencies.
- **Custom CSS3 Design System**: Responsive grid, CSS variables, healthcare teal color palette (`#0D9488`), and accessible typography (`Inter` & `JetBrains Mono`).

### Deployment & Cloud Infrastructure
- **Vercel Serverless**: `@vercel/python` builder v2 with ASGI `PathNormalizationMiddleware`, absolute path asset mounting, and lazy database schema initialization.
- **Render Cloud**: Managed web service via `render.yaml` blueprint with persistent PostgreSQL.
- **Docker & Docker Compose**: Multi-container orchestration (FastAPI web, PostgreSQL 16, Redis 7, Celery Worker, Celery Beat).

---

## 💡 How Every Module Works (Clinical Workflows)

### 1. Authentication & Role-Based Access Control (RBAC)
- **Token Lifecycle**: Issues short-lived access tokens (60 minutes) and long-lived refresh tokens (7 days).
- **Password Security**: Passwords are never stored in plaintext; they are hashed with bcrypt using automatic salt generation.
- **Role Enforcement**: Every request to a protected endpoint runs through `get_current_user` and `require_role(...)`. Unauthorized attempts return clean `403 Forbidden` JSON responses.

### 2. Patient Intake & Electronic Health Records (EHR)
- **Patient Chart**: Stores complete demographic details, blood group (`A+`, `O-`, etc.), recorded drug/food allergies, chronic medical conditions, and emergency contacts.
- **Soft Deletion**: Patients are marked with `is_deleted=True` to preserve historical legal and medical audit records.
- **Unified Patient Dashboard**: Aggregates all visits, active prescriptions, pending lab orders, and unpaid invoices into a single summary call.

### 3. Doctor Management & Appointment Scheduling
- **Doctor Directory**: Associates doctors with clinical departments, qualifications (e.g. AIIMS, NIMHANS), experience, and consultation fees in Indian Rupees (₹).
- **Double-Booking Prevention**: Validates physician availability across 30-minute time slots to strictly prevent overlapping appointments.
- **Visit Lifecycle**: Tracks appointments through states: `scheduled` → `confirmed` → `in_progress` → `completed` (or `cancelled`).
- **Clinical Completion**: Completing an appointment logs diagnosis, doctor notes, and automatically generates the corresponding consultation invoice.

### 4. Prescriptions & Automated Medical PDF Generation
- **Dynamic Formulations**: Doctors prescribe multiple line items per order with medicine name, dosage, frequency (e.g., `1-0-1 after food`), duration, quantity, and clinical instructions.
- **ReportLab PDF Engine**: Endpoint `/api/v1/prescriptions/{id}/pdf` compiles and streams a high-resolution, printable medical prescription formatted with official hospital headers, patient demographics, and doctor signatures.

### 5. Diagnostic Laboratory & Radiology Management
- **Test Modalities**: Handles `blood_work`, `xray`, `mri`, `ct_scan`, `ultrasound`, and `biopsy`.
- **Abnormal & Critical Value Alerts**: Medical lab technicians can flag abnormal or life-threatening critical results with a boolean toggle, immediately surfacing urgent physician warnings on dashboards.
- **Report Attachment**: Supports uploading digital lab reports (PDF/JPG/PNG) stored locally or in `/tmp/hospital_uploads`.

### 6. Billing & Financial Management (₹ INR with 5% GST)
- **Itemized Invoicing**: Line items support consultation fees, laboratory diagnostics, nursing, room charges, and pharmacy supplies.
- **Automated Taxation**: Automatically calculates subtotals, item-level discounts, statutory **5% healthcare GST**, and net payable totals in Indian Rupees (₹).
- **Payment Tracking**: Tracks payment status (`unpaid`, `partially_paid`, `paid`, `refunded`) across payment modes: Cash Counter, Credit/Debit Card, UPI, and Insurance Claims.
- **Revenue Analytics**: Real-time revenue reporting broken down by daily, weekly, monthly, and all-time collections.

### 7. Pharmacy Inventory & FIFO Stock Control
- **Formulary Catalog**: Standardized medicine registry with generic salt composition, therapeutic category, packaging units, and reorder levels.
- **FIFO Batch Dispensation**: When dispensing medicine, the system prioritizes batches with the earliest expiry dates (**First-In, First-Out**), mitigating spoilage and stock loss.
- **Automated Stock Alerts**: Real-time endpoints query medicines currently below clinical reorder levels and batches expiring within 30 days.

### 8. Analytics & Role-Adaptive Dashboard
- **Role-Aware Views**: 
  - **Admin**: Total active patients, monthly revenue, active consultations, low stock warnings, 14-day visit trend chart, and audit feed.
  - **Doctor**: Today's scheduled visits, assigned clinical patients, pending lab reviews, and recent prescriptions.
  - **Receptionist**: Daily registrations, open appointment queues, and pending cashier invoices.
  - **Patient**: Personal appointments, active medication schedule, and billing history.

---

## 🔑 Demo Login Accounts

Pre-configured demo accounts are available for instant testing on both [Live Vercel](https://utkalhospital.vercel.app/) and local environments:

| Role | Email | Password | Personnel Name & Designation | Primary Permissions |
| :--- | :--- | :--- | :--- | :--- |
| 👑 **Admin** | `admin@hospital.com` | `admin123` | **Dr. Admin** *(Medical Superintendent)* | Full administrative control across all 11 modules, staff, & financials |
| 🩺 **Doctor** | `doctor@hospital.com` | `doctor123` | **Dr. Swastik Bhardwaj** *(Head of Cardiology)* | Patient charts, diagnosis, issue prescriptions, order lab tests |
| 📋 **Receptionist** | `receptionist@hospital.com` | `reception123` | **Pooja Sharma** *(Front Desk Manager)* | Register patients, book appointments, generate invoices, record payments |
| 🧑‍🦽 **Patient** | `patient@hospital.com` | `patient123` | **Ramesh Chandra Pradhan** *(Patient)* | View personal health history, consultations, download PDF prescriptions |

---

## 🛡️ Role-Based Access Control (RBAC) Matrix

| Endpoint Group | Admin | Doctor | Receptionist | Patient |
| :--- | :---: | :---: | :---: | :---: |
| **User Administration** (`/api/v1/users`) | ✅ Full Access | ❌ Self only | ❌ Self only | ❌ Self only |
| **Patient Directory** (`/api/v1/patients`) | ✅ Full Access | ✅ View / Update | ✅ Full Access | ❌ Self only |
| **Doctors & Schedules** (`/api/v1/doctors`) | ✅ Full Access | ✅ Edit Schedule | ✅ View only | ✅ View only |
| **Appointments** (`/api/v1/appointments`) | ✅ Full Access | ✅ Complete Visit | ✅ Full Access | ✅ Self booking |
| **Prescriptions & PDF** (`/api/v1/prescriptions`) | ✅ Full Access | ✅ Create / Update | ✅ View only | ✅ View Self & PDF |
| **Lab Tests & Radiology** (`/api/v1/lab-tests`) | ✅ Full Access | ✅ Order / Update | ✅ View only | ✅ View Self Results |
| **Billing & Invoices** (`/api/v1/billing`) | ✅ Full Access | ❌ View only | ✅ Create & Pay | ❌ Self Invoices |
| **Pharmacy & Batches** (`/api/v1/pharmacy`) | ✅ Full Access | ✅ Dispense | ✅ Stock In | ❌ Denied |
| **Executive Analytics** (`/api/v1/dashboard`) | ✅ Full Analytics | ✅ Clinical View | ✅ Frontdesk View | ✅ Patient Portal |

---

## 🚀 Deployment Architecture & How It Works

### Option 1: Vercel Serverless Deployment
The repository is engineered specifically for Vercel's Serverless Python runtime (`@vercel/python`):

1. **Routing (`vercel.json`)**: Configured with standard `@vercel/python` builds and catch-all routes:
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "api/index.py",
         "use": "@vercel/python",
         "config": {
           "includeFiles": ["static/**", "app/**", "scripts/**"]
         }
       }
     ],
     "routes": [{ "src": "/(.*)", "dest": "api/index.py" }]
   }
   ```
2. **Path Normalization Middleware**: Serverless rewrites can prefix incoming paths with `/api/index.py`. The custom `PathNormalizationMiddleware` in `app/main.py` normalizes `scope["path"]` before routing occurs.
3. **Absolute File Resolution**: Static assets (`static/app/index.html`, CSS, JS) and uploads are located using absolute directory references anchored to `__file__`, preventing working directory mismatches in Lambda environments.
4. **Lazy Database Initialization**: Serverless environments do not reliably trigger ASGI startup `lifespan` handlers. The `get_db()` dependency in `app/database.py` contains atomic lazy initialization that automatically generates database tables and seeds demo clinical records on the very first database call.

### Option 2: Render Cloud Deployment
Configured via `render.yaml` for automatic infrastructure provisioning:
- **Web Service**: Runs production Uvicorn ASGI behind Gunicorn workers on Linux.
- **Database**: Dedicated Render PostgreSQL instance.
- **Background Worker**: Dedicated Celery worker processing asynchronous jobs.

### Option 3: Local Zero-Config Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/swastik7781/Hospital-System.git
   cd Hospital-System
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   # macOS / Linux:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Seed the database with clinical demo data:
   ```bash
   python scripts/seed.py
   ```
5. Launch the development server:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
6. Open your browser:
   - **Frontend Application**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - **Swagger UI Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Option 4: Single-Command Docker Deployment
```bash
docker compose up -d --build
```
Spins up:
- `hospital_db`: PostgreSQL 16 on port `5432`
- `hospital_redis`: Redis 7 on port `6379`
- `hospital_web`: FastAPI web server on port `8000`
- `hospital_celery_worker`: Background task processor
- `hospital_celery_beat`: Periodic cron scheduler

---

## 🧪 Automated Testing & Verification

The test suite runs using `pytest` and `httpx` against an isolated asynchronous database:

```bash
pytest -v
```

### Passing Test Suites (10/10)
- `tests/test_auth.py`: User registration, authentication, rate limiting, refresh tokens, role security.
- `tests/test_patients.py`: Patient CRUD, search query filtering, soft deletion, clinical dashboard.
- `tests/test_appointments.py`: Slot conflict prevention, lifecycle transitions, consultation completion.
- `tests/test_prescriptions.py`: Dynamic line-item issuing, active prescription query, ReportLab PDF streaming.
- `tests/test_lab_tests.py`: Ordering diagnostic modalities, entering clinical findings, critical value flags.
- `tests/test_billing.py`: Subtotals, discount computation, 5% healthcare GST, payments, revenue summary.
- `tests/test_pharmacy.py`: FIFO inventory deduction, low-stock threshold alerts, 30-day expiry queries.
- `tests/test_dashboard.py`: Role-adaptive KPIs and trends for Admin, Doctor, and Patient roles.

---

## 📁 Project Directory Structure

```
HOSPITAL FAST API MANAGEMENT/
├── api/
│   └── index.py                # Serverless ASGI entrypoint for Vercel
├── app/
│   ├── auth/                   # JWT creation, decoding, password hashing (bcrypt)
│   ├── crud/                   # Database CRUD operations per domain
│   ├── models/                 # SQLAlchemy 2.0 ORM database models
│   ├── routers/                # 11 Modular FastAPI APIRouters
│   ├── schemas/                # Pydantic v2 validation models
│   ├── tasks/                  # Celery background workers and periodic beat tasks
│   ├── utils/                  # PDF generators (ReportLab) & Rate Limiting (SlowAPI)
│   ├── config.py               # Pydantic settings & environment configuration
│   ├── database.py             # SQLAlchemy async engine, sessionmaker, and lazy init
│   └── main.py                 # FastAPI application, lifespan, middleware & routes
├── scripts/
│   └── seed.py                 # Clinical database seeder (Indian healthcare dataset)
├── static/
│   └── app/
│       ├── css/style.css       # Clean healthcare design system
│       ├── js/app.js           # Single Page Application interactive frontend
│       └── index.html          # Web application template & modal dialogs
├── tests/                      # 10 Pytest asynchronous test suites
├── docker-compose.yml          # Multi-container stack (FastAPI, Postgres, Redis, Celery)
├── Dockerfile                  # Container build recipe
├── render.yaml                 # Render Cloud blueprint
├── vercel.json                 # Vercel serverless routing & build configuration
├── requirements.txt            # Pinned project dependencies
├── STARTUP_GUIDE.md            # Comprehensive beginner setup and stop/start guide
├── DEPLOYMENT.md               # Step-by-step Vercel & Render cloud deployment manual
└── README.md                   # System documentation & architectural reference
```

---

## 📄 License
MIT License. Developed for enterprise clinical hospital and healthcare clinic management.
