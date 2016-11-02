# fc-meeting-app

## 1. Getting started
### Required applications:
- git (obviously) or a git GUI client
- python2
- pip
- [heroku toolbelt](https://devcenter.heroku.com/articles/heroku-command-line)

### Dependency installation
To install all the required project dependencies use pip:
```
pip install -r requirements.txt
```
If all goes well you should be able to run the collectstatic command of the django management script:
```
damian@V3560:~/fc-meeting-app$ python manage.py collectstatic --noinput

0 static files copied to '/home/damian/fc-meeting-app/RWE/staticfiles', 135
unmodified.
```

### Setting up the environment
In order to run the project you will need to either set up a PostgreSQL™ database  locally or get a heroku hosted one. No matter which option you choose you will need to set up an enviornment variable (``` DATABASE_URL  ```) with the [database URL](https://github.com/kennethreitz/dj-database-url). You can permamently set it in bash by appending the following line to ~/.bashrc (this is just an example of course):
```
export DATABASE_URL=postgres://username:password@host:port/database_name
```
At this point you should be able to run the django development server with the runserver command:
```
python manage.py runserver
```

By default the server is run on localhost:8000.

## 2. Running locally with heroku
If you haven't already goone through the [heroku tool tutorial](https://devcenter.heroku.com/articles/heroku-command-line) do it now. After adding your heroku account to your local config, try setting the heroku remotes in your repository:
```
heroku git:remote -a APP_NAME
```
APP_NAME should be the name of your review application.
If all goes well you will be able to see the configuration variables of your development app with this command:
```
heroku config
```
If this works you should be able to run the local server (which sets up an environment close to what will be used in production) with the following command:
```
heroku local web
```
By default the server starts up on localhost:5000
