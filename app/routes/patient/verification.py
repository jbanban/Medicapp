from flask import redirect, render_template, request, url_for, flash
from flask_login import current_user, login_required
from app.models.patient import Patient
from app.services.sms_services import send_sms_otp
from app.utils.email_service import send_email
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from app import db
import random

from . import patient_bp


@patient_bp.route("/verify/<method>", methods=["GET"])
@login_required
def verify_page(method):
    if method not in ["email", "sms"]:
        flash("Invalid verification method.", "danger")
        return redirect(url_for("patient.patient_profile"))

    return render_template(
        "patient/verification_page.html",
        method=method
    )

def send_sms_verification():
    patient = Patient.query.filter_by(
        account_id=current_user.account_id
    ).first_or_404()

    send_sms_otp(patient, patient.phone_number)

    flash("Verification code sent to your mobile number.", "success")
    return redirect(url_for("patient.verify_page", method="sms"))

def email_verification():
    patient = Patient.query.filter_by(
        account_id=current_user.account_id
    ).first_or_404()

    receipt_email = patient.email

    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))

    patient.email_otp = generate_password_hash(otp)
    patient.email_otp_expiry = datetime.utcnow() + timedelta(minutes=5)
    db.session.commit()

    body = f"""
        Hello,

        Your MedicApp email verification code is:

        {otp}

        This code will expire in 5 minutes.
        """

    send_email(
        subject="MedicApp Email Verification Code",
        recipients=[receipt_email],
        body=body
    )

    flash("Verification code sent to your email.", "success")
    return redirect(url_for("patient.verify_email_page"))



@patient_bp.route("/verify/<method>", methods=["POST"])
@login_required
def verify_submit(method):
    otp_input = request.form.get("otp")

    patient = Patient.query.filter_by(
        account_id=current_user.account_id
    ).first_or_404()

    if method == "email":
        stored_otp = patient.email_otp
        expiry = patient.email_otp_expiry
    elif method == "sms":
        stored_otp = patient.sms_otp
        expiry = patient.sms_otp_expiry
    else:
        flash("Invalid verification method.", "danger")
        return redirect(url_for("patient.patient_profile"))

    if not stored_otp or not expiry:
        flash("No verification request found.", "danger")
        return redirect(url_for("patient.patient_profile"))

    if datetime.utcnow() > expiry:
        flash("OTP expired. Please request a new one.", "danger")
        return redirect(url_for("patient.verify_page", method=method))

    if not check_password_hash(stored_otp, otp_input):
        flash("Invalid OTP.", "danger")
        return redirect(url_for("patient.verify_page", method=method))

    # Success
    if method == "email":
        patient.email_verified = True
        patient.email_otp = None
        patient.email_otp_expiry = None
    else:
        patient.sms_verified = True
        patient.sms_otp = None
        patient.sms_otp_expiry = None

    db.session.commit()

    flash(f"{method.upper()} verified successfully!", "success")
    return redirect(url_for("patient.patient_profile"))

@patient_bp.route("/resend_otp/<method>", methods=["POST"])
@login_required
def resend_otp(method):

    patient = Patient.query.filter_by(
        account_id=current_user.account_id
    ).first_or_404()

    if method == "email":
        email_verification(patient.email)

    elif method == "sms":
        send_sms_otp(patient, patient.phone)

    else:
        return {"success": False, "message": "Invalid method"}, 400

    return {"success": True}
