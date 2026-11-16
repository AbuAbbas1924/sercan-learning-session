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
    -e POSTGRES_USER=testpg \
    -e POSTGRES_PASSWORD=testpg \
    -e POSTGRES_DB=semi \
    -v todo-vol:/var/lib/postgresql \
    --name testpg-db postgres:19rc1-alpine
    echo "postgres has started"
}

build_base(){
    docker build -f Dockerfile-semi --target base -t testdocker:base .
}

build_dev(){
    docker build -f Dockerfile-semi --target dev -t testdocker:dev .
}

run_dev(){
    network || return
    MSYS_NO_PATHCONV=1 docker run --rm \
        --name testsemi \
        -p 8000:8000 \
        --network="$NETWORK" \
        -v "$(pwd -W):/app" \
        -e WATCHFILES_FORCE_POLLING=true \
        testdocker:dev
}

$@
