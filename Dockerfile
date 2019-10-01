# Use an official Python runtime as a parent image
FROM python:3.7-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./fhirpipe /app/fhirpipe
COPY requirements.txt /app
COPY setup.py /app
COPY README.md /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN pip install -e .

RUN python setup.py install
