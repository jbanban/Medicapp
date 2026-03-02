from flask import render_template, request, redirect, url_for, jsonify, flash
from flask_login import current_user, login_user
from app.extensions import login_manager
from app.models import Account, Patient, Doctor
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from . import auth_bp



@login_manager.user_loader
def load_user(account_id):
    return Account.query.get(int(account_id))


@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    # 🔹 GET → show login page
    if request.method == 'GET':
        return render_template('login.html')

    # 🔹 POST → process login
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return render_template('login.html', error="Username and password are required")

    user = Account.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return render_template('login.html', error="Invalid username or password")

    login_user(user, remember=True)

    return redirect_based_on_role(user)



@auth_bp.route("/me/jwt", methods=["GET"])
@jwt_required()
def me_jwt():
    user_id = get_jwt_identity()
    user = Account.query.get(user_id)

    if not user:
        return jsonify({"success": False}), 404

    return jsonify({
        "id": user.account_id,
        "username": user.username,
        "role": user.role
    }), 200


def redirect_based_on_role(user):

    if user.role in ('doctor', 'secretary'):
        if user.role == 'doctor':
            doctor = Doctor.query.filter_by(account_id=user.account_id).first()
            if not doctor:
                flash('Doctor profile not found. Contact admin.', 'error')
                return redirect(url_for('auth.login'))

            if doctor.status == "Deactivated":
                flash('Unable to login due to account being Deactivated.', 'error')
                return redirect(url_for('auth.login'))
            
        return redirect(url_for('doctor.doctor_dashboard'))
    
    elif user.role == 'patient':
        patient_profile = Patient.query.filter_by(account_id=user.account_id).first()
        if patient_profile:
            return redirect(url_for('patient.patient_dashboard'))
        return redirect(url_for('patient.create_profile'))

    elif user.role == 'admin':
        return redirect(url_for('admin.admin_dashboard'))

    return redirect(url_for('main.index'))

