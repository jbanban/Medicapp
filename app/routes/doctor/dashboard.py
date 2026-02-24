from datetime import date, datetime
from flask import render_template, abort
from flask_login import current_user, login_required
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.account import Account
from app.models.payment import PaymentRecord
from app.services.patient_cache import get_patient_cache
from collections import defaultdict
from sqlalchemy import func, extract
from app import db

from . import doctor_bp



# =============================================================================
#  HELPER: build monthly appointment counts for the current year
# =============================================================================
MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]

def _monthly_appointment_counts(doctor_id: int) -> dict:
    """
    Returns an ordered dict  { 'Jan': n, 'Feb': n, … 'Dec': n }
    for the current calendar year, filtered to the given doctor.
    """
    current_year = datetime.now().year

    rows = (
        db.session.query(
            extract("month", Appointment.appointment_date).label("month"),
            func.count(Appointment.appointment_id).label("count"),
        )
        .filter(
            Appointment.doctor_id == doctor_id,
            extract("year", Appointment.appointment_date) == current_year,
        )
        .group_by("month")
        .all()
    )

    # Seed every month with 0 so the chart always has 12 data points
    counts = {name: 0 for name in MONTH_NAMES}
    for row in rows:
        month_name = MONTH_NAMES[int(row.month) - 1]
        counts[month_name] = row.count

    return counts



# =============================================================================
#  HELPER: revenue totals
# =============================================================================
def _get_revenue(doctor_id: int) -> tuple:
    """
    Returns (total_amount_all_time, total_amount_this_month).
    Adjust the Payment model/columns to match yours.
    """
    today = date.today()

    total_amount = (
        db.session.query(func.coalesce(func.sum(PaymentRecord.amount), 0))
        .join(Appointment, Appointment.appointment_id == PaymentRecord.appointment_id)
        .filter(Appointment.doctor_id == doctor_id)
        .scalar()
    )

    total_amount_this_month = (
        db.session.query(func.coalesce(func.sum(PaymentRecord.amount), 0))
        .join(Appointment, Appointment.appointment_id == PaymentRecord.appointment_id)
        .filter(
            Appointment.doctor_id == doctor_id,
            extract("month", PaymentRecord.created_at) == today.month,
            extract("year",  PaymentRecord.created_at) == today.year,
        )
        .scalar()
    )

    return round(float(total_amount), 2), round(float(total_amount_this_month), 2)


# =============================================================================
#  HELPER: appointment status breakdown (for the summary strip)
# =============================================================================
def _get_appointment_status_counts(doctor_id: int) -> dict:
    """
    Returns { 'Completed': n, 'Upcoming': n, 'Cancelled': n }
    """
    rows = (
        db.session.query(
            Appointment.status,
            func.count(Appointment.appointment_id).label("count"),
        )
        .filter(Appointment.doctor_id == doctor_id)
        .group_by(Appointment.status)
        .all()
    )

    status_map = defaultdict(int)
    for row in rows:
        status_map[row.status] = row.count

    return {
        "completed":  status_map.get("Completed", 0),
        "upcoming":   status_map.get("Confirmed",  0) + status_map.get("Pending", 0),
        "cancelled":  status_map.get("Cancelled",  0),
    }


# =============================================================================
#  HELPER: today's appointments (for the schedule sidebar)
# =============================================================================
def _get_todays_appointments(doctor_id: int) -> list:
    """
    Returns today's appointments ordered by time, limited to a safe cap.
    """
    today = date.today()

    return (
        Appointment.query
        .filter(
            Appointment.doctor_id   == doctor_id,
            Appointment.appointment_date == today,
        )
        .order_by(Appointment.appointment_time)
        .limit(10)
        .all()
    )


def get_doctor_dashboard_counts(doctor_id):
    
    today = date.today()
    current_year = today.year
    current_month = today.month

    total_patients = (
        db.session.query(func.count(func.distinct(Appointment.patient_id)))
        .filter(Appointment.doctor_id == doctor_id)
        .scalar()
    )

    total_booked_appointments = (
        db.session.query(func.count(Appointment.appointment_id))
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == "Booked"
        )
        .scalar()
    )

    total_staff = (
        db.session.query(func.count(Account.account_id))
        .filter(
            Account.role == "Doctor",
            Account.role == "Secretary",
        ).scalar()
    )

    total_amount = (
        db.session.query(func.coalesce(func.sum(PaymentRecord.amount), 0))
        .scalar()
    )

    total_amount_this_month = (
        db.session.query(func.coalesce(func.sum(PaymentRecord.amount), 0))
        .join(Appointment)
        .filter(Appointment.doctor_id == doctor_id)
        .scalar()
    )

    return {
        "total_patients": total_patients or 0,
        "total_booked_appointments": total_booked_appointments or 0,
        "total_staff": total_staff or 0,
        "total_amount": total_amount or 0,
        "total_amount_month": total_amount_this_month or 0
    }


@doctor_bp.route('/dashboard')
@login_required
def doctor_dashboard():

    if current_user.role not in ["doctor", "secretary"]:
        abort(403)

    doctor = Doctor.query.filter_by(account_id=current_user.account_id).first()
    doctor_id = doctor.doctor_id

    # ── Gather all statistics ─────────────────────────────────────────────────
    monthly_counts      = _monthly_appointment_counts(doctor_id)
    total_amount, total_amount_this_month = _get_revenue(doctor_id)
    appointment_status  = _get_appointment_status_counts(doctor_id)
    todays_appointments = _get_todays_appointments(doctor_id)

    statistics = {
        "monthly_counts":     monthly_counts,
        "appointment_status": appointment_status,   # used by summary strip
    }

    appointments = Appointment.query.filter_by(
        doctor_id=doctor.doctor_id
    ).all()

    patients = []
    total_payment = 0

    for appt in appointments:
        decrypted_patient = get_patient_cache(appt.patient_id)

        if decrypted_patient:
            patients.append(decrypted_patient)

        if appt.payments:
            total_payment += sum(p.amount for p in appt.payments)


    total_doctor_count = get_doctor_dashboard_counts(doctor.doctor_id)

    return render_template(
        'doctor/doctor_dashboard.html',
        doctor                  = doctor,
        appointments            = appointments,
        patients                = patients,
        total_payment           = total_payment,
        total_count             = total_doctor_count,
        total_amount            = f"{total_amount:,.2f}",
        total_amount_this_month = f"{total_amount_this_month:,.2f}",
        statistics              = statistics,
        appointment             = todays_appointments,
    )
