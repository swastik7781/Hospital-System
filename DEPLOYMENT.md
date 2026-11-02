# 🚀 Deployment Guide: Vercel & Render

This repository is pre-configured and production-ready for deployment on **Vercel** (Serverless) and **Render** (Cloud Web Service & PostgreSQL).

---

## ⚡ Option 1: Deploy on Vercel (Instant Serverless)

The project includes:
- `vercel.json` (Vercel serverless rewrite rules)
- `api/index.py` (Serverless ASGI entrypoint)
- Automatic fallback to writable temp storage (`/tmp/hospital.db`) and auto-seeding on Vercel cold starts.

### Method A: Deploy via GitHub (Recommended)
1. Push your repository to GitHub (see [Push to GitHub](#-pushing-your-code-to-github)).
2. Go to **[vercel.com](https://vercel.com)** and log in.
3. Click **"Add New..."** → **"Project"**.
4. Import your GitHub repository (`HOSPITAL FAST API MANAGEMENT` or `utkal-hospital-ehr`).
5. **Framework Preset**: Select **Other**.
6. **Root Directory**: Leave as `./` (default).
7. Under **Environment Variables**, optionally add:
   - `ENVIRONMENT`: `production`
   - `SECRET_KEY`: *(any secure 32+ character string)*
   *(Optional)* If you connect an external PostgreSQL database (e.g. Supabase, Neon, or Render Postgres), add:
   - `DATABASE_URL`: `postgresql+asyncpg://user:password@host:port/dbname`
8. Click **Deploy**. Vercel will build and provide a live `https://<your-project>.vercel.app` URL!

---

### Method B: Deploy via Vercel CLI directly from your terminal

1. Open PowerShell or Command Prompt in this folder.
2. Run:
   ```cmd
   npx vercel
   ```
3. Follow the interactive prompts:
   - **Set up and deploy?** Press `y`
   - **Which scope do you want to deploy to?** Choose your Vercel account
   - **Link to existing project?** Press `n`
   - **What's your project's name?** Enter `utkal-hospital-ehr` (or press Enter)
   - **In which directory is your code located?** Press Enter (`./`)
   - **Want to modify these settings?** Press `n`
4. Once deployed, run `npx vercel --prod` to deploy to production.

---

## ⚡ Option 2: Deploy on Render (Full Cloud Service)

The project includes `render.yaml` which enables automated **Render Blueprints** or manual Web Service setup.

### Method A: 1-Click Blueprint on Render
1. Push your repository to GitHub.
2. Go to **[dashboard.render.com](https://dashboard.render.com/)**.
3. Click **"New +"** → **"Blueprint"**.
4. Connect your GitHub repository.
5. Render reads `render.yaml` and will configure the web service automatically.
6. Click **Apply**.

---

### Method B: Manual Web Service Setup on Render
1. Go to **[dashboard.render.com](https://dashboard.render.com/)**.
2. Click **"New +"** → **"Web Service"**.
3. Connect your GitHub repository.
4. Fill in the deployment settings:
   - **Name**: `utkal-hospital-ehr`
   - **Region**: Any (e.g., Singapore, Frankfurt, Oregon)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python scripts/seed.py
     ```
   - **Start Command**:
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: `Free`
5. Under **Environment Variables**, add:
   - `PYTHON_VERSION`: `3.11.9`
   - `ENVIRONMENT`: `production`
   - `SECRET_KEY`: *(click Generate or enter a secure key)*
   *(Optional Render PostgreSQL)*:
   If you created a Render PostgreSQL database, add:
   - `DATABASE_URL`: *(Your Internal Database URL from Render Database page)*
     *(The app automatically converts `postgres://` into `postgresql+asyncpg://`)*
6. Click **Create Web Service**.

---

## 🐙 Pushing Your Code to GitHub (First-Time Setup)

If you haven't uploaded this folder to GitHub yet, run these commands in PowerShell/terminal:

```powershell
# 1. Initialize Git repository
git init

# 2. Add all files
git add .

# 3. Create your initial commit
git commit -m "Initial commit: Utkal Hospital EHR System ready for Vercel & Render"

# 4. Rename default branch to main
git branch -M main

# 5. Create a new repository on https://github.com/new (e.g., named 'utkal-hospital-ehr')
# 6. Link your local repo to GitHub (replace <YOUR_USERNAME> with your GitHub username):
git remote add origin https://github.com/<YOUR_USERNAME>/utkal-hospital-ehr.git

# 7. Push the code
git push -u origin main
```

Once pushed, both **Vercel** and **Render** will automatically deploy whenever you push new changes to GitHub!

---

## 🔑 Production Access & Verification

Once your deployment finishes on Vercel or Render:

1. **Web Portal**: Visit `https://<your-deployment-url>/`
2. **Interactive Swagger Docs**: Visit `https://<your-deployment-url>/docs`
3. **Health Check**: Visit `https://<your-deployment-url>/health`

### Demo Credentials (Pre-seeded):
- **Admin**: `admin@hospital.com` / `admin123`
- **Doctor**: `doctor@hospital.com` / `doctor123`
- **Receptionist**: `receptionist@hospital.com` / `reception123`
- **Patient**: `patient@hospital.com` / `patient123`
