#!/bin/env python
import calendar
import sqlalchemy
from collections import OrderedDict
from sqlalchemy.orm import sessionmaker, scoped_session
from flask import Flask, request, g, redirect, url_for, \
     render_template, flash, jsonify
from decimal import Decimal
from datetime import datetime, timedelta
from pypickles.domain.customer import Customer
from pypickles.domain.coffee import Coffee
from pypickles.domain.payment import Payment

app = Flask(__name__)
app.config.update(dict(
    DATABASE='coffeepicklesdb',
    DB_USER='coffeeuser',
    DB_PORT='5432',
    DB_HOST='127.0.0.1',
    COFFEE_PRICE=1,
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

@app.route('/coffeedates/<user_name>')
def get_coffee_dates(user_name):
    history_days = 7
    db_session = get_db()
    user = db_session.query(Customer).filter(Customer.user_name == user_name).first()
    if user is None:
        return jsonify({"error": "user does not exist"})

    curr_date = datetime.today()
    base_dates = OrderedDict(((curr_date - timedelta(days=int(x))).strftime('%Y-%m-%d'), 0) for x in range(0, int(history_days)))
    c = db_session.query(sqlalchemy.func.to_char(Coffee.date, 'YYYY-MM-DD'),
                         sqlalchemy.func.count(Coffee.date)).filter(Coffee.user_id == user.id).group_by(sqlalchemy.func.to_char(Coffee.date, 'YYYY-MM-DD')).order_by(sqlalchemy.func.min(Coffee.date)).limit(history_days).all()
    for (k, v) in c:
        base_dates[str(k)] = int(v)

    return jsonify(base_dates)
#    return jsonify(list(base_dates.items()))


@app.route('/coffeedays/<user_name>')
def get_coffee_days(user_name):
    db_session = get_db()
    user = db_session.query(Customer).filter(Customer.user_name == user_name).first()
    if user is None:
        return jsonify({"error": "user does not exist"})

    data = OrderedDict((calendar.day_name[x], 0) for x in range(0,7))
    print data
    c = db_session.query(sqlalchemy.func.to_char(Coffee.date, 'FMDay'),
                         sqlalchemy.func.count(Coffee.date)).filter(Coffee.user_id == user.id).group_by(sqlalchemy.func.to_char(Coffee.date, 'FMDay')).all()
    for (k, v) in c:
        data[str(k)] = int(v)

    return jsonify(data)
#    return jsonify(list(data.items()))

@app.route('/coffee', methods=['POST'])
def add_coffee():
    try:
        if hasattr(g, 'user') and g.user is not None:
            c = Coffee(user=g.user, price=app.config['COFFEE_PRICE'])
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
