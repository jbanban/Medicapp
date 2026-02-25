import os
from app import db
from app.models.account import Account
from dotenv import load_dotenv

load_dotenv()

def ensure_admin_user():
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD', 'adminpass')

    if not admin_username or not admin_password:
        raise RuntimeError("ADMIN_USERNAME and ADMIN_PASSWORD must be set")
    
    admin_user = Account.query.filter_by(username=admin_username).first()

    if not admin_user:
        admin_user = Account(username=admin_username, role='admin')
        admin_user.set_password(admin_password)
        admin_user.active = True
        db.session.add(admin_user)
        db.session.commit()
        print(f'Admin user "{admin_username}" created.')
    else:
        admin_user.set_password(admin_password)
        db.session.commit()
        print(f'Admin user "{admin_username}" password updated.')
    
if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        ensure_admin_user()