# Contributing


Install [uv](https://docs.astral.sh/uv/)


    git clone ..
    uv venv .venv --python 3.12
    source .venv/bin/activate
    uv sync --extra docs


## Run tests
    pytests tests


## Demo Application

    python manage.py migrate
    python manage.py demo
    python manage.py runserver

Navigate to http://localhost:8000/admin/ and login using any username/password
