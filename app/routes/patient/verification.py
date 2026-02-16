from flask import redirect, render_template, request, url_for, flash, jsonify
from flask_login import current_user, login_required
from app.models.patient import Patient
from app.services.sms_services import send_sms_otp
from app.utils.email_service import send_email
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from app import db
import random

from . import patient_bp


# ===============================
# START VERIFICATION (Generate + Send OTP)
# ===============================
@patient_bp.route("/start_verification/<method>")
@login_required
def start_verification(method):

    if method not in ["email", "sms"]:
        flash("Invalid verification method.", "danger")
        return redirect(url_for("patient.patient_profile"))

    patient = Patient.query.filter_by(
        account_id=current_user.account_id
    ).first_or_404()

    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))

    hashed_otp = generate_password_hash(otp)
    expiry_time = datetime.utcnow() + timedelta(minutes=5)

    if method == "email":
        if not patient.email:
            flash("No email found.", "danger")
            return redirect(url_for("patient.patient_profile"))

        patient.email_otp = hashed_otp
        patient.email_otp_expiry = expiry_time

        send_email(
            subject="MedicApp Email Verification Code",
            recipients=[patient.email],
            body=f"""
                Hello {current_user.username},

                Your verification code is:

                {otp}

                This code will expire in 5 minutes.
                """
        )

    elif method == "sms":
        if not patient.phone_number:
            flash("No phone number found.", "danger")
            return redirect(url_for("patient.patient_profile"))

        patient.sms_otp = hashed_otp
        patient.sms_otp_expiry = expiry_time

        send_sms_otp(patient.phone_number, otp)

    db.session.commit()

    flash("Verification code sent successfully.", "success")

    return redirect(url_for("patient.verify_page", method=method))


# ===============================
# VERIFICATION PAGE
# ===============================
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


# ===============================
# SUBMIT OTP
# ===============================
@patient_bp.route("/verify/<method>", methods=["POST"])
@login_required
def verify_submit(method):

    otp_input = request.form.get("code")  # your input name is "code"

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

    # SUCCESS
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


# ===============================
# RESEND OTP (AJAX)
# ===============================
@patient_bp.route("/resend_otp/<method>", methods=["POST"])
@login_required
def resend_otp(method):

    if method not in ["email", "sms"]:
        return jsonify({"success": False}), 400

    patient = Patient.query.filter_by(
        account_id=current_user.account_id
    ).first_or_404()

    otp = str(random.randint(100000, 999999))
    hashed_otp = generate_password_hash(otp)
    expiry_time = datetime.utcnow() + timedelta(minutes=5)

    if method == "email":
        patient.email_otp = hashed_otp
        patient.email_otp_expiry = expiry_time

        send_email(
            subject="MedicApp Email Verification Code",
            recipients=[patient.email],
            body=f"Your new verification code is: {otp}"
        )

    else:
        patient.sms_otp = hashed_otp
        patient.sms_otp_expiry = expiry_time

        send_sms_otp(patient.phone_number, otp)

    db.session.commit()

    return jsonify({"success": True})
