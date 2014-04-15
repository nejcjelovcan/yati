# YATI - Yet Another Translation Interface

## Requirements
postgresql database

## Installation
```
sudo apt-get install python-pip postgresql-9.3 postgresql-server-dev-9.3 postgresql-contrib-9.3 python-dev translation-toolkit
sudo pip install -r requirements.txt
```

### Javascript setup
@TODO include prebuilt js in repository so that this step is optional

#### Get node.js, ubuntu way (with maunal link)
```
sudo apt-get install nodejs npm
sudo ln -s /usr/bin/nodejs /usr/bin/node
echo "ffffffuuuuuuuuuuuu"
```

#### Build javascript
```
sudo npm -g install grunt-cli 
cd yati_js/
npm install
grunt
```

### Django setup

#### Postgresql setup

Make a database template that loads fuzzystrmatch module by default
```
sudo -u postgres psql -d template1 -c 'create extension fuzzystrmatch;'
```

Make a new user (this will ask you for a password, remember it for later)
```
sudo -u postgres createuser -d -P yati
```

Create a database
```
sudo -u postgres createdb -T template1 -O yati yatidb
```

#### Sync database
Open `yati/settings.py` and set the database password to whatever you typed in when creating user

It can happen that syncdb will fail because of guardian library. In case it happens, comment out 'guardian' app in settings.py and run syncdb and migrate, then uncomment it and run migrate again
```
cd yati/
./manage.py syncdb
./manage.py migrate
./manage.py collectstatic --link
./manage.py createsuperuser
```

Run tests just to be sure:
```
./manage.py test
```

Run django server:
```
./manage.py runserver
```
