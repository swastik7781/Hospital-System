# 🏥 Utkal Hospital & Medical Research Centre — Enterprise Hospital & Clinic Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0%20(async)-D71F00.svg)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1.svg?logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D.svg?logo=redis)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-5.3+-37814A.svg?logo=celery)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose%20Ready-2496ED.svg?logo=docker)](https://www.docker.com/)

A comprehensive, production-grade Electronic Health Record (EHR) and clinical hospital management platform customized for **Utkal Hospital & Medical Research Centre** (Niladri Vihar, Chandrasekharpur, Bhubaneswar, Odisha). Built with **FastAPI**, **SQLAlchemy 2.0 (async)**, **PostgreSQL 16 / SQLite**, **Redis 7**, **Celery**, and a full interactive web application designed with a medical SaaS design language inspired by Linear, Stripe, and Calm.

> 📖 **Setting up on a new computer from a ZIP file?** Check out the step-by-step [STARTUP_GUIDE.md](STARTUP_GUIDE.md) covering Windows (PowerShell/CMD), macOS, Linux, starting, stopping, and FAQs.

---

## 📐 Architecture & Tech Stack

```
+---------------------------------------------------------------------------------------+
|                                    CLIENT PORTALS                                     |
|    Reception Desks  |  Physician Workstations  |  Pharmacy Dispensary  |  Patient App  |
+-------------------------------------------+-------------------------------------------+
                                            |
                                HTTP / WebSocket / JSON
                                            |
                                            v
+---------------------------------------------------------------------------------------+
|                                   FASTAPI GATEWAY                                     |
|  * CORS & Security Middleware    * SlowAPI Rate Limiter      * Request Logging        |
|  * JWT Auth (Access + Refresh)   * RBAC Security Guard       * Global Exception Handler|
+-------------------------------------------+-------------------------------------------+
                                            |
         +----------------------------------+----------------------------------+
         |                                  |                                  |
         v                                  v                                  v
+------------------+              +-------------------+              +------------------+
|   CORE ROUTERS   |              |  BUSINESS LOGIC   |              | TASK BACKGROUND  |
|  - Auth & Users  |              |  - Slot Conflict  |              |  - Celery Beat   |
|  - Patients EHR  |              |  - Billing & GST  |              |  - Reminders 24h |
|  - Doctors & Sch | <----------> |  - FIFO Dispense  | <----------> |  - Expiry Alerts |
|  - Appointments  |              |  - ReportLab PDF  |              |  - Worker Queue  |
|  - Prescriptions |              |                   |              +--------+---------+
|  - Lab Tests/Rad |              +-------------------+                       |
|  - Billing & Inv |                                                          |
|  - Pharmacy Stk  |                                                          |
|  - Dashboard KPI |                                                          |
+--------+---------+                                                          |
         |                                                                    |
         v                                                                    v
+-------------------------------------------+                      +--------------------+
|            SQLALCHEMY 2.0 ASYNC           |                      |     REDIS CACHE    |
|   Alembic Migrations / Connection Pool    |                      |  Broker & Backend  |
+--------------------+----------------------+                      +--------------------+
                     |
                     v
+-------------------------------------------+
|          POSTGRESQL 16 / SQLITE           |
|  Departments, Doctors, Patients, Visits,  |
|  Prescriptions, Lab Tests, Invoices, Meds |
+-------------------------------------------+
```

---

## ⚡ Quick Start

### 1. Zero-Config Local Setup (SQLite default)

