from ..extensions import db

class Payment(db.Model):
    __tablename__ = "payment"
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointment.appointment_id"))
    amount = db.Column(db.Float)
    payment_date = db.Column(db.String(20))
    payment_method = db.Column(db.String(50))

    appointment = db.relationship("Appointment", back_populates="payments")

    def __repr__(self):
        return f"<Payment {self.payment_id} Amount: {self.amount}>"