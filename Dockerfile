# Use an official Python runtime as a parent image
FROM python:3.7-slim

# Dependencies
RUN apt-get update \
    && apt-get -y install build-essential \
    && apt-get -y install postgresql python-psycopg2 libpq-dev libaio1 wget unzip

# Install the oracle client
RUN wget https://download.oracle.com/otn_software/linux/instantclient/195000/instantclient-basic-linux.x64-19.5.0.0.0dbru.zip
RUN unzip instantclient-basic-linux.x64-19.5.0.0.0dbru.zip -d /opt/oracle
ENV LD_LIBRARY_PATH="/opt/oracle/instantclient_19_5:${LD_LIBRARY_PATH}"
ENV PATH="/opt/oracle/instantclient_19_5:${PATH}"

# Set the working directory to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the current directory contents into the container at /app
COPY config_docker.yml /app/config.yml
COPY start.sh /app
COPY uwsgi.ini /app
COPY setup.py /app
COPY README.md /app
COPY fhirpipe /app/fhirpipe

RUN python setup.py install

CMD ["./start.sh"]
