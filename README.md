# FastAPI Template Project

## Installation

### Install pyenv (optional step)

1. install [pyenv](https://github.com/pyenv/pyenv) to system (if not)
2. install [python 3.14](https://www.python.org/downloads/) with pyenv
3. setup pyenv for use python 3.14 in project folder

### Install python (required)
1. install [python 3.14](https://www.python.org/downloads/)

### Install project

1. install [poetry](https://python-poetry.org/docs/)
2. clone this project
3. cd to project directory
4. run:

```shell 
poetry install --with dev
```

## Start application (in dev mode)

In root folder of project:

```shell
poetry run uvicorn app.main:get_app --host 0.0.0.0 --port 8000 --reload --factory
```

Or separately:

```shell
poetry shell
```

```shell
uvicorn app.main:get_app --host 0.0.0.0 --port 8000 --reload --factory
```

# How work with migrations:

[source upgrade](https://alembic.sqlalchemy.org/en/latest/tutorial.html#running-our-first-migration)

```shell
alembic upgrade head
```