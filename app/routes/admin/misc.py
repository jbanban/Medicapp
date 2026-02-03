from flask import render_template
from app.models.account import Account
from . import admin_bp

@admin_bp.route('/accounts/refresh')
def refresh_accounts():
    accounts = Account.query.all()
    return render_template(
        'admin/partials/accounts_table_body.html',
        accounts=accounts
    )
