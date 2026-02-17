from flask import render_template, request, redirect, url_for, session, flash
from app.models import Account
from app.extensions import db
from werkzeug.security import generate_password_hash
from . import auth_bp


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'patient')

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('auth.register'))

        existing_user = Account.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!", "danger")
            return redirect(url_for('auth.register'))

        new_account = Account(
            username=username,
            role=role,
            active=True
        )
        new_account.set_password(password) 

        db.session.add(new_account)
        db.session.commit()

        flash("Account successfully created!", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html')



# @auth_bp.route('/admin/register', methods=['GET', 'POST'])
# def admin_register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         new_user = User(username=username, password=generate_password_hash(password, method='sha256'))
#         db.session.add(new_user)
#         db.session.commit()
#         flash('Account created!', 'success')
#         return redirect(url_for('auth.admin_login'))
#     return render_template('admin/admin_register.html')