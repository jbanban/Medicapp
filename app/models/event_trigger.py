from sqlalchemy import event
from app.extensions import db
from app.models.user import User
from app.models.account import Account


@event.listens_for(User, "after_insert")
def create_account_for_user(mapper, connection, target: User):
    """
    Automatically create an Account whenever a User is created
    """
    account_table = Account.__table__

    connection.execute(
        account_table.insert().values(
            username=target.username,
            password_hash=target.password_hash,
            role=target.role
        )
    )
