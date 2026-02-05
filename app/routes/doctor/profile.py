from flask import render_template, redirect, session, url_for, request, flash, current_app
from flask import abort
from flask_login import login_required, current_user, logout_user
from app.models.doctor import Doctor
from app.models.doctors_background import DoctorsBackground
from app.services.file_uploads import allowed_image
from werkzeug.utils import secure_filename
from app import db
import os
from . import doctor_bp


@doctor_bp.route('/doctor_profile/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def doctor_profile(doctor_id):

    doctor = Doctor.query.get_or_404(doctor_id)

    # 🔒 SECURITY CHECK
    if doctor.account_id != current_user.account_id:
        return redirect(url_for('unauthorized'))

    return render_template(
        'doctor/doctor_profile.html',
        doctor=doctor
    )

@doctor_bp.route('/image/<int:doctor_id>/upload-photo', methods=['POST'])
@login_required
def upload_doctor_photo(doctor_id):

    user_id = current_user.account_id

    # Get doctor based on URL (doctor_id), not user_id
    doctor = Doctor.query.get_or_404(doctor_id)

    # Authorization check: ensure logged-in doctor owns this profile
    if doctor.account_id != user_id:
        return redirect(url_for('unauthorized'))

    # -------- FILE VALIDATION --------
    if "photo" not in request.files:
        flash("No file part in request.", "danger")
        return redirect(url_for('doctor.doctor_profile', doctor_id=doctor_id))

    file = request.files["photo"]

    if file.filename == '':
        flash("No file selected.", "danger")
        return redirect(url_for('doctor.doctor_profile', doctor_id=doctor_id))

    if file and allowed_image(file.filename):

        ext = file.filename.rsplit('.', 1)[1].lower()

        new_filename = f"{doctor.lastname.lower()}_{doctor.firstname.lower()}.{ext}"
        new_filename = secure_filename(new_filename)

        upload_folder = os.path.join('app' , 'static', 'uploads', 'doctors')
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, new_filename)

        if doctor.profile_image:
            old_path = os.path.join(
                current_app.root_path,
                'static', 
                doctor.profile_image)
            if os.path.exists(old_path):
                os.remove(old_path)


        flash("Profile picture updated!", "success")

    else:
        flash("Invalid file type. Only JPG and PNG allowed.", "danger")
        
    file.save(file_path)

    doctor.profile_image = f"uploads/doctors/{new_filename}"
    db.session.commit()

    return redirect(url_for('doctor.doctor_profile', doctor_id=doctor_id))

@doctor_bp.route('/background/add/<int:doctor_id>/<string:bg_type>', methods=['POST'])
@login_required
def add_background(doctor_id, bg_type):
    doctor = Doctor.query.get_or_404(doctor_id)

    if doctor.account_id != current_user.account_id:
        return redirect(url_for('unauthorized'))

    if bg_type not in ['qualification', 'experience', 'award', 'clinic']:
        abort(400)

    bg = DoctorsBackground(
        doctor_id=doctor_id,
        type=bg_type,
        title=request.form.get('title'),
        organization=request.form.get('organization'),
        year=request.form.get('year'),
        description=request.form.get('description')
    )

    db.session.add(bg)
    db.session.commit()

    flash(f"{bg_type.capitalize()} added.", "success")
    return redirect(url_for('doctor.doctor_profile', doctor_id=doctor_id))

@doctor_bp.route('/background/update/<int:bg_id>/<int:doctor_id>', methods=['POST'])
@login_required
def update_background(bg_id, doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    bg = DoctorsBackground.query.get_or_404(bg_id)

    if doctor.account_id != current_user.account_id or bg.doctor_id != doctor_id:
        return redirect(url_for('unauthorized'))

    bg.title = request.form.get('title')
    bg.organization = request.form.get('organization')
    bg.year = request.form.get('year')
    bg.description = request.form.get('description')

    db.session.commit()

    flash("Updated successfully.", "success")
    return redirect(url_for('doctor.doctor_profile', doctor_id=doctor_id))

@doctor_bp.route('/background/delete/<int:bg_id>/<int:doctor_id>', methods=['POST'])
@login_required
def delete_background(bg_id, doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    bg = DoctorsBackground.query.get_or_404(bg_id)

    if doctor.account_id != current_user.account_id or bg.doctor_id != doctor_id:
        return redirect(url_for('unauthorized'))

    db.session.delete(bg)
    db.session.commit()

    flash("Removed successfully.", "success")
    return redirect(url_for('doctor.doctor_profile', doctor_id=doctor_id))
@doctor_bp.route('/update_clinic_info/<int:doctor_id>', methods=['POST'])
@login_required
def update_clinic_info(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    # 🔒 Ownership check
    if doctor.account_id != current_user.account_id:
        return redirect(url_for('unauthorized'))

    # Get existing clinic background (ONLY type='clinic')
    clinic = DoctorsBackground.query.filter_by(
        doctor_id=doctor_id,
        type='clinic'
    ).first()

    # If none exists, create one
    if not clinic:
        clinic = DoctorsBackground(
            doctor_id=doctor_id,
            type='clinic',
            title='Clinic Information'
        )
        db.session.add(clinic)

    # Update fields
    clinic.clinic_name = request.form.get('clinic_name')
    clinic.clinic_address = request.form.get('clinic_address')
    clinic.clinic_days = request.form.get('clinic_days')
    clinic.clinic_hours_from = request.form.get('clinic_hours_from')
    clinic.clinic_hours_to = request.form.get('clinic_hours_to')

    db.session.commit()

    flash("Clinic information updated.", "success")
    return redirect(url_for('doctor.doctor_profile', doctor_id=doctor_id))


@doctor_bp.route('/update_doctor_settings/<int:doctor_id>', methods=['POST'])
@login_required
def update_doctor_settings(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    if doctor.account_id != current_user.account_id:
        return redirect(url_for('unauthorized'))

    # Checkbox logic (unchecked = missing from form)
    session['public_profile'] = 'public_profile' in request.form
    session['accept_appointments'] = 'accept_appointments' in request.form

    flash("Preferences saved (session-based).", "success")
    return redirect(url_for('doctor.doctor_profile', doctor_id=doctor_id))


@doctor_bp.route('/deactivate/<int:doctor_id>', methods=['POST'])
@login_required
def deactivate_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    # 🔒 Ownership check
    if doctor.account_id != current_user.account_id:
        return redirect(url_for('unauthorized'))

    account = doctor.account
    account.active = False

    db.session.commit()

    # Immediately log out the user
    logout_user()

    flash("Your profile has been deactivated.", "warning")
    return redirect(url_for('auth.login'))