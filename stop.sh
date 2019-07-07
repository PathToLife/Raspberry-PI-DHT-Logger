#!/usr/bin/env bash
if test -f "save_pid.txt"; then
	sudo kill -15 `cat save_pid.txt`
	rm save_pid.txt
fi
python3 clear_display.py
