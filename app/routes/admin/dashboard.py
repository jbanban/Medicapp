from flask import render_template, abort
from flask_login import current_user
from app.utils.admin_only import admin_required
from app.services.statistics import calculate_appointment_statistics
from . import admin_bp


@admin_bp.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    if not current_user.is_admin():
        abort(403)

    statistics = calculate_appointment_statistics()
    return render_template(
        "admin/admin_dashboard.html",
        statistics=statistics
    )