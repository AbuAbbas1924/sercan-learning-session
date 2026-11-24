#!/bin/bash

NETWORK=my-login-net

network() {
    docker network inspect "$NETWORK" >/dev/null 2>&1 ||
        docker network create "$NETWORK"
}

run_db(){
    network || return
    # Optionally add -d to run the container in the background.
    # --env-file .env supplies the database settings from .env.
    docker run \
    --rm \
    --network "$NETWORK" \
    -p 5432:5432 \
    --env-file .env \
    -v login-vol:/var/lib/postgresql \
    --name my-postgres-container \
    postgres:19rc1-alpine
}

build_dev(){
    docker build -f Dockerfile --target dev -t login-app:dev . 
}

run_dev(){
    network || return
    docker run \
    --rm \
    --env-file .env \
    --network="$NETWORK" \
    -p 8000:8000 \
    -v "$(pwd -W):/app" \
    -e WATCHFILES_FORCE_POLLING=true \
    --name my-fastapi-login-container \
    login-app:dev
}

"$@"
