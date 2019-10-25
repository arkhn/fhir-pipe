# Use an official Python runtime as a parent image
FROM python:3.7-slim

RUN apt-get update \
    && apt-get -y install build-essential \
    && apt-get -y install postgresql python-psycopg2 libpq-dev

# Set the working directory to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the current directory contents into the container at /app
COPY config_docker.yml /app/config.yml
COPY setup.py /app
COPY README.md /app
COPY ./fhirpipe /app/fhirpipe

RUN python setup.py install
