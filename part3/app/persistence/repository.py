from abc import ABC, abstractmethod
from app import db
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import as_declarative, declared_attr
import uuid
from datetime import datetime


@as_declarative()
class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class BaseModel(db.Model):
    __abstract__ = True  # SQLAlchemy ne crée pas de table pour BaseModel

    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Repository(ABC):
    @abstractmethod
    def add(self, obj):
        pass

    @abstractmethod
    def get(self, obj_id):
        pass

    @abstractmethod
    def get_all(self):
        pass

    # Modification : on attend une instance
    @abstractmethod
    def update(self, instance):
        pass

    @abstractmethod
    def delete(self, instance):
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        pass


class SQLAlchemyRepository(Repository):
    def __init__(self, model):
        self.model = model

    def add(self, instance):
        from app import db
        db.session.add(instance)
        db.session.commit()

    def get(self, id):
        from app import db
        return db.session.query(self.model).get(id)

    def get_all(self):
        from app import db
        return db.session.query(self.model).all()

    def update(self, instance):
        from app import db
        db.session.commit()

    def delete(self, instance):
        from app import db
        db.session.delete(instance)
        db.session.commit()

    def get_by_attribute(self, attr_name, attr_value):
        from app import db
        return db.session.query(self.model).filter(getattr(self.model, attr_name) == attr_value).first()
