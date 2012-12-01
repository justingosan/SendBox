#SendBox

A Django Sample App integrating the Box.com and SendGrid API. You can check out a demo here: [SendBox](http://sendbox.ap01.aws.af.cm/).
Also an online guide here: [SendBox Guide](http://sendbox.ap01.aws.af.cm/doc/) 


##Requirements:

Django 1.4+
ElementTree 1.2+
Requests 0.14+

[Box](http://box.com) App API Key
[SendGrid](http://sendgrid.com) API Key


Quick Setup:

Install the required modules:
'''shell
pip install -r requirements
'''

Start a django project:
'''shell
python django-admin.py startproject 'myproject'
'''

Tweak 'myproject/settings':
'''python
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
'''

Also setup 'myproject/urls':
'''python
urlpatterns = patterns('',
    ...
    url(r'', include('sendbox.urls')),
)
'''

Now back to the command line:
'''shell
python manage.py syncdb
#no need for admin user
'''

You're good to go! Run this to test it out:
'''shell
python manage.py runserver
'''