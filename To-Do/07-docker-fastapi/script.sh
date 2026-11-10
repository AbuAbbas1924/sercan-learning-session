#！/bin/bash

run_postgres(){
    echo "Running Postgres container..."
}

build_dev(){
    docker build --target dev -t todo-be:dev .
}

run_dev(){
    docker run --rm -p 8000:8000 \
    -v "${PWD}:/app" \
    -e WATCHFILES_FORCE_POLLING=true \
    --name todo-be todo-be:dev

}

run_db_dev(){
    run_postgres;
    run_dev;
}

build_prod(){
    docker build --target prod -t todo-be:prod .
}

run_prod(){
    docker run --rm -p 8000:8000 \
    --name todo-be todo-be:prod
}

$@