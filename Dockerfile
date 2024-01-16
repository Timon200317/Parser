FROM python:3.9.0

ENV DockerHOME=.

RUN mkdir -p $DockerHOME

WORKDIR $DockerHOME

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
COPY . $DockerHOME
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

COPY . .