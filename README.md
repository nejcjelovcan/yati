# YATI - Yet Another Translation Interface

## Requirements
postgresql database with array support (9.0+?)

## Installation
`sudo apt-get install python-pip python-virtualenv`

`virtualenv env`	# optional
`source env/bin/activate` 	# optional

`pip install -r requirements.txt`

`cd yati_js/`  	# optional? - must include prebuilt javascripts in repository
`npm install`   # optional?
`grunt`         # optional?

@TODO create psql database and update settings.py

`cd ../yati/`
`./manage.py syncdb`
`./manage.py migrate`
`./manage.py collectstatic`

