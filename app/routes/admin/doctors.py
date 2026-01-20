from flask import render_template, request, redirect, url_for, flash
from app.models import Account, Doctor
from app.extensions import db
from werkzeug.security import generate_password_hash
from . import admin_bp


@admin_bp.route('/admin_doctors', methods=['GET', 'POST'])
def admin_doctors():
    account_id = request.args.get('account_id', type=int)
    edit_account = Account.query.get(account_id) if account_id else None

    if request.method == 'POST':
        account_id = request.form.get('account_id')
        email = request.form['email']
        password = request.form.get('password')

        # EDIT
        if account_id:
            account = Account.query.get(account_id)
            account.email = email
            if password:
                account.password = generate_password_hash(password)
            db.session.commit()
            flash("Account updated successfully!", "success")

        # CREATE
        else:
            if Account.query.filter_by(email=email).first():
                flash("Email already exists!", "danger")
                return redirect(url_for('admin.admin_doctors'))

            new_account = Account(
                email=email,
                password=generate_password_hash(password),
                role='doctor'
            )
            db.session.add(new_account)
            db.session.commit()
            flash("Doctor account created!", "success")

        return redirect(url_for('admin.admin_doctors'))

    accounts = (
        db.session.query(Account)
        .outerjoin(Doctor, Doctor.account_id == Account.account_id)
        .filter(Account.role == 'doctor')
        .all()
    )

    doctors = Doctor.query.all()

    return render_template('admin/admin_doctors.html', 
                           accounts=accounts, 
                           doctors=doctors,
                           edit_account=edit_account
                           )


@admin_bp.route('/create_doctor_profile/<int:account_id>', methods=['GET', 'POST'])
def create_doctor_profile(account_id):
    selected_account = Account.query.get_or_404(account_id)


    if request.method == 'POST':
        new_doctor = Doctor(
            firstname=request.form['firstname'],
            middlename=request.form.get('middlename'),
            lastname=request.form['lastname'],
            age=request.form.get('age'),
            bloodtype=request.form.get('bloodtype'),
            height=request.form.get('height'),
            weight=request.form.get('weight'),
            specialization=request.form.get('specialization'),
            gender=request.form['gender'],
            dob=request.form['dob'],
            pob=request.form['pob'],
            civilstatus=request.form.get('civilstatus'),
            degree=request.form.get('degree'),
            nationality=request.form['nationality'],
            religion=request.form.get('religion'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            account_id=account_id
        )

        db.session.add(new_doctor)
        db.session.commit()

        flash("Doctor profile created successfully!", "success")
        return redirect(url_for('admin.admin_doctors'))

    return render_template(
        'admin/create_doctor_profile.html',
        selected_account=selected_account
    )


@admin_bp.route('/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    if request.method == 'POST':

        # Update doctor fields
        doctor.firstname = request.form['firstname']
        doctor.middlename = request.form.get('middlename')
        doctor.lastname = request.form['lastname']
        doctor.age = request.form.get('age')
        doctor.bloodtype = request.form.get('bloodtype')
        doctor.height = request.form.get('height')
        doctor.weight = request.form.get('weight')
        doctor.specialization = request.form.get('specialization')
        doctor.gender = request.form['gender']
        doctor.dob = request.form.get('dob')
        doctor.pob = request.form.get('pob')
        doctor.civilstatus = request.form.get('civilstatus')
        doctor.degree = request.form.get('degree')
        doctor.nationality = request.form.get('nationality')
        doctor.religion = request.form.get('religion')
        doctor.phone = request.form.get('phone')
        doctor.email = request.form.get('email')

        db.session.commit()

        flash("Doctor profile updated successfully!", "success")
        return redirect(url_for('admin.admin_doctors'))

    return render_template(
        'admin/editDoctorProfile.html',
        doctor=doctor,
    )
