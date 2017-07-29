#!/bin/env python
import simplejson
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from pypickles.domain import customer, coffee, payment, base
from pypickles.domain.customer import Customer
from pypickles.domain.coffee import Coffee
from pypickles.domain.payment import Payment
from decimal import Decimal


app = Flask(__name__)
app.config.update(dict(
    DATABASE='coffeepicklesdb',
    DB_USER='coffeeuser',
    DB_PORT='5432',
    DB_HOST='127.0.0.1',
    DEBUG=False
))
app.config.from_envvar('APP_CONFIG', silent=True)

def connect_db():
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(app.config['DB_USER'], app.config['DB_PASS'], app.config['DB_HOST'], app.config['DB_PORT'], app.config['DATABASE'])
    con = sqlalchemy.create_engine(url, client_encoding='utf8')
    meta = sqlalchemy.MetaData(bind=con, reflect=True)
    session_factory = sessionmaker(bind=con)
    session = scoped_session(session_factory)
    return session, meta


def init_db():
    """Initializes the database."""
    session, meta = connect_db()
    meta.drop_all()
    customer_table = sqlalchemy.Table('customer', meta,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column('balance', sqlalchemy.Numeric),
        sqlalchemy.Column('user_name', sqlalchemy.String)
    )
    coffee_table = sqlalchemy.Table('coffee', meta,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column('date', sqlalchemy.DateTime),
        sqlalchemy.Column('price', sqlalchemy.Numeric),
        sqlalchemy.Column('user_id', sqlalchemy.Integer)
    )
    payment_table = sqlalchemy.Table('payment', meta,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column('amount', sqlalchemy.Numeric),
        sqlalchemy.Column('date', sqlalchemy.DateTime),
        sqlalchemy.Column('user_id', sqlalchemy.Integer),
    )

    meta.create_all()
    c = Customer(user_name='user1',balance=0)
    session.add(c)
    session.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db_con'):
        g.db_con.close()


def get_db():
    """Closes the database again at the end of the request."""
    if not hasattr(g, 'db_con'):
        g.db_con, g.db_meta = connect_db()
    return g.db_con


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/coffeedate/<user_id>')
def get_coffee_days(user_id):
    session = get_db()
    c = customer.Customer.find_by_id(session, int(user_id))
    return simplejson.dumps(c.as_dict(), use_decimal=True)


@app.route('/coffeedays/<user_id>')
def get_reviews(user_id):
    session = get_db()
    c = customer.Customer.find_by_id(session, int(user_id))
    return simplejson.dumps(c.as_dict(), use_decimal=True)


@app.route('/coffee', methods=['POST'])
def add_coffee():
    errors = []
    results = {}
    user_id = 1
    try:
        session = get_db()
        c = customer.Customer.find_by_id(session, int(user_id))
        c = coffee.Coffee(user=c,price=1)
        session.add(c)
        session.commit()
    except Exception as err:
        errors.append(
            "Unable to add a coffee: {0}".format(str(err))
        )
    return render_template('home.html', errors=errors, results=results)

@app.route('/payment', methods=['POST'])
def add_payment():
    errors = []
    results = {}
    user_id = 1
    try:
        session = get_db()
        amount = Decimal(request.form['amount'])
        c = customer.Customer.find_by_id(session, int(user_id))
        p = payment.Payment(user=c, amount=amount)
        session.add(p)
        session.commit()
        print "done"
    except Exception as err:
        print "{0}".format(str(err))
        errors.append(
            "Please supply a payment amount as a positive number."
        )
    return render_template('home.html', errors=errors, results=results)


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0')
