# 🏥 Utkal Hospital Management System — Complete Setup & Operation Guide

Welcome to **Utkal Hospital & Medical Research Centre** (Hospital & Clinic Management System).  
This guide provides complete, step-by-step instructions to set up, start, stop, and troubleshoot this project on any new machine (Windows, macOS, or Linux) directly from a ZIP file.

---

## ⚡ Quick Start (TL;DR for Windows Users)

If you already have **Python 3.10+** installed, open **PowerShell** in the extracted project folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/seed.py
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open **[http://localhost:8000/](http://localhost:8000/)** in your browser!

---

## 📋 Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [First-Time Installation from ZIP](#2-first-time-installation-from-zip)
   - [Windows (PowerShell)](#option-a-windows-powershell-recommended)
   - [Windows (Command Prompt / CMD)](#option-b-windows-command-prompt-cmd)
   - [macOS & Linux (Terminal)](#option-c-macos--linux-terminal)
3. [Environment Configuration](#3-environment-configuration)
4. [Database Initialization & Seeding](#4-database-initialization--seeding)
5. [Verifying Installation with Automated Tests](#5-verifying-installation-with-automated-tests)
6. [How to START the System](#6-how-to-start-the-system)
7. [Demo Login Credentials](#7-demo-login-credentials)
8. [How to STOP the System](#8-how-to-stop-the-system)
9. [Running with Docker (Optional Production Mode)](#9-running-with-docker-optional-production-mode)
10. [Troubleshooting & FAQs](#10-troubleshooting--faqs)

---

## 1. Prerequisites

Before setting up, ensure the following are installed on your computer:

| Requirement | Minimum Version | Notes |
| :--- | :--- | :--- |
| **Python** | `3.10` or `3.11+` | Check: `python --version` (On Windows, ensure **"Add python.exe to PATH"** was checked during installation). |
| **pip** | Latest | Included with Python. Check: `pip --version` |
| **Web Browser** | Any modern browser | Chrome, Edge, Firefox, Brave, Safari |
| **Docker & Docker Compose** | *(Optional)* | Only needed if you wish to run the full containerized PostgreSQL + Redis + Celery stack. |

---

## 2. First-Time Installation from ZIP

### Step 1: Extract the ZIP Archive
1. Right-click the `.zip` file you downloaded and select **Extract All...** (or unzip via terminal).
2. Open the extracted folder: `HOSPITAL FAST API MANAGEMENT`.

---

### Option A: Windows PowerShell (Recommended)

1. Open **PowerShell** inside the project folder:
   - *Tip:* Press `Shift + Right-Click` in the folder and choose **"Open PowerShell window here"**, or type `powershell` in the File Explorer address bar and press Enter.

2. *(If needed)* Allow local script execution for the current session:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

3. Create an isolated virtual environment:
   ```powershell
   python -m venv .venv
   ```

4. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   *(You will see `(.venv)` appear at the beginning of your command prompt).*

5. Upgrade pip and install all project dependencies:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

### Option B: Windows Command Prompt (CMD)

1. Open `cmd.exe` in the project folder.
2. Create and activate virtual environment:
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate.bat
   ```
3. Install dependencies:
   ```cmd
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

### Option C: macOS & Linux (Terminal)

1. Open Terminal in the project root:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 3. Environment Configuration

A sample environment file `.env.example` is included. For local development with SQLite, no changes are strictly necessary, but you can copy it to `.env`:

- **Windows (PowerShell):**
  ```powershell
  Copy-Item .env.example .env
  ```
- **Windows (CMD):**
  ```cmd
  copy .env.example .env
  ```
- **macOS / Linux:**
  ```bash
  cp .env.example .env
  ```

---

## 4. Database Initialization & Seeding

The application comes with an automatic seeding script that creates all database tables and populates realistic demo clinical data for **Utkal Hospital & Medical Research Centre** (5 departments, 10 specialist doctors, 20 patients, 14-day appointment histories, prescriptions, lab reports, 5% GST billing invoices, and 30 pharmacy catalog medicines).

Run the seed script inside your activated environment:

```bash
python scripts/seed.py
```

**Expected output:**
```
[INIT] Re-initializing Database Schema for Utkal Hospital...
[USER] Creating Core Indian Users (Admin, Doctor, Receptionist, Patient)...
[DEPT] Creating 5 Departments...
[DOC] Creating 10 Renowned Indian Doctors...
[PATIENT] Creating 20 Indian Patients with Real Records...
[VISIT] Creating Appointments with Realistic Daily Volume...
[PRESC] Creating Prescriptions with Line Items...
[LAB] Creating Diagnostic Lab Reports...
[BILL] Creating 12 Invoices in Indian Rupees (INR) with GST...
[PHARM] Creating 30 Essential Medicines & Indian Pharmacy Batches...
[SUCCESS] Utkal Hospital database successfully initialized and seeded with Indian data!
```

---

## 5. Verifying Installation with Automated Tests

Run the comprehensive automated test suite to verify everything works properly on your operating system:

```bash
pytest -v
```

**Expected output:**
```
tests/test_appointments.py::test_appointment_booking_conflict_and_completion PASSED
tests/test_auth.py::test_register_and_login PASSED
tests/test_auth.py::test_login_invalid_password PASSED
tests/test_auth.py::test_role_based_access_control PASSED
tests/test_billing.py::test_billing_calculations_payments_and_revenue PASSED
tests/test_dashboard.py::test_dashboard_roles PASSED
tests/test_lab_tests.py::test_lab_test_lifecycle PASSED
tests/test_patients.py::test_patient_crud_and_soft_delete PASSED
tests/test_pharmacy.py::test_pharmacy_inventory_lifecycle PASSED
tests/test_prescriptions.py::test_prescription_lifecycle_and_pdf PASSED

==================== 10 passed in ~2.5s ====================
```

---

## 6. How to START the System

Ensure your virtual environment is active `(.venv)`, then run:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

*(Or use `make run` if you have `make` installed).*

### Open in your browser:
- 🏥 **Interactive Web Application**: [http://localhost:8000/](http://localhost:8000/)
- 📖 **Interactive Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 📑 **Alternative ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- 🩺 **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 7. Demo Login Credentials

The web application features an instant **Role-Based Login Gate** where you can click any preset card to sign in:

| Role | Email ID | Password | Personnel Name & Department | Access Scope |
| :--- | :--- | :--- | :--- | :--- |
| 👑 **Admin** | `admin@hospital.com` | `admin123` | **Dr. Admin** *(Medical Superintendent)* | Full access across all 11 modules, hospital settings & branding |
| 🩺 **Doctor** | `doctor@hospital.com` | `doctor123` | **Dr. Swastik Bhardwaj** *(Head of Cardiology)* | Consultations, issue prescriptions, order & update diagnostic lab tests |
| 📋 **Receptionist** | `receptionist@hospital.com` | `reception123` | **Pooja Sharma** *(Front Desk Manager)* | Register patients, book appointments, generate invoices, record payments |
| 🧑‍🦽 **Patient** | `patient@hospital.com` | `patient123` | **Ramesh Chandra Pradhan** *(Patient)* | Patient portal: view personal health timeline, download official prescription PDFs |

---

## 8. How to STOP the System

### Method 1: Normal Terminal Stop (Clean Shutdown)
In the terminal/PowerShell window where `uvicorn` is running:
- Press <kbd>Ctrl</kbd> + <kbd>C</kbd>
- The server will display `Application shutdown complete` and return to your prompt.

---

### Method 2: Force Kill (If Port 8000 Remains Occupied)
If the server was closed abruptly or the port is still in use:

- **On Windows (PowerShell):**
  ```powershell
  Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess -Force
  ```

- **On Windows (CMD):**
  ```cmd
  for /f "tokens=5" %a in ('netstat -aon ^| findstr :8000') do taskkill /f /pid %a
  ```

- **On macOS / Linux:**
  ```bash
  lsof -ti:8000 | xargs kill -9
  ```

---

## 9. Running with Docker (Optional Production Mode)

If you have **Docker Desktop** installed and wish to run with **PostgreSQL 16**, **Redis 7**, and **Celery background workers**:

### Start Docker Stack:
```bash
docker compose up -d --build
```
*(Automatically creates PostgreSQL database, runs migrations, seeds data, and starts FastAPI on port 8000).*

### Stop Docker Stack:
```bash
docker compose down
```
*(To also remove the database volume and start completely fresh: `docker compose down -v`).*

---

## 10. Troubleshooting & FAQs

### Q1: `Activate.ps1 cannot be loaded because running scripts is disabled on this system`
**Fix:** Run this command once in PowerShell:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
Then run `.\.venv\Scripts\Activate.ps1` again.

---

### Q2: `python is not recognized as an internal or external command`
**Fix:** Python is not added to your system PATH:
1. Re-run the Python Windows installer.
2. Select **Modify**, then ensure the checkbox **"Add Python to environment variables"** or **"Add python.exe to PATH"** is checked.
3. Restart PowerShell/terminal.

---

### Q3: `Address already in use: 127.0.0.1:8000`
**Fix:** Another process is already running on port 8000:
1. Stop the existing process using the [Force Kill command](#method-2-force-kill-if-port-8000-remains-occupied).
2. Or start on a different port:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
   ```

---

### Q4: `How do I reset or re-seed the database back to clean demo data?`
**Fix:** Simply re-run the seed script at any time:
```bash
python scripts/seed.py
```
This drops existing tables, re-creates the schema, and seeds clean Indian clinical records.

---

### Q5: `Where are generated prescription PDFs and uploads stored?`
**Answer:** Uploads and diagnostic files are stored in the `uploads/` directory inside the project root. Prescription PDFs are generated on the fly via ReportLab directly to streamable binary buffers.

---

## 📞 Support & Contacts
- **Institution**: Utkal Hospital & Medical Research Centre
- **Address**: Niladri Vihar, Chandrasekharpur, Bhubaneswar, Odisha 751021
- **Helpline**: +91 674 274 0100
- **Email**: contact@utkalhospital.com

