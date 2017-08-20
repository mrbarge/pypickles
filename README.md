pypickles
=========

Tracks and plots coffee consumption & purchases. A Python-based recreation of
jockey10's coffee-pickles-sprintboot application.

![pypickles](http://i.imgur.com/b3Euv2T.png)

### OpenShift-based Quickstart ###

pypickles can be built and run fairly easily on OpenShift. Here's a quick starting-from-scratch guide:

* Download [OpenShift Origin](https://www.openshift.org/)

* Start up a cluster, log in with your desired user and project.

```bash
# oc cluster up
```

* Create a PostgreSQL database.

```bash
# oc new-app \
    -e POSTGRESQL_USER=<username> \
    -e POSTGRESQL_PASSWORD=<password> \
    -e POSTGRESQL_DATABASE=<database_name> \
    centos/postgresql-95-centos7
```

* Create the pypickles app.

```bash
# oc new-app https://github.com/mrbarge/pypickles.git
```

* Create a config map that will represent the application's config.

```bash
# oc create configmap appconfig
```

* Edit the config map.

```bash
# oc edit configmap appconfig
```

Define the config using the database config used in step 3. Define DB_HOST as the IP address where your PostgreSQL pod is running.

```yaml
apiVersion: v1
data:
  application.properties: |
    DATABASE='<database_name>'
    DB_USER='<username>'
    DB_PASS='<password>'
    DB_PORT='5432'
    DB_HOST='<db host ip>'
    COFFEE_PRICE=1
    SERVER_PORT=8080
kind: ConfigMap
```
	
* Create a new volume and volume mount for your config map. The example below will place it under /appcfg

```bash
# oc volume dc/pypickles --name appcfg -t configmap --mount-path=/appcfg --configmap-name=appconfig --add
```

* Define the environment variable APP_CONFIG to point to the path of your config map file, as defined by the arguments of step 7.

```bash
# oc env dc/pypickles APP_CONFIG=/appcfg/application.properties
```

* Create a new route that exposes the service.

```bash
# oc expose svc/pypickles
```

* pypickles should now be running. A predefined user "user1" will have been created. See "User Authentication" below for options on how to use user authentication.

### Manual Installation ###

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

* https://github.com/jockey10/coffee-pickles-springboot/
