"""Initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-23 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Departments
    op.create_table(
        'departments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('floor', sa.String(length=50), nullable=True),
        sa.Column('head_doctor_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_departments_name'), 'departments', ['name'], unique=True)
    op.create_index(op.f('ix_departments_id'), 'departments', ['id'], unique=False)

    # Doctors
    op.create_table(
        'doctors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('specialization', sa.String(length=255), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=False),
        sa.Column('qualification', sa.String(length=255), nullable=False),
        sa.Column('experience_years', sa.Integer(), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('consultation_fee', sa.Float(), nullable=False),
        sa.Column('available_days', sa.JSON(), nullable=False),
        sa.Column('working_hours_start', sa.String(length=10), nullable=False),
        sa.Column('working_hours_end', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_doctors_full_name'), 'doctors', ['full_name'], unique=False)
    op.create_index(op.f('ix_doctors_id'), 'doctors', ['id'], unique=False)
    op.create_index(op.f('ix_doctors_specialization'), 'doctors', ['specialization'], unique=False)

    # Patients
    op.create_table(
        'patients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('gender', sa.String(length=20), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('blood_group', sa.String(length=10), nullable=True),
        sa.Column('allergies', sa.Text(), nullable=True),
        sa.Column('medical_history', sa.Text(), nullable=True),
        sa.Column('emergency_contact', sa.String(length=255), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patients_email'), 'patients', ['email'], unique=False)
    op.create_index(op.f('ix_patients_full_name'), 'patients', ['full_name'], unique=False)
    op.create_index(op.f('ix_patients_id'), 'patients', ['id'], unique=False)
    op.create_index(op.f('ix_patients_is_deleted'), 'patients', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_patients_phone'), 'patients', ['phone'], unique=False)

    # Appointments
    op.create_table(
        'appointments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('appointment_date', sa.Date(), nullable=False),
        sa.Column('time_slot', sa.String(length=20), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('diagnosis', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('recurrence_pattern', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_appointments_appointment_date'), 'appointments', ['appointment_date'], unique=False)
    op.create_index(op.f('ix_appointments_doctor_id'), 'appointments', ['doctor_id'], unique=False)
    op.create_index(op.f('ix_appointments_id'), 'appointments', ['id'], unique=False)
    op.create_index(op.f('ix_appointments_patient_id'), 'appointments', ['patient_id'], unique=False)
    op.create_index(op.f('ix_appointments_status'), 'appointments', ['status'], unique=False)
    op.create_index(op.f('ix_appointments_time_slot'), 'appointments', ['time_slot'], unique=False)

    # Prescriptions
    op.create_table(
        'prescriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('visit_id', sa.Integer(), nullable=True),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('prescription_date', sa.Date(), nullable=False),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['visit_id'], ['appointments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prescriptions_doctor_id'), 'prescriptions', ['doctor_id'], unique=False)
    op.create_index(op.f('ix_prescriptions_id'), 'prescriptions', ['id'], unique=False)
    op.create_index(op.f('ix_prescriptions_patient_id'), 'prescriptions', ['patient_id'], unique=False)

    # Prescription Items
    op.create_table(
        'prescription_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prescription_id', sa.Integer(), nullable=False),
        sa.Column('medicine_name', sa.String(length=255), nullable=False),
        sa.Column('dosage', sa.String(length=100), nullable=False),
        sa.Column('frequency', sa.String(length=100), nullable=False),
        sa.Column('duration', sa.String(length=100), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['prescription_id'], ['prescriptions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Lab Tests
    op.create_table(
        'lab_tests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('test_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('scheduled_date', sa.Date(), nullable=False),
        sa.Column('report_file', sa.String(length=500), nullable=True),
        sa.Column('findings', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('critical_value', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lab_tests_critical_value'), 'lab_tests', ['critical_value'], unique=False)
    op.create_index(op.f('ix_lab_tests_id'), 'lab_tests', ['id'], unique=False)
    op.create_index(op.f('ix_lab_tests_patient_id'), 'lab_tests', ['patient_id'], unique=False)
    op.create_index(op.f('ix_lab_tests_status'), 'lab_tests', ['status'], unique=False)

    # Invoices
    op.create_table(
        'invoices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_number', sa.String(length=50), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('subtotal', sa.Float(), nullable=False),
        sa.Column('discount', sa.Float(), nullable=False),
        sa.Column('tax', sa.Float(), nullable=False),
        sa.Column('total', sa.Float(), nullable=False),
        sa.Column('amount_paid', sa.Float(), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('payment_status', sa.String(length=50), nullable=False),
        sa.Column('provider_name', sa.String(length=255), nullable=True),
        sa.Column('policy_number', sa.String(length=100), nullable=True),
        sa.Column('claim_status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoices_id'), 'invoices', ['id'], unique=False)
    op.create_index(op.f('ix_invoices_invoice_number'), 'invoices', ['invoice_number'], unique=True)
    op.create_index(op.f('ix_invoices_patient_id'), 'invoices', ['patient_id'], unique=False)
    op.create_index(op.f('ix_invoices_payment_status'), 'invoices', ['payment_status'], unique=False)

    # Invoice Items
    op.create_table(
        'invoice_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Medicines
    op.create_table(
        'medicines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('generic_name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('reorder_level', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_medicines_category'), 'medicines', ['category'], unique=False)
    op.create_index(op.f('ix_medicines_generic_name'), 'medicines', ['generic_name'], unique=False)
    op.create_index(op.f('ix_medicines_id'), 'medicines', ['id'], unique=False)
    op.create_index(op.f('ix_medicines_name'), 'medicines', ['name'], unique=False)

    # Medicine Batches
    op.create_table(
        'medicine_batches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('medicine_id', sa.Integer(), nullable=False),
        sa.Column('batch_no', sa.String(length=100), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=False),
        sa.Column('quantity_in', sa.Integer(), nullable=False),
        sa.Column('quantity_out', sa.Integer(), nullable=False),
        sa.Column('current_stock', sa.Integer(), nullable=False),
        sa.Column('unit_cost', sa.Float(), nullable=False),
        sa.Column('supplier', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['medicine_id'], ['medicines.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_medicine_batches_batch_no'), 'medicine_batches', ['batch_no'], unique=False)
    op.create_index(op.f('ix_medicine_batches_expiry_date'), 'medicine_batches', ['expiry_date'], unique=False)
    op.create_index(op.f('ix_medicine_batches_id'), 'medicine_batches', ['id'], unique=False)
    op.create_index(op.f('ix_medicine_batches_medicine_id'), 'medicine_batches', ['medicine_id'], unique=False)

    # Stock Movements
    op.create_table(
        'stock_movements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('medicine_id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column('movement_type', sa.String(length=10), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('prescription_id', sa.Integer(), nullable=True),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['batch_id'], ['medicine_batches.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['medicine_id'], ['medicines.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['prescription_id'], ['prescriptions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('stock_movements')
    op.drop_table('medicine_batches')
    op.drop_table('medicines')
    op.drop_table('invoice_items')
    op.drop_table('invoices')
    op.drop_table('lab_tests')
    op.drop_table('prescription_items')
    op.drop_table('prescriptions')
    op.drop_table('appointments')
    op.drop_table('patients')
    op.drop_table('doctors')
    op.drop_table('departments')
    op.drop_table('users')
