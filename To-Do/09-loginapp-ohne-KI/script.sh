#!/bin/bash

NETWORK=todo-net

network() {
    docker network inspect "$NETWORK" >/dev/null 2>&1 ||
        docker network create "$NETWORK"
}

run_db(){
    network || return
    docker run -p 5432:5432 \
    --rm \
    --network "$NETWORK" \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_DB=postgres-db \
    -v login-vol:/var/lib/postgresql \
    --name my-postgres-container postgres:19rc1-alpine
}

build_dev(){
    docker build -f Dockerfile --target dev -t login-app:dev . 
}

run_dev(){
    network || return
    docker run --rm \
    --name my-fastapi-login-container \
    -p 8000:8000 \
    --network="$NETWORK" \
    -v "$(pwd -W):/app" \
    -e WATCHFILES_FORCE_POLLING=true \
    login-app:dev
}

"$@"