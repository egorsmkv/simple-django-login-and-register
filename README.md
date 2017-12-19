# Simple Django Login and Registration

An example of Django project with basic user functionality.

## Screenshots

| Log In | Registration | Authorized page |
| -------|--------------|-----------------|
| <img src="./screenshots/login.png" width="200"> | <img src="./screenshots/register.png" width="200"> | <img src="./screenshots/authorized_page.png" width="200"> |

| Password reset | Set new password | Password change |
| ---------------|------------------|-----------------|
| <img src="./screenshots/password_reset.png" width="200"> | <img src="./screenshots/set_new_password.png" width="200"> | <img src="./screenshots/password_change.png" width="200"> |

## Functionality

- Sign In
    - via username & password
    - via email & password
    - via email or username & password
- Sign Up
- Log Out
- Profile Activation via Email
- Password Reset
- Re-send Activation Code
- Password Changing
- Email Changing
- Profile Data Changing
- Multilingual: Ukrainian, Russian, Spanish, French, and German languages


## Installing

### Clone the project

```
git clone https://github.com/egorsmkv/simple-django-login-and-register
cd simple-django-login-and-register/source
```

### Create a virtual environment with `virtualenv`

### Install dependencies

```
pip install -r requirements-dev.txt # or requirements.txt if you deploy the project on a production server
```

### Configure the settings (connection to the database, connection to an SMTP server, and other options)

1. Edit `source/app/conf/development/settings.py` if you want to develop the project.

2. Edit `source/app/conf/production/settings.py` if you want to run the project in production.

### Apply migrations

```
./manage.py migrate
```

### Collect static files (only on a production server)

```
./manage.py collectstatic
```

### Running

#### A Development server

Just run this command:

```
./manage.py runserver
```

#### A Production server

- The systemd uses as a process control system. You can use [supervisord](http://supervisord.org) or another software.
- The gunicorn uses as a WSGI server. You can use [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) or another software.
- The nginx uses as a proxy server for the application.

##### If you have the `systemd` on your server

###### Create a systemd unit file, e.g. `/etc/systemd/system/simple-login.service`

```
[Unit]
Description=Simple Django Login
After=network.target

[Service]
User=web
Group=web
WorkingDirectory=/projects/web/simple-django-login-and-register/source

Environment="IS_PRODUCTION=yes"
Environment="PYTHONPATH=/projects/web/simple-django-login-and-register/source"

ExecStart=<FULL PATH TO gunicorn> -b 0.0.0.0:9022 app.wsgi
Restart=always
RestartSec=20

[Install]
WantedBy=multi-user.target
```

###### Reload the systemd

```
[sudo] systemctl daemon-reload
```

###### Start the unit

```
[sudo] systemctl start simple-login
```

Enable the unit if you want always start the application (e.g. reboot or application crash):

```
[sudo] systemctl enable simple-login
```

##### Create the nginx config

```
server {
	listen 80;
	server_name example.com;

	access_log /var/log/nginx/access-example.com.log main;
	error_log /var/log/nginx/error-example.com.log;

	location /static/ {
		alias /projects/web/simple-django-login-and-register/source/content/static/;
	}

	location /media/ {
		alias /projects/web/simple-django-login-and-register/source/content/media/;
	}

	location / {
		proxy_redirect off;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-Proto $scheme;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header Host $http_host;

		proxy_pass http://localhost:9022;
	}
}
```
