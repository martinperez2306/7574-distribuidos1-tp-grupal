#!/bin/bash

usage="Debe ingresar la frecuencia de caos (en segundos)"

if [ $# -eq 0 ]; then
  echo "$usage"
  exit 1    
fi

KILL_FRECUENCY=$1

./chaos.sh $KILL_FRECUENCY '^/acceptor$' '^/downloader$' '^/tag_unique$' '^/thumbnail_router_[[:digit:]]+$' '^/trending_router$' '^/trending_top$' '^/thumbnail_[[:digit:]]+$' '^/joiner_[[:digit:]]+$' '^/dropper_[[:digit:]]+$' '^/like_filter_[[:digit:]]+$'