#!/bin/bash

rm -rf /opt/docklet/local/log/*

bin/docklet-worker stop

sleep 1

bin/docklet-master stop

sleep 1

bin/docklet-master reinit

sleep 3

bin/docklet-worker start

sleep 3

bin/docklet-master restart
