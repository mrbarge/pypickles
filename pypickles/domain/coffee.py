from sqlalchemy import Column, Integer, DateTime, Numeric, ForeignKey, inspect
from sqlalchemy.orm import relationship
from pypickles.domain.base import Base
from pypickles.domain import coffee
from pypickles.domain import customer
from pypickles.domain import payment

class Coffee(Base):

    __tablename__ = 'coffee'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('customer.id'))
    user = relationship('Customer', back_populates='coffees')
    price = Column(Numeric)
    date = Column(DateTime)

    def __init__(self, user, price, date):
        self.user = user
        self.price = price
        self.date = date

    def __repr__(self):
        return "<Coffee(price='%d', date='%s')>" % \
            (self.price, self.date)

    @classmethod
    def get_id(cls):
        return Coffee.id

    @classmethod
    def get_user(cls):
        return Coffee.user

    @classmethod
    def find_by_id(cls, session, coffee_id):
        return session.query(Coffee).filter(Coffee.id == coffee_id).one()

    def as_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}
