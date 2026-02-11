from flask import json, jsonify, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import current_user, login_required
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.patient_history_background import PatientHistoryBackground
from app.models.medical_visibility import MedicalVisibility
from app.services.file_uploads import allowed_image
from app.services.patient_cache import get_patient_cache 
from app.services.empty_to_none import empty_to_none
from app.security.crypto import encrypt_value, decrypt_value, safe_decrypt
from app import db
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from . import patient_bp
from app.routes import patient




@patient_bp.route('/patient_profile')
@login_required
def patient_profile():
    
    patient = Patient.query.filter_by(account_id=current_user.account_id).first()
    if not patient:
        return redirect(url_for('patient.create_profile'))

    history = PatientHistoryBackground.query.filter_by(
        patient_id=patient.patient_id
    ).first()

    visibility = MedicalVisibility.query.filter_by(
        patient_id=patient.patient_id
    ).first()

    decrypted_patient = get_patient_cache(patient.patient_id)

    decrypted_patient_info = None
    if patient:
        decrypted_patient_info = {
            "gender": decrypt_value(patient.gender),
            "blood_type": safe_decrypt(patient.blood_type),
            "civil_status": decrypt_value(patient.civil_status),
            "birthdate": patient.birthdate,
            "age": patient.age,

            # CURRENT ADDRESS
            "current_house_no": safe_decrypt(patient.current_house_no),
            "current_street": safe_decrypt(patient.current_street),
            "current_barangay": decrypt_value(patient.current_barangay),
            "current_city": decrypt_value(patient.current_city),
            "current_province": decrypt_value(patient.current_province),
            "current_zipcode": decrypt_value(patient.current_zipcode),

            # PERMANENT ADDRESS
            "permanent_house_no": safe_decrypt(patient.permanent_house_no),
            "permanent_street": safe_decrypt(patient.permanent_street),
            "permanent_barangay": decrypt_value(patient.permanent_barangay),
            "permanent_city": decrypt_value(patient.permanent_city),
            "permanent_province": decrypt_value(patient.permanent_province),
            "permanent_zipcode": decrypt_value(patient.permanent_zipcode),

            # EMERGENCY CONTACT
            "ec_name": decrypt_value(patient.ec_name),
            "ec_relation": decrypt_value(patient.ec_relation),
            "ec_phone": decrypt_value(patient.ec_phone),
            "ec_address": decrypt_value(patient.ec_address),
        }

    decrypted_history = None
    if history:
        decrypted_history = {
            "pastMedicalHistory": decrypt_value(history.pastMedicalHistory),
            "beenHospitalized": decrypt_value(history.beenHospitalized),
            "hadSurgery": decrypt_value(history.hadSurgery),
            "allergies": decrypt_value(history.allergies),
            "ongoingMedications": decrypt_value(history.ongoingMedications),
            "familyHistory": decrypt_value(history.familyHistory),
        }

    visibility = MedicalVisibility.query.filter_by(
        patient_id=patient.patient_id
    ).first()

    return render_template(
        "patient/patient_profile.html",
        patient=decrypted_patient,
        patient_info=decrypted_patient_info,
        history=decrypted_history,
        visibility=visibility
    )



