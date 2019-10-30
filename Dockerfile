FROM alpine:3.10

RUN apk update

RUN apk add --no-cache \
    build-base \
    python3-dev

# Set the working directory to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

# Copy the current directory contents into the container at /app
COPY config_docker.yml /app/config.yml
COPY setup.py /app
COPY README.md /app
COPY ./fhirpipe /app/fhirpipe

RUN python3 setup.py install
