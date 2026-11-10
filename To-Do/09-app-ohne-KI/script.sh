#!/bin/bash

build_dev(){
    docker build --target dev -t todo-be:dev .
}

run_dev(){
    docker run --rm -p 8000:8000 \
    -v "${PWD}:/app" \
    -e WATCHFILES_FORCE_POLLING=true \
    --name todo-be todo-be:dev
}

$@ 