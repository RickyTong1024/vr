#!/bin/bash

#stop

kill $(ps -ef | grep 'python -u vraccount'|awk '{print $2}')
