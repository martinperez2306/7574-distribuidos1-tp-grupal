#!/bin/bash
var=$(docker ps -qf "name=client")

log_folder="./.tmp/logs"

#Create logs output folder.
mkdir -p $log_folder

for container_id in $var
do  
    image_name=$(docker ps -qf "id=${container_id}" --format "{{.Names}}")
    echo "Running Client $image_name"
    docker exec $container_id python3 main.py > $log_folder/$image_name.log 2>&1 &
done

wait