@patient_bp.route('/create_profile', methods=['GET', 'POST'])
@login_required
def create_profile():

    # Prevent duplicate profile creation
    existing = Patient.query.filter_by(account_id=current_user.account_id).first()
    if existing:
        return redirect(url_for('patient.patient_Dashboard'))

    errors = {}

    if request.method == 'POST':
        form = request.form

        # ---------------- BASIC INFO ----------------
        firstname = form.get('firstname', '').strip()
        middlename = empty_to_none(form.get('middlename', '').strip())
        lastname = form.get('lastname', '').strip()
        gender = form.get('gender', '').strip()
        birthdate_str = form.get('birthdate', '').strip()
        age = form.get('age', '').strip()
        blood_type = form.get('blood_type', '').strip()
        civil_status = form.get('civil_status', '').strip()

        # ---------------- CURRENT ADDRESS ------------------
        current_house_no = empty_to_none(form.get('current_house_no', '').strip())
        current_street = empty_to_none(form.get('current_street', '').strip())
        current_barangay = form.get('current_barangay', '').strip()
        current_city = form.get('current_city', '').strip()
        current_province = form.get('current_province', '').strip()
        current_zipcode = form.get('current_zipcode', '').strip()


        # ----------------- PERMANENT ADDRESS ----------------
        permanent_house_no = empty_to_none(form.get('permanent_house_no', '').strip())
        permanent_street = empty_to_none(form.get('permanent_street', '').strip())
        permanent_barangay = form.get('permanent_barangay', '').strip()
        permanent_city = form.get('permanent_city', '').strip()
        permanent_province = form.get('permanent_province', '').strip()
        permanent_zipcode = form.get('permanent_zipcode', '').strip()


        phone = form.get('phone', '').strip()
        email = form.get('email', '').strip()

        # ---------------- EMERGENCY CONTACT ----------------
        ec_name = form.get('ec_name', '').strip()
        ec_relation = form.get('ec_relation', '').strip()
        ec_phone = form.get('ec_phone', '').strip()
        ec_address = form.get('ec_address', '').strip()

        # ---------------- MEDICAL HISTORY ----------------
        pastMedicalHistory = form.get('pastMedicalHistory', '').strip()
        beenHospitalized = form.get('beenHospitalized', '').strip()
        hadSurgery = form.get('hadSurgery', '').strip()
        allergies = form.get('allergies', '').strip()
        ongoingMedications = form.get('ongoingMedications', '').strip()
        familyHistory = form.get('familyHistory', '').strip()

        # ---------------- VALIDATION ----------------

        if not firstname:
            errors['firstname'] = "First name is required"

        if not lastname:
            errors['lastname'] = "Last name is required"

        if not gender:
            errors['gender'] = "Gender is required"

        if not email:
            errors['email'] = "Email is required"

        if not phone:
            errors['phone'] = "Phone number is required"
        elif len(phone) < 10:
            errors['phone'] = "Phone number is too short"
        elif len(phone) > 13:
            errors['phone'] = "Phone number is too long"

        # Permanent address validation
        if not permanent_house_no:
            errors['permanent_house_no'] = "House / Unit No. is required"

        if not permanent_barangay:
            errors['permanent_barangay'] = "Barangay is required"

        if not permanent_city:
            errors['permanent_city'] = "City / Municipality is required"

        if not permanent_province:
            errors['permanent_province'] = "Province is required"

        if not permanent_zipcode:
            errors['permanent_zipcode'] = "Zip code is required"

        if current_zipcode and not current_zipcode.isdigit():
            errors['current_zipcode'] = "Zip code must be numeric"

        if permanent_zipcode and not permanent_zipcode.isdigit():
            errors['permanent_zipcode'] = "Zip code must be numeric"

        # Birthdate validation
        birthdate = None
        if not birthdate_str:
            errors['birthdate'] = "Birthdate is required"
        else:
            try:
                birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
            except ValueError:
                errors['birthdate'] = "Invalid birthdate format"

        # Medical history required fields
        if not pastMedicalHistory:
            errors['pastMedicalHistory'] = "Past medical history is required"
        if not beenHospitalized:
            errors['beenHospitalized'] = "This field is required"
        if not hadSurgery:
            errors['hadSurgery'] = "This field is required"
        if not allergies:
            errors['allergies'] = "Allergies field is required"
        if not ongoingMedications:
            errors['ongoingMedications'] = "Ongoing medications field is required"
        if not familyHistory:
            errors['familyHistory'] = "Family history is required"

        # ---------------- IF ERRORS → RE-RENDER FORM ----------------
        if errors:
            return render_template(
                'patient/create_profile.html',
                data=form,
                errors=errors
            )

        # ---------------- SAVE TO DATABASE ----------------
        try:
            patient = Patient(
                firstname=encrypt_value(firstname),
                middlename=safe_decrypt(middlename),
                lastname=encrypt_value(lastname),
                gender=encrypt_value(gender),
                birthdate=birthdate,  # optional: keep plaintext for queries
                age=age,
                blood_type=safe_decrypt(blood_type),
                civil_status=encrypt_value(civil_status),

                # CURRENT ADDRESS
                current_house_no=safe_decrypt(current_house_no),
                current_street=safe_decrypt(current_street),
                current_barangay=encrypt_value(current_barangay),
                current_city=encrypt_value(current_city),
                current_province=encrypt_value(current_province),
                current_zipcode=encrypt_value(current_zipcode),

                # PERMANENT ADDRESS
                permanent_house_no=safe_decrypt(permanent_house_no),
                permanent_street=safe_decrypt(permanent_street),
                permanent_barangay=encrypt_value(permanent_barangay),
                permanent_city=encrypt_value(permanent_city),
                permanent_province=encrypt_value(permanent_province),
                permanent_zipcode=encrypt_value(permanent_zipcode),

                phone=encrypt_value(phone),
                email=encrypt_value(email),

                ec_name=encrypt_value(ec_name),
                ec_relation=encrypt_value(ec_relation),
                ec_phone=encrypt_value(ec_phone),
                ec_address=encrypt_value(ec_address),

                account_id=current_user.account_id
            )
            db.session.add(patient)
            db.session.flush()

            # ---------------- CREATE DEFAULT VISIBILITY ----------------
            visibility = MedicalVisibility(
                pastMedicalHistory=False,
                beenHospitalized=False,
                hadSurgery=False,
                allergies=False,
                ongoingMedications=False,
                familyHistory=False,
                socialHistory=False,
                immunizations=False,
                recentTravelHistory=False,
                otherRelevantInfo=False,
            )
            db.session.add(visibility)

            # ----------- CREATE MEDICAL HISTORY ------------
            history = PatientHistoryBackground(
                patient_id=patient.patient_id,
                pastMedicalHistory=encrypt_value(pastMedicalHistory),
                beenHospitalized=encrypt_value(beenHospitalized),
                hadSurgery=encrypt_value(hadSurgery),
                allergies=encrypt_value(allergies),
                ongoingMedications=encrypt_value(ongoingMedications),
                familyHistory=encrypt_value(familyHistory),
            )

            db.session.add(history)
            db.session.commit()

            flash("Profile successfully created!", "success")
            return redirect(url_for('patient.patient_profile'))

        except Exception as e:
            db.session.rollback()
            flash("An unexpected error occurred. Please try again.", "danger")
            print("CREATE PROFILE ERROR:", e)

    # ---------------- GET REQUEST ----------------
    return render_template(
        'patient/create_profile.html',
        data={},
        errors={}
    )


