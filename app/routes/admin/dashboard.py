from flask import render_template, abort
from flask_login import current_user
from app.utils.admin_only import admin_required
from app.services.statistics import calculate_appointment_statistics, get_account_totals
from . import admin_bp


@admin_bp.route("/admin/dashboard", methods=["GET"])
@admin_required
def admin_dashboard():
    if not current_user.is_admin():
        abort(403)

    stats = calculate_appointment_statistics()
    totals = get_account_totals()

    statistics = {
        "monthly_counts": stats.get("monthly_counts", {}),
        "status_counts": stats.get("status_counts", {}),
        "busiest_day_of_week": stats.get("busiest_day_of_week"),
    }

    card_total = {
        "patients": totals.get("total_patients", 0),
        "doctors": totals.get("total_doctors", 0),
        "appointments": totals.get("total_appointments", 0),
        "revenue": totals.get("total_revenue", 0),
    }

    return render_template(
        "admin/admin_dashboard.html",
        statistics=statistics,
        totals=card_total
    )
