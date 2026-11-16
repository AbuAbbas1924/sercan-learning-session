#!/bin/bash

NETWORK=test-network

init_network(){
    docker network create $NETWORK
}

run_db(){
    if ! docker network inspect "$NETWORK" >/dev/null 2>&1; then
    init_network;
    echo "network $NETWORK created"
    fi

    docker run \
        --rm \
        --network $NETWORK \
        -p 5432:5432 \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=postgres \
        -e POSTGRES_DB=postgres \
        -v test-${pwd}:/var/lib/postgresql \
        --name test-postgres \
        postgres:19rc1-alpine
}

build_dev(){
    docker build -t pdb:dev --target dev .
}
run_dev(){
    docker run \
        --rm \
        --network $NETWORK \
        -p 8000:8000 \
        --name run_dev \
        pdb:dev
}

$@