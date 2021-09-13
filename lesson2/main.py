#-*- coding:utf-8 -*-
import time
from job import run_today
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()
# 时间： 周一到周五每天早上9点25, 执行run_today
sched.add_job(run_today, 'cron', day_of_week='mon-fri', hour=9, minute=25)
sched.start()