@patient_bp.route("/image/upload/<int:patient_id>", methods=["POST"])
@login_required
def update_profile_image(patient_id):


    patient = Patient.query.get_or_404(patient_id)
    if patient.account_id != current_user.account_id:
        return redirect(url_for("misc.unauthorized"))

    file = request.files.get("photo")
    if not file or file.filename == "":
        flash("No image selected.", "danger")
        return redirect(url_for("patient.patient_profile", patient_id=patient_id))

    if not allowed_image(file.filename):
        flash("Invalid file type. Only JPG, PNG, WEBP allowed.", "danger")
        return redirect(url_for("patient.patient_profile", patient_id=patient_id))

    ext = file.filename.rsplit(".", 1)[1].lower()

    filename = f"patient_{patient.patient_id}.{ext}"
    filename = secure_filename(filename)

    upload_folder = os.path.join(
        current_app.root_path,
        "static",
        "uploads",
        "patients"
    )
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, filename)

    if patient.profile_image:
        old_path = os.path.join(
            current_app.root_path,
            "static",
            patient.profile_image
        )
        if os.path.exists(old_path):
            os.remove(old_path)

    file.save(file_path)

    patient.profile_image = f"uploads/patients/{filename}"
    db.session.commit()

    flash("Profile picture updated successfully.", "success")
    return redirect(url_for("patient.patient_profile", patient_id=patient_id))


