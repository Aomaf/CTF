1. Make sure that you system has python >= 3.9
2. Create the a veritual python enviroment
	$ python3 -m venv env
3. Activate the source
Windows: $ env\Scripts\activate.bat
Linux-based:  $ source env/bin/activate

4. Install the following using pip
	$ pip install Django
	$ pip $ pip install asgiref
	$ pip install autopep8
	$ pip install dj-database-url
	$ pip install gunicorn
	$ pip install pycodestyle
	$ pip install python-decouple
	$ pip install pytz
	$ pip install sqlparse
	$ pip install toml
	$ pip install Unipath
	$ pip install whitenoise
	$ pip install six
	$ pip install django-random-id-model
	$ pip install django-mathfilters

5. Make migrations:
	$ (env) python website/manage.py migrate

6. Run server:
	$ (env) python website/manage.py runserver

7. Open web-browser and goto 127.0.0.1:8080
