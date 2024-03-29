# /bin/bash

# Start docker service
# sudo systemctl start docker  # (on linux)
# Start docker desktop on MacOS X

#docker network create mynet

docker run -d \
    --name mysql \
    --network mynet \
    -e MYSQL_ROOT_PASSWORD="ctfVGBUIJ67gyBUINXERCTr6vt7bHNJ" \
    -v opt_mysql:/var/lib/mysql \
    -p 3306:3306 \
    mysql:8.0.12

docker run -d \
    --name phpmyadmin \
    --network mynet \
    -e PMA_HOST=mysql \
    -p 8080:80 \
    phpmyadmin/phpmyadmin

# docker build -t xescrap .

