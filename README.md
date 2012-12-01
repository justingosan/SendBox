#SendBox

A Django Sample App integrating the Box.com and SendGrid API. You can check out a demo here: [SendBox](http://sendbox.ap01.aws.af.cm/).
Also an online guide here: [SendBox Guide](http://sendbox.ap01.aws.af.cm/doc/) 


##Requirements:

* [Django](https://www.djangoproject.com/) 1.4+
* [ElementTree](http://effbot.org/zone/element-index.htm) 1.2+
* [Requests](http://docs.python-requests.org/en/latest/) 0.14+
* [Box](http://box.com) App API Key
* [SendGrid](http://sendgrid.com) API Key


##Quick Setup:

1. Install the required modules:
	```
	pip install -r https://raw.github.com/justingo/SendBox/master/requirements.txt
	```
2. Start a django project:
	```
	python django-admin.py startproject 'myproject'
	```

3. Copy '/sendbox/' to project root (beside manage.py).

4. Tweak 'myproject/settings':
	```python
	BOX_API_KEY = '' # Box Key goes here

	SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

	#SendGrid Email Config
	SENDGRID_API_USER = '' # SendGrid API User here
	SENDGRID_API_KEY = ''  # SendGrid API Pass here
	DEFAULT_SUBJECT = "I've shared a file to you from Box.com!"
	SENDGRID_API_URL = "https://sendgrid.com/api/mail.send.json"

	# Could be any database (used for session storage)
	DATABASES = {
	    'default': {
	        'ENGINE': 'django.db.backends.sqlite3',
	        'Name' : 'database.sqltie'
	        ...
	    }
	}

	INSTALLED_APPS = (
	    ...
	    'sendbox',
	)
	```
5. Also setup 'myproject/urls':
	```python
	urlpatterns = patterns('',
	    ...
	    url(r'', include('sendbox.urls')),
	)
	```
6. Now back to the command line:
	```
	python manage.py syncdb
	#no need for admin user
	```

7. You're good to go! Run this to test it out:
	```
	python manage.py runserver
	```