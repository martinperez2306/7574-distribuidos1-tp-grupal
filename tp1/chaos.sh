#!/bin/bash

usage="Debe ingresar la frecuencia de caos (en segundos) y el listado de servicios a tirar"

if [ $# -eq 0 ]; then
  echo "$usage"
  exit 1    
fi

KILL_FRECUENCY=$1
KILLEABLES=("${@:2}")

random_select(){
    ARRAY=("$@")
    SIZE=${#ARRAY[@]}
    INDEX=$(($RANDOM % $SIZE))
    SELECTED=${ARRAY[$INDEX]}
    echo $SELECTED
}

while true
do

  KILL_SELECTED=$(random_select "${KILLEABLES[@]}")
  echo $KILL_SELECTED

  CONTAINERS=($(docker ps -aq --filter name="$KILL_SELECTED" --filter status=running))
  if [ ${#CONTAINERS[@]} -eq 0 ]; then
    echo "Waiting for at least one $KILL_SELECTED"
  else
    CONTAINER_SELECTED=$(random_select "${CONTAINERS[@]}")
    echo "Killing container $CONTAINER_SELECTED"
    docker kill $CONTAINER_SELECTED
  fi

  sleep $KILL_FRECUENCY

done