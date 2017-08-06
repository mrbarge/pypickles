pypickles
=========

Tracks and plots coffee consumption & purchases. A Python-based recreation of
jockey10's coffee-pickles-sprintboot application.

![pypickles](http://i.imgur.com/b3Euv2T.png)

### Installation ###

If using pypickles with a postgres database, you'll need the following dependency for SQLAlchemy:

```bash
yum install postgresql postgresql-devel
```

Then install into a python environment:
```bash
pip install -r requirements.txt
./app.py
```

Create an application config:

```
DB_USER=username
DB_PASS=password
DB_HOST=coffeepicklesdb
SERVER_PORT=8080
```

The application will use the APP_CONFIG environment variable to locate this config file.

Database tables will be initialised on first run.

### User Authentication ###

pypickles is intended to sit behind another web engine frontend, eg nginx or haproxy,
which can perform the SSL termination and pass on the client's PKI details to the application.
It depends upon the client's username being passed by the `X-SSL-Client-CN` header. An example
of setting this in HAProxy is below:

```
frontend web_front
  ...
  bind 127.0.0.1:8081 name https ssl crt ./server.pem ca-file ./ca.crt verify required
  http-request set-header X-SSL-Client-CN %{+Q}[ssl_c_s_dn(cn)]
  default_backend web_back
  ...

```

pypickles looks up the username in the `customer` table. An example user, `user1`, is created on
DB initialisation.

### See Also ###

* https://github.com/pallets/flask
* https://github.com/rosickey/flask-datatables