#!/bin/bash

#start
nohup python3 -u vraccount0.py 10000 &
nohup python3 -u vraccount1.py 10001 &
nohup python3 -u vraccount2.py 10002 &
nohup python3 -u vraccount3.py 10003 &

