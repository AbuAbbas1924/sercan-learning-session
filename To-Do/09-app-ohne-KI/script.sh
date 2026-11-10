#!/bin/bash

build_dev(){
    docker build --target dev -t todo-be:dev .
}

run_dev(){
    MSYS_NO_PATHCONV=1 docker run --rm -p 8000:8000 \
    -v "$(pwd -W):/app" \
    -e WATCHFILES_FORCE_POLLING=true \
    --name todo-be todo-be:dev
}

$@ 