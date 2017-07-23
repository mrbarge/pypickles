# -*- coding:utf-8 -*-

import json
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from pypickles.domain import customer, coffee, payment, base
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify


app = Flask(__name__)
app.config.update(dict(
    DATABASE='coffeepicklesdb',
    DB_USER='coffeeuser',
    DB_PORT='5432',
    DB_HOST='127.0.0.1'
    DEBUG=False
))
app.config.from_envvar('DB_PASS', silent=True)


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
    pass


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
    return jsonify(c)


@app.route('/coffeedays/<user_id>')
def get_reviews(book_id):
    session = get_db()
    c = customer.Customer.find_by_id(session, int(user_id))
    return jsonify(c)


@app.route('/coffee', methods=['POST'])
def add_coffee(user_id):
    pass
    session = get_db()
    c = customer.Customer.find_by_id(session, int(user_id))
    return jsonify(c)


@app.route('/payment', methods=['POST'])
def add_payment(user_id):
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0')
