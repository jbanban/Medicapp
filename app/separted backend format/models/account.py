from ..extensions import db

class Account(db.Model):
    __tablename__ = "account"
    account_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="patient")

    # one-to-one relationships
    patient = db.relationship("Patient", back_populates="account", uselist=False)
    doctor = db.relationship("Doctor", back_populates="account", uselist=False)

    def get_id(self):
        return str(self.account_id)
    
    def __repr__(self):
        return f"<Account {self.email} ({self.role})>"
