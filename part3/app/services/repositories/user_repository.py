from app.models.user import User
from app import db


class UserRepository:
    def __init__(self):
        self.model = User

    def add(self, user):
        db.session.add(user)
        db.session.commit()

    def get(self, user_id):
        return self.model.query.get(user_id)

    def get_all(self):
        return self.model.query.all()

    def get_user_by_email(self, email):
        return self.model.query.filter_by(email=email).first()

    def update(self, user):
        db.session.commit()

    def delete(self, user):
        db.session.delete(user)
        db.session.commit()
