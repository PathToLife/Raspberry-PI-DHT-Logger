#!/usr/bin/env bash
nohup sudo python3 main.py > temp.log 2>&1 &
echo $! >save_pid.txt
