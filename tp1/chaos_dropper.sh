#!/bin/bash

usage="Debe ingresar la frecuencia de caos (en segundos)"

if [ $# -eq 0 ]; then
  echo "$usage"
  exit 1    
fi

KILL_FRECUENCY=$1

./chaos.sh $KILL_FRECUENCY '^/dropper_[[:digit:]]+$'