#!/usr/bin/env sh

REPOSITORY=$1
QUERY=$2

if [ -z "$QUERY" ]; then
    open "$REPOSITORY"
else
    open "$REPOSITORY/search?q=$QUERY"
fi
