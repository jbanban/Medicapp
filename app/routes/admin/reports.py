from flask import render_template
from . import admin_bp


@admin_bp.route('/admin_reports')
def admin_reports():
    return render_template('admin/admin_reports.html')