@patient_bp.route("/image/delete/<int:patient_id>", methods=["POST"])
@login_required
def delete_profile_image(patient_id):


    patient = Patient.query.get_or_404(patient_id)

    # Authorization
    if patient.account_id != current_user.account_id:
        return redirect(url_for("misc.unauthorized"))

    # No image to delete
    if not patient.profile_image:
        flash("No profile image to delete.", "warning")
        return redirect(url_for("patient.patient_profile", patient_id=patient_id))

    # Build absolute file path
    image_path = os.path.join(
        current_app.root_path,
        "static",
        patient.profile_image
    )

    # Remove file if it exists
    if os.path.exists(image_path):
        os.remove(image_path)

    # Remove reference from DB
    patient.profile_image = None
    db.session.commit()

    flash("Profile image deleted successfully.", "success")
    return redirect(url_for("patient.patient_profile", patient_id=patient_id))


@patient_bp.route("/profile/update/<int:patient_id>", methods=["POST"])
@login_required
def update_profile_details(patient_id):
        
    patient = Patient.query.filter_by(
        account_id=current_user.account_id
    ).first_or_404()
    
    form = request.form

    try:
        # ---------------- BASIC INFO ----------------
        patient.firstname = form.get("firstname")
        patient.middlename = form.get("middlename")
        patient.lastname = form.get("lastname")
        patient.email = encrypt_value(form.get("email"))
        patient.phone = encrypt_value(form.get("phone"))
        patient.gender = encrypt_value(form.get("gender"))
        patient.blood_type = encrypt_value(form.get("blood_type"))
        patient.civil_status = encrypt_value(form.get("civil_status"))

        birthdate = form.get("birthdate")
        if birthdate:
            patient.birthdate = datetime.strptime(birthdate, "%Y-%m-%d").date()
            patient.age = (
                datetime.today().year - patient.birthdate.year
                - ((datetime.today().month, datetime.today().day)
                   < (patient.birthdate.month, patient.birthdate.day))
            )

        # ---------------- CURRENT ADDRESS ----------------
        patient.current_house_no = encrypt_value(form.get("current_house_no"))
        patient.current_street = encrypt_value(form.get("current_street"))
        patient.current_barangay = encrypt_value(form.get("current_barangay"))
        patient.current_city = encrypt_value(form.get("current_city"))
        patient.current_province = encrypt_value(form.get("current_province"))
        patient.current_zipcode = encrypt_value(form.get("current_zipcode"))

        # ---------------- PERMANENT ADDRESS ----------------
        patient.permanent_house_no = encrypt_value(form.get("permanent_house_no"))
        patient.permanent_street = encrypt_value(form.get("permanent_street"))
        patient.permanent_barangay = encrypt_value(form.get("permanent_barangay"))
        patient.permanent_city = encrypt_value(form.get("permanent_city"))
        patient.permanent_province = encrypt_value(form.get("permanent_province"))
        patient.permanent_zipcode = encrypt_value(form.get("permanent_zipcode"))

        # ---------------- EMERGENCY CONTACT ----------------
        patient.ec_name = encrypt_value(form.get("ec_name"))
        patient.ec_relation = encrypt_value(form.get("ec_relation"))
        patient.ec_phone = encrypt_value(form.get("ec_phone"))
        patient.ec_address = encrypt_value(form.get("ec_address"))

        db.session.commit()
        flash("Profile details updated successfully.", "success")

    except Exception as e:
        db.session.rollback()
        flash("Failed to update profile details.", "danger")
        print("PROFILE UPDATE ERROR:", e)

    return redirect(url_for("patient.patient_profile"))


