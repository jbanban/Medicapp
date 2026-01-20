from flask import render_template, request, redirect, url_for, session, flash
from app.models import Account, User
from app.extensions import db
from werkzeug.security import generate_password_hash
from . import auth_bp


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'patient')

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('auth.register'))

        existing_user = Account.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists!", "danger")
            return redirect(url_for('auth.register'))

        hashed_pw = generate_password_hash(password, method='scrypt')
        new_account = Account(email=email, password=hashed_pw, role=role)

        db.session.add(new_account)
        db.session.commit()

        flash("Account successfully created!", "success")
        return redirect(url_for('auth.register'))

    return render_template('register.html')



@auth_bp.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        new_user = User(username=username, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        flash('Account created!', 'success')
        return redirect(url_for('auth.admin_login'))
    return render_template('admin/admin_register.html')