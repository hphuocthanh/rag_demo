#!/usr/bin/env bash

# wait-for-it.sh - Wait until a specified host and port are available, then run a command

set -e

host="$1"
port="$2"
shift 2
cmd="$@"

echo "Waiting for $host:$port to be available..."

while ! nc -z "$host" "$port"; do
  sleep 2
  echo "Still waiting for $host:$port..."
done

echo "$host:$port is available. Proceeding with execution."
exec $cmd