@patient_bp.route("/view_profile/<int:patient_id>")
@login_required
def view_profile(patient_id):

    # Get patient
    patient = Patient.query.get_or_404(patient_id)

    # Get medical history
    history = PatientHistoryBackground.query.filter_by(
        patient_id=patient.patient_id
    ).first()

    appointment = Appointment.query.filter_by(
        patient_id=patient.patient_id
    ).first()

    # Decrypt main patient fields using your cache
    decrypted_patient = get_patient_cache(patient.patient_id)

    info = Patient.query.get(patient.patient_id)
    if info:
        decrypted_patient.update({
            "gender": decrypt_value(info.gender),
            "blood_type": safe_decrypt(info.blood_type),
            "civil_status": decrypt_value(info.civil_status),
            "birthdate": info.birthdate,
            "age": info.age,
            # EMERGENCY CONTACT
            "ec_name": decrypt_value(info.ec_name),
            "ec_relation": decrypt_value(info.ec_relation),
            "ec_phone": decrypt_value(info.ec_phone),
            "ec_address": decrypt_value(info.ec_address),
            # CURRENT ADDRESS
            "current_house_no": safe_decrypt(info.current_house_no),
            "current_street": safe_decrypt(info.current_street),
            "current_barangay": decrypt_value(info.current_barangay),
            "current_city": decrypt_value(info.current_city),
            "current_province": decrypt_value(info.current_province),
            "current_zipcode": decrypt_value(info.current_zipcode),
            # PERMANENT ADDRESS
            "permanent_house_no": safe_decrypt(info.permanent_house_no),
            "permanent_street": safe_decrypt(info.permanent_street),
            "permanent_barangay": decrypt_value(info.permanent_barangay),
            "permanent_city": decrypt_value(info.permanent_city),
            "permanent_province": decrypt_value(info.permanent_province),
            "permanent_zipcode": decrypt_value(info.permanent_zipcode),
        })

    # Decrypt medical history safely
    decrypted_history = None
    if history:
        decrypted_history = {
            "pastMedicalHistory": decrypt_value(history.pastMedicalHistory),
            "beenHospitalized": decrypt_value(history.beenHospitalized),
            "hadSurgery": decrypt_value(history.hadSurgery),
            "allergies": decrypt_value(history.allergies),
            "ongoingMedications": decrypt_value(history.ongoingMedications),
            "familyHistory": decrypt_value(history.familyHistory),
            "socialHistory": safe_decrypt(getattr(history, "socialHistory", None)),
            "immunizations": safe_decrypt(getattr(history, "immunizations", None)),
            "recentTravelHistory": safe_decrypt(getattr(history, "recentTravelHistory", None)),
            "otherRelevantInfo": safe_decrypt(getattr(history, "otherRelevantInfo", None)),
        }

    visibility = MedicalVisibility.query.filter_by(
        patient_id=patient.patient_id
    ).first()

    # Default: everything hidden if no record exists
    default_state = {
        "pastMedicalHistory": False,
        "beenHospitalized": False,
        "hadSurgery": False,
        "allergies": False,
        "ongoingMedications": False,
        "familyHistory": False,
        "socialHistory": False,
        "immunizations": False,
        "recentTravelHistory": False,
        "otherRelevantInfo": False,
    }

    if visibility:
        visibility_dict = {
            "pastMedicalHistory": visibility.pastMedicalHistory,
            "beenHospitalized": visibility.beenHospitalized,
            "hadSurgery": visibility.hadSurgery,
            "allergies": visibility.allergies,
            "ongoingMedications": visibility.ongoingMedications,
            "familyHistory": visibility.familyHistory,
            "socialHistory": visibility.socialHistory,
            "immunizations": visibility.immunizations,
            "recentTravelHistory": visibility.recentTravelHistory,
            "otherRelevantInfo": visibility.otherRelevantInfo,
        }
    else:
        visibility_dict = default_state

    return render_template(
        "patient/viewProfile.html",
        patient=decrypted_patient,
        history=decrypted_history,
        appointment=appointment,
        visibility=visibility_dict
    )
