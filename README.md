# Event management app

This app allows user to manage events (create, fetch, update and delete) as well as register\unregister for them

## Project prerequirements

Pipenv needs to be installed

## Project setup

**Step 1**
pipenv shell

**Step 2**
pipenv install

**Step 3**
python manage.py migrate

**Step 4**
python manage.py runserver


## Docker

Alternatively you can run the project with docker.
Run the following command:

**docker-compose up --build**

## Migrations

You can run migrations in two following ways

**Docker**

docker-compose exec web pipenv run python manage.py migrate

**Regular way**

python manage.py migrate


## Swagger link

http://localhost:8000/swagger/


## Unit Test setup

**Regular way**         

Run the following command in command line: **pytest**

**Docker**

Run the following command in command line: **docker-compose exec web pipenv run pytest**       

