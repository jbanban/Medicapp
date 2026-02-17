
import app


@app.cli.command("init-admin")
def init_admin():
    """Create default admin user"""
    from app.models import Account
    from app.extensions import db
    from werkzeug.security import generate_password_hash

    if Account.query.filter_by(username="admin").first():
        print("Admin already exists")
        return

    admin = Account(
        username="admin",
        password_hash=generate_password_hash("admin123"),
        role="admin",
        active=True
    )
    db.session.add(admin)
    db.session.commit()
    print("Admin user created")
