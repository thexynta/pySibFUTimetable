#!/bin/bash

cd ~/PycharmProjects/pySibFUTimetable_bot
./scheduleCronExec.py $1 $2 >> ./logs/cron_exec.log
