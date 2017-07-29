from sqlalchemy import Column, Integer, String, Numeric, inspect
from sqlalchemy.orm import relationship
from pypickles.domain.base import Base

class Customer(Base):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    user_name = Column(String)
    balance = Column(Numeric)

    # one-to-many
    payments = relationship('Payment', back_populates='user')
    coffees = relationship('Coffee', back_populates='user')

    def __init__(self, user_name, balance=0):
        self.user_name = user_name
        self.balance = balance

    def __eq__(self, other):
        return isinstance(other, Customer) and other.id == self.id and other.user_name == self.user_name

    def __repr__(self):
        return "<Customer(user_name='%s', balance=%d)>" % \
            (self.user_name, self.balance)

    @classmethod
    def get_id(cls):
        return Customer.id

    @classmethod
    def find_by_id(cls, session, customer_id):
        return session.query(Customer).filter(Customer.id == customer_id).one()

    def as_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}
