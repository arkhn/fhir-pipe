#!/bin/sh


if [ "$#" -ne 1 ]; then
  echo "Usage: $0 http(s)://fhir-api.com" >&2
  exit 1
fi

i=0
while [ $i -lt 60 ]; do
  if curl -s $1 > /dev/null; then break; fi
  echo "API is unavailable - sleeping" >&2
  sleep 1
  i=$((i+1))
done
if [ $i -eq 60 ]; then exit 1; fi

echo "API is up - resuming execution"
