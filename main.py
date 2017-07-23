#!/bin/env python

import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from pypickles.domain import coffee, customer, payment

def connect(user, password, db, host='localhost', port=5432):
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)
    con = sqlalchemy.create_engine(url, client_encoding='utf8')
    meta = sqlalchemy.MetaData(bind=con, reflect=True)
    return con, meta

def main():
    con, meta = connect('user', 'pass', 'db', 'host')
    session_factory = sessionmaker(bind=con)
    Session = scoped_session(session_factory)
    u = Session.query(customer.Customer)
    for c in u:
        coffees = c.coffees
        for p in coffees:
            print(p)


if __name__ == '__main__':
    main()
