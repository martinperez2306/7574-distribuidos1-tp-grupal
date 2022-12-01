#!/bin/bash

KILLEABLES=('^/thumbnail_router$' '^/thumbnail_[[:digit:]]+$' '^/joiner_[[:digit:]]+$')
echo $KILLEABLES
SIZE=${#KILLEABLES[@]}
echo $SIZE
INDEX=$(($RANDOM % $SIZE))
echo $INDEX
KILL_SELECTED=${KILLEABLES[$INDEX]}
echo $KILL_SELECTED
CONTAINERS=($(docker ps -aq --filter name="$KILL_SELECTED"))
echo ${#CONTAINERS[@]}