from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from app.models import Account, Patient, User
from app.extensions import db
from . import auth_bp


@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = Account.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.account_id
            session['role'] = user.role

            role = session['role'] 

            if role == 'doctor':
                flash('Logged in successfully.', 'success')
                return redirect(url_for('doctor.doctor_dashboard'))
            elif role == 'patient':
                flash('Logged in successfully.', 'success')
                patient_profile = db.session.query(Patient).filter_by(account_id=user.account_id).first()
                if patient_profile:
                    return redirect(url_for('patient.patient_dashboard'))
                else:
                    return redirect(url_for('patient.create_profile')) 
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
            return render_template('login.html')
    return render_template('login.html')



@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Logged in successfully.', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            return render_template('admin/admin_login.html')
    return render_template('admin/admin_login.html')