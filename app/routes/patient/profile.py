from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.account import Account
from app.models.patient_history_background import PatientHistoryBackground
from app.models.medical_visibility import MedicalVisibility
from app.models.appointment_visibility import AppointmentVisibility
from app.services.file_uploads import allowed_image
from app.services.patient_cache import get_patient_cache 
from app.services.empty_to_none import empty_to_none
from werkzeug.utils import secure_filename
from datetime import datetime
from app import db
import os

from . import patient_bp


def calculated_age(birthdate):
    return (
        datetime.today().year - birthdate.year
        - ((datetime.today().month, datetime.today().day)
           < (birthdate.month, birthdate.day))
    )


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
            "gender": patient.gender,
            "blood_type": patient.blood_type,
            "civil_status": patient.civil_status,
            "birthdate": patient.birthdate,
            "age": patient.age,

            # CURRENT ADDRESS
            "current_house_no": patient.current_house_no,
            "current_street": patient.current_street,
            "current_barangay": patient.current_barangay,
            "current_city": patient.current_city,
            "current_province": patient.current_province,
            "current_zipcode": patient.current_zipcode,

            # PERMANENT ADDRESS
            "permanent_house_no": patient.permanent_house_no,
            "permanent_street": patient.permanent_street,
            "permanent_barangay": patient.permanent_barangay,
            "permanent_city": patient.permanent_city,
            "permanent_province": patient.permanent_province,
            "permanent_zipcode": patient.permanent_zipcode,

            # EMERGENCY CONTACT
            "ec_name": patient.ec_name,
            "ec_relation": patient.ec_relation,
            "ec_phone": patient.ec_phone,
            "ec_address": patient.ec_address,
        }

    decrypted_history = None
    if history:
        decrypted_history = {
            "pastMedicalHistory": history.pastMedicalHistory,
            "beenHospitalized": history.beenHospitalized,
            "hadSurgery": history.hadSurgery,
            "allergies": history.allergies,
            "ongoingMedications": history.ongoingMedications,
            "familyHistory": history.familyHistory,
        }

    M_visibility = MedicalVisibility.query.filter_by(
        patient_id=patient.patient_id
    ).first()

    A_visibility = AppointmentVisibility.query.filter_by(
        patient_id=patient.patient_id
    ).first()

    appointments = Appointment.query.filter(
        Appointment.patient_id == patient.patient_id,
        Appointment.status.in_(["Done", "Paid"])
    ).all()
    
    result = []

    for appt in appointments:

        record = appt.record

        if not record:
            result.append({
                "appointment_id": appt.appointment_id,
                "date": None,
                "diagnosis": None,
                "notes": None,
            })
            continue

        result.append({
            "appointment_id": appt.appointment_id,
            "date": record.visit_date,
            "diagnosis": record.diagnosis,
            "notes": record.notes,
            "second_opinion": record.second_op
        })

    return render_template(
        "patient/patient_profile.html",
        decrypted_patient=decrypted_patient,
        patient_info=decrypted_patient_info,
        history=decrypted_history,
        visibility_M=M_visibility,
        visibility_A=A_visibility,
        appointments=result,
        patient=patient
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
                firstname=firstname,
                middlename=middlename,
                lastname=lastname,
                gender=gender, 
                birthdate=birthdate,
                age=calculated_age(birthdate),
                blood_type=blood_type, 
                civil_status=civil_status,

                current_house_no=current_house_no,
                current_street=current_street,
                current_barangay=current_barangay,
                current_city=current_city,
                current_province=current_province,
                current_zipcode=current_zipcode,

                permanent_house_no=permanent_house_no,
                permanent_street=permanent_street,
                permanent_barangay=permanent_barangay,
                permanent_city=permanent_city,
                permanent_province=permanent_province,
                permanent_zipcode=permanent_zipcode,

                phone=phone,
                email=email,

                ec_name=ec_name,
                ec_relation=ec_relation,
                ec_phone=ec_phone,
                ec_address=ec_address,

                account_id=current_user.account_id
            )

            db.session.add(patient)
            db.session.flush()

            # ---------------- CREATE DEFAULT VISIBILITY ----------------
            visibility = MedicalVisibility(
                patient_id=patient.patient_id,
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
                pastMedicalHistory=pastMedicalHistory,
                beenHospitalized=beenHospitalized,
                hadSurgery=hadSurgery,
                allergies=allergies,
                ongoingMedications=ongoingMedications,
                familyHistory=familyHistory,
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
        patient.email = form.get("email")
        patient.phone = form.get("phone")
        patient.gender = form.get("gender")
        patient.blood_type = form.get("blood_type")
        patient.civil_status = form.get("civil_status")

        birthdate = form.get("birthdate")
        if birthdate:
            patient.birthdate = datetime.strptime(birthdate, "%Y-%m-%d").date()
            patient.age = (
                datetime.today().year - patient.birthdate.year
                - ((datetime.today().month, datetime.today().day)
                   < (patient.birthdate.month, patient.birthdate.day))
            )

        # ---------------- CURRENT ADDRESS ----------------
        patient.current_house_no = form.get("current_house_no")
        patient.current_street = form.get("current_street")
        patient.current_barangay = form.get("current_barangay")
        patient.current_city = form.get("current_city")
        patient.current_province = form.get("current_province")
        patient.current_zipcode = form.get("current_zipcode")

        # ---------------- PERMANENT ADDRESS ----------------
        patient.permanent_house_no = form.get("permanent_house_no")
        patient.permanent_street = form.get("permanent_street")
        patient.permanent_barangay = form.get("permanent_barangay")
        patient.permanent_city = form.get("permanent_city")
        patient.permanent_province = form.get("permanent_province")
        patient.permanent_zipcode = form.get("permanent_zipcode")

        # ---------------- EMERGENCY CONTACT ----------------
        patient.ec_name = form.get("ec_name")
        patient.ec_relation = form.get("ec_relation")
        patient.ec_phone = form.get("ec_phone")
        patient.ec_address = form.get("ec_address")

        db.session.commit()
        flash("Profile details updated successfully.", "success")

    except Exception as e:
        db.session.rollback()
        flash("Failed to update profile details.", "danger")
        print("PROFILE UPDATE ERROR:", e)

    return redirect(url_for("patient.patient_profile"))

