# NAAC

### change directory to server
```
cd server
```

### Create a virtual environment
```
python -m venv venv
```

### get into the virtual environment
```
venv\Scripts\activate
```

### change directory to api
```
cd api
```
### make the sqlite3 database migrations 
```
python manage.py makemigrations
```

### migrate the sqlite3 database
```
python manage.py migrate
```

### create a superuser(admin)
```
python manage.py createsuperuser
```

### run the django project
```
python manage.py runserver
```