```bash
# 1. Clone or navigate to repository
cd "HOSPITAL FAST API MANAGEMENT"

# 2. Create virtual environment & install dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Seed database with Utkal Hospital departments, doctors, patients, visits & pharmacy batches
python scripts/seed.py

# 4. Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Open **Interactive Web Application**: [http://localhost:8000/](http://localhost:8000/)
- Open **Interactive OpenAPI Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- Open **Alternative ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### 2. Single-Command Docker Deployment (PostgreSQL + Redis + Celery)

```bash
docker compose up -d --build
```
This automatically spins up:
- `hospital_db`: PostgreSQL 16 on port `5432`
- `hospital_redis`: Redis 7 on port `6379`
- `hospital_web`: FastAPI web server on port `8000` (auto-runs migrations & seeds demo records)
- `hospital_celery_worker`: Background report & reminder processor
- `hospital_celery_beat`: Periodic scheduler (daily 24h reminders & low stock monitors)

---

### 3. Cloud Deployment (Vercel & Render Ready)

The project includes built-in configurations for:
- 🌐 **Vercel**: `vercel.json` & `api/index.py` for serverless deployment
- ☁️ **Render**: `render.yaml` for automated web service & database blueprints

Refer to the complete [DEPLOYMENT.md](DEPLOYMENT.md) guide for 1-click instructions.

---

## 🔑 Demo Login Accounts

All accounts are pre-configured with complete mock datasets and can be selected with 1-click from the login gate:

| Role | Email | Password | Personnel Name & Details | Permissions |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | `admin@hospital.com` | `admin123` | **Dr. Admin** *(Medical Superintendent)* | Full administrative access across all 11 modules, hospital settings & branding |
| **Doctor** | `doctor@hospital.com` | `doctor123` | **Dr. Swastik Bhardwaj** *(Head of Cardiology)* | Patient charts, diagnosis, issue prescriptions, order & review lab tests |
| **Receptionist** | `receptionist@hospital.com` | `reception123` | **Pooja Sharma** *(Front Desk Manager)* | Register patients, book appointments, generate invoices, record cash/card payments |
| **Patient** | `patient@hospital.com` | `patient123` | **Ramesh Chandra Pradhan** *(Patient Portal)* | View personal health history, consultations, download official PDF prescriptions |

---

## 🛡️ Role-Based Access Control (RBAC) Matrix

| Endpoint Group | Admin | Doctor | Receptionist | Patient |
| :--- | :---: | :---: | :---: | :---: |
| **User Management** (`/users/`) | ✅ Full | ❌ Profile only | ❌ Profile only | ❌ Profile only |
| **Patients List & Register** (`/patients/`) | ✅ Full | ✅ View/Update | ✅ Full | ❌ Self only |
| **Doctors & Schedules** (`/doctors/`) | ✅ Full | ✅ Self schedule | ✅ View only | ✅ View only |
| **Appointments Booking** (`/appointments/`) | ✅ Full | ✅ Complete visit | ✅ Full | ✅ Self booking |
| **Prescriptions & PDF** (`/prescriptions/`) | ✅ Full | ✅ Create/Update | ✅ View only | ✅ View self & PDF |
| **Lab Tests & Radiology** (`/lab-tests/`) | ✅ Full | ✅ Order/Update | ✅ View only | ✅ View self reports |
| **Billing & Invoices** (`/billing/`) | ✅ Full | ❌ View only | ✅ Create/Pay | ❌ Self invoices |
| **Pharmacy & Inventory** (`/pharmacy/`) | ✅ Full | ✅ Dispense | ✅ Stock-In | ❌ Denied |
| **Dashboard Analytics** (`/dashboard/admin`) | ✅ Full | ✅ Clinical view | ✅ Frontdesk view | ✅ Self portal |

---

## 📋 Comprehensive API Endpoints

### 1. Authentication (`/api/v1/auth`)
- `POST /register`: Register new user account
- `POST /login`: Generate JWT access & refresh tokens *(Rate limited: 20/min)*
- `POST /refresh`: Exchange refresh token for new access token
- `POST /password-reset-request`: Password reset link dispatcher
- `POST /password-reset-confirm`: Reset account password

### 2. Patients (`/api/v1/patients`)
- `GET /`: Searchable, filterable paginated patient directory
- `POST /`: Register patient with demographics, blood group, allergies, emergency contacts
- `GET /{id}`: Retrieve comprehensive patient chart
- `PATCH /{id}`: Partial update patient information
- `DELETE /{id}`: Safe soft-delete (`is_deleted=True`)
- `GET /{id}/dashboard`: Real-time patient summary (visits, active Rx, pending labs, unpaid bills)
- `GET /{id}/visits`: Combinable filter visit history (date range, doctor, status)

### 3. Doctors & Schedules (`/api/v1/doctors`)
- `GET /`: Filterable by specialization, department, search term
- `POST /`: Add clinical doctor with working hours and consultation fees (₹)
- `GET /{id}`: Doctor profile details
- `PATCH /{id}`: Update doctor information
- `GET /{id}/schedule`: Generate weekly 30-min slot availability grid

### 4. Appointments & Visits (`/api/v1/appointments`)
- `POST /`: Book appointment with double-booking conflict detection & auto-generated consultation invoice
- `GET /`: Filter by patient, doctor, department, status, date range
- `GET /{id}`: Appointment details
- `PATCH /{id}`: Reschedule or status transitions (`scheduled` → `confirmed` → `in_progress` → `completed`)
- `POST /{id}/complete`: Record clinical diagnosis and physician consultation notes

### 5. Prescriptions (`/api/v1/prescriptions`)
- `POST /`: Issue prescription with dynamic line items (medicine, dosage, frequency, duration, quantity, notes)
- `GET /`: List prescriptions
- `GET /{id}`: Retrieve prescription details
- `GET /{id}/pdf`: Generate & stream printable medical PDF order on Utkal Hospital letterhead
- `GET /patient/{patient_id}/active`: List active prescriptions from the last 30 days

### 6. Lab Tests & Radiology (`/api/v1/lab-tests`)
- `POST /`: Order diagnostic test (`blood_work`, `xray`, `mri`, `ct_scan`, `ultrasound`, `biopsy`)
- `GET /`: Filter by status, test type, or critical flag
- `PATCH /{id}`: Update test progress, specimen findings, and abnormal/critical value flags
- `POST /{id}/upload-report`: Upload report file (PDF/image) and mark completed

### 7. Billing & Invoices (`/api/v1/billing`)
- `POST /invoices`: Create invoice with auto-calculated subtotal, discount, 5% healthcare GST, and total
- `GET /invoices`: Filter by patient, payment status, payment method
- `PATCH /invoices/{id}`: Record partial/full payments or submit insurance claims
- `GET /revenue-summary`: Real-time revenue analytics (today, this week, this month, total in INR ₹)

### 8. Pharmacy & Inventory (`/api/v1/pharmacy`)
- `GET /medicines`: List medicines with live stock balance & low-stock flags
- `POST /medicines`: Create new pharmaceutical formulary catalog item
- `POST /stock-in`: Purchase inventory batch with expiry date, quantity, unit cost (₹), supplier
- `POST /stock-out`: Dispense medicine using FIFO (earliest expiring batch first)
- `GET /alerts/low-stock`: Query medicines below clinical reorder levels
- `GET /alerts/expiring`: Query batches expiring within 30 days
- `GET /valuation`: Total inventory valuation, unit count, and risk alerts

### 9. Dashboard (`/api/v1/dashboard`)
- `GET /admin`: Complete executive dashboard with role-adaptive KPIs, 14-day visit trends, revenue trends, live activity feed, and clinical alerts

---

## 🧪 Automated Testing

The test suite runs with `pytest` and `httpx` in an isolated asynchronous test database:

```bash
pytest -v
```

**Test Coverage Highlights (10/10 Passing Test Suites):**
- `test_auth.py`: Registration, login, rate limiting, refresh tokens, role security enforcement
- `test_patients.py`: Patient CRUD, search query matching, dashboard summary, soft delete
- `test_appointments.py`: Double booking conflict prevention, status workflow, completion diagnosis
- `test_prescriptions.py`: Multi-line prescriptions, active patient filter, ReportLab PDF stream validation
- `test_lab_tests.py`: Ordering diagnostic tests, updating clinical findings, critical value flagging
- `test_billing.py`: Subtotal, discount, 5% GST calculations, payment status updates, revenue metrics
- `test_pharmacy.py`: FIFO stock dispensation, low stock trigger, expiry warnings, valuation calculations
- `test_dashboard.py`: Admin, Doctor, and Patient role-adaptive dashboard responses

---

## 🖼️ UI Features & Modals

The interactive web portal located at `static/app/index.html` provides a zero-setup single page application:
- **Deep Teal Healthcare Palette (`#0D9488`)**: Calm, crisp hospital SaaS aesthetic
- **Real-Time Role Gate**: 1-click credential switcher for Admin, Doctor, Receptionist, and Patient
- **Live Search**: Instant client-side filtering across patients, doctors, appointments, prescriptions, and pharmacy
- **Prescription Generator**: Multi-line medicine issuing modal with downloadable PDF letterheads
- **Diagnostic Lab Manager**: Order MRI, CT Scans, Blood Panels, and flag critical findings with urgent physician alerts
- **GST Billing & Invoicing**: Automated 5% GST computation, partial payments, and POS/Insurance support
- **FIFO Pharmacy Dispensary**: Expiry-aware stock dispensation and real-time reorder thresholds
- **Patient EHR Chart**: Consolidated clinical history modal showing consultations, prescriptions, and labs

---

## 📄 License
MIT License. Crafted for enterprise clinical hospital management.
