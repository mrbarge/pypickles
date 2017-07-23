from sqlalchemy import Column, DateTime, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from pypickles.domain.base import Base

class Payment(Base):
    __tablename__ = 'payment'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('customer.id'))
    user = relationship('Customer', back_populates='payments')
    amount = Column(Numeric)
    date = Column(DateTime)

    def __init__(self, user, amount, date):
        self.user = user
        self.amount = amount
        self.date = date

    def __repr__(self):
        return "<Payment(amount='%d', date='%s')>" % \
            (self.amount, self.date)

    @classmethod
    def get_id(cls):
        return Payment.id

    @classmethod
    def find_by_id(cls, session, payment_id):
        return session.query(Payment).filter(Payment.id == payment_id).one()
