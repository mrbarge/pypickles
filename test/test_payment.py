import sqlalchemy
import datetime
from sqlalchemy.orm import sessionmaker, scoped_session
import unittest
from pypickles.domain import coffee, base, customer, payment


class TestPayment(unittest.TestCase):

    def setUp(self):
        self.engine = sqlalchemy.create_engine('sqlite:///:memory:')
        session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(session_factory)

        base.Base.metadata.create_all(self.engine)
        self.customer = customer.Customer(user_name='test')
        self.session.add(self.customer)
        self.payment = payment.Payment(user=self.customer, amount='1.5', date=datetime.datetime.utcnow())
        self.session.add(self.payment)
        self.session.commit()

    def tearDown(self):
        base.Base.metadata.drop_all(self.engine)

    def test_query_panel(self):
        expected = [self.payment]
        result = self.session.query(payment.Payment).all()
        self.assertEqual(result, expected)

