#!/bin/bash

function start_icestorm {
    mkdir -p IceStorm
    icebox --Ice.Config=./config/icebox.config &
}

function wait_icestorm {
    while ! ss -ltnp 2> /dev/null | grep ":10000" > /dev/null; do
        sleep 1
        echo "Waiting..."
    done
}

function create_topics {
    for topic in $*; do
        echo "Create topic $topic"
        icestormadmin --Ice.Config=config/icestorm.config -e "create $topic"
    done
}

echo "Launching IceStorm..."
start_icestorm

echo "Waiting for IceStorm to become available..."
wait_icestorm

echo "Creting topics..."
create_topics "discovery" "authentication" "directory" "blob"
#create_topics "Discovery" "AuthenticationQuery" "DirectoryQuery" "BlobQuery"
