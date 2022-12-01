#!/bin/bash

usage="Debe ingresar la frecuencia de caos (en segundos)"

if [ $# -eq 0 ]; then
  echo "$usage"
  exit 1    
fi

KILL_FRECUENCY=$1

random_select(){
    ARRAY=("$@")
    SIZE=${#ARRAY[@]}
    INDEX=$(($RANDOM % $SIZE))
    SELECTED=${ARRAY[$INDEX]}
    echo $SELECTED
}

KILLEABLES=('^/thumbnail_router$' '^/thumbnail_[[:digit:]]+$' '^/joiner_[[:digit:]]+$')
KILL_SELECTED=$(random_select "${KILLEABLES[@]}")
echo $KILL_SELECTED

CONTAINERS=($(docker ps -aq --filter name="$KILL_SELECTED" --filter status=running))
CONTAINER_SELECTED=$(random_select "${CONTAINERS[@]}")

echo "Killing container $CONTAINER_SELECTED"