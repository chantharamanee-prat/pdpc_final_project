# How to start the server

## Start docker compose

1. **Run:** docker-compose up -d
2. Open http://localhost:8000
3. If facing an error. follow steps below

## Migrate database
1. **Run:** docker-compose exec web python manage.py migrate
2. Open http://localhost:8000 again

## Create admin user
1. **Run:** docker-compose exec web python manage.py createsuperuser
2. Open http://localhost:8000/admin
3. Use username & password from (1)

