import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
import unittest
from pypickles.domain import customer, base

class TestCustomer(unittest.TestCase):

    def setUp(self):
        self.engine = sqlalchemy.create_engine('sqlite:///:memory:')
        session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(session_factory)

        base.Base.metadata.create_all(self.engine)
        self.customer = customer.Customer(user_name='test')
        self.session.add(self.customer)
        self.session.commit()

    def tearDown(self):
        base.Base.metadata.drop_all(self.engine)

    def test_query_panel(self):
        expected = [self.customer]
        result = self.session.query(customer.Customer).all()
        self.assertEqual(result, expected)