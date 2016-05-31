#!/bin/bash

rm -rf /opt/docklet/local/log/*

bin/docklet-worker stop

bin/docklet-master stop

bin/docklet-master init

bin/docklet-worker start

bin/docklet-master restart
