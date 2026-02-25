
from datetime import date
from flask import jsonify, render_template, request
from sqlalchemy import extract
from app.models.account import Account
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.payment import PaymentRecord
from app.utils.admin_only import admin_required
from . import admin_bp

def doctor_appointment_summary(data):
    doctor_id = data.get("doctor_id")
    month = data.get("month")

    if not month:
        return jsonify({"error": "Month required"}), 400

    year, month_num = month.split("-")

    query = Appointment.query.filter(
        Appointment.appointment_date.like(f"{year}-{month_num}%")
    )

    if doctor_id:
        query = query.filter(Appointment.doctor_id == int(doctor_id))

    appointments = query.all()

    rows = [{
        "date": a.appointment_date,
        "patient": a.patient.full_name if a.patient else "N/A",
        "status": a.status
    } for a in appointments]

    return jsonify({
        "doctor_id": doctor_id,
        "month": month,
        "rows": rows
    })



def patients_account_summary(data):
    month = data.get("month")

    if not month:
        return jsonify({"error": "Month is required"}), 400

    year, month_num = month.split("-")

    total_accounts = Account.query.filter(
        Account.role == "patient",
        Account.created_at.like(f"{year}-{month_num}%")
    ).count()

    return jsonify({
        "month": month,
        "total_accounts": total_accounts
    })



def doctors_revenue_summary(data):
    doctor_id = data.get("doctor_id")
    month = data.get("month")  # format: YYYY-MM

    if not month:
        return jsonify({"error": "Month is required"}), 400

    year, month_num = month.split("-")

    # Base query (filter by month using LIKE because date is string)
    query = Appointment.query.filter(
        Appointment.appointment_date.like(f"{year}-{month_num}%")
    )

    # Filter specific doctor if selected
    if doctor_id:
        query = query.filter(Appointment.doctor_id == int(doctor_id))

    appointments = query.all()

    rows = []
    total_revenue = 0

    for appointment in appointments:
        for payment in appointment.payments:

            # Optional: only count paid payments
            if payment.payment_status.lower() != "paid":
                continue

            rows.append({
                "date": appointment.appointment_date,
                "doctor": f"{appointment.doctor.firstname} {appointment.doctor.lastname}"
                          if appointment.doctor else "Unknown",
                "patient": appointment.patient.full_name
                           if appointment.patient else "N/A",
                "amount": float(payment.amount)
            })

            total_revenue += float(payment.amount)

    return jsonify({
        "doctor_id": doctor_id,
        "month": month,
        "rows": rows,
        "total_revenue": total_revenue
    })


def doctors_summary(data):
    doctor_id = data.get("doctor_id")  # optional
    month = data.get("month")          # required (YYYY-MM)

    if not month:
        return jsonify({"error": "Month is required"}), 400

    # Validate month format
    try:
        year, month_number = month.split("-")
        year = int(year)
        month_number = int(month_number)
    except ValueError:
        return jsonify({"error": "Invalid month format. Use YYYY-MM"}), 400

    # Base query
    query = Doctor.query.filter(
        extract("year", Doctor.created_at) == year,
        extract("month", Doctor.created_at) == month_number
    )

    # Optional doctor filter
    if doctor_id:
        query = query.filter(Doctor.doctor_id == doctor_id)

    doctors = query.order_by(Doctor.created_at.desc()).all()

    active_count = query.filter(Doctor.status == "active").count()
    inactive_count = query.filter(Doctor.status == "inactive").count()
    
    rows = [
        {
            "doctor": f"Dr. {doctor.firstname} {doctor.lastname}",
            "created_at": doctor.created_at.strftime("%Y-%m-%d"),
            "status": doctor.status.lower() if doctor.status else "inactive"
        }
        for doctor in doctors
    ]

    return jsonify({
        "rows": rows,
        "total": len(rows),
        "active": active_count,
        "inactive": inactive_count
    })


@admin_bp.route('/admin_reports', methods=['GET', 'POST'])
@admin_required
def admin_reports():
    if request.method == 'POST':
        return generate_report()

    doctors = Doctor.query.all()

    return render_template('admin/reports.html', doctors=doctors)


@admin_bp.route('/reports/generate', methods=['POST'])
@admin_required
def generate_report():
    data = request.get_json()
    report_type = data.get("report_type")

    if report_type == "patientsAccountSummary":
        return patients_account_summary(data)

    elif report_type == "doctorAppointmentSummary":
        return doctor_appointment_summary(data)

    elif report_type == "doctorsRevenueSummary":
        return doctors_revenue_summary(data)
    
    elif report_type == "doctorsSummary":
        return doctors_summary(data)

    return jsonify({"error": "Invalid report type"}), 400


