from flask import render_template
from app.services.statistics import calculate_appointment_statistics
from . import admin_bp


@admin_bp.route("/admin/dashboard")
def admin_dashboard():
    statistics = calculate_appointment_statistics()
    return render_template(
        "admin/admin_dashboard.html",
        statistics=statistics
    )