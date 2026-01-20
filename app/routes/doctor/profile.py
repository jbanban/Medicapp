from flask import render_template, session, redirect, url_for, request, flash
from app.models.doctor import Doctor
from werkzeug.utils import secure_filename
from app import db
import os
from app.services.file_uploads import allowed_image, validate_file_size
from . import doctor_bp


@doctor_bp.route('/doctor_profile/<int:doctor_id>', methods=['GET', 'POST'])
def doctor_profile(doctor_id):
    if session.get('role') != 'doctor':
        return redirect(url_for('unauthorized'))

    user_id = session.get('user_id')

    doctor = Doctor.query.get_or_404(doctor_id)

    # 🔒 SECURITY CHECK
    if doctor.account_id != user_id:
        return redirect(url_for('unauthorized'))

    return render_template(
        'doctor/doctor_profile.html',
        doctor=doctor
    )

@doctor_bp.route('/image/<int:doctor_id>/upload-photo', methods=['POST'])
def upload_doctor_photo(doctor_id):

    user_id = session.get('user_id')

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
            old_path = os.path.join('static', doctor.profile_image)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except:
                    pass

        file.save(file_path)

        doctor.profile_image = f"uploads/doctors/{new_filename}"
        db.session.commit()

        flash("Profile picture updated!", "success")

    else:
        flash("Invalid file type. Only JPG and PNG allowed.", "danger")

    return redirect(url_for('doctor.doctor_profile', doctor_id=doctor_id))


@doctor_bp.route('/qualification/add/<int:doctor_id>', methods=['POST'])
def add_qualification(doctor_id):
    flash("Add qualification (not implemented yet).", "info")
    return redirect(url_for('doctor.doctor_profile', doctor_id=doctor_id))


@doctor_bp.route('/qualification/delete/<int:qual_id>/<int:doctor_id>', methods=['POST'])
def delete_qualification(qual_id, doctor_id):
    flash("Delete qualification (not implemented yet).", "info")
    return redirect(url_for('doctor.doctor_profile', doctor_id=doctor_id))


# -----------------------------
# EXPERIENCE
# -----------------------------

@doctor_bp.route('/experience/add/<int:doctor_id>', methods=['POST'])
def add_experience(doctor_id):
    flash("Add experience (not implemented yet).", "info")
    return redirect(url_for('doctor.doctor_profile', doctor_id=doctor_id))


@doctor_bp.route('/experience/delete/<int:exp_id>/<int:doctor_id>', methods=['POST'])
def delete_experience(exp_id, doctor_id):
    flash("Delete experience (not implemented yet).", "info")
    return redirect(url_for('doctor.doctor_profile', doctor_id=doctor_id))


# -----------------------------
# AWARDS
# -----------------------------

@doctor_bp.route('/award/add/<int:doctor_id>', methods=['POST'])
def add_award(doctor_id):
    flash("Add award (not implemented yet).", "info")
    return redirect(url_for('doctor.doctor_profile', doctor_id=doctor_id))


@doctor_bp.route('/award/delete/<int:award_id>/<int:doctor_id>', methods=['POST'])
def delete_award(award_id, doctor_id):
    flash("Delete award (not implemented yet).", "info")
    return redirect(url_for('doctor.doctor_profile', doctor_id=doctor_id))


# -----------------------------
# CLINIC INFO
# -----------------------------

@doctor_bp.route('/clinic/update/<int:doctor_id>', methods=['POST'])
def update_clinic_info(doctor_id):
    flash("Clinic info updated (stub).", "success")
    return redirect(url_for('doctor.doctor_profile', doctor_id=doctor_id))


# -----------------------------
# SETTINGS
# -----------------------------

@doctor_bp.route('/settings/update/<int:doctor_id>', methods=['POST'])
def update_doctor_settings(doctor_id):
    flash("Settings updated (stub).", "success")
    return redirect(url_for('doctor.doctor_profile', doctor_id=doctor_id))


# -----------------------------
# DEACTIVATE
# -----------------------------

@doctor_bp.route('/deactivate/<int:doctor_id>', methods=['POST'])
def deactivate_doctor(doctor_id):
    flash("Doctor profile deactivated (stub).", "warning")
    return redirect(url_for('auth.logout'))
