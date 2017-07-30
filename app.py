#!/bin/env python
import simplejson
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from flask import Flask, request, flash, session, g, redirect, url_for, abort, \
     render_template, flash
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
app.secret_key = app.config['SECRET_KEY']

def get_db_engine():
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(app.config['DB_USER'], app.config['DB_PASS'], app.config['DB_HOST'], app.config['DB_PORT'], app.config['DATABASE'])
    con = sqlalchemy.create_engine(url, client_encoding='utf8')
    return con

def get_db_session():
    conn = get_db_engine()
    if not hasattr(g, 'db_conn'):
        g.db_conn = conn

    meta = sqlalchemy.MetaData(bind=conn, reflect=True)
    session_factory = sessionmaker(bind=conn)
    session = scoped_session(session_factory)
    return session, meta

def init_db():
    """Initializes the database."""
    engine = get_db_engine()
    conn = engine.connect()

    metadata = sqlalchemy.MetaData()
    customer_table = sqlalchemy.Table('customer', metadata,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column('balance', sqlalchemy.Numeric),
        sqlalchemy.Column('user_name', sqlalchemy.String)
    )
    coffee_table = sqlalchemy.Table('coffee', metadata,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column('date', sqlalchemy.DateTime),
        sqlalchemy.Column('price', sqlalchemy.Numeric),
        sqlalchemy.Column('user_id', sqlalchemy.Integer)
    )
    payment_table = sqlalchemy.Table('payment', metadata,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column('amount', sqlalchemy.Numeric),
        sqlalchemy.Column('date', sqlalchemy.DateTime),
        sqlalchemy.Column('user_id', sqlalchemy.Integer),
    )
    metadata.create_all(engine, checkfirst=True)

    try:
        conn.execute(customer_table.insert(), id=1, balance=0, user_name='user1')
    except sqlalchemy.exc.IntegrityError:
        pass

    conn.close()

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db_session'):
        g.db_session.close()

def get_db():
    """Closes the database again at the end of the request."""
    if not hasattr(g, 'db_session'):
        g.db_session, g.db_meta = get_db_session()
    return g.db_session

@app.before_request
def before_request():
    db_session = get_db()
    g.user = None
    c = db_session.query(Customer).filter(Customer.user_name=='user1').first()
    if c is not None:
        g.user = c

@app.route('/')
def index():
    if hasattr(g, 'user') and g.user is not None:
        session = get_db()
        recent_payments = session.query(Payment).filter(Payment.user == g.user).order_by(Payment.date.desc()).limit(5).all()
        num_coffees = session.query(Coffee).filter(Coffee.user == g.user).count()
    return render_template('home.html',payments=recent_payments, user=g.user, coffee_total=num_coffees)

@app.route('/coffeedate/<user_id>')
def get_coffee_days(user_id):
    db_session = get_db()
    c = Customer.find_by_id(db_session, int(user_id))
    return simplejson.dumps(c.as_dict(), use_decimal=True)

@app.route('/coffeedays/<user_id>')
def get_reviews(user_id):
    db_session = get_db()
    c = Customer.find_by_id(db_session, int(user_id))
    return simplejson.dumps(c.as_dict(), use_decimal=True)

@app.route('/coffee', methods=['POST'])
def add_coffee():
    try:
        if hasattr(g, 'user') and g.user is not None:
            c = Coffee(user=g.user, price=1)
            db_session = get_db()
            db_session.query(Customer).filter(Customer.id == g.user.id).update({'balance': g.user.balance - c.price})
            db_session.add(c)
            db_session.commit()
            flash('Recorded a coffee.', 'Info')
        else:
            flash('You are not a registered user.', 'Error')
    except Exception as err:
        flash('Unable to add a coffee: {0}'.format(str(err)), 'Error')
    return redirect(url_for('index'))
    #return render_template('home.html')

@app.route('/payment', methods=['POST'])
def add_payment():
    user_id = 1
    try:
        if hasattr(g, 'user') and g.user is not None:
            session = get_db()
            amount = Decimal(request.form['amount'])
            p = Payment(user=g.user, amount=amount)
            session.add(p)
            session.query(Customer).filter(Customer.id == g.user.id).update({'balance': g.user.balance + p.amount})
            session.commit()
            flash('Added payment of ${}'.format(amount), 'Info')
        else:
            flash('You are not a registered user.', 'Error')
    except Exception as err:
        flash('Please supply a payment amount as a positive number.', 'Error')
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0',debug=True)
