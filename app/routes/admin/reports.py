
from datetime import date
from flask import jsonify, render_template, request
from sqlalchemy import extract
from app.models.account import Account
from app.models.appointment import Appointment
from app.models.payment import PaymentRecord
from app.utils.admin_only import admin_required
from . import admin_bp

def doctor_appointment_summary(data):
    doctor_id = data.get("doctor_id")
    month = data.get("month")  # format: YYYY-MM

    year, month_num = month.split("-")

    appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        extract("year", Appointment.date) == int(year),
        extract("month", Appointment.date) == int(month_num)
    ).all()

    rows = [{
        "date": a.date.strftime("%Y-%m-%d"),
        "patient": a.patient.name,
        "status": a.status
    } for a in appointments]

    return jsonify({
        "doctor_id": doctor_id,
        "month": month,
        "rows": rows
    })


def patients_account_summary(data):
    month = data.get("month")  # YYYY-MM
    year, month_num = month.split("-")

    accounts = Account.query.filter(
        extract("year", Account.created_at) == int(year),
        extract("month", Account.created_at) == int(month_num)
    ).all()

    rows = [{
        "patient": acc.patient.name,
        "amount": acc.balance,
        "status": "Paid" if acc.balance == 0 else "Unpaid"
    } for acc in accounts]

    return jsonify({
        "month": month,
        "rows": rows
    })

def doctors_revenue_summary(data):
    doctor_id = data.get("doctor_id")
    month = data.get("month")  # YYYY-MM

    year, month_num = month.split("-")

    appointments = (
        Appointment.query
        .join(
            PaymentRecord,
            Appointment.appointment_id == PaymentRecord.appointment_id
        )
        .filter(
            Appointment.doctor_id == doctor_id,
            extract("year", Appointment.date) == int(year),
            extract("month", Appointment.date) == int(month_num)
        )
        .all()
    )


    rows = [{
        "date": a.date.strftime("%Y-%m-%d"),
        "patient": a.patient.name,
        "amount": a.amount
    } for a in appointments]

    total_revenue = sum(a.amount for a in appointments)

    return jsonify({
        "doctor_id": doctor_id,
        "month": month,
        "rows": rows,
        "total": total_revenue
    })

@admin_bp.route('/admin_reports', methods=['GET', 'POST'])
@admin_required
def admin_reports():
    if request.method == 'POST':
        return generate_report()

    doctors = Account.query.filter_by(role="doctor").all()
    return render_template('admin/reports.html', doctors=doctors)

def generate_report():
    data = request.get_json()
    report_type = data.get("report_type")

    if report_type == "doctorAppointmentSummary":
        return doctor_appointment_summary(data)

    elif report_type == "patientsAccountSummary":
        return patients_account_summary(data)

    elif report_type == "doctorsRevenueSummary":
        return doctors_revenue_summary(data)

    return jsonify({"error": "Invalid report type"}), 400

