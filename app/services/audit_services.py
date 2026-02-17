from flask import request
from app.extensions import db
from app.models import AuditLog


def log_activity(account_id, action, description):

    ip = request.remote_addr if request else None

    log = AuditLog(
        account_id=account_id,
        action=action,
        description=description,
        ip_address=ip
    )

    db.session.add(log)
    db.session.commit()
