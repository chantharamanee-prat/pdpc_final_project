# Create super user
python manage.py createsuperuser

# Default username and password
admin user: admin
password: admin

# How to create database migration
## Use when the database schema in code was changed

python manage.py makemigrations pdpc (project name)
python manage.py migrate

# run project
python manage.py runserver