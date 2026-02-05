
from flask import render_template
from app.utils.admin_only import admin_required
from . import admin_bp


@admin_bp.route('/admin_reports')
@admin_required
def admin_reports():
    return render_template('admin/admin_reports.html')
