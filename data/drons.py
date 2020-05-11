import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Drons(SqlAlchemyBase):
    __tablename__ = 'Drons'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=True)
    cost = sqlalchemy.Column(sqlalchemy.String(255), nullable=True)
