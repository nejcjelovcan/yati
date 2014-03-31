# YATI - Yet Another Translation Interface

## Requirements
postgresql database

## Installation
```
sudo apt-get install python-pip
pip install -r requirements.txt
```

### Javascript setup
@TODO install node and npm
@TODO include prebuilt js in repository so that this step is optional
```
cd yati_js/  	
npm install
grunt
```
### Django setup
@TODO create psql database and update settings.py
```
cd yati/
./manage.py syncdb
./manage.py migrate
./manage.py collectstatic
./manage.py runserver
```
