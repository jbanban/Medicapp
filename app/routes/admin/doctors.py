from flask import render_template, request, redirect, url_for, flash, jsonify
from app.models import Account, Doctor
from app.extensions import db
from werkzeug.security import generate_password_hash
from app.services.empty_to_none import empty_to_none
from app.security.crypto import decrypt_value, safe_decrypt
from app.extensions import cache
from . import admin_bp

@admin_bp.route('/admin_doctors', methods=['GET', 'POST'])
def admin_doctors():
    account_id = request.args.get('account_id', type=int)
    edit_account = Account.query.get(account_id) if account_id else None

    if request.method == 'POST':
        account_id = request.form.get('account_id=')
        username = request.form['username']
        password = request.form.get('password')

        # EDIT
        if account_id:
            account = Account.query.get(account_id)
            account.username = username

            if password:
                account.password = generate_password_hash(password)

            db.session.commit()

            return jsonify({
                "success": True,
                "message": "Account updated successfully",
                "data": {
                    "id": account.id,
                    "username": account.username,
                    "role": account.role
                }
            }), 200

        # CREATE
        else:
            if Account.query.filter_by(username=username).first():
                return jsonify({
                    "success": False,
                    "message": "Username already exists"
                }), 400

            new_account = Account(
                username=username,
                password=generate_password_hash(password),
                role='doctor'
            )
            db.session.add(new_account)
            db.session.commit()

            return jsonify({
                "success": True,
                "message": "Doctor account created successfully",
                "data": {
                    "id": new_account.account_id,
                    "username": new_account.username,
                    "role": new_account.role
                }
            }), 201
    
    doctors = Doctor.query.all()
        
    doctors_data = [
        {
            "doctor_id": d.doctor_id,
            "account_id": d.account_id,

            # AUTO-DECRYPTED by EncryptedColumn
            "firstname": d.firstname,
            "middlename": d.middlename,
            "lastname": d.lastname,
            "gender": d.gender,
            "dob": d.dob,
            "pob": d.pob,
            "bloodtype": d.bloodtype,
            "civilstatus": d.civilstatus,
            "nationality": d.nationality,
            "religion": d.religion,
            "phone": d.phone,
            "email": d.email,

            # NOT ENCRYPTED
            "age": d.age,
            "specialization": d.specialization,
            "profile_image": d.profile_image,

            "full_name": " ".join(filter(None, [
                d.firstname,
                d.middlename,
                d.lastname
            ]))
        }
        for d in doctors
    ]




    accounts = (
        db.session.query(Account)
        .outerjoin(Doctor, Doctor.account_id == Account.account_id)
        .filter(Account.role == 'doctor')
        .all()
    )


    return render_template('admin/admin_doctors.html', 
                           accounts=accounts, 
                           doctors=doctors_data,
                           edit_account=edit_account
                           )


@admin_bp.route('/create_doctor_profile/<int:account_id>', methods=['GET', 'POST'])
def create_doctor_profile(account_id):
    selected_account = Account.query.get_or_404(account_id)

    errors = {}

    if request.method == 'POST':

        form = request.form

        firstname = form.get('firstname', '').strip()
        middlename = form.get('middlename', '').strip()
        lastname = form.get('lastname', '').strip()
        age = form.get('age', '').strip()
        bloodtype = form.get('bloodtype', '').strip()
        height = form.get('height', '').strip()
        weight = form.get('weight', '').strip()
        specialization = form.get('specialization', '').strip()
        gender = form.get('gender', '').strip()
        dob = form.get('dob', '').strip()
        pob = form.get('pob', '').strip()
        civilstatus = form.get('civilstatus', '').strip()
        degree = form.get('degree', '').strip()
        nationality = form.get('nationality', '').strip()
        religion = form.get('religion', '').strip()
        phone = form.get('phone', '').strip()
        email = form.get('email', '').strip()

        account_id=account_id

         # ---------------- VALIDATION ----------------

        if not firstname:
            errors['firstname'] = "First name is required."
        if not lastname:
            errors['lastname'] = "Last name is required."
        if not age:
            errors['age'] = "Valid age is required."
        if not gender:
            errors['gender'] = "Gender is required."
        if not dob:
            errors['dob'] = "Date of birth is required."
        if not pob:
            errors['pob'] = "Place of birth is required."
        if not civilstatus:
            errors['civilstatus'] = "Civil status is required."
        if not degree:
            errors['degree'] = "Degree is required."
        if not nationality: 
            errors['nationality'] = "Nationality is required."
        if not religion:
            errors['religion'] = "Religion is required."
        if not phone:
            errors['phone'] = "Phone number is required."
        if not email:
            errors['email'] = "Email is required."


        # ---------------- IF ERRORS → RE-RENDER FORM ----------------
        if errors:
            return render_template(
                'patient/create_profile.html',
                data=form,
                errors=errors
            )
        
        # ------------------- SAVE TO DATABASE ------------------
        try:
            doctor = Doctor(
                firstname=firstname,
                middlename=middlename or None,
                lastname=lastname,

                age=int(age),
                bloodtype=bloodtype or None,
                height=height or None,
                weight=weight or None,
                specialization=specialization,

                gender=gender,
                dob=dob,
                pob=pob,
                civilstatus=civilstatus,
                degree=degree,
                nationality=nationality,
                religion=religion,

                phone=phone,
                email=email,

                account_id=account_id
            )

            db.session.add(doctor)
            db.session.commit()

            flash("Doctor profile created successfully!", "success")
            return redirect(url_for('admin.admin_doctors'))

        except Exception as e:
            db.session.rollback()
            flash("An unexpected error occurred. Please try again.", "danger")
            print("CREATE PROFILE ERROR:", e)
        

    return render_template(
        'admin/create_doctor_profile.html',
        selected_account=selected_account
    )

@admin_bp.route('/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    if request.method == 'POST':
        form = request.form

        # ---------- REQUIRED (EncryptedColumn auto-encrypts) ----------
        doctor.firstname = form.get("firstname")
        doctor.lastname = form.get("lastname")
        doctor.gender = form.get("gender")
        doctor.dob = form.get("dob")
        doctor.phone = form.get("phone")
        doctor.email = form.get("email")

        # ---------- OPTIONAL (use empty_to_none) ----------
        doctor.middlename = empty_to_none(form.get("middlename"))
        doctor.bloodtype = empty_to_none(form.get("bloodtype"))
        doctor.civilstatus = empty_to_none(form.get("civilstatus"))
        doctor.pob = empty_to_none(form.get("pob"))
        doctor.degree = empty_to_none(form.get("degree"))
        doctor.nationality = empty_to_none(form.get("nationality"))
        doctor.religion = empty_to_none(form.get("religion"))
        doctor.height = empty_to_none(form.get("height"))
        doctor.weight = empty_to_none(form.get("weight"))

        # ---------- NOT ENCRYPTED ----------
        doctor.age = int(form.get("age")) if form.get("age") else None
        doctor.specialization = form.get("specialization")

        db.session.commit()

        flash("Doctor profile updated successfully!", "success")
        return redirect(url_for('admin.admin_doctors'))

    return render_template(
        'admin/editDoctorProfile.html',
        doctor=doctor
    )
