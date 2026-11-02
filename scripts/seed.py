import asyncio
import os
import sys

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime, timedelta
import random

from sqlalchemy import select
from app.database import async_session_maker, engine, Base
from app.models.user import User, UserRole
from app.models.department import Department
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.appointment import Appointment, AppointmentStatus
from app.models.prescription import Prescription, PrescriptionItem
from app.models.lab_test import LabTest, LabTestType, LabTestStatus
from app.models.billing import Invoice, InvoiceItem, PaymentMethod, PaymentStatus
from app.models.pharmacy import Medicine, MedicineBatch, StockMovement
from app.auth.password import get_password_hash


async def seed(drop_first: bool = False):
    print("[INIT] Initializing Database Schema for Utkal Hospital...")
    async with engine.begin() as conn:
        if drop_first:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as db:
        print("[USER] Creating Core Indian Users (Admin, Doctor, Receptionist, Patient)...")
        admin_user = User(
            email="admin@hospital.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Dr. Admin / Medical Superintendent",
            role=UserRole.ADMIN,
            is_active=True,
            phone="+91 94370 12345",
        )
        doctor_user = User(
            email="doctor@hospital.com",
            hashed_password=get_password_hash("doctor123"),
            full_name="Dr. Swastik Bhardwaj",
            role=UserRole.DOCTOR,
            is_active=True,
            phone="+91 98610 54321",
        )
        receptionist_user = User(
            email="receptionist@hospital.com",
            hashed_password=get_password_hash("reception123"),
            full_name="Pooja Sharma (Front Desk)",
            role=UserRole.RECEPTIONIST,
            is_active=True,
            phone="+91 674 274 0100",
        )
        patient_user = User(
            email="patient@hospital.com",
            hashed_password=get_password_hash("patient123"),
            full_name="Ramesh Chandra Pradhan",
            role=UserRole.PATIENT,
            is_active=True,
            phone="+91 99370 88776",
        )
        db.add_all([admin_user, doctor_user, receptionist_user, patient_user])
        await db.flush()

        # 1. 5 Clinical Departments
        print("[DEPT] Creating 5 Departments...")
        departments_data = [
            {"name": "Cardiology & Cardiac Sciences", "description": "Interventional Cardiology & Electrophysiology", "floor": "3rd Floor, Block A"},
            {"name": "Neurology & Neurosurgery", "description": "Comprehensive Brain, Spine & Stroke Care", "floor": "4th Floor, Block B"},
            {"name": "Pediatrics & Neonatology", "description": "Children, Adolescent & Newborn Intensive Care", "floor": "2nd Floor, Block C"},
            {"name": "Orthopedics & Joint Replacement", "description": "Advanced Joint Reconstruction & Trauma", "floor": "1st Floor, Block A"},
            {"name": "General Internal Medicine", "description": "Adult Preventive Medicine, Diabetes & Critical Care", "floor": "Ground Floor, OPD Wing"},
        ]
        dept_objs = []
        for d in departments_data:
            dept = Department(**d)
            db.add(dept)
            dept_objs.append(dept)
        await db.flush()

        # 2. 10 Indian Doctors
        print("[DOC] Creating 10 Renowned Indian Doctors...")
        doctors_data = [
            ("Dr. Swastik Bhardwaj", "Cardiology", dept_objs[0].id, "MD, DM (Cardiology) - AIIMS New Delhi", 16, "+91 98610 54321", "swastik.bhardwaj@utkalhospital.com", 1500.0, doctor_user.id),
            ("Dr. Auroshikha Tripathy", "Neurology", dept_objs[1].id, "MBBS, MD, DM (Neurology) - NIMHANS", 14, "+91 98610 54322", "auroshikha.tripathy@utkalhospital.com", 1800.0, None),
            ("Dr. Ramyak Ray", "Pediatrics", dept_objs[2].id, "MBBS, MD (Pediatrics) - PGIMER Chandigarh", 12, "+91 98610 54323", "ramyak.ray@utkalhospital.com", 1200.0, None),
            ("Dr. Pratyush Nishank", "Orthopedics", dept_objs[3].id, "MS (Ortho), MCh - AIIMS Bhubaneswar", 15, "+91 98610 54324", "pratyush.nishank@utkalhospital.com", 1600.0, None),
            ("Dr. Priya Sharma", "General Internal Medicine", dept_objs[4].id, "MBBS, MD (Medicine) - CMC Vellore", 13, "+91 98610 54325", "priya.sharma@utkalhospital.com", 1000.0, None),
            ("Dr. Rajesh Mohanty", "Cardiology", dept_objs[0].id, "MD, FACC - Apollo Hospitals", 18, "+91 98610 54326", "rajesh.mohanty@utkalhospital.com", 1400.0, None),
            ("Dr. Rohan Patnaik", "Neurology", dept_objs[1].id, "MS, MCh (Neurosurgery) - SCB Medical", 11, "+91 98610 54327", "rohan.patnaik@utkalhospital.com", 1700.0, None),
            ("Dr. Ananya Mishra", "Pediatrics", dept_objs[2].id, "MBBS, DCH, DNB (Pediatrics) - KIMS", 9, "+91 98610 54328", "ananya.mishra@utkalhospital.com", 1100.0, None),
            ("Dr. Sneha Das", "Orthopedics", dept_objs[3].id, "MS (Ortho) - AIIMS New Delhi", 10, "+91 98610 54329", "sneha.das@utkalhospital.com", 1500.0, None),
            ("Dr. Devashish Senapati", "General Internal Medicine", dept_objs[4].id, "MD (Medicine), FCCP - SUM Ultimate", 17, "+91 98610 54330", "devashish.senapati@utkalhospital.com", 900.0, None),
        ]
        doc_objs = []
        for name, spec, d_id, qual, exp, ph, em, fee, u_id in doctors_data:
            doc = Doctor(
                full_name=name,
                specialization=spec,
                department_id=d_id,
                qualification=qual,
                experience_years=exp,
                phone=ph,
                email=em,
                consultation_fee=fee,
                available_days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                working_hours_start="09:00",
                working_hours_end="18:00",
                user_id=u_id,
            )
            db.add(doc)
            doc_objs.append(doc)
        await db.flush()

        # Update department heads
        dept_objs[0].head_doctor_id = doc_objs[0].id
        dept_objs[1].head_doctor_id = doc_objs[1].id
        dept_objs[2].head_doctor_id = doc_objs[2].id
        dept_objs[3].head_doctor_id = doc_objs[3].id
        dept_objs[4].head_doctor_id = doc_objs[4].id
        await db.flush()

        # 3. 20 Indian Patients
        print("[PATIENT] Creating 20 Indian Patients with Real Records...")
        patient_names = [
            ("Ramesh Chandra Pradhan", "1985-04-12", "Male", "+91 99370 88776", "ramesh.pradhan@example.com", "O+", "Penicillin", patient_user.id, "Bhubaneswar, Odisha"),
            ("Manoj Kumar Sahoo", "1978-08-23", "Male", "+91 94371 22334", "manoj.sahoo@example.com", "B+", "None", None, "Cuttack, Odisha"),
            ("Subhashree Mohapatra", "1992-11-03", "Female", "+91 98612 33445", "subhashree.m@example.com", "A+", "Sulfa drugs", None, "Bhubaneswar, Odisha"),
            ("Rajesh Nayak", "1982-01-15", "Male", "+91 97760 44556", "rajesh.nayak@example.com", "AB+", "Aspirin", None, "Puri, Odisha"),
            ("Pooja Priyadarshini", "1990-06-30", "Female", "+91 99380 55667", "pooja.p@example.com", "O-", "None", None, "Rourkela, Odisha"),
            ("Abhinav Rout", "1995-09-14", "Male", "+91 94380 66778", "abhinav.rout@example.com", "A-", "Peanuts", None, "Bhubaneswar, Odisha"),
            ("Smrutirekha Mishra", "1994-03-21", "Female", "+91 98611 77889", "smruti.mishra@example.com", "B-", "None", None, "Sambalpur, Odisha"),
            ("Deepak Das", "1993-07-08", "Male", "+91 99372 88990", "deepak.das@example.com", "O+", "Latex", None, "Balasore, Odisha"),
            ("Lipsa Jena", "1991-05-18", "Female", "+91 94373 99001", "lipsa.jena@example.com", "AB-", "None", None, "Bhubaneswar, Odisha"),
            ("Alok Kumar Panda", "1989-12-05", "Male", "+91 98613 11223", "alok.panda@example.com", "A+", "None", None, "Berhampur, Odisha"),
            ("Madhumita Barik", "1990-02-14", "Female", "+91 97761 22334", "madhu.barik@example.com", "O+", "Ibuprofen", None, "Bhubaneswar, Odisha"),
            ("Srikant Behera", "1987-10-25", "Male", "+91 99381 33445", "srikant.behera@example.com", "B+", "None", None, "Cuttack, Odisha"),
            ("Swagatika Ray", "1992-04-09", "Female", "+91 94381 44556", "swagatika.ray@example.com", "A+", "Pollen", None, "Bhubaneswar, Odisha"),
            ("Biswajit Tripathy", "1988-08-19", "Male", "+91 98614 55667", "biswajit.t@example.com", "O+", "None", None, "Angul, Odisha"),
            ("Priyanka Swain", "1991-09-02", "Female", "+91 99373 66778", "priyanka.swain@example.com", "A-", "None", None, "Bhubaneswar, Odisha"),
            ("Bibhuti Bhusan Das", "1960-01-10", "Male", "+91 94374 77889", "bibhuti.das@example.com", "O+", "Codeine", None, "Puri, Odisha"),
            ("Minati Das", "1965-06-17", "Female", "+91 98615 88990", "minati.das@example.com", "B+", "None", None, "Bhubaneswar, Odisha"),
            ("Prasanna Kumar Mohanty", "1962-03-04", "Male", "+91 97762 99001", "prasanna.mohanty@example.com", "O+", "None", None, "Cuttack, Odisha"),
            ("Geetanjali Sahu", "1967-11-28", "Female", "+91 99382 11223", "geeta.sahu@example.com", "A+", "None", None, "Bhubaneswar, Odisha"),
            ("Soumya Ranjan Parida", "1986-05-12", "Male", "+91 94382 22334", "soumya.parida@example.com", "AB+", "Amoxicillin", None, "Jajpur, Odisha"),
        ]
        patient_objs = []
        for name, dob, gender, ph, em, bg, allergies, u_id, addr in patient_names:
            pat = Patient(
                full_name=name,
                date_of_birth=datetime.strptime(dob, "%Y-%m-%d").date(),
                gender=gender,
                phone=ph,
                email=em,
                address=addr,
                blood_group=bg,
                allergies=allergies,
                medical_history="Diagnosed with Type-2 Diabetes in 2022; regular HbA1c screening." if "Das" in name or "Pradhan" in name else "Seasonal allergic rhinitis; no chronic comorbidities.",
                emergency_contact="+91 94370 00000 (Spouse/Next of Kin)",
                user_id=u_id,
            )
            db.add(pat)
            patient_objs.append(pat)
        await db.flush()

        # 4. Realistic Appointments Spread across the last 14 days, today, and upcoming
        print("[VISIT] Creating Appointments with Realistic Daily Volume...")
        slots = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00", "15:30", "16:00"]
        reasons = [
            "Cardiology review & ECG evaluation",
            "Persistent tension headache & migraine",
            "Child wellness & MMR booster vaccination",
            "Right knee osteoarthritis pain & stiffness",
            "Comprehensive annual executive physical checkup",
            "Chest tightness & post-exertional fatigue",
            "Vertigo & inner-ear imbalance assessment",
            "Pediatric seasonal bronchitis checkup",
            "Post-operative joint reconstruction follow-up",
            "Hypertension & glycemic medication titration"
        ]
        
        appointment_objs = []
        today = date.today()
        
        # Populate each of the past 14 days with 3-8 appointments so telemetry is 100% real
        app_id_counter = 0
        for day_offset in range(14, -1, -1):
            target_date = today - timedelta(days=day_offset)
            daily_count = 4 + (day_offset * 3) % 5  # between 4 and 8 visits per day
            for k in range(daily_count):
                pat = patient_objs[(app_id_counter + k) % len(patient_objs)]
                doc = doc_objs[(app_id_counter * 2 + k) % len(doc_objs)]
                slot = slots[k % len(slots)]
                
                if day_offset > 0:
                    stat = AppointmentStatus.COMPLETED if k % 5 != 0 else AppointmentStatus.NO_SHOW
                elif day_offset == 0:
                    stat = AppointmentStatus.CONFIRMED if k % 2 == 0 else AppointmentStatus.IN_PROGRESS
                else:
                    stat = AppointmentStatus.SCHEDULED
                    
                app = Appointment(
                    patient_id=pat.id,
                    doctor_id=doc.id,
                    appointment_date=target_date,
                    time_slot=slot,
                    reason=reasons[(app_id_counter + k) % len(reasons)],
                    status=stat,
                    diagnosis="Essential Hypertension Stage-1; lifestyle and diet protocol prescribed." if stat == AppointmentStatus.COMPLETED else None,
                    notes="Patient showed good adherence. Scheduled for follow-up in 4 weeks." if stat == AppointmentStatus.COMPLETED else None,
                    is_recurring=(k % 4 == 0),
                    recurrence_pattern="monthly" if (k % 4 == 0) else None,
                )
                db.add(app)
                appointment_objs.append(app)
            app_id_counter += daily_count
        await db.flush()

        # 5. 12 Prescriptions with Line Items
        print("[PRESC] Creating Prescriptions with Line Items...")
        presc_objs = []
        for i in range(12):
            pat = patient_objs[i % len(patient_objs)]
            doc = doc_objs[i % len(doc_objs)]
            visit = appointment_objs[i]
            
            presc = Prescription(
                visit_id=visit.id,
                patient_id=pat.id,
                doctor_id=doc.id,
                prescription_date=today - timedelta(days=i),
                instructions="Take prescribed medications strictly after food. Keep yourself well hydrated. Review in 15 days if symptoms persist.",
            )
            db.add(presc)
            await db.flush()

            items = [
                PrescriptionItem(
                    prescription_id=presc.id,
                    medicine_name="Amoxicillin & Potassium Clavulanate 625mg",
                    dosage="625mg",
                    frequency="Twice daily (after breakfast & dinner)",
                    duration="5 days",
                    quantity=10,
                    notes="Complete antibiotic schedule without skipping",
                ),
                PrescriptionItem(
                    prescription_id=presc.id,
                    medicine_name="Paracetamol 650mg (Dolo 650)",
                    dosage="650mg",
                    frequency="SOS for fever or headache",
                    duration="3 days",
                    quantity=6,
                    notes="Maintain minimum 6 hours gap between doses",
                ),
                PrescriptionItem(
                    prescription_id=presc.id,
                    medicine_name="Pantoprazole 40mg (Pan 40)",
                    dosage="40mg",
                    frequency="Once daily (empty stomach, 30 min before breakfast)",
                    duration="10 days",
                    quantity=10,
                    notes="Antacid protection",
                ),
            ]
            for itm in items:
                db.add(itm)
            presc_objs.append(presc)
        await db.flush()

        # 6. 15 Diagnostic Lab Reports
        print("[LAB] Creating Diagnostic Lab Reports...")
        test_types = [
            LabTestType.BLOOD_WORK,
            LabTestType.XRAY,
            LabTestType.MRI,
            LabTestType.CT_SCAN,
            LabTestType.ULTRASOUND,
            LabTestType.BIOPSY,
        ]
        lab_objs = []
        for i in range(15):
            pat = patient_objs[(i * 2) % len(patient_objs)]
            doc = doc_objs[i % len(doc_objs)]
            tt = test_types[i % len(test_types)]
            stat = LabTestStatus.COMPLETED if i < 11 else LabTestStatus.IN_PROGRESS
            crit = (i in [1, 6])  # abnormal/critical flags
            
            lab = LabTest(
                patient_id=pat.id,
                doctor_id=doc.id,
                test_type=tt,
                status=stat,
                scheduled_date=today - timedelta(days=i),
                report_file=f"/uploads/sample_report_{i+1}.pdf" if stat == LabTestStatus.COMPLETED else None,
                findings="Platelet count low (52,000 /uL) - Urgent hematology consultation advised." if crit else "Complete Hemogram: Hb 13.8 g/dL, TLC 7,800 /cu.mm, Platelets 2.4 Lakhs - All normal.",
                notes="Patient informed regarding clinical findings." if stat == LabTestStatus.COMPLETED else "Specimen under automated biochemistry analysis.",
                critical_value=crit,
            )
            db.add(lab)
            lab_objs.append(lab)
        await db.flush()

        # 7. 12 Financial Invoices with Indian Rupee (INR) Calculations and GST
        print("[BILL] Creating 12 Invoices in Indian Rupees (INR) with GST...")
        for i in range(12):
            pat = patient_objs[i % len(patient_objs)]
            doc = doc_objs[i % len(doc_objs)]
            
            consult_fee = doc.consultation_fee
            investigation_fee = 500.0 + (i * 100.0)
            subtotal = consult_fee + investigation_fee
            discount = 200.0 if i % 3 == 0 else 0.0
            taxable = subtotal - discount
            tax = round(taxable * 0.05, 2)  # 5% healthcare GST
            total = round(taxable + tax, 2)
            
            p_status = PaymentStatus.PAID if i < 7 else (PaymentStatus.PARTIAL if i < 9 else PaymentStatus.PENDING)
            amt_paid = total if p_status == PaymentStatus.PAID else (round(total * 0.5, 2) if p_status == PaymentStatus.PARTIAL else 0.0)

            inv = Invoice(
                invoice_number=f"INV-UTKAL-20261023-{1000 + i}",
                patient_id=pat.id,
                subtotal=subtotal,
                discount=discount,
                tax=tax,
                total=total,
                amount_paid=amt_paid,
                payment_method=PaymentMethod.CARD if i % 3 == 0 else (PaymentMethod.INSURANCE if i % 3 == 1 else PaymentMethod.CASH),
                payment_status=p_status,
                provider_name="Star Health & Allied Insurance" if i % 3 == 1 else None,
                policy_number=f"STAR-UTK-8899-{i}" if i % 3 == 1 else None,
                claim_status="approved" if (i % 3 == 1 and p_status == PaymentStatus.PAID) else "submitted",
            )
            db.add(inv)
            await db.flush()

            items = [
                InvoiceItem(
                    invoice_id=inv.id,
                    description=f"Specialist OPD Consultation - {doc.full_name} ({doc.specialization})",
                    quantity=1,
                    unit_price=consult_fee,
                    total_price=consult_fee,
                ),
                InvoiceItem(
                    invoice_id=inv.id,
                    description="Diagnostic Clinical Panel & Blood Profile",
                    quantity=1,
                    unit_price=investigation_fee,
                    total_price=investigation_fee,
                ),
            ]
            for itm in items:
                db.add(itm)
        await db.flush()

        # 8. 30 Medicines with Batches in Indian Rupees
        print("[PHARM] Creating 30 Essential Medicines & Indian Pharmacy Batches...")
        medicines_catalog = [
            ("Amoxicillin 500mg", "Amoxicillin Trihydrate", "Antibiotic", "capsule", 50, 150, 4.50),
            ("Paracetamol 650mg (Dolo)", "Acetaminophen", "Analgesic & Antipyretic", "tablet", 100, 500, 1.80),
            ("Ibuprofen 400mg", "Ibuprofen", "NSAID", "tablet", 60, 200, 2.50),
            ("Metformin 500mg (Glycomet)", "Metformin Hydrochloride", "Antidiabetic", "tablet", 80, 300, 3.20),
            ("Atorvastatin 10mg (Atorva)", "Atorvastatin Calcium", "Cardiovascular", "tablet", 40, 180, 8.50),
            ("Pantoprazole 40mg (Pan 40)", "Pantoprazole Sodium", "Gastrointestinal", "tablet", 50, 250, 7.50),
            ("Amlodipine 5mg (Amlong)", "Amlodipine Besylate", "Cardiovascular", "tablet", 40, 220, 3.50),
            ("Telmisartan 40mg (Telma)", "Telmisartan", "Cardiovascular", "tablet", 40, 180, 6.40),
            ("Azithromycin 500mg (Azithral)", "Azithromycin", "Antibiotic", "tablet", 30, 100, 22.00),
            ("Thyronorm 50mcg", "Levothyroxine Sodium", "Endocrine", "tablet", 50, 200, 2.80),
            ("Asthalin Inhaler", "Salbutamol", "Respiratory", "inhaler", 20, 60, 135.00),
            ("Cetirizine 10mg (Cetzine)", "Cetirizine Hydrochloride", "Antihistamine", "tablet", 50, 180, 2.20),
            ("Metoprolol 25mg (Betaloc)", "Metoprolol Tartrate", "Cardiovascular", "tablet", 40, 120, 4.50),
            ("Losartan 50mg (Losar)", "Losartan Potassium", "Cardiovascular", "tablet", 40, 140, 5.50),
            ("Rabeprazole 20mg (Razo)", "Rabeprazole Sodium", "Gastrointestinal", "tablet", 30, 90, 8.00),
            ("Ciprofloxacin 500mg (Ciplox)", "Ciprofloxacin", "Antibiotic", "tablet", 25, 70, 7.50),
            ("Doxycycline 100mg (Doxt)", "Doxycycline Hyclate", "Antibiotic", "capsule", 30, 85, 6.00),
            ("Gabapentin 300mg (Gabapin)", "Gabapentin", "Neurology", "capsule", 40, 110, 14.50),
            ("Chlorthalidone 12.5mg", "Chlorthalidone", "Cardiovascular", "tablet", 35, 120, 3.50),
            ("Wysolone 10mg", "Prednisolone", "Corticosteroid", "tablet", 30, 90, 2.80),
            ("Escitalopram 10mg (Nexito)", "Escitalopram Oxalate", "Psychiatry", "tablet", 30, 100, 9.50),
            ("Torsemide 10mg (Dytor)", "Torsemide", "Cardiovascular", "tablet", 30, 110, 5.00),
            ("Tramadol 50mg (Ultracet)", "Tramadol + Paracetamol", "Analgesic", "tablet", 25, 60, 12.00),
            ("Clopidogrel 75mg (Clopilet)", "Clopidogrel Bisulfate", "Cardiovascular", "tablet", 30, 85, 11.00),
            ("Montair-LC", "Montelukast + Levocetirizine", "Respiratory", "tablet", 30, 110, 15.00),
            ("Insulin Lantus 100IU", "Insulin Glargine", "Antidiabetic", "vial", 15, 30, 680.00),
            ("Fortwin Injection", "Pentazocine", "Analgesic", "ampoule", 15, 8, 25.00),  # Low stock test!
            ("Monocef 1g Injection", "Ceftriaxone Sodium", "Antibiotic", "vial", 25, 12, 65.00),   # Low stock test!
            ("Normal Saline 0.9% 500ml", "Sodium Chloride", "IV Fluids", "bottle", 50, 250, 35.00),
            ("RL (Ringer Lactate) 500ml", "Lactated Ringer", "IV Fluids", "bottle", 40, 180, 42.00),
        ]

        for idx, (name, gen_name, cat, unit, reorder, qty, cost) in enumerate(medicines_catalog):
            med = Medicine(
                name=name,
                generic_name=gen_name,
                category=cat,
                unit=unit,
                reorder_level=reorder,
            )
            db.add(med)
            await db.flush()

            exp_date = today + timedelta(days=18 if idx in [2, 10] else 365)
            batch = MedicineBatch(
                medicine_id=med.id,
                batch_no=f"BAT-UTK-2026-{100 + idx}",
                expiry_date=exp_date,
                quantity_in=qty,
                quantity_out=0,
                unit_cost=cost,
                supplier="Utkal Medicos & Pharma Distributors",
            )
            db.add(batch)

        await db.commit()
        print("[SUCCESS] Utkal Hospital database successfully initialized and seeded with Indian data!")


if __name__ == "__main__":
    asyncio.run(seed(drop_first=True))
