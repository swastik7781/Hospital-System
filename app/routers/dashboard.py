from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.department import Department
from app.models.appointment import Appointment, AppointmentStatus
from app.models.prescription import Prescription
from app.models.lab_test import LabTest, LabTestStatus
from app.models.billing import Invoice, PaymentStatus
from app.models.pharmacy import Medicine, MedicineBatch
from app.schemas.dashboard import (
    AdminDashboardResponse,
    DashboardKPIs,
    ChartDataPoint,
    ActivityItem,
    AlertItem,
)
from app.auth.dependencies import require_roles, get_current_active_user
from app.crud.pharmacy import get_low_stock_medicines, get_expiring_batches
from app.crud.patient import get_patient_by_user_id

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/admin",
    response_model=AdminDashboardResponse,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.DOCTOR, UserRole.RECEPTIONIST, UserRole.PATIENT]))],
)
async def get_admin_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()
    now = datetime.utcnow()
    start_today = datetime(now.year, now.month, now.day)
    start_month = datetime(now.year, now.month, 1)

    # ================= ROLE: PATIENT =================
    if current_user.role == UserRole.PATIENT:
        patient = await get_patient_by_user_id(db, current_user.id)
        p_id = patient.id if patient else None

        if p_id:
            # Patient appointments
            p_total_visits = (await db.execute(select(func.count(Appointment.id)).where(Appointment.patient_id == p_id))).scalar_one()
            p_today_app = (await db.execute(select(func.count(Appointment.id)).where(and_(Appointment.patient_id == p_id, Appointment.appointment_date >= today)))).scalar_one()
            
            # Patient invoices
            p_bills_res = await db.execute(select(func.sum(Invoice.total)).where(Invoice.patient_id == p_id))
            p_bills_total = float(p_bills_res.scalar_one() or 0.0)
            
            # Active prescriptions
            p_presc_count = (await db.execute(select(func.count(Prescription.id)).where(Prescription.patient_id == p_id))).scalar_one()
            
            # Pending reports
            p_rep_count = (await db.execute(select(func.count(LabTest.id)).where(and_(LabTest.patient_id == p_id, LabTest.status != LabTestStatus.COMPLETED)))).scalar_one()

            # Visits by day (patient's past visits)
            app_by_day = []
            for i in range(13, -1, -1):
                day_date = today - timedelta(days=i)
                cnt = (await db.execute(select(func.count(Appointment.id)).where(and_(Appointment.patient_id == p_id, Appointment.appointment_date == day_date)))).scalar_one()
                app_by_day.append(ChartDataPoint(label=day_date.strftime("%b %d"), value=cnt))

            # Patient Recent activity
            recent_activity = []
            rec_apps = await db.execute(
                select(Appointment).options(selectinload(Appointment.doctor)).where(Appointment.patient_id == p_id).order_by(Appointment.id.desc()).limit(3)
            )
            for a in rec_apps.scalars().all():
                d_name = a.doctor.full_name if a.doctor else "Specialist"
                recent_activity.append(
                    ActivityItem(
                        id=f"app-{a.id}",
                        type="appointment",
                        title=f"Appointment {a.status.value.title()}",
                        description=f"Consultation with {d_name} for '{a.reason}'",
                        timestamp=str(a.appointment_date),
                        badge_color="#0D9488" if a.status == AppointmentStatus.CONFIRMED else "#3B82F6",
                    )
                )

            # Patient alerts
            alerts = []
            crit_labs = await db.execute(
                select(LabTest).where(and_(LabTest.patient_id == p_id, LabTest.critical_value.is_(True))).order_by(LabTest.id.desc()).limit(2)
            )
            for cl in crit_labs.scalars().all():
                alerts.append(
                    AlertItem(
                        id=f"crit-{cl.id}",
                        category="critical_lab",
                        title="Critical Diagnostic Report",
                        message=f"{cl.test_type.value.upper()} flagged with findings. Please consult your physician.",
                        severity="error",
                        created_at=str(cl.scheduled_date),
                    )
                )

            return AdminDashboardResponse(
                kpis=DashboardKPIs(
                    total_patients=p_total_visits,
                    today_appointments=p_today_app,
                    revenue_today=0.0,
                    revenue_this_month=p_bills_total,
                    active_prescriptions=p_presc_count,
                    low_stock_count=0,
                    pending_reports=p_rep_count,
                ),
                appointments_by_day=app_by_day,
                revenue_trend=[],
                visits_by_department=[],
                top_doctors=[],
                recent_activity=recent_activity,
                alerts=alerts,
            )

    # ================= ROLE: DOCTOR =================
    if current_user.role == UserRole.DOCTOR:
        doc_res = await db.execute(select(Doctor).where(Doctor.user_id == current_user.id))
        doctor = doc_res.scalar_one_or_none()
        doc_id = doctor.id if doctor else None

        if doc_id:
            d_patients_count = (await db.execute(select(func.count(func.distinct(Appointment.patient_id))).where(Appointment.doctor_id == doc_id))).scalar_one()
            d_today_app = (await db.execute(select(func.count(Appointment.id)).where(and_(Appointment.doctor_id == doc_id, Appointment.appointment_date == today)))).scalar_one()
            d_presc_count = (await db.execute(select(func.count(Prescription.id)).where(Prescription.doctor_id == doc_id))).scalar_one()
            d_reports_count = (await db.execute(select(func.count(LabTest.id)).where(and_(LabTest.doctor_id == doc_id, LabTest.status != LabTestStatus.COMPLETED)))).scalar_one()

            # Visits by day for this doctor
            app_by_day = []
            for i in range(13, -1, -1):
                day_date = today - timedelta(days=i)
                cnt = (await db.execute(select(func.count(Appointment.id)).where(and_(Appointment.doctor_id == doc_id, Appointment.appointment_date == day_date)))).scalar_one()
                app_by_day.append(ChartDataPoint(label=day_date.strftime("%b %d"), value=cnt))

            recent_activity = []
            rec_apps = await db.execute(
                select(Appointment).options(selectinload(Appointment.patient)).where(Appointment.doctor_id == doc_id).order_by(Appointment.id.desc()).limit(4)
            )
            for a in rec_apps.scalars().all():
                p_name = a.patient.full_name if a.patient else "Patient"
                recent_activity.append(
                    ActivityItem(
                        id=f"app-{a.id}",
                        type="appointment",
                        title=f"Consultation {a.status.value.title()}",
                        description=f"Patient: {p_name} ({a.time_slot}) - '{a.reason}'",
                        timestamp=str(a.appointment_date),
                        badge_color="#0D9488" if a.status == AppointmentStatus.CONFIRMED else "#3B82F6",
                    )
                )

            alerts = []
            crit_labs = await db.execute(
                select(LabTest).options(selectinload(LabTest.patient)).where(and_(LabTest.doctor_id == doc_id, LabTest.critical_value.is_(True))).order_by(LabTest.id.desc()).limit(3)
            )
            for cl in crit_labs.scalars().all():
                p_name = cl.patient.full_name if cl.patient else "Patient"
                alerts.append(
                    AlertItem(
                        id=f"crit-{cl.id}",
                        category="critical_lab",
                        title="Abnormal / Critical Diagnostic Result",
                        message=f"Patient {p_name}: {cl.test_type.value.upper()} flagged. Immediate clinical review required.",
                        severity="error",
                        created_at=str(cl.scheduled_date),
                    )
                )

            return AdminDashboardResponse(
                kpis=DashboardKPIs(
                    total_patients=d_patients_count,
                    today_appointments=d_today_app,
                    revenue_today=0.0,
                    revenue_this_month=0.0,
                    active_prescriptions=d_presc_count,
                    low_stock_count=0,
                    pending_reports=d_reports_count,
                ),
                appointments_by_day=app_by_day,
                revenue_trend=[],
                visits_by_department=[],
                top_doctors=[],
                recent_activity=recent_activity,
                alerts=alerts,
            )

    # ================= ROLE: ADMIN / RECEPTIONIST =================
    p_res = await db.execute(select(func.count(Patient.id)).where(Patient.is_deleted.is_(False)))
    total_patients = p_res.scalar_one()

    a_today_res = await db.execute(select(func.count(Appointment.id)).where(Appointment.appointment_date == today))
    today_appointments = a_today_res.scalar_one()

    rev_today_res = await db.execute(
        select(func.sum(Invoice.amount_paid)).where(Invoice.created_at >= start_today)
    )
    revenue_today = float(rev_today_res.scalar_one() or 0.0)

    rev_month_res = await db.execute(
        select(func.sum(Invoice.amount_paid)).where(Invoice.created_at >= start_month)
    )
    revenue_this_month = float(rev_month_res.scalar_one() or 0.0)

    thirty_days_ago = today - timedelta(days=30)
    presc_res = await db.execute(select(func.count(Prescription.id)).where(Prescription.prescription_date >= thirty_days_ago))
    active_prescriptions = presc_res.scalar_one()

    low_stock_list = await get_low_stock_medicines(db)
    low_stock_count = len(low_stock_list)

    reports_res = await db.execute(select(func.count(LabTest.id)).where(LabTest.status != LabTestStatus.COMPLETED))
    pending_reports = reports_res.scalar_one()

    kpis = DashboardKPIs(
        total_patients=total_patients,
        today_appointments=today_appointments,
        revenue_today=revenue_today,
        revenue_this_month=revenue_this_month,
        active_prescriptions=active_prescriptions,
        low_stock_count=low_stock_count,
        pending_reports=pending_reports,
    )

    # Appointments by day (last 14 days)
    app_by_day = []
    for i in range(13, -1, -1):
        day_date = today - timedelta(days=i)
        day_res = await db.execute(select(func.count(Appointment.id)).where(Appointment.appointment_date == day_date))
        cnt = day_res.scalar_one()
        app_by_day.append(ChartDataPoint(label=day_date.strftime("%b %d"), value=cnt))

    # Revenue trend
    rev_trend = []
    for w in range(5, -1, -1):
        w_start = start_today - timedelta(days=w * 7 + 6)
        w_end = start_today - timedelta(days=w * 7)
        w_res = await db.execute(
            select(func.sum(Invoice.amount_paid)).where(
                and_(Invoice.created_at >= w_start, Invoice.created_at <= w_end + timedelta(days=1))
            )
        )
        val = float(w_res.scalar_one() or 0.0)
        rev_trend.append(ChartDataPoint(label=f"Wk -{w}" if w > 0 else "This Wk", value=val))

    # Visits by department
    dept_res = await db.execute(
        select(Department.name, func.count(Appointment.id))
        .join(Doctor, Doctor.department_id == Department.id)
        .join(Appointment, Appointment.doctor_id == Doctor.id)
        .group_by(Department.name)
    )
    visits_by_dept = [ChartDataPoint(label=row[0], value=row[1]) for row in dept_res.all()]

    # Top doctors
    doc_res = await db.execute(
        select(Doctor.full_name, func.count(Appointment.id))
        .join(Appointment, Appointment.doctor_id == Doctor.id)
        .group_by(Doctor.full_name)
        .order_by(func.count(Appointment.id).desc())
        .limit(5)
    )
    top_doctors = [ChartDataPoint(label=row[0], value=row[1]) for row in doc_res.all()]

    # Recent activity
    recent_activity = []
    rec_apps = await db.execute(
        select(Appointment).options(selectinload(Appointment.patient), selectinload(Appointment.doctor)).order_by(Appointment.id.desc()).limit(3)
    )
    for a in rec_apps.scalars().all():
        p_name = a.patient.full_name if a.patient else "Patient"
        d_name = a.doctor.full_name if a.doctor else "Doctor"
        recent_activity.append(
            ActivityItem(
                id=f"app-{a.id}",
                type="appointment",
                title=f"Appointment {a.status.value.title()}",
                description=f"{p_name} with {d_name} for '{a.reason}'",
                timestamp=str(a.appointment_date),
                badge_color="#0D9488" if a.status == AppointmentStatus.CONFIRMED else "#3B82F6",
            )
        )

    # Alerts
    alerts = []
    crit_labs = await db.execute(
        select(LabTest).options(selectinload(LabTest.patient)).where(LabTest.critical_value.is_(True)).order_by(LabTest.id.desc()).limit(3)
    )
    for cl in crit_labs.scalars().all():
        alerts.append(
            AlertItem(
                id=f"crit-{cl.id}",
                category="critical_lab",
                title="Critical Lab Result Flagged",
                message=f"Patient {cl.patient.full_name if cl.patient else 'Unknown'}: {cl.test_type.value.upper()} flagged with abnormal values. Immediate physician review needed.",
                severity="error",
                created_at=str(cl.scheduled_date),
            )
        )

    exp_batches = await get_expiring_batches(db, days=30)
    for eb in exp_batches[:3]:
        alerts.append(
            AlertItem(
                id=f"exp-{eb['batch_id']}",
                category="expiring_medicine",
                title=f"Medicine Expiring Soon: {eb['medicine_name']}",
                message=f"Batch {eb['batch_no']} has {eb['current_stock']} units expiring in {eb['days_until_expiry']} days.",
                severity="warning",
                created_at=str(date.today()),
            )
        )

    return AdminDashboardResponse(
        kpis=kpis,
        appointments_by_day=app_by_day,
        revenue_trend=rev_trend,
        visits_by_department=visits_by_dept,
        top_doctors=top_doctors,
        recent_activity=recent_activity,
        alerts=alerts,
    )
