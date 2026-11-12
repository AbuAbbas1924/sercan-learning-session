#!/bin/bash

NETWORK=todo-net

network() {
    docker network inspect "$NETWORK" >/dev/null 2>&1 ||
        docker network create "$NETWORK"
}

run_db(){
    network
    docker run -p 5432:5432 \
    -d \
    --network $NETWORK \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_DB=sercan_todo \
    -v todo-vol:/var/lib/postgresql \
    --name todo-db postgres:19rc1-alpine
    echo "postgres has started"
}

build_dev(){
    docker build --target dev -t todo-be:dev .
}

run_dev(){
    network
    MSYS_NO_PATHCONV=1 docker run --rm -p 8000:8000 \
    --network=$NETWORK \
    -v "$(pwd -W):/app" \
    -e WATCHFILES_FORCE_POLLING=true \
    --name todo-be todo-be:dev
}

$@ 