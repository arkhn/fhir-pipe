#!/bin/sh


i=0
while [ $i -lt 15 ]; do
  if psql  postgres://$3:$4@$1:$2/$5 -c '\q' > /dev/null; then break; fi
  echo "Postgres is unavailable - sleeping" >&2
  sleep 1
  i=$((i+1))
done
if [ $i -eq 15 ]; then exit 1; fi

echo "Postgres is up - resuming execution"
